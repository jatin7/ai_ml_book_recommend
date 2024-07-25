import os
import boto3
import snowflake.connector
from botocore.exceptions import NoCredentialsError, ClientError

# Load environment variables
SNOWFLAKE_ACCOUNT = os.getenv('SNOWFLAKE_ACCOUNT')
SNOWFLAKE_USER = os.getenv('SNOWFLAKE_USER')
SNOWFLAKE_PASSWORD = os.getenv('SNOWFLAKE_PASSWORD')
SNOWFLAKE_WAREHOUSE = 'SF_TUTS_WH'
SNOWFLAKE_DATABASE = 'FINALPROJECT'
SNOWFLAKE_SCHEMA = 'PUBLIC'
SNOWFLAKE_ROLE = 'ACCOUNTADMIN'
SNOWFLAKE_TABLE = 'INVENTORY'
AWS_S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
AWS_REGION = os.getenv('AWS_REGION')

# Establish a connection to Snowflake
conn = snowflake.connector.connect(
    user=SNOWFLAKE_USER,
    password=SNOWFLAKE_PASSWORD,
    account=SNOWFLAKE_ACCOUNT,
    warehouse=SNOWFLAKE_WAREHOUSE,
    database=SNOWFLAKE_DATABASE,
    schema=SNOWFLAKE_SCHEMA,
    role=SNOWFLAKE_ROLE
)

# Establish a connection to AWS S3
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=AWS_REGION
)

# Function to check if an S3 file exists and generate presigned URL
def get_presigned_url_if_exists(bucket, object_name, expiration=1296000):
    """Check if S3 object exists and generate a presigned URL if it does."""
    try:
        s3_client.head_object(Bucket=bucket, Key=object_name)
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
        print(f"Generated presigned URL: {response}")
        return response
    except ClientError as e:
        print(f"File does not exist or error generating URL: {object_name}, {e}")
        return None
    except NoCredentialsError:
        print("Credentials not available")
        return None

# Process each book with NULL audio_link
with conn.cursor() as cur:
    cur.execute(f"SELECT BOOK_ID FROM {SNOWFLAKE_TABLE} WHERE AUDIO_LINK IS NULL AND BOOK_ID IN (73423,74809,70288,73438,73173,72885,74831,74463,74363,74385,74809,73423,72634,72742,73438,70288,74363,74385,74463,73173,74809,73423,70288,73173,74385,73438,72885,74363,74463,74831)")
    book_ids = cur.fetchall()

    for book_id_tuple in book_ids:
        book_id = book_id_tuple[0]
        file_key = f"{book_id}.mp3"
        
        # Start a transaction
        cur.execute("BEGIN")
        
        # Generate presigned URL if the file exists
        presigned_url = get_presigned_url_if_exists(AWS_S3_BUCKET_NAME, file_key)
        if presigned_url:
            try:
                # Update the record
                cur.execute(f"UPDATE {SNOWFLAKE_TABLE} SET AUDIO_LINK = %s WHERE BOOK_ID = %s", (presigned_url, book_id))
                # Commit after each update
                cur.execute("COMMIT")
                print(f"Updated AUDIO_LINK for BOOK_ID {book_id} with URL.")
            except Exception as update_error:
                print(f"Failed to update Snowflake for BOOK_ID {book_id}: {update_error}")
                cur.execute("ROLLBACK")
        else:
            print(f"No file or presigned URL for BOOK_ID {book_id}.")
            cur.execute("ROLLBACK")

conn.close()
