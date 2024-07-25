from fastapi import FastAPI, HTTPException
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from snowflake.connector import Error
import pandas as pd
import os
import numpy as np
import snowflake
app = FastAPI()


conn = snowflake.connector.connect(
    user=os.getenv('SNOWFLAKE_USER'),
    password=os.getenv('SNOWFLAKE_PASSWORD'),
    account=os.getenv('SNOWFLAKE_ACCOUNT'),
    warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),  
    database=os.getenv('SNOWFLAKE_DATABASE'),   
    schema=os.getenv('SNOWFLAKE_SCHEMA'),        
    role=os.getenv('SNOWFLAKE_ROLE')         

)
    
       
# Function to update bookshelf flag in Snowflake
def update_bookshelf_flag(user_id: int, book_id: int, new_flag: int):
    try:
        # Execute UPDATE statement
        with conn.cursor() as cur:
            cur.execute(
                f""" UPDATE USER_HISTORY
                    SET BOOKSHELF_FLAG = {new_flag}  
                    WHERE USER_ID = {user_id} 
                    AND BOOK_ID = {book_id};"""
            )

    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    # finally:
    #     conn.close()



def recommend_books(user_id:int):
    print("we are in backend utils snowflake_connector recommend_books fucntion")
    sql_query = f"SELECT * FROM USER_RECOMENDATIONS WHERE user_id = '{user_id}'"
    # try:
    with conn.cursor() as cur:
        cur.execute(sql_query)
        rows = cur.fetchall()
        print("rows",rows)
        columns = [desc[0] for desc in cur.description]  # Fetch column names
        df = pd.DataFrame(rows, columns=columns)
        print(df)
        return df


def get_user_recommendation_data(user_id):
    sql_query = f'''
    SELECT VALUE AS book_id
    FROM USER_RECOMMENDATION,
    LATERAL SPLIT_TO_TABLE(user_recommendation.RECOMMENDATIONS, ',') s
    WHERE USER_ID = {user_id}'''
    # try:
    with conn.cursor() as cur:
        cur.execute(sql_query)
        rows = cur.fetchall()
        print("rows",rows)
        columns = [desc[0] for desc in cur.description]  # Fetch column names
        df = pd.DataFrame(rows, columns=columns)
        print(df)
        return df



def match_survey_book_attributes(mood,theme,plot_complexity,pace,length):
    print("values: ", mood, plot_complexity, pace)
    #genre_values = genre.split(',')
    print("we are inside backend snowflake connector match_survey_book_attributes, theme:", theme)
    #theme_str = ', '.join(f"'{item}'" for item in theme)

    # Construct the SQL query dynamically
    #sql_query = f"""SELECT * FROM BOOK_ATTRIBUTES WHERE mood = '{mood}' AND theme in ('{theme}') AND plot_complexity = '{plot_complexity}' AND pace='{pace}' AND length = '{length}'"""
    sql_query = f"""SELECT * FROM BOOK_ATTRIBUTES WHERE mood in {mood} AND (plot_complexity = {plot_complexity} or length = {length} or pace={pace} )"""

    print("##########", sql_query , "##########")
    try: 
        with conn.cursor() as cur:
            cur.execute(sql_query)
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description] 
            df_result = pd.DataFrame(rows, columns=columns)

            print(df_result)
            return df_result
    except Exception as e:
        print("Error executing SQL query:", e)
        return None



def add_to_user_history(user_id: int, book_id: str, flag: int):
   
    try:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM USER_HISTORY WHERE USER_ID = %s AND BOOK_ID = %s", (user_id, book_id))
                count = cur.fetchone()[0]
                
                if count == 0:
                    # If the combination does not exist, proceed with the insertion
                    query = """INSERT INTO USER_HISTORY (USER_ID, BOOK_ID, BOOKSHELF_FLAG, HISTORY_ID) 
                            VALUES (%s, %s, %s, USER_HISTORY_SEQUENCE.NEXTVAL);"""
                    cur.execute(query, (user_id, book_id, flag))
                    conn.commit()
                    print(f"Successfully added to your list.")
                else:
                    # If the combination already exists, update the existing record 
                    print(f"The book is already in your list.")
                    
                    cur.execute("UPDATE USER_HISTORY SET BOOKSHELF_FLAG = %s WHERE USER_ID = %s AND BOOK_ID = %s", (flag, user_id, book_id))
                    conn.commit()
                    print("Updated the book's flag in your list.")

            print(f"Successfully added to your list.")

    except Exception as e:
        print(f"An error occurred: {e}")
        raise  # Re-raise the exception for handling in the calling code

def get_book_title_match(book_title:str):
    book_title = book_title.lower()
    sql_query = f"SELECT * FROM INVENTORY WHERE lower(TITLE) = '{book_title}'"
    print(sql_query)
    try:
        with conn.cursor() as cur:
            cur.execute(sql_query)
            rows = cur.fetchall()
            print("rows",rows)
            columns = [desc[0] for desc in cur.description]  # Fetch column names
            df = pd.DataFrame(rows, columns=columns)
            #print(df)
            return df
    except Exception as e:
        print("Error:", e)  # Debugging statement
        return None

