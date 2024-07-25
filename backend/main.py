
from utils.snowflake_connector import get_snowflake_inventory_data_with_book_title,get_snowflake_inventory_data_with_book_id, update_bookshelf_flag, recommend_books, get_user_history_data,add_to_user_history,match_survey_book_attributes,get_book_title_match,add_user_recommendations,get_user_recommendation_data
from utils.snowflake_connector import get_user_history_data_recommendations, get_snowflake_user_book_features_data,get_snowflake_all_book_features_data, add_vector_already_generated
from utils  import snowflake_connector
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from utils.login_backend import verify_password,get_password_hash,authenticate_user,create_access_token
from utils import snowflake_connector
from snowflake.connector import connect, ProgrammingError
import json
from typing import List, Union
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import pandas as pd
 
class Recommendation(BaseModel):
    user_id: int
    recommendations: list[str]

app = FastAPI()

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


ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class UserInDB(BaseModel):
    username: str
    password: str

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.get('id')}


@app.post("/register")
async def register_user(user: UserInDB):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (user.username,))
    count = cursor.fetchone()[0]
    if count > 0:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (user.username, hashed_password))
    conn.commit()
    return {"message": "User successfully registered", "username": user.username}


# # Temp FastAPI endpoint to fetch recommendation data
# @app.get("/recommendation")
# async def get_recommendation():
#     print("we are in async def get_recommendation")
#     recommended_book_list = snowflake_connector.recommend_books()
#     print("in the async def: ", recommended_book_list)
#     return recommended_book_list



@app.put("/insert_user_history_{user_id}_{book_id}_{flag}")
async def insert_user_history(user_id: int, book_id: int, flag: int):
    add_to_user_history(user_id, book_id, flag)
    return {"message": "User history inserted successfully."}


# @app.get("/snowflake_inventory/book_id/{book_id}")
# async def get_snowflake_inventory_details_book_id(book_id: int):
#     #print("------get_snowflake_inventory_details_book_id---------------book_id", book_id)
#     print("Fetching inventory data from Snowflake with book_id")
#     from starlette.concurrency import run_in_threadpool
#     inventory_data = await run_in_threadpool(get_snowflake_inventory_data_with_book_id, book_id=book_id)
#     return inventory_data.to_json(orient="records")

from starlette.concurrency import run_in_threadpool

@app.get("/snowflake_inventory/book_id/{book_id}")
async def get_snowflake_inventory_details_book_id(book_id: int):
    print("Fetching inventory data from Snowflake with book_id")
    try:
        inventory_data = await run_in_threadpool(get_snowflake_inventory_data_with_book_id, book_id=book_id)
        return inventory_data.to_json(orient="records")
    except Exception as e:  # It's better to catch a more specific exception
        raise HTTPException(status_code=500, detail=str(e))


# @app.get("/snowflake_inventory/title/{title}")
# async def get_snowflake_inventory_details_title(title: str):
#     print("Fetching inventory data from Snowflake with title.")
#     from starlette.concurrency import run_in_threadpool
#     inventory_data = await run_in_threadpool(get_snowflake_inventory_data_with_book_title, book_title=title)
#     return inventory_data.to_json(orient="records")

@app.get("/snowflake_inventory/title/{title}")
async def get_snowflake_inventory_details_title(title: str):
    try:
        inventory_data = get_snowflake_inventory_data_with_book_title(title)
        if inventory_data is None:
            return []  # or handle the empty case differently as you see fit
        return inventory_data.to_json(orient="records")
    except Exception as e:
        # If an exception occurs, log it and return a 500 error
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")



@app.get("/snowflake_inventory/match/{title}")
async def get_book_details_title_match(title: str):
    try:
        inventory_data = get_book_title_match(title)
        if inventory_data is None:
            return []  # or handle the empty case differently as you see fit
        return inventory_data.to_json(orient="records")
    except Exception as e:
        # If an exception occurs, log it and return a 500 error
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")



@app.put("/update_user_history_{user_id}_{book_id}_{new_flag}")
async def update_user_history_flag(user_id: int, book_id: int, new_flag: int):
    update_bookshelf_flag(user_id, book_id, new_flag)
    return {"message": "Bookshelf flag updated successfully."}


@app.get("/snowflake_user_history/{user_id}")
async def get_snowflake_user_history(user_id: int):
    try:
        print("Fetching user history data from Snowflake.")
        user_history = get_user_history_data(user_id)
        return user_history.to_json(orient='records')  # Return JSON representation of DataFrame
    except Exception as e:
        return {"error": str(e)}


@app.get("/book_attributes/{mood}_{theme}_{plot_complexity}_{pace}_{length}")
async def match_book_attributes(mood,theme,plot_complexity,pace,length):
    try:
        print("Fetching user history data from Snowflake.")
        matched_books = match_survey_book_attributes(mood,theme,plot_complexity,pace,length)
        print("async def match_book_attributes:",matched_books)
        if matched_books is not None:
            return matched_books.to_dict(orient='records') # Return JSON representation of DataFrame
        else:
            return {"error": "No matched books found."}
    except Exception as e:
        return {"error": str(e)}


@app.put("/update_user_recommendations_table")
async def user_recommendations(user_id: List[int] = Query(...), book_ids: List[str] = Query(...) ):
    try:
        print(f"Received user_ids: {user_id}")
        print(f"Received book_ids: {book_ids}")
        df_recommendations = pd.DataFrame({
            'user_id': user_id,
            'book_ids': book_ids
        })
        print(f"DataFrame created: {df_recommendations}")
        add_user_recommendations(df_recommendations)
        return {"message": "User_Recommendations Table updated successfully."}
    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/snowflake_user_recommendation/{user_id}")
async def get_snowflake_user_recommendation(user_id: int = None):
    try:
        print("Fetching user recommednation data from Snowflake.")
        user_recommendation = get_user_recommendation_data(user_id)
        return user_recommendation.to_json(orient='records')  # Return JSON representation of DataFrame
    except Exception as e:
        return {"error": str(e)}


##################################### 


@app.get("/snowflake_recommendation_user_history")
async def get_snowflake_recommendation_user_history():
    try:
        print("Fetching user history data for recommendation from Snowflake.")
        user_history = get_user_history_data_recommendations()
        return user_history.to_json(orient='records')  # Return JSON representation of DataFrame
    except Exception as e:
        return {"error": str(e)}
   
 
@app.get("/snowflake_user_history_book_features")
async def get_snowflake_user_history_book_features():
   
    print("Fetching user book data from Snowflake.")
    from starlette.concurrency import run_in_threadpool
    # Run the synchronous database operation in a background thread
    user_book_data = await run_in_threadpool(get_snowflake_user_book_features_data)
    #print(user_book_data)
    # Convert DataFrame to JSON for HTTP response
    return user_book_data.to_json(orient="records")
 
 
@app.get("/snowflake_all_book_features")
async def get_snowflake_all_book_features():
   
    print("Fetching all book data from Snowflake.")
    from starlette.concurrency import run_in_threadpool
    # Run the synchronous database operation in a background thread
    all_book_data = await run_in_threadpool(get_snowflake_all_book_features_data)
    #print(all_book_data)
    # Convert DataFrame to JSON for HTTP response
    return all_book_data.to_json(orient="records")
 
 
 
@app.put("/update_vector_generated_table")
async def vector_generated_books(book_ids: List[str] = Query(...)):
    add_vector_already_generated(book_ids)
    return {"message": "Vector_generated Table updated successfully."}





######################################
  
if __name__ == "__main__":
    import uvicorn
    app()


