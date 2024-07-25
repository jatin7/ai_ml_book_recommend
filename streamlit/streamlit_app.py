import streamlit as st
import user_dashboard
import search_book,book_recommendation,user_survey
import login
import requests
from dotenv import load_dotenv
import os

'''
# Initialize session state for page navigation
if 'page' not in st.session_state:
    st.session_state['page'] = ''

if 'data' not in st.session_state:
    st.session_state['data'] = {}

if 'login' not in st.session_state:
    st.session_state['login'] = False 


def main():
    print("we are in pages login_main function ")
    login.new()
       
    if st.session_state['login'] :
        st.sidebar.title("Navigation")
        PAGES = {
            "Dashboard": user_dashboard,
            "Search": search_book,
            "Recommendation": book_recommendation,
            "Survey": user_survey
        }
    
        st.sidebar.title('Navigation')
        selection = st.sidebar.radio("Go to", list(PAGES.keys()))

        if st.sidebar.button('Logout'):
            st.session_state['login'] = False
            st.rerun()

        if st.session_state['login']:
            page = PAGES[selection]
            page_function = getattr(
                page, 'show_' + selection.lower().replace(' ', '_'))
            page_function()

    # if st.session_state['login']:
    #     st.sidebar.title("Navigation")
    #     PAGES = {
    #         "Dashboard": user_dashboard,
    #         "Search": search_book,
    #         "Recommendation": book_recommendation,
    #         "Survey": user_survey
    #     }
    
    #     st.sidebar.title('Navigation')
    #     selection = st.sidebar.radio("Go to", list(PAGES.keys()))

    #     if st.sidebar.button('Logout'):
    #         st.session_state['login'] = False
    #         st.rerun()

    #     page = PAGES[selection]
    #     page_function = getattr(
    #         page, 'show_' + selection.lower().replace(' ', '_'))
    #     page_function()
    # else:
    #     login.new()
    #     if st.session_state.page == 'register':
    #         login.registration_form()

    #     if st.session_state['login']:
    #         st.success("Logged in successfully!")

    # print("login state:", st.session_state['login'])  # Check the state
    # if not st.session_state['login']:  # Display login form if not logged in
    #     print("Showing login form...")
    #     login.new()
    #     if st.session_state.page == 'register':
    #         login.registration_form()
    # else:
    #     st.sidebar.title("Navigation")
    #     PAGES = {
    #         "Dashboard": user_dashboard,
    #         "Search": search_book,
    #         "Recommendation": book_recommendation,
    #         "Survey": user_survey
    #     }
    
    #     st.sidebar.title('Navigation')
    #     selection = st.sidebar.radio("Go to", list(PAGES.keys()))

    #     if st.sidebar.button('Logout'):
    #         st.session_state['login'] = False
    #         st.rerun()

    #     page = PAGES[selection]
    #     page_function = getattr(
    #         page, 'show_' + selection.lower().replace(' ', '_'))
    #     page_function()

'''
# Load environment variables from .env file
load_dotenv()

# Access environment variables
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL")

# Initialize session state for page navigation
if 'page' not in st.session_state:
    st.session_state.page = ''

if 'login' not in st.session_state:
    st.session_state.login = False

def login(username: str, password: str):
    """Attempt to log in a user."""
    response = requests.post(f"{FASTAPI_BASE_URL}/token", data={"username": username, "password": password})
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to log in")
        return None

def register(username: str, password: str):
    """Attempt to register a new user."""
    response = requests.post(f"{FASTAPI_BASE_URL}/register", json={"username": username, "password": password})
    if response.status_code == 200:
        st.success("User successfully registered")
    else:
        st.error("Failed to register")

# Function to create a form for Login
def login_form():
    st.subheader("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        token_response = login(username, password)
        if token_response:
            st.session_state.token = token_response["access_token"]
            st.session_state['page'] = 'login'
            st.success(f"Welcome back, {username}!")
            new()
            # You might want to navigate to a different page here or do something else
    if st.button("Not registered? Click here to Register"):
        st.session_state.page = 'register'
        new()


# Function to create a form for Registration
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
        st.session_state.page = ''
        new()

def new():

    # Render the active page based on session state
    if st.session_state.page == '':
        login_form()
    elif st.session_state.page == 'register':
        registration_form()
    elif st.session_state['page']=='login':
        st.success('User Dashboard')


if __name__ == "__main__":
    new()


