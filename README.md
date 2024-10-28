# Learning LESS: <u>L</u>ogical <u>E</u>quivalence for <u>S</u>tructured Querie<u>S</u>

## Getting Started:
- Download BIRD [Dev set](https://bird-bench.oss-cn-beijing.aliyuncs.com/dev.zip) to `data` folder and rename it to `bird_dev`.
- Create file called `API-KEY` under `src` folder, and paste your OpenAI API key inside.

## Loading Rule Generation Progress:
- You can stop rule generation using `Ctrl + C` during code execution.
- After each rule is accepted, current set of rules are automatically saved in `logs/progress.pkl`.
  - To examine: use the following template. 
    ```
    import pickle as pk
    with open(<progress.pkl file path>, 'rb') as file:
        index, rules = pk.load(file)
    ```
  - `index: int` marks the number of queries that have already been checked for potential equivalence rules.
  - `rules: list[str]` are all the accepted equivalence rules stored in a `list`.
- When you run `less.py` again, past progress will be automatically loaded, if any.