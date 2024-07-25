import pandas as pd
import os

def preprocess_isbns(isbn_str):
    # Split the ISBN string into a list, remove spaces and hyphens
    return [isbn.replace('-', '').strip() for isbn in isbn_str.split(',') if isbn]

def process_chunk(chunk):
    # Remove specified columns
    #columns_to_drop = ['PublicationYear', 'Publisher', 'ItemType', 'ItemCollection', 'FloatingItem', 'ISBN']
    columns_to_drop = ['PublicationYear', 'Publisher', 'ItemType', 'ItemCollection', 'FloatingItem', 'ISBN', 'ItemLocation', 'Subjects','Author','Title']
    
    # Split ISBNs and clean them
    chunk['ISBN_list'] = chunk['ISBN'].apply(preprocess_isbns)

    chunk.drop(columns=columns_to_drop, inplace=True, errors='ignore')

    
    return chunk

# Directory of your CSV files
input_directory = '../Data/Library_Inventory/Partitions/'
output_directory = '../Data/Library_Inventory/Cleaned_Partitions/'

# Ensure the output directory exists
os.makedirs(output_directory, exist_ok=True)

# Process each file
for filename in os.listdir(input_directory):
    if filename.endswith('.csv'):
        input_filepath = os.path.join(input_directory, filename)
        # Change the filename to indicate processing
        processed_filename = filename.replace('.csv', '_processed.csv')
        output_filepath = os.path.join(output_directory, processed_filename)
        
        # Initialize an empty flag to manage header writing
        header_written = False

        # Read and process in chunks
        for chunk in pd.read_csv(input_filepath, chunksize=50000):  # Adjust chunk size based on memory capacity
            processed_chunk = process_chunk(chunk)
            
            # Write processed chunk to file
            processed_chunk.to_csv(output_filepath, mode='a', index=False, header=not header_written)
            header_written = True  # Update flag to ensure header is not written again

        print(f"Processed {filename}")
