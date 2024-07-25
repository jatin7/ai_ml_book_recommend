import pandas as pd

# Specify the paths to your CSV files
file_path1 = 'CSV/goodreads_merged.csv'
file_path2 = 'CSV/out_young_books.csv'

# Load the CSV files into DataFrames
df1 = pd.read_csv(file_path1)
df2 = pd.read_csv(file_path2)

# Merge the two DataFrames
merged_df = pd.concat([df1, df2])

# Remove duplicates by 'title' column. Keep the first occurrence
cleaned_df = merged_df.drop_duplicates(subset='title', keep='first')

# Specify the path for the output CSV file
output_file_path = '../Data/GoodReads/GoodReads_books.csv'

# Save the cleaned DataFrame to a new CSV file
cleaned_df.to_csv(output_file_path, index=False)

print("Merged and cleaned CSV saved as:", output_file_path)