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
    
    for question_num in range(1, 23):
        print(f"\nRunning query for question {question_num}:")
        
        with open(f'benchmark_queries/{question_num:02d}.sql', 'r') as f:
            query = f.read()
        
        ai = AI()
        
        for model in get_models()[:1]:
            print(f"Running query for model: {model}")
            
            for system_prompt, user_prompt in generate_prompts(question_num):
                try:
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                    response = ai.generate(messages, model)
                    extracted_sql = extract_query_from_response(response)
                    
                    result, execution_time = run_query(extracted_sql, question_num)
                    
                    print(f"Execution time: {execution_time:.4f} seconds")
                    
                    validated = validate_answer(question_num, result)
                    print(f"Answer is valid: {validated}")
                
                except Exception as e:
                    print(f"Error occurred: {str(e)}")
                    execution_time = -1  # Use -1 to indicate error in execution time
                    validated = False
                    response = str(e)
                    extracted_sql = ""
                
                store_results(question_num, execution_time, validated, 
                              model, system_prompt, 
                              response, extracted_sql)

if __name__ == "__main__":
    main()

    exit()
    raise(ValueError("Stop here for now"))

    query1 = """select
    l_returnflag,
    l_linestatus,
    sum(l_quantity) as sum_qty,
    sum(l_extendedprice) as sum_base_price,
    sum(l_extendedprice * (1 - l_discount)) as sum_disc_price,
    sum(l_extendedprice * (1 - l_discount) * (1 + l_tax)) as sum_charge,
    avg(l_quantity) as avg_qty,
    avg(l_extendedprice) as avg_price,
    avg(l_discount) as avg_disc,
    count(*) as count_order
from
    lineitem
where
    l_shipdate <= date('1998-12-01', '-90 days')
group by
    l_returnflag,
    l_linestatus
order by
    l_returnflag,
    l_linestatus;"""

    query2 = """SELECT
    L_RETURNFLAG,
    L_LINESTATUS,
    SUM(L_QUANTITY) AS sum_qty,
    SUM(L_EXTENDEDPRICE) AS sum_base_price,
    SUM(L_EXTENDEDPRICE * (1 - CAST(L_DISCOUNT AS REAL) / 100.0)) AS sum_disc_price,
    SUM(L_EXTENDEDPRICE * (1 - CAST(L_DISCOUNT AS REAL) / 100.0) * (1 + CAST(L_TAX AS REAL) / 100.0)) AS sum_charge,
    AVG(CAST(L_QUANTITY AS REAL)) AS avg_qty,
    AVG(CAST(L_EXTENDEDPRICE AS REAL)) AS avg_price,
    AVG(CAST(L_DISCOUNT AS REAL)) AS avg_disc,
    COUNT(*) AS count_order
FROM
    LINEITEM
WHERE
    L_SHIPDATE <= '1998-09-02'
GROUP BY
    L_RETURNFLAG,
    L_LINESTATUS
ORDER BY
    L_RETURNFLAG,
    L_LINESTATUS;
    """

    # Run query 1
    results1, execution_time1 = run_query(query1, 1)
    print("Results for query 1:")
    print(results1)
    validated1 = validate_answer(1, results1)
    print(f"Execution time for query 1: {execution_time1:.4f} seconds")
    print(f"Answer for query 1 is valid: {validated1}")

    print("\n" + "="*50 + "\n")

    # Run query 2
    results2, execution_time2 = run_query(query2, 1)
    print("Results for query 2:")
    print(results2)
    validated2 = validate_answer(1, results2)
    print(f"Execution time for query 2: {execution_time2:.4f} seconds")
    print(f"Answer for query 2 is valid: {validated2}")
