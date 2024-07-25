
import streamlit as st
import requests
import pandas as pd
import json
from dotenv import load_dotenv
from pandas import json_normalize
import os
load_dotenv()
FASTAPI_URL = os.getenv("FASTAPI_BASE_URL")


def fetch_user_history_from_snowflake(user_id):
    print("we are inside fetch_user_history_from_snowflake ")
    try:
        response = requests.get(f"{FASTAPI_URL}/snowflake_user_history/{user_id}")
        response.raise_for_status()  # Raise exception for 4xx or 5xx status codes

        user_history_data = response.json() 
        user_history_data = json.loads(user_history_data)
        print("we are in fetch_user_history_from_snowflake",user_history_data )
       
        #if user_history_data is not None:
            # Convert JSON data to DataFrame
        #df = pd.DataFrame(user_history_data)
        df = pd.DataFrame(user_history_data)
        print(type(df.columns))
        
        
        return df
        # else:
        #     return None

    except Exception as e:
        print("Error fetching user history from Snowflake:", e)
        return None


def display_single_book(book_title,book_author, cover_url,total_ratings, item_count):
  
    with st.container():
        cols = st.columns(2)  # Create columns for the grid layout
        with cols[0]:
            if cover_url:
                st.image(cover_url, caption=book_title, width=150)
            else:
                print("oops! no cover_image")
        
        with cols[1]:
            st.write("**Title:**", book_title)
            st.write("**Author:**", book_author)
            st.write("**Average Rating:**", total_ratings )
            st.write("**Available items:**", item_count)


def get_book_details_title_author(book_title, author, genre):
    book_title = book_title.lower()
    response = requests.get(f"{FASTAPI_URL}/snowflake_inventory/match/{book_title}")
    
    response.raise_for_status()
    
    if response.status_code == 200:
       
        #book_info_data = json.loads(response.text)  
        # print("|||||||||||||||",book_info_data)
        # book_info_data = json.loads(book_info_data)
        #book_info_data = response.json()
        book_info_data = json.loads(response.text)
        book_info_df = pd.read_json(book_info_data)

        #book_info_data = f"'{book_info_data}'"
        #book_info_data = json.loads(book_info_data)
        # Multiple books  
        #book_info_data = json.loads(response.text)
          
        #book_info_data = response.json() 
      
        #book_info_data = json.loads(book_info_data)  

        #print("response.json() : ", book_info_data)
        # book_info_data = json.loads(book_info_data)   
        # print("json.loads(book_info_data): ", book_info_data) 
        #book_info_df = pd.DataFrame(book_info_data)
        #flat_data = json_normalize(book_info_data)
        #book_info_df = pd.DataFrame(book_info_data)


        # Check if book_info_data is a list of dictionaries
       

        # print('********')
        # print(book_info_df)
    #df = pd.DataFrame(book_data)
    print("++++++++++++++++", len(book_info_df))
    return book_info_df


def get_book_details_title(book_title):
    print("inside get_book_details_title ")
    #print("book_title",book_title)
    book_title = book_title.lower()
    response = requests.get(f"{FASTAPI_URL}/snowflake_inventory/title/{book_title}")
    
    response.raise_for_status()
    
    if response.status_code == 200:
        book_info_data = response.json()
        book_info_data = json.loads(response.text)  
        print("|||||||||||||||",book_info_data)
        book_info_data = json.loads(book_info_data)
        # book_info_data = response.json()
        # Multiple books            
        book_data = {
                "Title" : [],
                "Cover_URL": [],
                "Book_ID": [],
                "Author": [],
                "Total_Ratings": [],
                "Item_Count": []
            }
            
        for book_info in book_info_data:
                book_data["Title"].append(book_info.get("TITLE"))
                book_data["Cover_URL"].append(book_info.get("COVER_PHOTO"))
                book_data["Book_ID"].append(book_info.get("BOOK_ID"))
                book_data["Author"].append(book_info.get("AUTHOR"))
                book_data["Total_Ratings"].append(book_info.get("TOTAL_RATINGS"))
                book_data["Item_Count"].append(book_info.get("ITEMCOUNT"))
             
            
        df = pd.DataFrame(book_data)
        return df
      

def get_book_details_id(book_id):
    print("inside get book details id")
    
    response = requests.get(f"{FASTAPI_URL}/snowflake_inventory/book_id/{int(book_id)}")

    response.raise_for_status()
    # audio_link = None
    if response.status_code == 200:

        book_info_data = json.loads(response.text)  
        book_info_data = json.loads(book_info_data)
        cover_url = book_info_data[0].get("COVER_PHOTO")
        book_title = book_info_data[0].get("TITLE")
        book_author = book_info_data[0].get("AUTHOR")
        total_ratings = book_info_data[0].get("TOTAL_RATINGS")
        item_count = book_info_data[0].get("ITEMCOUNT")
        # audio_link = book_info_data[0].get("AUDIO_LINK")
    
    return book_title, book_author, cover_url,total_ratings, item_count

