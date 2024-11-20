from openai import OpenAI
import util, less_prompts, logging, os, time, json, argparse


with open(f'{os.path.dirname(__file__)}/API-KEY', 'r') as key:
    api_key = key.readline()
client = OpenAI(api_key=api_key)

DEFAULT_MODEL = "gpt-4o"
ANNOTATED_BIRD_FALSEPOGNEG_FILEPATH = f'{os.path.dirname(os.path.dirname(__file__))}/data/annotated_bird_falsepogneg.csv'
DATABASES_FILEPATH = f'{os.path.dirname(os.path.dirname(__file__))}/data/bird_dev/dev_databases'


def less(
    shuffle: bool,
    top_k: int,
    override_auto_cot: bool,
    start_index: int,
    current_rules: list[str],
    log_dir: str,
    model: str = DEFAULT_MODEL
):
    """
    Executes LESS rule generation pipeline to generate SQL equivalence rules.

    Args:
        model: The model name to use for generating SQL equivalence rules. Defaults
        to the constant DEFAULT_MODEL.

    The function performs the following steps:
    1. Preprocesses annotated data to obtain SQL queries and database schemas.
    2. Uses the provided model to generate rule candidates based on the gold and
       predicted SQL queries.
    3. Prompts the user to accept or reject each rule candidate.
    4. Logs the details of each rule generation attempt.
    5. Prints completion statistics including elapsed time and the number of rules
       generated.
    """
    data = util.preprocess_annotated_data(
        annotated_falsepogneg_filepath=ANNOTATED_BIRD_FALSEPOGNEG_FILEPATH,
        db_dir_path=DATABASES_FILEPATH
    )
    new_rules = current_rules
    start_time = time.time()
    for index, row in data.iterrows():
        if index < start_index:
            continue
        
        db_schema, gold_query, pred_query = row['db_schema'], row['gold'], row['pred']

        prompt = (
            less_prompts.RuleGenerationPrompts.SYSTEM_PROMPT() + '\n\n\n\n' + 
            less_prompts.RuleGenerationPrompts.EXAMPLE_RULES(
                rules=[] if override_auto_cot else new_rules,
                # rules=less_prompts.RuleGenerationPrompts.ESM_P_RULES() + new_rules,
                shuffle=shuffle, top_k=top_k
            ) + '\n\n\n\n' + 
            less_prompts.RuleGenerationPrompts.GUIDELINES() + '\n\n\n\n' +
            less_prompts.RuleGenerationPrompts.QUERY(
                schema=db_schema, 
                gold=gold_query,
                machine=pred_query
            )
        )

        response = client.chat.completions.create(
            model=model,
            temperature=0.5,
            messages=[{'role': 'user', 'content': prompt}],
            stop=less_prompts.NEW_RULE_TAG[-1]
        )
        rule_candidate = response.choices[0].message.content
        rule_candidate = rule_candidate[rule_candidate.find(less_prompts.NEW_RULE_TAG[0]):rule_candidate.find(less_prompts.NEW_RULE_TAG[-1])]
        rule_candidate = rule_candidate[len(less_prompts.NEW_RULE_TAG[0]+'\n'):]
        
        print(f"RULE CANDIDATE {index+1}/{len(data)}:\n{rule_candidate}")
        if rule_candidate.strip() == 'Not equivalent':
            print("No equivalence rule generated since queries are not logically equivalent.\n")
            yield index+1, new_rules
            continue
        if rule_candidate.strip() == 'Rule exists':
            print("No new equivalence rule generated: rule already exists.\n")
            yield index+1, new_rules
            continue
        
        user_check = ''
        while user_check.lower() not in {'y', 'n'}:
            user_check = input("Type \"y\" to accept, \"n\" to reject the current RULE CANDIDATE\n")
        print()
        if user_check == 'y':
            print("---------------- NEW RULE ADDED TO PROMPT ----------------\n")
            new_rules.append(rule_candidate)

        cur_time = time.time()
        record_sample_log(
            log_dir=log_dir,
            index=index,
            gold_query=gold_query,
            pred_query=pred_query,
            db_schema=db_schema,
            model=model,
            prompt=prompt,
            response=response,
            rule_candidate=rule_candidate,
            user_check=user_check,
            time=cur_time
        )
        
        yield index+1, new_rules
        
    end_time = time.time()
    elapsed_time = end_time - start_time
    logging.info(f"Number of rule candidates: {len(new_rules)}")
    print("---------------------------------------------------------------")
    print(f"COMPLETION STATS:")
    print(f"Elapsed time: {elapsed_time:.2f} seconds")
    print(f"Number of rule candidates: {len(new_rules)}")
    print("---------------------------------------------------------------")


