import pandas as pd
import numpy as np

df = pd.read_csv('../Data/GoodReads/Cleaned/GoodReads_books_cleaned.csv')

df = df.dropna(subset=['title'])
df = df.dropna(subset=['description'])

# Step 2: Add an 'book_id' column that auto-increments starting from 1
df.insert(0, 'book_id', range(1, 1 + len(df)))

# Step 3: Add an 'audio_link' column at the end with all values set to None
df['audio_link'] = np.nan

# Remove non ascii characters
df['description'] = df['description'].apply(lambda x: x.encode('ascii', errors='ignore').decode('ascii'))
df['author'] = df['author'].apply(lambda x: x.encode('ascii', errors='ignore').decode('ascii'))
df['title'] = df['title'].apply(lambda x: x.encode('ascii', errors='ignore').decode('ascii'))

df = df.dropna(subset=['title'])
df = df.dropna(subset=['description'])
df = df.dropna(subset=['author'])

df.to_csv('../Data/GoodReads/Cleaned/GoodReads_books_cleaned_2.csv', index=False)