import openai
from src import util

ANNOTATED_BIRD_FALSEPOGNEG_FILEPATH = 'data/annotated_bird_falsepogneg.csv'
DATABASES_FILEPATH = 'data/bird_dev/dev_databases'
BASE_PROMPT = f"""
"""

def less():
    data = util.preprocess_annotated_data(
        filename=ANNOTATED_BIRD_FALSEPOGNEG_FILEPATH,
        db_dir_path=DATABASES_FILEPATH
    )

    for index, row in data.iterrows():
        pass
    

