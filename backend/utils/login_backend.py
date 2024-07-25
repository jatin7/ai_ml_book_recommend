
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from passlib.context import CryptContext
from pymongo import MongoClient
from datetime import datetime, timedelta
from typing import Optional
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus
from pydantic import BaseModel
from snowflake.connector import connect

app = FastAPI()

# Load environment variables
load_dotenv()

conn = connect(
    user=os.getenv('SNOWFLAKE_USER'),
    password=os.getenv('SNOWFLAKE_PASSWORD'),
    account=os.getenv('SNOWFLAKE_ACCOUNT'),
    warehouse='SF_TUTS_WH',  # Adjusted as per your working setup
    database='FINALPROJECT',   # Adjusted as per your working setup
    schema='PUBLIC',        # Adjusted as per your working setup
    role='ACCOUNTADMIN'           # Adjusted as per your working setup
)



# JWT Configuration
SECRET_KEY = os.getenv('JWT_SECRET_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class UserInDB(BaseModel):
    username: str
    password: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str):
    cursor = conn.cursor()
    cursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
    row = cursor.fetchone()
    if not row:
        return False
    user_id, hashed_password = row
    if not verify_password(password, hashed_password):
        return False
    return {"id": user_id, "username": username}

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



# from fastapi import FastAPI, HTTPException, Depends
# from jose import jwt
# from passlib.context import CryptContext
# from pymongo import MongoClient
# from datetime import datetime, timedelta
# from typing import Optional
# import os
# from dotenv import load_dotenv
# from urllib.parse import quote_plus
# from pydantic import BaseModel
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# app = FastAPI()

# # Load environment variables
# load_dotenv()

# # URL encode MongoDB credentials
# mongodb_username = quote_plus(os.getenv("MONGODB_USERNAME", ""))
# mongodb_password = quote_plus(os.getenv("MONGODB_PASSWORD", ""))
# mongodb_host = os.getenv("MONGODB_HOST", "")

# # MongoDB setup
# MONGODB_URL = f"mongodb+srv://{mongodb_username}:{mongodb_password}@{mongodb_host}/?retryWrites=true&w=majority"
# client = MongoClient(MONGODB_URL)
# db = client.user_db
# users_collection = db.users

# # JWT Configuration
# SECRET_KEY = os.getenv("SECRET_KEY", "daFVXeE9Dijzy8np6aNG_NRLiqjd4iVc6pqvZ-IUvW4")  # Ensure you have a secret key
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# class UserInDB(BaseModel):
#     username: str
#     password: str

# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)

# def get_password_hash(password):
#     return pwd_context.hash(password)

# def authenticate_user(username: str, password: str):
#     user = users_collection.find_one({"username": username})
#     if not user:
#         return False
#     if not verify_password(password, user["password"]):
#         return False
#     return user

# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=15)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt

# def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
#     user = authenticate_user(form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(status_code=400, detail="Incorrect username or password")
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user["username"]}, expires_delta=access_token_expires
#     )
#     return {"access_token": access_token, "token_type": "bearer"}


# def register_user(user: UserInDB):
#     user_in_db = users_collection.find_one({"username": user.username})
#     if user_in_db:
#         raise HTTPException(status_code=400, detail="Username already registered")
#     hashed_password = get_password_hash(user.password)
#     users_collection.insert_one({"username": user.username, "password": hashed_password})
#     return {"message": "User successfully registered", "username": user.username}
