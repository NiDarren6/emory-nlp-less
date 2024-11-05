import pandas as pd
import os
import sys
from collections import defaultdict

sys.path.insert(0, 'emory-nlp-less/src')
from util import get_sqlite_schema

def load_gold_pred_data(base_dir, db_dir_path, dev_folders, output_dir):
    data_frames = {}
    db_schema_cache = defaultdict(str)
    
    for folder in dev_folders:
        folder_path = os.path.join(base_dir, folder)
        
        gold_path = os.path.join(folder_path, 'gold.txt')
        print(f"Checking for gold.txt at: {gold_path}")  
        if not os.path.exists(gold_path):
            print(f"Warning: gold.txt not found in {folder}")
            continue

        
        gold_entries = []
        with open(gold_path, 'r') as file:
            for line in file:
                if line.strip():
                    parts = line.strip().split('\t')
                    if len(parts) == 2:
                        sql_query, db_name = parts
                        if db_name not in db_schema_cache:
                            db_schema_cache[db_name] = get_sqlite_schema(db_name, db_dir_path)
                        gold_entries.append({'gold': sql_query, 'db_name': db_name, 'db_schema': db_schema_cache[db_name]})
        
        gold_df = pd.DataFrame(gold_entries)
        
        for file_name in os.listdir(folder_path):
            if file_name.endswith('.txt') and file_name != 'gold.txt':
                model_name = file_name.replace('.txt', '')
                pred_path = os.path.join(folder_path, file_name)
                
                pred_lines = [line.strip() for line in open(pred_path, 'r') if line.strip()]
                
                if len(pred_lines) == len(gold_df):
                    gold_df[model_name] = pred_lines
                else:
                    print(f"Warning: {model_name} predictions in {folder} do not match gold length.")
        
        data_frames[folder] = gold_df
        output_path = os.path.join(output_dir, f'{folder}_dataframe.csv')
        gold_df.to_csv(output_path, index=False)
        print(f"DataFrame for {folder} saved to {output_path}")
    
    return data_frames

base_dir = '../data'
db_dir_path = '../data/testsuitedatabases/database'
output_dir = '../data/evaluation_dfs'
dev_folders = ['spider_dev', 'spider_test', 'cosql_dev']
os.makedirs(output_dir, exist_ok=True)

data_frames = load_gold_pred_data(base_dir, db_dir_path, dev_folders, output_dir)
