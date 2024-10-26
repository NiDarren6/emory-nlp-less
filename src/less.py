from openai import OpenAI
import util
import less_prompts
import logging
import os

client = OpenAI()

DEFAULT_MODEL = "gpt-4o"
ANNOTATED_BIRD_FALSEPOGNEG_FILEPATH = 'data/annotated_bird_falsepogneg.csv'
DATABASES_FILEPATH = 'data/bird_dev/dev_databases'


def less(
    model: str = DEFAULT_MODEL
):
    data = util.preprocess_annotated_data(
        annotated_falsepogneg_filepath=ANNOTATED_BIRD_FALSEPOGNEG_FILEPATH,
        db_dir_path=DATABASES_FILEPATH
    )
    new_rules = []
    
    for index, row in data.iterrows():
        gold_query = row['gold']
        pred_query = row['pred']
        db_schema = row['db_schema']
        
        system_prompt = less_prompts.RuleGenerationPrompts.SYSTEM_PROMPT(
            esmp_rules=less_prompts.RuleGenerationPrompts.ESM_P_RULES,
            new_rules=new_rules
        )
        user_prompt = less_prompts.RuleGenerationPrompts.USER_PROMPT(
            gold_query=gold_query, 
            pred_query=pred_query, 
            db_schema=db_schema
        )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {  
                    "role": "system", 
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        )
        rule_candidate = response.choices[0].message.content

        print(f"RULE CANDIDATE:\n{rule_candidate}")
        user_check = input("Type \"y\" to accept, \"n\" to reject the current RULE CANDIDATE\n")

        if user_check == 'y':
            print("\n---------------- NEW RULE ADDED TO PROMPT ----------------\n")
            new_rules.append(rule_candidate)
        elif user_check == 'n':
            pass
        else:
            print("Invalid input. Please enter \"y\" or \"n\".")

        record_sample_log(
            index=index,
            gold_query=gold_query,
            pred_query=pred_query,
            db_schema=db_schema,
            model=model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response=response,
            rule_candidate=rule_candidate,
            user_check=user_check
        )


def record_sample_log(index, gold_query, pred_query, db_schema, model, system_prompt, user_prompt, response, rule_candidate, user_check):
    """Generate a log file for each step"""    
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, f"less_experiment_log.txt")
    logging.basicConfig(filename=log_file, level=logging.INFO)
    logging.info(f"-----------------------------------------------------")
    logging.info(f"index: {index}")
    logging.info(f"gold_query: {gold_query}")
    logging.info(f"pred_query: {pred_query}")
    logging.info(f"db_schema: {db_schema}")
    logging.info(f"model: {model}")
    logging.info(f"system_prompt: {system_prompt}")
    logging.info(f"user_prompt: {user_prompt}")
    logging.info(f"response: {response}")
    logging.info(f"rule_candidate: {rule_candidate}")
    logging.info(f"user_check: {user_check}")
    logging.info(f"-----------------------------------------------------")

if __name__ == "__main__":
    less()
