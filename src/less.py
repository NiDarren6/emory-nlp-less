import util
import less_prompts
import logging
import os
import time
from openai import OpenAI

client = OpenAI()

DEFAULT_MODEL = "gpt-4o"
ANNOTATED_BIRD_FALSEPOGNEG_FILEPATH = 'data/annotated_bird_falsepogneg.csv'
DATABASES_FILEPATH = 'data/bird_dev/dev_databases'


def less(
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
    new_rules = []
    start_time = time.time()
    for index, row in data.iterrows():
        gold_query = row['gold']
        pred_query = row['pred']
        db_schema = row['db_schema']
        new_rules_str = "\n".join(new_rules)

        system_prompt = less_prompts.RuleGenerationPrompts.SYSTEM_PROMPT(
            esmp_rules=less_prompts.RuleGenerationPrompts.ESM_P_RULES,
            new_rules=new_rules_str
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

        print(f"RULE CANDIDATE {index+1}/{184}:\n{rule_candidate}")
        user_check = input("Type \"y\" to accept, \"n\" to reject the current RULE CANDIDATE\n")
        if user_check == 'y':
            print("\n---------------- NEW RULE ADDED TO PROMPT ----------------\n")
            new_rules.append(rule_candidate)
        elif user_check == 'n':
            pass
        else:
            print("Invalid input. Please enter \"y\" or \"n\".")

        cur_time = time.time()
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
            user_check=user_check,
            time=cur_time
        )
    end_time = time.time()
    elapsed_time = end_time - start_time
    logging.info(f"Number of rule candidates: {len(new_rules)}")
    print("---------------------------------------------------------------")
    print(f"COMPLETION STATS:")
    print(f"Elapsed time: {elapsed_time:.2f} seconds")
    print(f"Number of rule candidates: {len(new_rules)}")
    print("---------------------------------------------------------------")


def record_sample_log(
    index: int,
    gold_query: str,
    pred_query: str,
    db_schema: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
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
    logging.info(f"time: {time}")
    logging.info(f"-----------------------------------------------------")

if __name__ == "__main__":
    less()
