'''
import dask.dataframe as dd

# Specify the path to your books CSV file
path_to_books_csv = '../Data/GoodReads/GoodReads_books.csv'

# Define data types explicitly to avoid dtype inference issues
dtypes = {
    'isbn': 'object',   # Treat as object initially for manipulation
    'isbn13': 'object'
}

# Load the books dataset using Dask, specifying dtypes
books_dd = dd.read_csv(path_to_books_csv, dtype=dtypes)

# Remove unnecessary columns 'bookformat' and 'pages'
books_dd = books_dd.drop(['bookformat', 'pages'], axis=1)

# Add a new column 'audio_link' with null values using map_partitions
def add_audio_link(df):
    df['audio_link'] = None
    return df

books_dd = books_dd.map_partitions(add_audio_link)

# Handle ISBN filling and conversion
def process_isbn(df):
    df['isbn'] = df['isbn'].fillna('0000000000')  # Fill NaNs
    df['isbn13'] = df['isbn13'].fillna('0')  # Fill NaNs for isbn13
    df['isbn13'] = df['isbn13'].astype(str)  # Convert isbn13 to string
    return df

books_dd = books_dd.map_partitions(process_isbn)

# Rename columns
books_dd = books_dd.rename(columns={
    'desc': 'description',
    'img': 'cover_photo',
    'rating': 'book_rating',
    'reviews': 'no_of_reviews'
})

# Optionally, you can save the modified dataframe to a new CSV file
output_path = '../Data/GoodReads/Cleaned/GoodReads_books_cleaned.csv'
books_dd.to_csv(output_path, index=False, single_file=True)
'''
import dask.dataframe as dd
import pandas as pd
from langdetect import detect
import requests
import json

def get_book_summary(isbn, api_key):
    """Fetch book summary from Google Books API using ISBN."""
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}&key={api_key}"
    response = requests.get(url)
    data = response.json()
    if 'items' in data:
        book_info = data['items'][0]  # Assuming the first result is the book we want
        return book_info.get('volumeInfo', {}).get('description', 'No description available.')
    else:
        return 'No description available.'

def translate_text(text, api_key, target='en'):
    """Translate text to the target language (default is English) using Google Translate API."""
    if pd.isna(text):
        return text
    try:
        src_lang = detect(text)
        if src_lang != target:
            data = {'q': text, 'target': target, 'key': api_key}
            response = requests.post("https://translation.googleapis.com/language/translate/v2", data=data)
            result = json.loads(response.text)
            return result['data']['translations'][0]['translatedText']
        return text
    except Exception as e:
        print(f"Error translating {text}: {e}")
        return text  # Return the original text if any error occurs

def process_descriptions(df, api_key):
    """Fill missing descriptions if possible and translate non-English descriptions."""
    for index, row in df.iterrows():
        isbn = row['isbn']
        description = row['description']
        
        # Check if ISBN is available and non-empty
        if pd.notna(isbn) and isbn.strip():
            if pd.isna(description) or description.strip() == '':
                # Attempt to fetch description if it is missing or empty
                fetched_description = get_book_summary(isbn, api_key)
                if fetched_description and fetched_description != 'No description available.':
                    df.at[index, 'description'] = fetched_description
                # If no fetched description, move on to next iteration
                continue

        # Translate the description if it exists and is necessary
        if pd.notna(description) and description.strip() != '':
            df.at[index, 'description'] = translate_text(description, api_key)

        else:
            print(f"No valid ISBN or existing description for index {index}, skipping translation.")
    return df

# Setup and configurations
GOOGLE_API_KEY = ''  # Ensure this is securely configured
path_to_books_csv = '../Data/GoodReads/GoodReads_books.csv'
dtypes = {'isbn': 'object', 'isbn13': 'object'}
books_dd = dd.read_csv(path_to_books_csv, dtype=dtypes)
books_dd = books_dd.drop(['bookformat'], axis=1)

# Dask DataFrame operations
books_dd = books_dd.rename(columns={'desc': 'description', 'img': 'cover_photo', 'rating': 'book_rating', 'reviews': 'no_of_reviews'})
books_dd = books_dd.map_partitions(lambda df: process_descriptions(df, GOOGLE_API_KEY))

# Optionally, save the modified dataframe
output_path = '../Data/GoodReads/Cleaned/GoodReads_books_cleaned.csv'
books_dd.to_csv(output_path, index=False, single_file=True)

