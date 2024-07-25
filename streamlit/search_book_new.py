# import streamlit as st
# from utils import book_details
# from utils.book_details import add_to_user_history
 
# def search_book(user_id):
#     st.title("Book Search")
#     print("inside book search")
#     book_title = st.text_input("Enter the book title:")
#     if st.button("Search", key='search_book'):
#         if book_title:
#             book_details_df = book_details.get_book_details_title(book_title)
#             if book_details_df is not None:
#                 for index, row in book_details_df.iterrows():
#                     book_id= row['Book_ID']
#                     book_details.display_single_book(row['Title'],row['Author'], row['Cover_URL'],row['Total_Ratings'], row['Item_Count'])
 
#                     # Check if the button has been clicked
#                     start_reading_clicked = st.cache_resource('start_reading_clicked', default=False)
#                     add_to_tbr_clicked = st.cache_resource('add_to_tbr_clicked', default=False)
#                     already_read_clicked = st.cache_resource('already_read_clicked', default=False)
 
#                     if st.button("Started Reading", key=f"add_to_currently_reading_{book_id}"):
#                         # Set the button state to True
#                         st.cache_resource('start_reading_clicked', True)
 
#                     if st.button("Add to TBR", key=f'add_to_tbr_{book_id}'):
#                         # Set the button state to True
#                         st.cache_resource('add_to_tbr_clicked', True)
 
#                     if st.button("Already Read?", key=f'add_to_read_{book_id}'):
#                         # Set the button state to True
#                         st.cache_resource('already_read_clicked', True)
#                     # Process button clicks
#                     if start_reading_clicked:
#                         flag = 0
#                         add_to_user_history(user_id, book_id, flag)
#                         st.success("Book added to Currently Reading!")
 
#                     if add_to_tbr_clicked:
#                         flag = 1
#                         add_to_user_history(user_id, book_id, flag)
#                         st.success("Book added to TBR!")
 
#                     if already_read_clicked:
#                         flag = 2
#                         add_to_user_history(user_id, book_id, flag)
#                         st.success("Book added to Read books!")
 
#         else:
#             st.error("Book Not available")
#             if st.button("While you wait, let me recommend you something you might like", key='recommend'):
#                 print("recommended_book()")
#     if st.button("Want to explore", key='explore'):
#         print("recommended_book()")
 
# def main():    
#     user_data = st.session_state.get('data', None)
#     user_id = user_data['u_id']
#     search_book(user_id)
# if __name__ == "__main__":
#     main()