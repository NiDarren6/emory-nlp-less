# Learning *LESS*: *L*ogical *E*quivalence for *S*tructured Querie*S*

## Getting Started:
- Download BIRD [Dev set](https://bird-bench.oss-cn-beijing.aliyuncs.com/dev.zip) to `data` folder and rename it to `bird_dev`.
- Create file called `API-KEY` under `src` folder, and paste your OpenAI API key inside.

## Loading Rule Generation Progress:
- You can stop rule generation using `Ctrl + C` during code execution.
- After each rule is accepted, current set of rules are automatically saved in `logs/current-rules.json`.
  - You can (optionally) load it using the following template. 
    ```
    import json
    with open(<current-rules.json file path>, 'r') as file:
        progress = json.load(fp=file)
    index, rules = progress['index'], ['\n'.join(rule) for rule in progress['rules'].values()]
    ```
  - `current-rules.json` is stored as a dictionary with two keys: `'index'` and `'rules'`:
    - Value of `'index'` marks the number of queries that have already been checked for potential equivalence rules.
    - Value of `'rules'` is formatted as a dictionary.
  - After extraction, `rules: list[str]` is a `list` of all the accepted equivalence rules.
- When you run `less.py` again, past progress will be automatically loaded, if any.