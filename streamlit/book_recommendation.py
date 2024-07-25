import json
import streamlit as st
from utils.book_details import display_recommended_book_list
import pandas as pd
import requests
import subprocess

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access environment variables
FASTAPI_URL = os.getenv("FASTAPI_BASE_URL")


def recommended_book(user_id):
    print("we are in recommended_book function")
    try:
        response = requests.get(f"{FASTAPI_URL}/snowflake_user_recommendation/{user_id}")
        print("___________", response)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
      
        recommended_books = json.loads(response.text)  
        recommended_books_df = pd.read_json(recommended_books)
        #print(recommended_books_df)
        recommended_books_df = recommended_books_df[:6]
        
        display_recommended_book_list(recommended_books_df)
    except requests.RequestException as e:
        print("Error fetching recommended books:", e)
        st.error("Failed to fetch recommended books.")
    except Exception as e:
        print("An unexpected error occurred:", e)


def main():
    
    # user_data = st.session_state.get('data', None)
    # if user_data is not None and 'u_id' in user_data:
    #     user_id = user_data['u_id']
    # recommended_book(user_id)
    user_data = st.session_state.get('data', None)
    if user_data is not None and 'u_id' in user_data:
        user_id = user_data['u_id']
    
    if st.button("Refresh Recommendations"):
        subprocess.run(["python", "utils/get_user_profile.py"])  # Execute the get_user_profile.py script
        st.experimental_rerun()  # Rerun the app to reflect changes

    recommended_book(user_id)


if __name__ == "__main__":
    main()