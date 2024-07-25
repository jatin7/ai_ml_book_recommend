import os
import pandas as pd
import openai
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from dotenv import load_dotenv
import re
from openai import OpenAI
import csv

# Load environment variables
load_dotenv()
# openai.api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY_1"))

# Establish a connection to Snowflake
conn = snowflake.connector.connect(
    user=os.getenv('SNOWFLAKE_USER'),
    password=os.getenv('SNOWFLAKE_PASSWORD'),
    account=os.getenv('SNOWFLAKE_ACCOUNT'),
    warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
    database=os.getenv('SNOWFLAKE_DATABASE'),
    schema=os.getenv('SNOWFLAKE_SCHEMA'),
    role=os.getenv('SNOWFLAKE_ROLE')
)

def generate_prompt(title, author, detailed=False):
    if detailed:
        intro = """
        You are a literary expert who has a deep understanding of various books and their content. I will provide you with the titles and authors of books, and I need you to score them based on the following attributes, using numerical values only:
        
        1. Pace: Score from 1 to 10 where 1 indicates a slow pace, 5 indicates a medium pace, and 10 indicates a high pace.
        2. Length: Score from 1 to 10 where 1 indicates a short book, 5 indicates a medium-length book, and 10 indicates a long book.
        3. Plot Complexity: Score from 1 to 10 where 1 indicates an easy plot, 5 indicates a medium complexity plot, and 10 indicates a complex plot.
        4. Themes: Assign numbers from 1 to 10 based on the presence of themes. Provide separate scores for each theme such as Justice, Love, Redemption, Courage, Coming of Age, Survival, Identity, Betrayal, Sacrifice, Freedom vs. Oppression.
        5. Mood: Assign numbers from 1 to 10 based on the mood of the book where 1 to 2 is Heartfelt, 3 to 4 is Inspiring, 5 to 6 is Dark and Mysterious, 7 to 8 is Thought-Provoking nature and 9 to 10 is Contemplative.
        
        For Mood and Themes if there are multiple values please provide as a list, each separated by a pipe '|'.
        Provide the numerical scores for the book titled '{title}' by '{author}' in the same format as the example above. Respond only with numbers separated by spaces. Try to fill all the scores, do not miss any responses.
        """
    else:
        intro = "Please score the following attributes based on your understanding of the book's content. Provide only numerical values separated by spaces."

    prompt = f"{intro}Provide the numerical scores for the book titled '{title}' by '{author}'."
    return prompt

def parse_response(response_text):
    # Initialize the scores dictionary with None values
    scores = {
        'PACE': None,
        'LENGTH': None,
        'PLOT_COMPLEXITY': None,
        'THEMES': None,
        'MOOD': None
    }

    # Extract numerical values and anything that follows a colon, which indicates descriptive text
    matches = re.findall(r'(\b\d+\b|:\s*\d+)', response_text)

    # Clean up the matches and extract numbers
    cleaned_matches = [match.strip(": ") for match in matches]

    # Assign the cleaned numbers to the correct dictionary keys
    if len(cleaned_matches) > 0:
        scores['PACE'] = cleaned_matches[0]
    if len(cleaned_matches) > 1:
        scores['LENGTH'] = cleaned_matches[1]
    if len(cleaned_matches) > 2:
        scores['PLOT_COMPLEXITY'] = cleaned_matches[2]
    if len(cleaned_matches) > 3:
        # Join theme scores with a pipe '|' and assign to 'THEMES'
        themes = cleaned_matches[3:]
        # Remove duplicates while preserving order
        themes = list(dict.fromkeys(themes))
        scores['THEMES'] = '|'.join(themes)
    if len(cleaned_matches) > 4:
        # Assign the last number as the mood
        scores['MOOD'] = cleaned_matches[-1]

    print(scores)
    return scores