def get_snowflake_inventory_data_with_book_title(book_title:str):
    book_title = book_title.lower()
    sql_query = f"SELECT * FROM INVENTORY WHERE lower(TITLE) like '%{book_title}%'"
    #print(sql_query)
    try:
        with conn.cursor() as cur:
            cur.execute(sql_query)
            rows = cur.fetchall()
            print("rows",rows)
            columns = [desc[0] for desc in cur.description]  # Fetch column names
            df = pd.DataFrame(rows, columns=columns)
            print(df)
            return df
    except Exception as e:
        print("Error:", e)  # Debugging statement
        return None
    # finally: 
    #     con.close() 

# def get_snowflake_inventory_data_with_book_id(book_id:int):
#     sql_query = f"SELECT * FROM INVENTORY WHERE BOOK_ID = '{book_id}'"
#     print("get_snowflake_inventory_data_with_book_id",sql_query)
    
#     try:
#         with con.cursor() as cur:
#             cur.execute(sql_query)
#             rows = cur.fetchall()
#             print("rows",rows)
#             columns = [desc[0] for desc in cur.description]  # Fetch column names
#             df = pd.DataFrame(rows, columns=columns)
#             print(df)
#             return df
#     except Exception as e:
#         print("Error:", e)  # Debugging statement
#         return None

# def get_snowflake_inventory_data_with_book_id(book_id: int):
#     print("get_snowflake_inventory_data_with_book_id",book_id )
#     sql_query = f"SELECT * FROM INVENTORY WHERE BOOK_ID = '{book_id}'"
#     # try:
#     try:
#         with conn.cursor() as cur:
#             cur.execute(sql_query)
#             rows = cur.fetchall()
#             print("rows",rows)
#             columns = [desc[0] for desc in cur.description]  # Fetch column names
#             df = pd.DataFrame(rows, columns=columns)
#             print(df)
#             return df
#     except Error as e:
#         raise HTTPException(status_code=500, detail=str(e))
#     finally:
#         conn.close()

def get_snowflake_inventory_data_with_book_id(book_id: int):
    print("get_snowflake_inventory_data_with_book_id", book_id)
    sql_query = f"SELECT * FROM INVENTORY WHERE BOOK_ID = '{book_id}'"
    
    # Open a new connection for each call
    with snowflake.connector.connect(
    user=os.getenv('SNOWFLAKE_USER'),
    password=os.getenv('SNOWFLAKE_PASSWORD'),
    account=os.getenv('SNOWFLAKE_ACCOUNT'),
    warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),  
    database=os.getenv('SNOWFLAKE_DATABASE'),   
    schema=os.getenv('SNOWFLAKE_SCHEMA'),        
    role=os.getenv('SNOWFLAKE_ROLE')         

    ) as conn:
        try:
            with conn.cursor() as cur:
                cur.execute(sql_query)
                rows = cur.fetchall()
                print("rows", rows)
                columns = [desc[0] for desc in cur.description]  # Fetch column names
                df = pd.DataFrame(rows, columns=columns)
                print(df)
                return df
        except Exception as e:  # It's better to catch a more specific exception
            raise HTTPException(status_code=500, detail=str(e))

def get_user_history_data(user_id):
    sql_query = f"SELECT * FROM USER_HISTORY WHERE USER_ID = '{user_id}'"
    print("get_user_history_data", sql_query)
    # try:
    with conn.cursor() as cur:
        cur.execute(sql_query)
        rows = cur.fetchall()
        print("rows",rows)
        columns = [desc[0] for desc in cur.description]  # Fetch column names
        df = pd.DataFrame(rows, columns=columns)
        print(df)
        return df
    # finally: 
    #     con.close() 


def get_user_data(username):
    
    sql_query = f"SELECT * FROM USER WHERE USERNAME = '{username}'"
    
    with conn.cursor() as cur:
        cur.execute(sql_query)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]  # Fetch column names
        df = pd.DataFrame(rows, columns=columns)
        return df


def add_user_recommendations(df):
    try:
        with conn.cursor() as cur:
            cur.execute("CREATE OR REPLACE TEMPORARY TABLE TEMP_USER_RECOMMENDATIONS (USER_ID INTEGER, RECOMMENDATIONS STRING)")
 
            # Convert the DataFrame to a list of tuples for insertion
            data_to_insert = list(df.itertuples(index=False, name=None))
 
            # Bulk insert data into the temporary table
            cur.executemany("INSERT INTO TEMP_USER_RECOMMENDATIONS (USER_ID, RECOMMENDATIONS) VALUES (%s, %s)", data_to_insert)
 
            # Adjust the SQL syntax based on your database type
            cur.execute("""
                MERGE INTO USER_RECOMMENDATION AS TARGET
                USING TEMP_USER_RECOMMENDATIONS AS SOURCE
                ON TARGET.USER_ID = SOURCE.USER_ID
                WHEN MATCHED THEN
                    UPDATE SET TARGET.RECOMMENDATIONS = SOURCE.RECOMMENDATIONS
                WHEN NOT MATCHED THEN
                    INSERT (USER_ID, RECOMMENDATIONS) VALUES (SOURCE.USER_ID, SOURCE.RECOMMENDATIONS)
            """)
            conn.commit()
 
    except Error as e:
        # Log the error for debugging
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    

