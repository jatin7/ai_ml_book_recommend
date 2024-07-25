from sodapy import Socrata
import pandas as pd
import time
import pandas as pd
import os
import datetime

def fetch_data(client, limit, offset):
    max_retries = 5
    retries = 0
    # Get today's date in the format 'YYYY-MM-DD'
    today_date = datetime.date.today().isoformat()
    query = f"""
    SELECT bibnum, title, author, isbn, publicationyear, publisher, subjects, itemtype, 
    itemcollection, floatingitem, itemlocation, reportdate, itemcount 
    WHERE (isbn IS NOT NULL) AND (reportdate > '{today_date}' AND reportdate IS NOT NULL)
    LIMIT {limit} OFFSET {offset}
    """
    while retries <= max_retries:
        try:
            batch = client.get("6vkj-f5xf", query=query)
            return batch
        except Exception as e:
            retries += 1
            print(f"Retry {retries}/{max_retries} after error: {e}")
            time.sleep(5)  # Delay before retrying
            if retries > max_retries:
                return None  # Return None if all retries fail

def process_batch(batch):
    df = pd.DataFrame(batch)
    # Process data here or write it to disk
    df.to_csv('Data/Library_Inventory/Seattle_Library_Inventory.csv', mode='a', header=False, index=False)  # Append to a CSV file

def estimate_rows_per_file(file_name, target_size_mb=1024):
    # Sample the first 5000 rows to estimate row size
    sample_df = pd.read_csv(file_name, nrows=5000)
    sample_size = sample_df.memory_usage(deep=True).sum()
    average_row_size = sample_size / 5000
    average_row_size = average_row_size/2
    rows_per_file = int((target_size_mb * 1024 * 1024) / average_row_size)
    return rows_per_file

def split_csv(file_name, target_size_mb, output_folder):
    # Ensure the output directory exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Estimate the number of rows per partition
    rows_per_file = estimate_rows_per_file(file_name, target_size_mb)
    
    # Calculate total number of rows (this might take time for large files)
    total_rows = sum(1 for row in open(file_name, 'r', encoding='utf-8'))
    
    # Number of files to be created
    n_splits = (total_rows + rows_per_file - 1) // rows_per_file

    # Start splitting the file
    for i in range(n_splits):
        skip_rows = range(1, i * rows_per_file + 1) if i > 0 else 0
        df = pd.read_csv(file_name, 
                         skiprows=skip_rows,
                         nrows=rows_per_file,
                         header=None if i else 0)
        
        # Define new file name with the output folder path
        new_file_name = f'{output_folder}/part_{i+1}.csv'
        df.to_csv(new_file_name, index=False, header=bool(i == 0))
        print(f'Part {i+1} written as {new_file_name}')


def main():
    client = Socrata("data.seattle.gov", None, timeout=60)
    limit = 1000000
    offset = 0
    n = 0
    while True:
        n += 1
        batch = fetch_data(client, limit, offset)
        if not batch:
            break  # Break the loop if fetch_data returns None
        process_batch(batch)
        if len(batch) < limit:
            break  # End loop if last batch is smaller than limit
        offset += limit
        print(f"Batch {n} processed")

    split_csv('Data/Library_Inventory/Seattle_Library_Inventory.csv', 1024, 'Data/Library_Inventory/Partitions')

    client.close()

if __name__ == "__main__":
    main()
