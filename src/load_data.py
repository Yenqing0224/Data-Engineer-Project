import requests
import json
import logging
import os
import snowflake.connector
from datetime import datetime
import boto3
from dotenv import load_dotenv


load_dotenv()

# Init logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def upload_to_s3(data, symbol="bitcoin"):
    if not data:
        logging.warning("No data available to upload.")
        return

    bucket_name = os.getenv('AWS_S3_BUCKET_NAME')

    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )

    current_date = datetime.now().strftime('%Y-%m-%d')
    s3_key = f"raw_data/{symbol}/{current_date}.json"

    try:
        logging.info(f"Uploading data to s3://{bucket_name}/{s3_key} ...")
        # Convert dictionary to JSON string, then upload
        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=json.dumps(data)
        )
        logging.info("Upload to AWS S3 completely successful!")
        return s3_key
    except Exception as e:
        logging.error(f"S3 Upload failed: {e}")


def upload_to_snowflake(s3_key, symbol="bitcoin"):
    if not s3_key:
        logging.error("No S3 key provided. Skipping Snowflake load.")
        return
    
    bucket_name = os.getenv('AWS_S3_BUCKET_NAME')

    logging.info("Connecting to Snowflake data warehouse...")

    conn = snowflake.connector.connect(
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        warehouse='CRYPTO_WH',      # 指定让哪台发动机来算
        database='CRYPTO_DB',      # 指定去哪个大展厅
        schema='RAW'               # 指定进哪个接货房
    )
    
    
    cursor = conn.cursor()

    create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS CRYPTO_DB.RAW.BITCOIN_RAW (
            RAW_DATA VARIANT
        );
    """

    copy_sql = f"""
        COPY INTO CRYPTO_DB.RAW.BITCOIN_RAW
        FROM 's3://{bucket_name}/{s3_key}'
        CREDENTIALS = (
            AWS_KEY_ID = '{os.getenv('AWS_ACCESS_KEY_ID')}' 
            AWS_SECRET_KEY = '{os.getenv('AWS_SECRET_ACCESS_KEY')}'
        )
        FILE_FORMAT = (
            TYPE = 'JSON'
            STRIP_OUTER_ARRAY = TRUE  -- 依然保留拆分数组的绝杀技
        );
    """
    
    try:
        logging.info("Ensuring target table exists...")
        cursor.execute(create_table_sql)
        logging.info(f"Executing Snowflake COPY INTO from s3://{bucket_name}/{s3_key} ...")
        cursor.execute(copy_sql)
        
        # 抓取执行结果
        results = cursor.fetchall()
        for row in results:
            logging.info(f"Snowflake Ingestion Result: Status={row[1]}, Rows Parsed={row[3]}, Rows Loaded={row[4]}")
            
        conn.commit()
    except Exception as e:
        logging.error(f"Snowflake COPY INTO failed: {e}")
    finally:
        cursor.close()
        conn.close()
        logging.info("Snowflake connection closed safely.")


if __name__ == "__main__":
    # Local test
    from extract_data import fetch_data
    
    # Fetch Data
    raw_prices = fetch_data(symbol="bitcoin", limit=100)
    # Upload to S3
    saved_key = upload_to_s3(raw_prices, symbol="bitcoin")
    # Upload to snowflake
    upload_to_snowflake(saved_key, symbol="bitcoin")