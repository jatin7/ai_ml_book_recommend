import pandas as pd
import json

# Path to your .jl file
input_file = 'book_goodreads_young_book.jl'
output_file = 'CSV/out_young_books.csv'

# Read .jl file and convert each line to a dictionary
data = []
with open(input_file, 'r') as file:
    for line in file:
        json_data = json.loads(line)
        # Check if 'ratingHistogram' is in the JSON data
        if 'ratingHistogram' in json_data and json_data['ratingHistogram']:
            # Calculate average rating
            total_ratings = sum(json_data['ratingHistogram'])
            weighted_sum = sum(rating * (index + 1) for index, rating in enumerate(json_data['ratingHistogram']))
            average_rating = weighted_sum / total_ratings if total_ratings > 0 else 0
            json_data['ratingHistogram'] = round(average_rating,2)
        data.append(json_data)

# Convert list of dictionaries to a DataFrame
df = pd.DataFrame(data)

column_mappings = {
    'author': 'author',
    'bookformat': 'language',  
    'desc': 'description',
    'genre': 'genres',
    'img': 'imageUrl',
    'isbn': 'isbn',
    'isbn13': 'isbn13',
    'link': 'url',
    'pages': 'numPages',
    'rating': 'ratingHistogram',  # This assumes you want the computed average rating
    'reviews': 'reviewsCount',
    'title': 'title',
    'totalratings': 'ratingsCount'
}

# Select and reorder columns based on mappings, only if they exist in the data
columns_to_select = [column_mappings[col] for col in column_mappings if column_mappings[col] in df.columns]
mapped_df = df[columns_to_select]

# Rename columns to your specified names
column_names = [col for col in column_mappings]
mapped_df.columns = column_names

# Filter rows where bookformat is 'English'
filtered_df = mapped_df[mapped_df['bookformat'] == 'English']

filtered_df = filtered_df.dropna(subset=['desc'])
filtered_df = filtered_df.dropna(subset=['title'])

# Clean descriptions and author fields to remove non-ASCII characters and reformat author
filtered_df['desc'] = filtered_df['desc'].apply(lambda x: x.encode('ascii', errors='ignore').decode('ascii'))
filtered_df['author'] = filtered_df['author'].apply(lambda authors: ', '.join(authors).encode('ascii', errors='ignore').decode('ascii') if isinstance(authors, list) else authors.encode('ascii', errors='ignore').decode('ascii'))

# Write DataFrame to CSV
filtered_df.to_csv(output_file, index=False)