def get_book_details_id_recommendation(book_id):
    print("inside get book details id")
    
    response = requests.get(f"{FASTAPI_URL}/snowflake_inventory/book_id/{int(book_id)}")

    response.raise_for_status()
    audio_link = None
    if response.status_code == 200:

        book_info_data = json.loads(response.text)  
        book_info_data = json.loads(book_info_data)
        cover_url = book_info_data[0].get("COVER_PHOTO")
        book_title = book_info_data[0].get("TITLE")
        book_author = book_info_data[0].get("AUTHOR")
        total_ratings = book_info_data[0].get("TOTAL_RATINGS")
        item_count = book_info_data[0].get("ITEMCOUNT")
        audio_link = book_info_data[0].get("AUDIO_LINK")
    
    return book_title, book_author, cover_url,total_ratings, item_count, audio_link


def display_book_list(book_list):

    #print("display_book_list")
    book_list = pd.DataFrame(book_list)
    #print("in display book list: ", book_list)


    for index, row in book_list.iterrows():
        try:
            book_id = row["BOOK_ID"]
            book_title, book_author, cover_url,total_ratings, item_count = get_book_details_id(book_id)
            with st.container():      
                cols = st.columns(2)  # Create columns for the grid layout
                with cols[0]:
                    if cover_url:
                        st.image(cover_url, caption=book_title, width=150)
                    else:
                        print("cover image is unavailable!!")
                with cols[1]:
                    st.write("**Title:**", book_title)
                    st.write("**Author:**", book_author)
                    st.write("**Average Rating:**", total_ratings )
                    st.write("**Available items:**", item_count)
                    st.write("Please rate this book out of 5:")
                    slider_key = f"rating_slider_{book_id}_{index}"
                    your_rating = st.slider("Rating", key=slider_key, min_value=1, max_value=5)
        except KeyError as e:
            print(f"Error accessing book data: {e}") 


def display_book_homepage(book_title):
    #print("we are in display_book_homepage function ")

    # Query FastAPI endpoint for book information
    fastapi_url = f"http://localhost:8000//book-info"
    response = requests.get(fastapi_url)
    if response.status_code == 200:
        data = response.json()
        cover_url = data.get("url")
    else:
        cover_url = None


    response = requests.get(f"{fastapi_url}/{book_title}")
    if response.status_code == 200:
        data = response.json()
        authors = data.get("author")
        summary = data.get("summary")
        cover_url = data.get("cover_link")
        pagecount = data.get("pagecount")
        category = data.get("category")
        averageRating = data.get("averageRating")
        previewLink = data.get("previewLink")
        wiki_summary = data.get("wiki_summary")
    else:
        st.write("Book information not found.")
        return

    with st.container():
        col1, col2 = st.columns((1, 1))
        with col1:
            if cover_url:
                st.image(cover_url, caption="Book Cover", use_column_width=True)
            else:
                st.write("No cover image available.")

        with col2:
            st.subheader("Author:")
            st.write(authors)

            st.subheader("Page Count:")
            st.write(pagecount)

            st.subheader("Category/Genre:")
            st.write(category)

            st.subheader("Average Rating:")
            st.write(averageRating)

            st.subheader("Preview Link:")
            st.write(previewLink)

    st.subheader("Summary:")
    st.write(summary)

    st.subheader("Wikipedia Summary:")
    st.write(wiki_summary)



# def display_recommended_book_list(book_list):

#     #print("display_book_list")
#     book_list = pd.DataFrame(book_list)
#     #print("in display book list: ", book_list)


#     for index, row in book_list.iterrows():
#         try:
#             book_id = row["BOOK_ID"]
#             book_title, book_author, cover_url,total_ratings, item_count = get_book_details_id(book_id)
#             with st.container():      
#                 cols = st.columns(2)  # Create columns for the grid layout
#                 with cols[0]:
#                     if cover_url:
#                         st.image(cover_url, caption=book_title, width=150)
#                     else:
#                         print("cover image is unavailable!!")
#                 with cols[1]:
#                     st.write("**Title:**", book_title)
#                     st.write("**Author:**", book_author)
#                     st.write("**Average Rating:**", total_ratings )
#                     st.write("**Available items:**", item_count)
                    
                    
#         except KeyError as e:
#             print(f"Error accessing book data: {e}") 

