import requests
import json
import logging
import os
from datetime import datetime
import boto3
from dotenv import load_dotenv


load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def fetch_data(symbol="bitcoin", interval="daily", limit=100):
    # CoinGecko API
    url = f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart"
    params = {
        "vs_currency" : "usd",
        "interval" : interval,
        "days" : limit
    }

    logging.info(f"Starting CoinGecko API request... Target: {symbol}, Interval: {interval}, Days: {limit}")

    try:
        response = requests.get(url, params=params, timeout=10)
        
        # Raise an exception for bad HTTP status codes (e.g., 404, 500)
        response.raise_for_status() 
        
        data = response.json()
        prices = data.get("prices", [])
        
        logging.info(f"Successfully fetched {len(prices)} records!")
        return prices
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch data due to network error or API limits: {e}")
        return None
    

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
    except Exception as e:
        logging.error(f"S3 Upload failed: {e}")


def save_to_local(data, filepath="data/raw_btc_data.json"):
    """
    Safely save the extracted JSON data to a local file.
    """
    if not data:
        logging.warning("No data available to save.")
        return
        
    # Ensure the target directory exists; create it if it doesn't
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Save the data with indentation for better readability
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        
    logging.info(f"Data successfully saved to local path: {filepath}")


if __name__ == "__main__":
    cryptocurrency = fetch_data(symbol="bitcoin", interval="daily", limit=100)
    upload_to_s3(cryptocurrency, symbol="bitcoin")