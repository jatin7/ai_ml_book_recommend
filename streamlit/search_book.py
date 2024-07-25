
import requests
import streamlit as st
from utils import book_details
from book_recommendation import recommended_book
from utils.book_details import add_to_user_history

# Initialize session state variables if they aren't already defined
# if 'button_clicked' not in st.session_state:
#     st.session_state['button_clicked'] = ''

# if 'book_statuses' not in st.session_state:
#     st.session_state.book_statuses = {}

def initialize_state():
    if 'search_results' not in st.session_state:
        st.session_state['search_results'] = None
    if 'book_statuses' not in st.session_state:
        st.session_state['book_statuses'] = {}



def search_book(user_id):
    st.title("Book Search")
    print("inside book search")
    book_title = st.text_input("Enter the book title:")

    if st.button("Search", key='search_book'):
        st.session_state['search_results'] = book_details.get_book_details_title(book_title)
    if st.session_state['search_results'] is not None:
                # st.session_state['search_results'] = book_details.get_book_details_title(book_title)
            # if book_details_df is not None:

        for _, row in st.session_state['search_results'].iterrows():
            book_id= row['Book_ID']
            
            book_details.display_single_book(row['Title'],row['Author'], row['Cover_URL'],row['Total_Ratings'], row['Item_Count'])

            # Get status from session state
            status = st.radio("Select book status:", ["Started Reading", "Add to TBR", "Already Read?"], 
                                key=f"radio_{book_id}", index=st.session_state.book_statuses.get(book_id, None))
            st.write("You selected:", status)
            st.text(row['Title'])

            if status:
                if status == "Started Reading":
                    flag = 0
                    add_to_user_history(user_id, book_id, flag)
                    st.success("Book added to Currently Reading!")
                    st.session_state.book_statuses[book_id] = 0

                if status == "Add to TBR":
                    flag = 1
                    add_to_user_history(user_id, book_id, flag)
                    st.success("Book added to TBR!")
                    st.session_state.book_statuses[book_id] = 1

                if status == "Already Read?":
                    flag = 2
                    add_to_user_history(user_id, book_id, flag)
                    st.success("Book added to Read books!")
                    st.session_state.book_statuses[book_id] = 2

    else:
        st.write("Enter Book Name")
        if st.button("While you wait, let me recommend you something you might like", key = 'recommend'):
            recommended_book(user_id)
            #print("recommended_book()")
    
    if st.button("Want to explore", key = 'explore'):
        #recommended_book()
        recommended_book(user_id)
        print("recommended_book()")
    
        
def main():    
    initialize_state()
    user_data = st.session_state.get('data', None)
    if user_data is not None and 'u_id' in user_data:
        user_id = user_data['u_id']
        search_book(user_id)
    else:
        st.error("Please log in to continue.")
    # user_data = st.session_state.get('data', None)
    # user_id = user_data['u_id']

    # search_book(user_id)
    

if __name__ == "__main__":
    main()

# main.py

# import streamlit as st
# from utils import book_details

# # Ensure this function is called before anything else to set up the session state
# def initialize_state():
#     if 'search_results' not in st.session_state:
#         st.session_state['search_results'] = None
#     if 'book_statuses' not in st.session_state:
#         st.session_state['book_statuses'] = {}

# def search_book(user_id):
#     st.title("Book Search")
#     book_title = st.text_input("Enter the book title:")

#     # Debug print
#     st.write('Debug: Before button')

#     if st.button("Search", key='search_book'):
#         # Debug print
#         st.write('Debug: Button clicked')

#         # Make sure this function is actually retrieving data
#         search_results = book_details.get_book_details_title(book_title)
        
#         # Debug print
#         st.write('Debug: Search results obtained', search_results)

#         st.session_state['search_results'] = search_results

#     # Display results
#     if st.session_state['search_results'] is not None:
#         for _, row in st.session_state['search_results'].iterrows():
#             book_details.display_single_book(row)
#             # Debug print
#             st.write('Debug: Displaying book', row['Title'])

# # In your main or wherever the search_book is called
# def main():
#     initialize_state()
#     user_data = st.session_state.get('data', None)
#     if user_data and 'u_id' in user_data:
#         user_id = user_data['u_id']
#         search_book(user_id)
#     else:
#         st.error("Please log in to continue.")

# if __name__ == "__main__":
#     main()