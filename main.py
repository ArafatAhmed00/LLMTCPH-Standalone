import json
import os
import re
import sqlite3

from ai import AI
from helpers import create_prompt_question, run_query, validate_answer

def create_results_db() -> None:
    """Create a SQLite database to store the results of the queries."""
    conn = sqlite3.connect('results.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS results
                      (question_num INTEGER, execution_time REAL, validated BOOLEAN, 
                       model TEXT, system_prompt TEXT, 
                       model_response TEXT, extracted_sql TEXT)''')
    conn.commit()
    conn.close()

def store_results(question_num: int, execution_time: float, validated: bool, 
                  model: str, system_prompt: str, 
                  model_response: str, extracted_sql: str) -> None:
    """Store the results of a query in the SQLite database."""
    conn = sqlite3.connect('results.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO results 
                      (question_num, execution_time, validated, model, 
                       system_prompt, model_response, extracted_sql) 
                      VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                   (question_num, execution_time, validated, model, 
                    system_prompt, model_response, extracted_sql))
    conn.commit()
    conn.close()

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
    
    # Get expected columns from the .ans file
    with open(f'expected_results/{question_num:02d}.ans', 'r') as f:
        expected_columns = f.readline().strip()
    
    # Get all system prompts
    system_prompt_files = [f for f in os.listdir('prompts/system') if f.endswith('.txt')]
    for system_file in system_prompt_files:
        with open(os.path.join('prompts/system', system_file), 'r') as f:
            system_content = f.read()
        
        if system_file == 'improve_solution.txt':
            with open(f'benchmark_queries/{question_num:02d}.sql', 'r') as query_file:
                original_query = query_file.read()
            system_content += f'\n\n<original_query>{original_query}</original_query>'
        
        system_content += f'\n\n<expected_columns>{expected_columns}</expected_columns>'
        
        system_prompts.append((system_content, user_prompt))
    
    return system_prompts

def extract_query_from_response(response: str) -> str:
    """Extract the query from the response."""
    match = re.search(r'<query>(.*?)</query>', response, re.DOTALL)
    return match.group(1).strip() if match else ''

def main() -> None:
    """Run the main program."""
    create_results_db()
    
    for question_num in range(17, 23):
        print(f"\nRunning query for question {question_num}:")
        
        with open(f'benchmark_queries/{question_num:02d}.sql', 'r') as f:
            query = f.read()
        
        ai = AI()
        
        for model in get_models():
            print(f"Running query for model: {model}")
            
            for system_prompt, user_prompt in generate_prompts(question_num):
                response = ""
                extracted_sql = ""
                execution_time = -1
                validated = False
                result = None

                try:
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                    response = ai.generate(messages, model)
                except Exception as e:
                    print(f"Error generating response: {str(e)}")
                    response = str(e)
                    store_results(question_num, execution_time, validated, 
                                  model, system_prompt, response, extracted_sql)
                    continue

                try:
                    extracted_sql = extract_query_from_response(response)
                except Exception as e:
                    print(f"Error extracting SQL: {str(e)}")
                    store_results(question_num, execution_time, validated, 
                                  model, system_prompt, response, extracted_sql)
                    continue

                try:
                    result, execution_time = run_query(extracted_sql, question_num)
                    print(f"Execution time: {execution_time:.4f} seconds")
                except Exception as e:
                    print(f"Error running query: {str(e)}")
                    store_results(question_num, execution_time, validated, 
                                  model, system_prompt, response, extracted_sql)
                    continue

                try:
                    validated = validate_answer(question_num, result)
                    print(f"Answer is valid: {validated}")
                except Exception as e:
                    print(f"Error validating answer: {str(e)}")

                store_results(question_num, execution_time, validated, 
                              model, system_prompt, response, extracted_sql)

if __name__ == "__main__":
    main()

# TODO: Delete Llama 405b (non-instruct)