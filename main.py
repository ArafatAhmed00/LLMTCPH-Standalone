import json

from helpers import create_prompt_question, run_query, validate_answer

def store_results(question_num: int, execution_time: float, validated: bool, prompt_num: int, model: str) -> None:
    """Store the results of a query in a CSV file."""
    with open('results.csv', 'a') as f:
        f.write(f"{question_num},{execution_time},{validated},{prompt_num},{model}\n")

def create_results_csv() -> None:
    """Create a CSV file to store the results of the queries."""
    with open('results.csv', 'w') as f:
        f.write("Question,Execution Time,Validated,Prompt,Model\n")

def get_models() -> list[str]:
    """Get a list of models to test."""
    with open('models.json', 'r') as f:
        models_data = json.load(f)
    return models_data['models']
