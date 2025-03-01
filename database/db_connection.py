import os
import sqlite3
from constants import db_file, sql_file_path



db_full_path = os.path.abspath(db_file)


def get_connection():
    conn = sqlite3.connect(db_full_path)
    return conn

def extract_queries(file_path):
    """
    Extract SQL queries from the given file.
    Each query ends with a semicolon (;).
    """
    queries = []
    with open(file_path, 'r') as file:
        query = ""
        for line in file:
            line = line.strip()
            if line.endswith(";"):  # If the line ends a query
                query += " " + line
                queries.append(query.strip())  # Add to query list
                query = ""  # Reset for the next query
            else:
                query += " " + line
    return queries


def execute_queries(db_name, queries):
    """
    Execute each SQL query on the given SQLite database.
    Parameters:
        db_name (str): Name of the SQLite database file.
        queries (list): List of SQL queries to execute.
    """
    # Connect to SQLite database (creates the file if it doesn't exist)
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    try:
        for query in queries:
            print(f"Executing query:\n{query}\n")
            cursor.execute(query)  # Execute the query
        conn.commit()  # Commit all changes
        print("All queries executed successfully.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()


def initialize_database():
    # File containing SQL queries
    full_path = os.path.abspath(sql_file_path)

    # Extract queries from the file
    queries = extract_queries(full_path)

    # Execute queries on the SQLite database
    execute_queries(db_full_path, queries)
