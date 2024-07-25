'''
# Sample data for demonstration
data_book_features = {
    'book_id': [101, 102, 103, 104],
    'pace': [7, 5, 6, np.nan],  # Example of a missing value
    'length': [8, 5, np.nan, 6],  # Example of a missing value
    'plot_complexity': [6, 4, 9, 5],
    'theme': ['4|5', '3|6|7', '1|4', '3|5'],
    'mood': [3, 7, np.nan, 2],  # Example of a missing value
    'author': ['Author A', 'Author B', 'Author C', 'Author A'],
    'summary': ['A tale of adventure', 'A story of love', 'A complex mystery unfolds', 'A journey of self-discovery'],
    'genre_list': ['Adventure,Fantasy', 'Romance', '', 'Self-help,Inspirational'],  # Example of an empty value
    'public_rating': [4.5, 3.0, 4.0, 3.5],
    'number_of_reviews': [200, 150, 300, 180]
}

# Convert dictionary to DataFrame
book_features = pd.DataFrame(data_book_features)
'''

'''
def generate_vectors(book_features):
    # Generate embeddings for summaries and genres
    book_features['summary_embeddings'] = list(model.encode(book_features['summary']))
    book_features['genre_embeddings'] = list(model.encode(book_features['genre_list']))

    # Split the theme values and encode them
    theme_values = book_features['theme'].str.get_dummies('|')

    # Convert theme_values to DataFrame
    theme_values = pd.DataFrame(theme_values, index=book_features.index)

    # Fill missing values
    book_features.fillna(0, inplace=True)  # Fill missing numerical values with 0
    book_features['genre_list'].replace('', 'Unknown', inplace=True)  # Replace empty genre list with 'Unknown'

    
    # Function to calculate weighted profile for books
    def calculate_book_profile(row):
        metadata_weight = row['public_rating'] / 5 * np.log1p(row['number_of_reviews'])
        feature_vector = np.concatenate(
            (row[['pace', 'length', 'plot_complexity']].values,
            row['summary_embeddings'],
            row['genre_embeddings'],
            np.array(theme_values.loc[row.name]).astype(float),  # Access the corresponding row in theme_values DataFrame
            np.array([row['mood']]).astype(float))
        )
        return feature_vector * metadata_weight

    
    # Apply the function to calculate profiles for all books
    book_profiles = book_features.apply(calculate_book_profile, axis=1).tolist()
    book_profiles = pd.DataFrame(book_profiles, index=book_features['book_id'])

    # Normalize book profiles (here, a simple example)
    book_profiles = book_profiles.div(np.linalg.norm(book_profiles, axis=1, keepdims=True))
    
    return book_profiles

'''

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, PodSpec
import requests
import os
from dotenv import load_dotenv
import json
from sklearn.decomposition import PCA

load_dotenv()

FASTAPI_URL = os.getenv('FASTAPI_URL')
# Load a pre-trained SBERT model
model = SentenceTransformer('all-MiniLM-L6-v2')


def get_book_data():
    response = requests.get(f"{FASTAPI_URL}/snowflake_all_book_features")
    response.raise_for_status()

    if response.status_code == 200:
            book_info_data = json.loads(response.text)  
            book_features = pd.read_json(book_info_data)
            print(book_features.head(5))

    return book_features


def preprocess_book_data(book_features):
    book_features.columns = book_features.columns.str.lower()
    book_features['genre_list'] = book_features['genre_list'].fillna('')


    # Remove newline characters from 'SUMMARY' column
    book_features['summary'] = book_features['summary'].str.replace('\n', '')

    return book_features


def generate_vectors(book_features):
    # Generate embeddings for summaries and genres
    book_features['summary_embeddings'] = list(model.encode(book_features['summary']))
    book_features['genre_embeddings'] = list(model.encode(book_features['genre_list']))

    # Split the theme values and encode them
    theme_values = book_features['theme'].str.get_dummies('|')

    # Convert theme_values to DataFrame
    theme_values = pd.DataFrame(theme_values, index=book_features.index)

    # Fill missing values
    book_features.fillna(0, inplace=True)  # Fill missing numerical values with 0
    book_features['genre_list'].replace('', 'Unknown', inplace=True)  # Replace empty genre list with 'Unknown'

    
    # Function to calculate weighted profile for books
    def calculate_book_profile(row):
        metadata_weight = row['public_rating'] / 5 * np.log1p(row['number_of_reviews'])
        feature_vector = np.concatenate(
            (row[['pace', 'length', 'plot_complexity']].values,
            row['summary_embeddings'],
            row['genre_embeddings'],
            np.array(theme_values.loc[row.name]).astype(float),  # Access the corresponding row in theme_values DataFrame
            np.array([row['mood']]).astype(float))
        )
        return feature_vector * metadata_weight

    
    # Apply the function to calculate profiles for all books
    book_profiles = book_features.apply(calculate_book_profile, axis=1).tolist()
    
    '''
    book_profiles = pd.DataFrame(book_profiles, index=book_features['book_id'])

    # Normalize book profiles (here, a simple example)
    book_profiles = book_profiles.div(np.linalg.norm(book_profiles, axis=1, keepdims=True))
    '''
    #print(book_profiles)
    # Padding vectors to ensure a minimum length of 799
    max_length = 799
    padded_book_profiles = [np.pad(profile, (0, max_length - len(profile)), 'constant') if len(profile) < max_length else profile for profile in book_profiles]
    book_profiles = pd.DataFrame(padded_book_profiles, index=book_features['book_id'])

    # Normalize book profiles
    book_profiles = book_profiles.div(np.linalg.norm(book_profiles, axis=1, keepdims=True))
    
    return book_profiles

def add_to_vector_generated(book_profiles):
    book_list = book_profiles
    response = requests.put(f"{FASTAPI_URL}/update_vector_generated_table", params={"book_ids": book_list})
    print('Book added to vectors generated')


def intialize_pinecone_and_insert(api_key, host_name,df_book_profiles):
    pc = Pinecone(api_key=api_key)
    index = pc.Index(host = host_name)

    vectors = [(str(index), row.tolist()) for index, row in df_book_profiles.iterrows()]  # Prepare vectors with ID and vector

    def batch_upsert(vectors, batch_size=500):
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            index.upsert(vectors=batch)
            print(f"Batch {i//batch_size + 1} upserted successfully")

    batch_upsert(vectors, batch_size=500)

    print('vectors saved to pinecone')
    book_ids = df_book_profiles.index.tolist()
    #print(book_ids)
    add_to_vector_generated(book_ids)


if __name__ == "__main__":
 
    
    book_features = get_book_data()
    if book_features is not None:
        book_features = preprocess_book_data(book_features)
        book_profiles = generate_vectors(book_features)

        df_book_profiles = pd.DataFrame(book_profiles)
        print(df_book_profiles)

        '''
        print(book_features)
        print('****************Values**************')
        book_profiles_array = book_profiles.values  # Convert DataFrame to NumPy array
        print(book_profiles_array[:5])

        print('***************Index***********************')
        book_profiles_array = book_profiles.index
        print(book_profiles_array[:5])
        
        print('**********Dimension***********')
        print(df_book_profiles.shape[1])
        '''

        #Initialize Pinecone
        api_key = os.getenv('PINECONE_API')
        host_name = os.getenv('PINECONE_HOST')

        intialize_pinecone_and_insert(api_key, host_name, df_book_profiles)
    else:
        print('No New Books')



