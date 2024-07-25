'''
import dask.dataframe as dd
import glob
import ast
import pandas as pd

# Function to safely parse the ISBN_list from a string to a list
def safe_literal_eval(x):
    try:
        return ast.literal_eval(x)
    except ValueError:
        return []

# Step 1: Load the goodreads dataset with Dask
goodreads_path = '../Data/GoodReads/Cleaned/GoodReads_books_cleaned_2.csv'

goodreads_pd = pd.read_csv(goodreads_path)

# Convert to Dask DataFrame
goodreads = dd.from_pandas(goodreads_pd, npartitions=10)


# Step 2: Load and concatenate all inventory CSV files from a folder
inventory_path = '../Data/LibraryInventory/Cleaned_Partitions_New/*.csv'
inventory_files = glob.glob(inventory_path)
inventory = dd.read_csv(inventory_files, dtype={'ISBN_list': 'object'})

inventory['ISBN_list'] = inventory['ISBN_list'].map(safe_literal_eval, meta=('ISBN_list', object))

# Explode the ISBN_list to individual rows
inventory = inventory.explode('ISBN_list')

# Step 4: Convert ReportDate to datetime and get the latest ReportDate for each ISBN
inventory['ReportDate'] = dd.to_datetime(inventory['ReportDate'])
inventory = inventory.map_partitions(lambda df: df.sort_values('ReportDate')).groupby('ISBN_list').tail(1)

# Step 5: Perform the left join
result = goodreads.merge(inventory, left_on='isbn', right_on='ISBN_list', how='left')

# Select the necessary columns, focusing on 'ItemCount' from inventory
result = result[['book_id', 'author', 'title', 'ItemCount']]

# Step 6: Optionally handle missing data
result['ItemCount'] = result['ItemCount'].fillna(0)  # Assuming you want to fill missing values with 0

# Step 7: Compute the result (performs all the operations)
final_result = result.compute()

# Step 8: Save or print the result
final_result.to_csv('../Data/BookInventory/joined_data.csv', index=False)
'''

'''
import pandas as pd
import glob  # For easy file pattern matching
import ast

# Step 1: Load the goodreads dataset
goodreads = pd.read_csv('../Data/GoodReads/Cleaned/GoodReads_books_cleaned_2.csv')

inventory_files = glob.glob('../Data/Library_Inventory/Cleaned_Partitions_New/part_*_processed.csv')

# Check if inventory_files list is empty
if not inventory_files:
    raise FileNotFoundError("No CSV files found in the specified directory. Check the path and file extension.")

# Now that we've checked for the presence of files, concatenate them
inventory = pd.concat((pd.read_csv(file) for file in inventory_files))

# Assume ISBN_list is stored as a string representation of a list; if different, adjust parsing logic
# Convert string list to actual list (if needed, depends on your data format)

inventory['ISBN_list'] = inventory['ISBN_list'].apply(ast.literal_eval)

# Explode the ISBN_list into separate rows
inventory = inventory.explode('ISBN_list')

# Step 4: Filter inventory for Latest ReportDate for Each ISBN
inventory['ReportDate'] = pd.to_datetime(inventory['ReportDate'])
inventory = inventory.sort_values('ReportDate').groupby('ISBN_list', as_index=False).last()

# Step 5: Perform the left join
result = pd.merge(goodreads, inventory, left_on='isbn', right_on='ISBN_list', how='left')

# Select only the necessary columns, focusing on 'ItemCount' from inventory
result = result[['book_id', 'author', 'description','genre','cover_photo','isbn','isbn13','link','book_rating','no_of_reviews','title', 'totalratings','audio_link','ItemCount']]

# Step 6: Optionally handle missing data
result['ItemCount'].fillna(0, inplace=True)  # Assuming you want to fill missing values with 0

# Save or print the result
result.to_csv('joined_data.csv', index=False)

result.to_csv('../Data/BookInventory/joined_data.csv', index=False)
'''

# Load the goodreads dataset


# Get a list of all inventory part files

