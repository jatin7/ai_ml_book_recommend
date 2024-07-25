import streamlit as st
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access environment variables
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL")

# Initialize session state for page navigation
if 'page' not in st.session_state:
    st.session_state.page = 'login'

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
            st.session_state['login'] = True
            st.success(f"Welcome back, {username}!")
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

# if __name__ == "__main__":
#     new()