import json
import os

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

def generate_prompts(question_num: int) -> list[tuple[str, str]]:
    """Generate system prompts for each question number."""
    system_prompts = []
    
    with open('tpch_questions.json', 'r') as f:
        questions = json.load(f)
    
    with open('prompts/rag/database_schema.txt', 'r') as schema_file:
        database_schema = schema_file.read()
    
    prompt = questions.get(str(question_num))
    if prompt:
        user_prompt = "<natural_language_query>" + prompt + "</natural_language_query>" + '\n\n<database_schema>' + database_schema + '</database_schema>'
    
    # Get all system prompts
    system_prompt_files = [f for f in os.listdir('prompts/system') if f.endswith('.txt')]
    for system_file in system_prompt_files:
        with open(os.path.join('prompts/system', system_file), 'r') as f:
            system_content = f.read()
        
        if system_file == 'improve_solution.txt':
            with open(f'benchmark_queries/{question_num:02d}.sql', 'r') as query_file:
                original_query = query_file.read()
            system_content += f'\n\n<original_query>{original_query}</original_query>'
        
        system_prompts.append((system_content, user_prompt))
    
    return system_prompts
