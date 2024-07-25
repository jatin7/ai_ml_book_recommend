import streamlit as st
from utils.book_details import display_book_list, display_single_book, update_book_status,fetch_user_history_from_snowflake,get_book_details_id
import requests
import user_survey
import time
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access environment variables
FASTAPI_URL = os.getenv("FASTAPI_BASE_URL")



def display_user_dashboard(user_history_data,user_first_name,user_id):
        #print(" display_user_dashboard got this user_history_data ",user_history_data)
        st.title(f"{user_first_name}'s Dashboard")
        st.subheader(f"Hello {user_first_name}!")

        # Get books based on exclusive shelves
        currently_reading = user_history_data[user_history_data["BOOKSHELF_FLAG"] == 0]
        print("currently_reading before tab1",currently_reading)
        tbr_books = user_history_data[user_history_data["BOOKSHELF_FLAG"] == 1]
        read_books = user_history_data[user_history_data["BOOKSHELF_FLAG"] == 2]

        tab1, tab2, tab3 = st.tabs(["Currently Reading", "To Be Read (TBR)", "Read"])

        with tab1:

            print("we are in tab1")
            print(currently_reading)
            if currently_reading.empty:
                st.write("You are not currently reading anything.")
            else:
                for index, row in currently_reading.iterrows():
                    book_id = row['BOOK_ID']
                    book_title, book_author, cover_url,total_ratings, item_count = get_book_details_id(book_id)
                    print("in user dashboard tab1",  book_title, book_author, cover_url,total_ratings, item_count)
                   
                    display_single_book(book_title, book_author, cover_url,total_ratings, item_count)
                    unique_key = f"finished_button_{book_id}" 
                    if st.button("Finished Book", key=unique_key):
                        print("inside finished book")
                        new_flag = 2  # The flag value for 'read' is 2
                        
                        endpoint = f"{FASTAPI_URL}/update_user_history_{user_id}_{int(book_id)}_{new_flag}"
                        response = requests.put(endpoint)
                        print("@@@@",response)
                        if response.status_code == 200:
                            print("Bookshelf flag updated successfully")
                            st.success("Bookshelf flag updated successfully.")
                            #st.rerun()
                        else:
                            st.error("Failed to update bookshelf flag.")


        with tab2:
            print("we are in tab2 ")
            if tbr_books.empty:
                st.write("You have not added anything yet in your TBR.")
            else:
                for index, row in tbr_books[:5].iterrows():
                    #display_single_book(row['BOOK_ID'])
                    book_id =  int(row['BOOK_ID'])
                    book_title, book_author, cover_url,total_ratings, item_count = get_book_details_id(book_id)
                    display_single_book(book_title, book_author, cover_url,total_ratings, item_count)
                    unique_key = f"started_reading_{book_id}" 
                    # if st.button("Started Reading", key=unique_key):
                    #     new_flag = 0
                    #     update_book_status(user_id, book_id, new_flag)
                    #     st.rerun()
                    unique_form_key = f"book_reading_form_{book_id}"
                    #unique_form_key = f"book_reading_form_{book_id}_{int(time.time())}"
                    with st.form(key=unique_form_key):
                        st.write("Click the button if you've started reading:")
                        if st.form_submit_button("Started Reading"):
                            new_flag = 0
                            update_book_status(user_id, book_id, new_flag)
                        
                        
        with tab3:
            print("we are in tab3 ")
            if tbr_books.empty:
                st.write("You have not read anything yet.")
            else:
                print("read_books:", read_books)
                display_book_list(read_books)
                

    


def main():

    user_data = st.session_state.get('data', None)
    if user_data is None or 'u_id' not in user_data or 'username' not in user_data:
        st.error("User data not found or incomplete. Please log in.")
    else:
        user_id = user_data['u_id']
        username = user_data['username']
        user_first_name = username.split("@")[0]
        print("@", user_id)
        user_history_data = fetch_user_history_from_snowflake(user_id)
        print("--------user_history_data", user_history_data)
       
        if user_history_data.shape[0] > 0:

            display_user_dashboard(user_history_data, user_first_name,user_id)
     
        else:
            st.write("You need to write user survey page")
            user_survey.chatbot(user_id= user_id)
        


if __name__ == "__main__":
    main()