'''

import pandas as pd
import glob
import numpy as np  # For generating random numbers

# Load the goodreads dataset
goodreads = pd.read_csv('../Data/GoodReads/Cleaned/GoodReads_books_cleaned_2.csv')

# Get a list of all inventory part files
inventory_files = glob.glob('../Data/Library_Inventory/Cleaned_Partitions_New/part_*_processed.csv')
if not inventory_files:
    raise FileNotFoundError("No inventory files found. Please check the directory and file pattern.")

# Prepare a function to process and explode the ISBN_list
def process_inventory(file):
    df = pd.read_csv(file)
    import ast
    df['ISBN_list'] = df['ISBN_list'].apply(ast.literal_eval)  # Adjust if your format differs
    df = df.explode('ISBN_list')
    df['ReportDate'] = pd.to_datetime(df['ReportDate'])
    return df

# Initialize a DataFrame to hold the result of incremental joins
joined_data = goodreads.copy()

# Process each inventory file one by one
for file in sorted(inventory_files):  # Sorting to maintain a consistent order, e.g., by part number
    print(f"Processing file: {file}")  # Print the file being processed
    inventory_part = process_inventory(file)

    # Filter for the latest ReportDate per ISBN in this part
    latest_inventory_part = inventory_part.sort_values('ReportDate').groupby('ISBN_list', as_index=False).last()

    # Perform the left join with the current part
    joined_data = pd.merge(joined_data, latest_inventory_part[['ISBN_list', 'ItemCount', 'ReportDate']],
                           left_on='isbn', right_on='ISBN_list', how='left', suffixes=('', '_new'))

    # Resolve multiple entries by keeping only the latest ReportDate
    for index, row in joined_data.iterrows():
        if pd.notna(row['ReportDate']) and (pd.isna(row['ReportDate']) or row['ReportDate'] > row['ReportDate']):
            joined_data.at[index, 'ItemCount'] = row['ItemCount_new']
            joined_data.at[index, 'ReportDate'] = row['ReportDate_new']

    # Drop the temporary new columns
    joined_data.drop(columns=['ISBN_list', 'ReportDate'], inplace=True)

# Fill missing ItemCount values with random integers from 0 to 25
joined_data['ItemCount'].fillna(pd.Series(np.random.randint(0, 26, size=len(joined_data))), inplace=True)

# Save or analyze the result
joined_data.to_csv('../Data/BookInventory/joined_data.csv', index=False)
'''

import pandas as pd
import os
import numpy as np

# Load the Goodreads dataset
goodreads_df = pd.read_csv('../Data/GoodReads/Cleaned/GoodReads_books_cleaned_2.csv')

# Define a function to preprocess and clean each inventory chunk
def process_chunk(chunk):
    # Assuming ISBN_list is stored as a string that represents a list; convert it
    chunk['ISBN_list'] = chunk['ISBN_list'].apply(eval)
    return chunk

# Directory where inventory CSV files are stored
inventory_dir = '../Data/Library_Inventory/Cleaned_Partitions_New/'
inventory_files = [f for f in os.listdir(inventory_dir) if f.endswith('.csv')]

# Process all inventory files in chunks and combine them into a single DataFrame
inventory_chunks = []
for file_name in inventory_files:
    file_path = os.path.join(inventory_dir, file_name)
    inventory_iter = pd.read_csv(file_path, chunksize=500000)  # Adjust chunk size based on your system's capabilities
    for chunk in inventory_iter:
        processed_chunk = process_chunk(chunk)
        inventory_chunks.append(processed_chunk)

inventory_df = pd.concat(inventory_chunks)

# Explode the ISBN_list to make each ISBN its own row and rename for clarity
inventory_df = inventory_df.explode('ISBN_list')
inventory_df.rename(columns={'ISBN_list': 'isbn'}, inplace=True)

# Sort by ISBN and ReportDate and drop duplicates to keep the latest entry for each ISBN
inventory_df.sort_values(by=['isbn', 'ReportDate'], ascending=[True, False], inplace=True)
inventory_df.drop_duplicates(subset='isbn', keep='first', inplace=True)

# Merge the Goodreads dataframe with the processed inventory dataframe
result_df = pd.merge(goodreads_df, inventory_df[['isbn', 'ItemCount']], how='left', on='isbn')

result_df['ItemCount'] = result_df['ItemCount'].fillna(pd.Series(np.random.randint(0, 16, size=len(result_df))))

# Optionally, write the result to a new CSV file
result_df.to_csv('../Data/BookInventory/merged_dataset.csv', index=False)

