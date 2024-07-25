import os
import pandas as pd
from dotenv import load_dotenv
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

# Load environment variables
load_dotenv()

# Establish a connection to Snowflake
conn = snowflake.connector.connect(
    user=os.getenv('SNOWFLAKE_USER'),
    password=os.getenv('SNOWFLAKE_PASSWORD'),
    account=os.getenv('SNOWFLAKE_ACCOUNT'),
    warehouse='SF_TUTS_WH',  # Adjusted as per your working setup
    database='SF_TUTS',   # Adjusted as per your working setup
    schema='PUBLIC',        # Adjusted as per your working setup
    role='ACCOUNTADMIN'           # Adjusted as per your working setup
)

# conn.cursor().execute("USE DATABASE SF_DB_CASE1")
# conn.cursor().execute("USE SCHEMA SF_CASE1")
# Function to map pandas data types to Snowflake SQL types
def pandas_dtype_to_snowflake_sql_type(dtype):
    mapping = {
        'int64': 'NUMBER',
        'float64': 'FLOAT',
        'bool': 'BOOLEAN',
        'datetime64[ns]': 'TIMESTAMP_NTZ',
        'object': 'VARCHAR'
    }
    return mapping.get(str(dtype), 'VARCHAR')

# Function to dynamically create tables based on DataFrame's structure
def create_table_from_df(df, table_name, conn):
    print(f"Creating table: {table_name}")  # Debug print
    if not table_name[0].isalpha() or not table_name.isidentifier():
        table_name = f'"{table_name}"'
    column_definitions = ', '.join([f'"{col.upper()}" {pandas_dtype_to_snowflake_sql_type(str(dtype))}' for col, dtype in df.dtypes.items()])
    create_table_sql = f"CREATE OR REPLACE TABLE {table_name} ({column_definitions})"
    print(create_table_sql)
    conn.cursor().execute("CREATE DATABASE IF NOT EXISTS FINALPROJECT")
    conn.cursor().execute("USE DATABASE FINALPROJECT")
    conn.cursor().execute("""
        CREATE WAREHOUSE IF NOT EXISTS SF_TUTS_WH
        WITH WAREHOUSE_SIZE = 'MEDIUM'
        AUTO_SUSPEND = 300
        AUTO_RESUME = TRUE
        WAREHOUSE_TYPE = 'STANDARD';
    """)
    conn.cursor().execute("CREATE SCHEMA IF NOT EXISTS PUBLIC")
    conn.cursor().execute("USE SCHEMA PUBLIC")
    # conn.cursor().execute(create_database)
    conn.cursor().execute(f"TRUNCATE TABLE {table_name}")
    conn.cursor().execute(create_table_sql)

# Function to upload a CSV file to Snowflake
def upload_csv_to_snowflake(csv_path, table_name, conn):
    df = pd.read_csv(csv_path)
    df.columns = [col.upper() for col in df.columns]  # Ensure column names are uppercase for Snowflake compatibility
    create_table_from_df(df, table_name, conn)
    write_pandas(conn, df, table_name.upper())
    print("Data Transfer Completed!!")

# Main script
if __name__ == "__main__":
    csv_file_path = 'merged_dataset.csv'  # Update with the actual path to the CSV file
    table_name = 'INVENTORY'  # Set your desired table name here
    if os.path.exists(csv_file_path):
        upload_csv_to_snowflake(csv_file_path, table_name, conn)
    else:
        print("CSV file not found.")
    conn.close()  # Close the Snowflake connection
