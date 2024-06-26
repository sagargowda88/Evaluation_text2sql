 import pandas as pd
import sqlite3

# Sample data for the first actual data CSV file ('actual_data_1.csv')
actual_data_1 = {
    'id_1': [1, 2, 3, 4, 5],
    'name_1': ['John', 'Alice', 'Bob', 'Emily', 'Charlie'],
    'age_1': [28, 32, 25, 35, 29],
    'city_1': ['New York', 'Los Angeles', 'Chicago', 'San Francisco', 'Boston'],
    'salary_1': [75000, 80000, 70000, 90000, 85000],
    'department_1': ['Sales', 'Marketing', 'IT', 'HR', 'Finance']
}

# Create a DataFrame for the first actual data
df_1 = pd.DataFrame(actual_data_1)

# Sample data for the second actual data CSV file ('actual_data_2.csv')
actual_data_2 = {
    'id_2': [1, 2, 3, 4, 5],
    'name_2': ['Mike', 'Eva', 'David', 'Sophia', 'Frank'],
    'age_2': [32, 28, 30, 27, 35],
    'city_2': ['Chicago', 'New York', 'Los Angeles', 'San Francisco', 'Boston'],
    'salary_2': [85000, 90000, 80000, 95000, 88000],
    'department_2': ['IT', 'Sales', 'Marketing', 'HR', 'Finance']
}

# Create a DataFrame for the second actual data
df_2 = pd.DataFrame(actual_data_2)

# List of mixed SQL queries for predicted and true queries
predicted_queries = [
    'SELECT * FROM df_1 WHERE age_1 > 25',  # Use df_1 as table name
    'SELECT name_1, age_1 FROM df_1 WHERE city_1 = "Chicago"',  # Use df_1 as table name
    'SELECT MAX(salary_1) FROM df_1 WHERE department_1 = "Sales"',  # Use df_1 as table name
]

true_queries = [
    'SELECT * FROM df_1 WHERE age_1 > 25',  # Use df_2 as table name
    'SELECT name_1, age_1 FROM df_1 WHERE city_1 = "New York"',  # Use df_2 as table name
    'SELECT MAX(salary_1) FROM df_1 WHERE department_1 = "IT"',  # Use df_2 as table name
]

# Create an in-memory SQLite database connection
conn = sqlite3.connect(':memory:')

# Load DataFrames into the SQLite database
df_1.to_sql('df_1', conn, index=False, if_exists='replace')
df_2.to_sql('df_2', conn, index=False, if_exists='replace')

# Function to execute queries and check if results are similar
def check_results_similarity(predicted_queries, true_queries):
    similarity_list = []

    for predicted_query, true_query in zip(predicted_queries, true_queries):
        # Execute the SQL queries on the respective DataFrames
        predicted_result_df = pd.read_sql_query(predicted_query, conn)
        true_result_df = pd.read_sql_query(true_query, conn)

        # If one query uses '*' and the other uses specific column names
        if '*' in predicted_query and '*' not in true_query:
            # Use column names from the true query in place of '*'
            true_columns = [col.strip() for col in true_query.split('SELECT')[1].split('FROM')[0].split(',')]
            predicted_query = predicted_query.replace('*', ', '.join(true_columns))
        elif '*' in true_query and '*' not in predicted_query:
            # Use column names from the predicted query in place of '*'
            predicted_columns = [col.strip() for col in predicted_query.split('SELECT')[1].split('FROM')[0].split(',')]
            true_query = true_query.replace('*', ', '.join(predicted_columns))

        # Check if results are similar for each pair of queries
        similarity = 'Yes' if predicted_result_df.equals(true_result_df) else 'No'
        similarity_list.append(similarity)

        print(f"Results for Predicted Query:\n{predicted_query}\nand\nTrue Query:\n{true_query}\nare {similarity}")

    return similarity_list

# Check results similarity
similarity_result = check_results_similarity(predicted_queries, true_queries)

# Close the SQLite connection
conn.close()

# Create a DataFrame with the results
result_df = pd.DataFrame({'predicted_queries': predicted_queries, 'true_queries': true_queries, 'similarity': similarity_result})

# Save the DataFrame to a CSV file
result_df.to_csv('results.csv', index=False)