def display_recommended_book_list(book_list):
    book_list = pd.DataFrame(book_list)

    for index, row in book_list.iterrows():
        try:
            book_id = row["BOOK_ID"]
            book_title, book_author, cover_url, total_ratings, item_count, audio_link = get_book_details_id_recommendation(book_id)
            with st.container():      
                cols = st.columns([1, 2, 1])  # Adjust column ratios if necessary
                with cols[0]:
                    if cover_url:
                        st.image(cover_url, caption=book_title, width=150)
                    else:
                        st.write("Cover image is unavailable")
                with cols[1]:
                    st.write("**Title:**", book_title)
                    st.write("**Author:**", book_author)
                    st.write("**Average Rating:**", total_ratings )
                    st.write("**Available items:**", item_count)
                with cols[2]:  # This is the new column for the audio player
                    if audio_link:  # Check if there is an audio file link available
                        st.audio(audio_link, format='audio/mp3', start_time=0)
                    else:
                        st.write("Audio preview unavailable")
        except KeyError as e:
            st.write(f"Error accessing book data: {e}")


def update_book_status(user_id, book_id, new_flag):

    print("inside add_to_user_history")
    endpoint = f"{FASTAPI_URL}/update_user_history_{user_id}_{book_id}_{new_flag}"
    print("endpoint:",endpoint)
    response = requests.put(endpoint)
    print("response", response)
    if response.status_code == 200:
        st.success("added in Bookshelf successfully.")
        print("added in Bookshelf successfully")
    

def add_to_user_history(user_id:int ,book_id: int, flag: int):
    print("inside add_to_user_history")
    endpoint = f"{FASTAPI_URL}/insert_user_history_{user_id}_{book_id}_{flag}"
    print("endpoint:",endpoint)
    response = requests.put(endpoint)
    print("response", response)
    if response.status_code == 200:
        st.success("added in Bookshelf successfully.")
        print("added in Bookshelf successfully")
        #st.rerun()
    
def matched_books(user_id,genre,mood,theme,plot_complexity,pace,length):
    print("-----------we are inside utils > book_details > matched_books")
    print(genre,mood,theme,plot_complexity,pace,length)
    
    response = requests.get(f"{FASTAPI_URL}/book_attributes/{mood}_{theme}_{plot_complexity}_{pace}_{length}")

    response.raise_for_status()
    print("inside matched_books after fastapi url ", response.status_code)

    if response.status_code == 200:

        #matched_book_data = json.loads(matched_book_data)
        matched_book_data = json.loads(response.text)  
        #print("fastapi repsonse",matched_book_data)
        #matched_book_data_df = pd.DataFrame.from_records([matched_book_data])
        matched_book_data_df = pd.DataFrame(matched_book_data)
        matched_book_data_df = matched_book_data_df[:10]
        print("<<<<<<<<<<<< matched_book_data_df:",matched_book_data_df)
        
        #matched_books_from_inventory_df = ['BOOK_ID','AUTHOR','DESCRIPTION','GENRE','COVER_PHOTO','ISBN','ISBN13','LINK','PAGES','BOOK_RATING','NO_OF_REVIEWS','TITLE','TOTALRATINGS','AUDIO_LINK','ITEMCOUNT']
        columns = ['BOOK_ID', 'AUTHOR', 'DESCRIPTION', 'GENRE', 'COVER_PHOTO', 
           'ISBN', 'ISBN13', 'LINK', 'PAGES', 'BOOK_RATING', 
           'NO_OF_REVIEWS', 'TITLE', 'TOTALRATINGS', 'AUDIO_LINK', 'ITEMCOUNT']
        
        matched_books_from_inventory_df = pd.DataFrame(columns=columns)
        for index,row in matched_book_data_df.iterrows():
            #print(row[0])
            book_title = row['TITLE']
            author = row['AUTHOR']
            
            #matched_books_from_inventory_df.loc[len(matched_books_from_inventory_df)] = get_book_details_title_author(book_title,author,genre)
            matched_books_from_inventory_df = pd.concat([matched_books_from_inventory_df,get_book_details_title_author(book_title,author,genre)], ignore_index=True)
            #display_single_book(book_title, book_author, cover_url,total_ratings, item_count)
            print("!!!!!!!!  type(matched_books_from_inventory_df:",type(matched_books_from_inventory_df))
        
        print('*****************************************')
        #print(f"User_id's")
        print(matched_books_from_inventory_df)
        print('*****************************************')
        #print(f"Usersssss {user_id}")
        matched_books_from_inventory_df['user_id'] = user_id
        matched_books_from_inventory_df = matched_books_from_inventory_df[['user_id','BOOK_ID']]

        matched_books_from_inventory_df = matched_books_from_inventory_df.groupby('user_id')['BOOK_ID'].agg(lambda x: ','.join(x.astype(str))).reset_index()
        
        user_ids = matched_books_from_inventory_df['user_id'].tolist()
        book_ids_strings = matched_books_from_inventory_df['BOOK_ID'].tolist()

        response = requests.put(f"{FASTAPI_URL}/update_user_recommendations_table", params={"user_id": user_ids, "book_ids":book_ids_strings})
        print(response)
        
        