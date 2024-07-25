

import streamlit as st
import requests
import search_book, book_recommendation, user_survey, user_dashboard, search_book_new
 
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access environment variables
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL")
 
# Initialize session state variables if they aren't already defined
if 'login' not in st.session_state:
    st.session_state['login'] = False
if 'token' not in st.session_state:
    st.session_state['token'] = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'data' not in st.session_state:
    st.session_state['data'] = {}
 
def call_user_dashboard():
    st.sidebar.title("Navigation")
    PAGES = {
        "User Dashboard": user_dashboard,
        "Search Book": search_book,
        "Book Recommendation": book_recommendation
       
    }
 
    selection = st.sidebar.radio("Go to", list(PAGES.keys()))
 
    if st.sidebar.button('Logout'):
        st.session_state['login'] = False
        st.session_state['token'] = None
        st.session_state.page = 'login'
        #st.rerun()
 
    page = PAGES[selection]
    page_function = getattr(page, 'main', None)
    if page_function:
        page_function()
    else:
        st.error(f"Function 'main' not found in {selection}.")
 
def login(username: str, password: str):
    response = requests.post(f"{FASTAPI_BASE_URL}/token", data={"username": username, "password": password})
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to log in")
        return None
 
def register(username: str, password: str):
    response = requests.post(f"{FASTAPI_BASE_URL}/register", json={"username": username, "password": password})
    if response.status_code == 200:
        st.success("User successfully registered")
    else:
        st.error("Failed to register")
 
def login_form():
    st.subheader("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        token_response = login(username, password)
        if token_response:
            st.session_state.token = token_response["access_token"]
            st.session_state.login = True
            st.session_state.user_id = token_response['user_id']
            st.success(f"Welcome back, {username}!")
 
            user_id = token_response['user_id']  
            data = {"u_id":user_id, "username": username}
            st.session_state['data'] = data
 
 
            st.rerun()
 
    if st.button("Not registered? Click here to Register"):
        st.session_state.page = 'register'
        st.rerun()
 
def registration_form():
    st.subheader("Register")
    username = st.text_input("Choose a Username", key="register_username")
    password = st.text_input("Choose a Password", type="password", key="register_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
    if st.button("Register"):
        if password == confirm_password:
            register(username, password)
        else:
            st.error("Passwords do not match")
    if st.button("Already registered? Click here to Login"):
        st.session_state.page = 'login'
 
def main():
    if st.session_state.login:
        call_user_dashboard()
    elif st.session_state.page == 'register':
        registration_form()
    else:
        login_form()
 
if __name__ == "__main__":
    main()