def record_sample_log(
    log_dir: str,
    index: int,
    gold_query: str,
    pred_query: str,
    db_schema: str,
    model: str,
    prompt: str,
    response: str,
    rule_candidate: str,
    user_check: str,
    time: float
) -> None:
    """
    Records sample data to a log file.
    
    Parameters:
    index (int): Sample index
    gold_query (str): Gold query
    pred_query (str): Predicted query
    db_schema (str): Database schema
    model (str): Model name
    system_prompt (str): System prompt
    user_prompt (str): User prompt
    response (str): Model response
    rule_candidate (str): Rule candidate generated by the model
    user_check (str): User check result ('y' or 'n')
    time (float): Time taken to check the rule candidate
    """    
    log_file = os.path.join(log_dir, f"less_experiment_log.txt")
    logging.basicConfig(filename=log_file, level=logging.INFO)
    logging.info(f"-----------------------------------------------------")
    logging.info(f"index: {index}")
    logging.info(f"gold_query: {gold_query}")
    logging.info(f"pred_query: {pred_query}")
    logging.info(f"db_schema: {db_schema}")
    logging.info(f"model: {model}")
    logging.info(f"prompt: {prompt}")
    logging.info(f"response: {response}")
    logging.info(f"rule_candidate: {rule_candidate}")
    logging.info(f"user_check: {user_check}")
    logging.info(f"time: {time}")
    logging.info(f"-----------------------------------------------------")


def main(args):
    shuffle, top_k, esmp, override = args.shuffle, args.top_k_rules, args.use_esmp_rules, args.override_auto_cot
    
    # logs directory
    log_dir = f'{os.path.dirname(os.path.dirname(__file__))}/logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # load current progress, if any
    progress = {'index': 0, 'rules': dict()}
    if os.path.exists(f'{log_dir}/current-rules.json'):
        with open(f'{log_dir}/current-rules.json', 'r') as progress:
            progress = json.load(fp=progress)
    index, current_rules = progress['index'], ['\n'.join(rule) for rule in progress['rules'].values()]

    # run LESS
    print(f'Looking to start at row {index+1} in the dataset...\n')
    for index, current_rules in less(shuffle=shuffle, top_k=top_k, override_auto_cot=override, start_index=index, current_rules=current_rules, log_dir=log_dir):
        progress['index'] , progress['rules'] = index, {f'{i+1}': rule.split('\n') for i, rule in enumerate(current_rules)}
        with open(f'{os.path.dirname(os.path.dirname(__file__))}/logs/current-rules.json', 'w') as file:
            json.dump(obj=progress, fp=file, indent=4)

    # save config of run
    config = dict()
    if os.path.exists(f'{log_dir}/config.json'):
        with open(f'{log_dir}/config.json', 'r') as config:
            config = json.load(fp=config)
    run = len(config.keys())+1
    config[f'Run {run}'] = {
        'Shuffle example rules': shuffle,
        'Top k rules to select': False if top_k == 0 else top_k,
        'Use ESM+ rules in example rules': esmp,
        'Override LESS auto-CoT': override,
        'Save rules to JSON file': f'rules-run{run}.json'
    }
    with open(f'{log_dir}/config.json', 'w') as file:
        json.dump(obj=config, fp=file, indent=4)
    
    # finalize the output file names
    os.rename(
        src=f'{os.path.dirname(os.path.dirname(__file__))}/logs/current-rules.json', 
        dst=f'{os.path.dirname(os.path.dirname(__file__))}/logs/rules-run{run}.json'
    )
    os.rename(
        src=f'{os.path.dirname(os.path.dirname(__file__))}/logs/less_experiment_log.txt', 
        dst=f'{os.path.dirname(os.path.dirname(__file__))}/logs/rules-run{run}-log.txt'
    )
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--shuffle', action='store_true', help='(bool) include -s if example rules should be SHUFFLED in the prompt')
    parser.add_argument('-k', '--top_k_rules', default=0, type=int, help='(int) number of existing rules to sample for example rules in the prompt')
    parser.add_argument('-e', '--use_esmp_rules', action='store_true', help='(bool) include -e if ESM+ rules should be considered for example rules in the prompt')
    parser.add_argument('-o', '--override_auto_cot', action='store_true', help='(bool) include -o to prevent LESS from using auto-CoT')
    args = parser.parse_args()
    main(args=args)
