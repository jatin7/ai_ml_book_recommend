import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, PodSpec
import requests
import os
from dotenv import load_dotenv
import json
from sklearn.decomposition import PCA
from sklearn.random_projection import GaussianRandomProjection
 
load_dotenv()
 
FASTAPI_URL = os.getenv('FASTAPI_URL')
 
def get_user_history():
    response = requests.get(f"{FASTAPI_URL}/snowflake_recommendation_user_history")
    response.raise_for_status()
 
    if response.status_code == 200:
            user_info_data = json.loads(response.text)  
            user_features = pd.read_json(user_info_data)
            #print(user_features.head(5))
 
    return user_features
 
def get_user_book_data():
    response = requests.get(f"{FASTAPI_URL}/snowflake_user_history_book_features")
    response.raise_for_status()
 
    if response.status_code == 200:
            book_info_data = json.loads(response.text)  
            book_features = pd.read_json(book_info_data)
            #print(book_features.head(5))
 
    return book_features
 
def generate_embeddings(user_history, book_features):
    # Impute missing numeric data with the median
    for column in ['pace', 'length', 'plot_complexity', 'mood']:
        book_features[column].fillna(0, inplace=True)
 
    # Load a pre-trained SBERT model
    model = SentenceTransformer('all-MiniLM-L6-v2')
 
    # Generate embeddings for summaries and genres
    book_features['summary_embeddings'] = list(model.encode(book_features['summary'], show_progress_bar=False))
    book_features['genre_embeddings'] = list(model.encode(book_features['genre_list'], show_progress_bar=False))
 
    # One-hot encode the categorical features (themes and genres)
    book_features['mood'] = book_features['mood'].replace({None: np.nan})
    book_features['mood'].fillna(0, inplace=True)
 
    theme_encoded = book_features['theme'].str.get_dummies('|').add_prefix('theme_')
    genre_encoded = book_features['genre_list'].str.get_dummies('|').add_prefix('genre_')
 
    # Include the encoded themes and genres back into book_features
    book_features = pd.concat([book_features, theme_encoded, genre_encoded], axis=1)
    book_features.drop(['theme', 'genre_list'], axis=1, inplace=True)
 
    # Merge user history with book features
    user_books = user_history.merge(book_features, on='book_id')
 
    # Function to calculate weighted profile
   
    def calculate_profile(row):
        # Define weights based on the flag
        flag_weight = 0.1 if row['flag'] == 0 else (0.5 if row['flag'] == 1 else 1)
        # Define default rating weight
        rating_weight = 3 if pd.isnull(row['rating']) and row['flag'] == 2 else (row['rating'] if not pd.isnull(row['rating']) else 0.1)
        total_weight = flag_weight * rating_weight
        metadata_weight = row['public_rating'] / 5 * np.log1p(row['number_of_reviews'])
       
        # Select theme and genre columns dynamically
        theme_genre_cols = [col for col in row.index if col.startswith('theme_') or col.startswith('genre_')]
        #print("Theme and Genre Columns:", theme_genre_cols)
        theme_genre_values = row[theme_genre_cols].values
        #print("Theme and Genre Values:", theme_genre_values)
       
        # Convert non-numeric values to NaN
        theme_genre_values_numeric = pd.to_numeric(theme_genre_values.flatten(), errors='coerce')
        theme_genre_values_numeric = np.nan_to_num(theme_genre_values_numeric, nan=0)  # Replace NaNs with 0
       
        # Change to int
        theme_genre_values_numeric = theme_genre_values_numeric.astype(int)
       
        theme_genre_values_numeric = theme_genre_values_numeric.reshape(theme_genre_values.shape)
       
        # Concatenate feature vectors
        feature_vector = np.concatenate((
            row[['pace', 'length', 'plot_complexity', 'mood']].values.astype(float),
            row['summary_embeddings'],
            row['genre_embeddings'],
            theme_genre_values_numeric
        ))
       
        return feature_vector * total_weight * metadata_weight                
    # Apply the function and sum up the profiles
    user_profiles = user_books.apply(calculate_profile, axis=1).tolist()
    user_profiles = pd.DataFrame(user_profiles, index=user_books['user_id']).groupby('user_id').sum()
 
    # Ensure all profiles are exactly 799 dimensions
    desired_length = 799
    user_profiles = user_profiles.apply(lambda x: np.pad(x, (0, max(0, desired_length - len(x))), 'constant') if len(x) < desired_length else x[:desired_length], axis=1)
 
    # Normalize user profiles
    user_profiles = user_profiles.div(np.linalg.norm(user_profiles, axis=1, keepdims=True))
 
    return user_profiles
 
 
 
