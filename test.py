from helpers import create_prompt_question, run_query, validate_answer


if __name__ == "__main__":
    for question_num in range(1, 23):
        print(f"\nRunning query for question {question_num}:")
        
        with open(f'benchmark_queries/{question_num:02d}.sql', 'r') as f:
            query = f.read()
        
        result, execution_time = run_query(query, question_num)
        
        print(f"Execution time: {execution_time:.4f} seconds")

        validated = validate_answer(question_num, result)
        print(f"Answer is valid: {validated}")
