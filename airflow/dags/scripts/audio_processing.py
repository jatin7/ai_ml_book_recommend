import os
import io
import boto3
import snowflake.connector
from gtts import gTTS, gTTSError
import time
from dotenv import load_dotenv
# from espeakng import ESpeakNG

# Load environment variables
load_dotenv()

# Constants for Snowflake
SNOWFLAKE_ACCOUNT = os.getenv('SNOWFLAKE_ACCOUNT')
SNOWFLAKE_USER = os.getenv('SNOWFLAKE_USER')
SNOWFLAKE_PASSWORD = os.getenv('SNOWFLAKE_PASSWORD')
SNOWFLAKE_WAREHOUSE = 'SF_TUTS_WH'
SNOWFLAKE_DATABASE = 'FINALPROJECT'
SNOWFLAKE_SCHEMA = 'PUBLIC'
SNOWFLAKE_ROLE = 'ACCOUNTADMIN'
TABLE_NAME = 'INVENTORY'
TEXT_COLUMN = 'DESCRIPTION'
COMPARE_COLUMN = 'BOOK_ID'

# Constants for AWS S3
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION')
# AWS_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
AWS_BUCKET_NAME = "team4finalproject"

# Function to fetch text and book_id from Snowflake
def fetch_data_from_snowflake():
    conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA,
        role=SNOWFLAKE_ROLE
    )
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT {COMPARE_COLUMN}, {TEXT_COLUMN} FROM {TABLE_NAME} WHERE {COMPARE_COLUMN} IN (73423,74809,70288,73438,73173,72885,74831,74463,74363,74385,74809,73423,72634,72742,73438,70288,74363,74385,74463,73173,74809,73423,70288,73173,74385,73438,72885,74363,74463,74831)")
        return cursor.fetchall()  # Fetch all rows
    finally:
        cursor.close()
        conn.close()

# Function to convert text to speech using Google gTTS
def convert_text_to_speech(text, book_id):
    retry_delay = 5  # Start with a 5-second delay
    max_retries = 5  # Set the maximum number of retries

    for attempt in range(max_retries):
        try:
            tts = gTTS(text, lang='en')
            mp3_fp = io.BytesIO()
            tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)
            print(f"Generated speech for book ID {book_id}")
            return mp3_fp
        except gTTSError as e:
            if "429 (Too Many Requests)" in str(e):
                print(f"Rate limit hit, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                raise
        except Exception as e:
            print(f"Failed to generate speech for book ID {book_id}: {e}")
            break  # Break out of the loop on non-retryable errors

    print(f"Failed to generate speech for book ID {book_id} after {max_retries} attempts")
    return None



# Function to upload a file to AWS S3
def upload_to_s3(file_buffer, book_id):
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=AWS_REGION)
    file_key = f'{book_id}.mp3'
    s3.upload_fileobj(file_buffer, AWS_BUCKET_NAME, file_key)
    print(f"Uploaded {file_key} to S3.")

# Main function
def main():
    data = fetch_data_from_snowflake()
    if data:
        for book_id, text in data:
            if text:
                print(f"Processing book ID: {book_id}...")
                audio_buffer = convert_text_to_speech(text, book_id)
                upload_to_s3(audio_buffer, book_id)
            else:
                print(f"No description to convert for book ID {book_id}.")
    else:
        print("No data found in the database.")

if __name__ == "__main__":
    main()