def initialize_pinecone_and_query(api_key, host_name, df_user_profiles, df_user_history):
    pc = Pinecone(api_key=api_key)
    index = pc.Index(host=host_name)
    '''
    all_results = []
 
    for user_id, row in df_user_profiles.iterrows():
        # Extract vector from the DataFrame row, converting numpy array to list
        vector = row.values.tolist()
       
        # Query Pinecone index with the user's vector, requesting the top 10 similar book vectors
        query_result = index.query(vector=vector, top_k=20)
        #print(query_result)
        for match in query_result["matches"]:
            book_id = match["id"]
            similarity_score = match["score"]
           
            all_results.append({
                "user_id": user_id,
                "book_id": book_id,
                "similarity_score": similarity_score
            })
 
    # Convert list of dicts to DataFrame
    result_df = pd.DataFrame(all_results)
'''
    all_results = []
 
    for user_id, row in df_user_profiles.iterrows():
        # Extract vector from the DataFrame row, converting numpy array to list
        vector = row.values.tolist()
 
        # Retrieve the books the user has already read
        read_books = set(df_user_history[df_user_history['user_id'] == user_id]['book_id'])
 
        # Query Pinecone index with the user's vector, initially requesting a larger number of results
        query_result = index.query(vector=vector, top_k=30)
        recommendations = []
 
        # Filter out books the user has already read, keeping the order based on similarity score
        for match in query_result["matches"]:
            if match["id"] not in read_books:
                recommendations.append((match["id"], match["score"]))
                # Stop when 10 unique recommendations are found
                if len(recommendations) == 10:
                    break
 
        # Add filtered recommendations to the result list
        for book_id, similarity_score in recommendations:
            all_results.append({
                "user_id": user_id,
                "book_id": book_id,
                "similarity_score": similarity_score
            })
 
    # Convert list of dicts to DataFrame
    result_df = pd.DataFrame(all_results)
 
    # Group by 'user_id' and concatenate 'book_id' based on 'similarity_score'
    result_df = result_df.sort_values(by=['user_id', 'similarity_score'], ascending=[True, False]) \
                .groupby('user_id')['book_id'] \
                .apply(lambda x: ','.join(map(str, x))) \
                .reset_index()
 
    # Rename columns for clarity
    result_df.columns = ['user_id', 'book_ids']
 
    return result_df
 
def add_to_user_recommendations(user_recommendations):
    user_ids = user_recommendations['user_id'].tolist()
    book_ids_strings = user_recommendations['book_ids'].tolist()
    response = requests.put(f"{FASTAPI_URL}/update_user_recommendations_table", params={"user_id": user_ids, "book_ids":book_ids_strings})
    print(response)
 
 
if __name__ == "__main__":
     # Convert dictionaries to DataFrames
   
    user_history = get_user_history()
    book_features = get_user_book_data()
 
    book_features.columns = book_features.columns.str.lower()
    user_history.columns = user_history.columns.str.lower()
 
    #print(user_history.head())
    #print(book_features.head())
 
    user_profiles = generate_embeddings(user_history, book_features)
 
    df_user_profiles = pd.DataFrame(user_profiles)
    print(user_profiles)
 
    #Initialize Pinecone
    api_key = os.getenv('PINECONE_API')
    host_name = os.getenv('PINECONE_HOST')
 
    #intialize_pinecone_and_insert(api_key, host_name,user_profiles)
    result = initialize_pinecone_and_query(api_key, host_name, df_user_profiles, user_history)
    print(result)
 
    add_to_user_recommendations(result)