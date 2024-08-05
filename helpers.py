import json
import sqlite3
import timeit

def get_table_names():
    """
    Opens the tpch.db database and returns all table names.
    
    Returns:
        list: A list of table names in the database.
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('tpch.db')
        cursor = conn.cursor()

        # Query to get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        
        # Fetch all results
        tables = cursor.fetchall()
        
        # Close the connection
        conn.close()
        
        # Extract table names from the result tuples
        return [table[0] for table in tables]
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return []

def get_database_schema():
    """
    Retrieves the CREATE statements for all tables in the tpch.db database.
    
    Returns:
        str: A formatted string representation of the CREATE statements for each table.
    """
    try:
        conn = sqlite3.connect('tpch.db')
        cursor = conn.cursor()
        
        # Get all table names
        tables = get_table_names()
        
        formatted_schema = ""
        for table in tables:
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}';")
            create_statement = cursor.fetchone()
            if create_statement:
                formatted_schema += f"Table: {table}\n"
                formatted_schema += f"CREATE STATEMENT: {create_statement[0]}\n\n"
        
        conn.close()
        return formatted_schema.strip()
    except Exception as e:
        print(f"An error occurred while retrieving the database schema: {e}")
        return "Error: Unable to retrieve database schema"

def get_and_format_top_n_rows(table_names=None, n=5):
    """
    Retrieves and formats the top n rows (including the header) for specified table(s) or all tables.
    
    Args:
        table_names (str or list, optional): Name of the table or list of table names. 
                                             If None, retrieves data for all tables.
        n (int, optional): Number of rows to retrieve. Defaults to 5.
    
    Returns:
        str: A formatted string representation of the table data.
    """
    def get_top_n_rows():
        try:
            conn = sqlite3.connect('tpch.db')
            cursor = conn.cursor()
            
            if table_names is None:
                tables = get_table_names()
            elif isinstance(table_names, str):
                tables = [table_names]
            else:
                tables = table_names
            
            result = {}
            for table in tables:
                # Get column names
                cursor.execute(f"PRAGMA table_info({table});")
                columns = [column[1] for column in cursor.fetchall()]
                
                # Get top n rows
                cursor.execute(f"SELECT * FROM {table} LIMIT {n};")
                rows = cursor.fetchall()
                
                # Combine header and rows
                result[table] = [columns] + [list(row) for row in rows]
            
            conn.close()
            return result
        except Exception as e:
            print(f"An error occurred while retrieving top rows: {e}")
            return {}

    table_data = get_top_n_rows()
    
    formatted_output = ""
    for table, rows in table_data.items():
        formatted_output += f"Table: {table}\n"
        if not rows:
            formatted_output += "No data available.\n\n"
            continue
        
        # Calculate column widths
        col_widths = [max(len(str(item)) for item in col) for col in zip(*rows)]
        
        # Create formatted rows
        for i, row in enumerate(rows):
            formatted_row = " | ".join(f"{str(item):<{col_widths[j]}}" for j, item in enumerate(row))
            formatted_output += formatted_row + "\n"
            if i == 0:  # Add a separator line after the header
                formatted_output += "-" * (sum(col_widths) + 3 * (len(col_widths) - 1)) + "\n"
        
        formatted_output += "\n"
    
    return formatted_output.strip()

def create_prompt_question(question_num: int) -> str:
    """
    Creates a formatted prompt question based on the question number.
    
    Args:
        question_num (int): The question number.
    
    Returns:
        str: The formatted prompt question.
    
    Raises:
        ValueError: If the question number is not found.
    """
    # Data retrieved from https://github.com/eyalroz/tpch-tools
    with open('tpch_questions.json', 'r') as f:
        questions = json.load(f)
    
    question = questions.get(str(question_num))
    if question is None:
        raise ValueError(f"Question number {question_num} not found.")
    
    # Get expected columns from the .ans file
    ans_file_path = f'expected_results/{question_num:02d}.ans'
    with open(ans_file_path, 'r') as f:
        expected_columns = f.readline().strip()
    
    return f"{question}\n\nExpected columns: {expected_columns}"

def run_query(query: str, question_num: int) -> tuple[list[any], float]:
    """
    Executes the given SQL query on the tpch.db database and tracks execution time.
    
    Args:
        query (str): The SQL query to execute.
    
    Returns:
        tuple: A tuple containing a list of all returned values and the execution time in seconds.
    """
    start_time = timeit.default_timer()
    try:
        conn = sqlite3.connect('tpch.db')
        cursor = conn.cursor()
        
        cursor.execute(query)
        results = [item for sublist in cursor.fetchall() for item in sublist]
        
        conn.close()
        execution_time = timeit.default_timer() - start_time
        return results, execution_time
    except Exception as e:
        print(f"An error occurred while executing the query: {e}")
        return [], 0.0
