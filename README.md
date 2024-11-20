# *LESS*: *L*earning Logical *E*quivalence for *S*tructured Querie*S*

## Getting Started:
- Download BIRD [Dev set](https://bird-bench.oss-cn-beijing.aliyuncs.com/dev.zip) to `data` folder and rename it to `bird_dev`.
- Create file called `API-KEY` under `src` folder, and paste your OpenAI API key inside.

## Loading Rule Generation Progress:
- You can stop rule generation using `Ctrl + C` during code execution.
- After each rule is accepted, current set of rules are automatically saved in `logs/rules-run#.json`.
  - You can (optionally) load it using the following template. 
    ```
    import json
    with open(<rules-run#.json file path>, 'r') as file:
        progress = json.load(fp=file)
    index, rules = progress['index'], ['\n'.join(rule) for rule in progress['rules'].values()]
    ```
  - `rules-run#.json` is stored as a dictionary with two keys: `'index'` and `'rules'`:
    - Value of `'index'` marks the number of queries that have already been checked for potential equivalence rules.
    - Value of `'rules'` is formatted as a dictionary.
  - After extraction, `rules: list[str]` is a `list` of all the accepted equivalence rules.
- When you run `less.py` again, past progress will be automatically loaded, if any.

## Running `less.py`:
- `less.py` contains two arguments:
  - `-s` or `--shuffle` (boolean): Include -s if example rules should be SHUFFLED in the prompt
  - `-k` or `--top_k_rules` (int): Number of existing rules to sample for example rules in the prompt
    - `-k 0` turns off top k sampling of the rules.
  - `-e` or `--use_esmp_rules` (boolean): Include -e if ESM+ rules should be considered for example rules in the prompt
  - `-o` or `--override_auto_cot` (boolean): Include -o to prevent LESS from using auto-CoT
- Example command: `python less.py -s -k 20`.