def query_openai(title, author):
    prompt = generate_prompt(title, author)
    MODEL = "gpt-3.5-turbo"
    response = client.chat.completions.create(
    model=MODEL,  # Make sure this matches the model you have access to
    messages=[
        {"role": "system", "content": "You are a literary expert who has a deep understanding of various books and their content."},
        {"role": "user", "content": prompt}
    ],
    temperature=0,
    max_tokens=200,
)
    response_text = response.choices[0].message.content
    print(f"Response from OpenAI for '{title}': {response_text}")
    
    # scores = parse_response(response_text)
    scores_dict = parse_response(response_text)
    
    if scores_dict:  # If the dictionary is not empty
        return {
            'TITLE': title,
            'AUTHOR': author,
            'PACE': scores_dict.get('PACE'),  # .get() returns None if key is not found
            'LENGTH': scores_dict.get('LENGTH'),
            'PLOT_COMPLEXITY': scores_dict.get('PLOT_COMPLEXITY'),
            'THEMES': scores_dict.get('THEMES'),  # This will be a list if present
            'MOOD': scores_dict.get('MOOD')  # This will be a list if present
        }
    else:
        print(f"Not enough data in response to parse for '{title}' by '{author}'.")
        return None

def process_books():
    # Explicitly setting the database and schema to avoid context-related errors
    with conn.cursor() as cursor:
        cursor.execute("USE WAREHOUSE SF_TUTS_WH;")
        cursor.execute("USE DATABASE FINALPROJECT;")
        cursor.execute("USE SCHEMA PUBLIC;")

        cursor.execute("SELECT TITLE, AUTHOR FROM INVENTORY WHERE BOOK_ID IN (SELECT DISTINCT BOOK_ID FROM BOOK_ID_NULL ORDER BY BOOK_ID DESC)  ORDER BY BOOK_ID DESC")
        # cursor.execute("SELECT TOP 5 TITLE, AUTHOR FROM INVENTORY WHERE BOOK_ID IN (62970)")
        books = cursor.fetchall()

    results = []
    for title, author in books:
        print(f"Querying OpenAI for book: {title} by {author}")
        book_data = query_openai(title, author)
        if book_data:  # Only append if book_data is not None
            results.append(book_data)
        else:
            print(f"Failed to process book: {title} by {author}")

    if results:
        # Ensure that only entries with complete data are included
        complete_results = [r for r in results if r is not None]
        df = pd.DataFrame(complete_results, columns=['TITLE', 'AUTHOR', 'PACE', 'LENGTH', 'PLOT_COMPLEXITY', 'THEMES', 'MOOD'])
        df.to_csv('book_attributes_null.csv', index=False, sep='|', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        print("Results saved to CSV.")
    else:
        print("No results to save.")

def pandas_dtype_to_snowflake_sql_type(dtype):
    mapping = {
        'int64': 'NUMBER',
        'float64': 'FLOAT',
        'bool': 'BOOLEAN',
        'datetime64[ns]': 'TIMESTAMP_NTZ',
        'object': 'VARCHAR'
    }
    return mapping.get(str(dtype), 'VARCHAR')

def create_table_from_df(df, table_name, conn):
    # Setting context inside the function to ensure correct database operations
    cursor = conn.cursor()
    cursor.execute("USE WAREHOUSE SF_TUTS_WH;")
    cursor.execute("USE DATABASE FINALPROJECT;")
    cursor.execute("USE SCHEMA PUBLIC;")

    print(f"Creating table: {table_name}")
    if not table_name[0].isalpha() or not table_name.isidentifier():
        table_name = f'"{table_name}"'
    column_definitions = ', '.join([f'"{col.upper()}" {pandas_dtype_to_snowflake_sql_type(str(dtype))}' for col, dtype in df.dtypes.items()])
    create_table_sql = f"CREATE OR REPLACE TABLE {table_name} ({column_definitions})"

    print(create_table_sql)  # Print SQL for debugging
    cursor.execute(create_table_sql)
    # cursor.execute(f"TRUNCATE TABLE {table_name}")

def upload_csv_to_snowflake(csv_path, table_name, conn):
    df = pd.read_csv(csv_path, sep='|', quotechar='"')
    df.columns = [col.upper() for col in df.columns]  # Ensure column names are uppercase for Snowflake compatibility
    create_table_from_df(df, table_name, conn)  # Create or replace and set up table
    write_pandas(conn, df, table_name.upper())  # Use Snowflake's bulk upload
    print("Data Transfer Completed!!")

if __name__ == "__main__":
    # process_books()
    csv_file_path = 'book_attributes_null.csv'
    table_name = 'BOOK_ATTRIBUTES_NULL_NEW'
    if os.path.exists(csv_file_path):
        upload_csv_to_snowflake(csv_file_path, table_name, conn)
    conn.close()  # Always ensure to close the connection