########################################################

def get_user_history_data_recommendations():
    sql_query = '''
        SELECT
            USER_ID,
            BOOK_ID,
            BOOKSHELF_FLAG AS flag,
            null AS rating
        FROM
            USER_HISTORY
        WHERE
            USER_ID IN (201,301,401)
    '''
    try:
        with conn.cursor() as cur:
            cur.execute(sql_query)
            rows = cur.fetchall()
            #print("rows",rows)
            columns = [desc[0] for desc in cur.description]  # Fetch column names
            df = pd.DataFrame(rows, columns=columns)
            #print(df)
            return df
    except Exception as e:
        print("Error:", e)  # Print any errors encountered during the execution
        return None
 
def get_snowflake_user_book_features_data():
    sql_query = '''WITH User_Books AS
                (
                SELECT DISTINCT(BOOK_ID) FROM USER_HISTORY t1
                WHERE t1.USER_ID IN (201,301,401)
                ), user_books_inventory AS
                (
                SELECT
                    t2.book_id,
                    t2.title,
                    t2.author,
                    t2.description as summary,
                    t2.genre as genre_list,
                    t2.book_rating as public_rating,
                    t2.totalratings as number_of_reviews
                FROM
                INVENTORY t2
                WHERE t2.book_id IN (SELECT * FROM User_Books)
                ), user_book_attribute AS
                (
                SELECT * FROM BOOK_ATTRIBUTES_BKP WHERE title in (SELECT distinct(title) FROM user_books_inventory)
                )
 
                SELECT
                    t2.book_id,
                    t2.author,
                    t2.summary,
                    t2.genre_list,
                    t2.public_rating,
                    t2.number_of_reviews,
                    t1.pace,
                    t1.length,
                    t1.plot_complexity,
                    t1.themes as theme,
                    t1.mood
                FROM
                user_books_inventory t2
                JOIN
                user_book_attribute t1
                ON t2.title = t1.title
                WHERE t2.book_id IN (SELECT BOOK_ID FROM VECTOR_GENERATED)
                '''
    try:
        with conn.cursor() as cur:
            cur.execute(sql_query)
            rows = cur.fetchall()
            #print("rows",rows)
            columns = [desc[0] for desc in cur.description]  # Fetch column names
            df = pd.DataFrame(rows, columns=columns)
            #print(df)
            return df
    except Exception as e:
        print("Error:", e)  # Print any errors encountered during the execution
        return None
 
 
def get_snowflake_all_book_features_data():
    sql_query = '''
                WITH CTE AS(
                    SELECT
                        t2.book_id,
                        t2.author,
                        t2.description as summary,
                        t2.genre as genre_list,
                        t2.book_rating as public_rating,
                        t2.totalratings as number_of_reviews,
                        t1.pace,
                        t1.length,
                        t1.plot_complexity,
                        t1.themes as theme,
                        t1.mood
                    FROM
                    BOOK_ATTRIBUTES t1 JOIN INVENTORY t2
                    ON t1.title = t2.title and t1.author = t2.author
                    WHERE length IS NOT NULL
                        AND mood IS NOT NULL
                        AND pace IS NOT NULL
                        AND plot_complexity IS NOT NULL
                        AND themes IS NOT NULL
                    )
 
                    SELECT *
                    FROM CTE WHERE book_id NOT IN (SELECT BOOK_ID FROM VECTOR_GENERATED) AND THEME IS NOT NULL
                '''
    try:
        with conn.cursor() as cur:
            cur.execute(sql_query)
            rows = cur.fetchall()
            #print("rows",rows)
            columns = [desc[0] for desc in cur.description]  # Fetch column names
            df = pd.DataFrame(rows, columns=columns)
            #print(df)
            return df
    except Exception as e:
        print("Error:", e)  # Print any errors encountered during the execution
        return None
 
 
def add_vector_already_generated(book_id: list):
   
    try:
        with conn.cursor() as cur:
            for book_id in book_id:
                # Check if the vector for the book ID already exists
                cur.execute("SELECT * FROM VECTOR_GENERATED WHERE BOOK_ID = %s", (book_id,))
                result = cur.fetchone()
                if not result:
                    # Vector does not exist for this book ID, insert it
                    cur.execute("INSERT INTO VECTOR_GENERATED (BOOK_ID) VALUES (%s)", (book_id,))
                    conn.commit()  # Commit the transaction
 
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    

#################################

