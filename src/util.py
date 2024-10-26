"""
This module provides functions to preprocess annotated data for the falsepogneg
task.

The main function is `preprocess_annotated_data`, which takes in a CSV file
containing annotated data and a directory containing the corresponding SQLite
databases. It returns a Pandas DataFrame containing the preprocessed data.

The function works by iterating over the rows of the CSV file, extracting the
database name from each row, and adding the database schema to the row. The
database schema is obtained using the `get_sqlite_schema` function.

The `get_sqlite_schema` function takes in a database name and a directory
containing the corresponding SQLite database file. It returns a string
containing the SQL CREATE statements for all database objects.

"""

import os
import re
import sqlite3
import pandas as pd
from collections import defaultdict

ANNOTATED_BIRD_FALSEPOGNEG_FILEPATH = 'data/annotated_bird_falsepogneg.csv'
DATABASES_FILEPATH = 'data/bird_dev/dev_databases'


def preprocess_annotated_data(
        annotated_falsepogneg_filepath: str,
        db_dir_path: str
) -> pd.DataFrame:
    """
    Preprocesses annotated data for the falsepogneg task.

    Args:
        annotated_falsepogneg_filepath: Path to a CSV file containing annotated
            data.
        db_dir_path: Path to a directory containing the corresponding SQLite
            databases.

    Returns:
        A Pandas DataFrame containing the preprocessed data.
    """
    # Import data
    data = pd.read_csv(annotated_falsepogneg_filepath)
    data = data[['gold', 'pred', 'True equivalence']]

    db_schema = defaultdict(str)
    pattern = r"^(.*?)\t"

    # Process data and save
    for i, gold_value in enumerate(data['gold']):
        match = re.match(pattern, gold_value)
        if match:
            gold_query = match.group(1)
            db_name = gold_value[match.end():]

            if db_name not in db_schema:
                db_schema[db_name] += get_sqlite_schema(
                    db_name=db_name,
                    db_dir_path=db_dir_path
                )
            
            data.loc[i, 'db_schema'] = db_schema[db_name]
        else:
            print(f"WARNING: No database name found in row {i}")

    return data


def get_sqlite_schema(
        db_name: str,
        db_dir_path: str
) -> str:
    """
    Retrieves the database schema of a SQLite file as a string.

    Args:
        db_name: Name of the database.
        db_dir_path: Path to a directory containing the corresponding SQLite
            database file.

    Returns:
        A string containing the SQL CREATE statements for all database objects.
    """
    db_file = os.path.join(db_dir_path, db_name, db_name + '.sqlite')

    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()

        # Query the sqlite_master table to get schema information
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' OR type='index' OR type='view' OR type='trigger'")
        schema = ""
        for row in cursor.fetchall():
            if row[0] is not None:  # Add this check
                schema += row[0] + ";\n"

    return schema
