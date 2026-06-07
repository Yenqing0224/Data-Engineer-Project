import requests
import json
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def fetch_data(symbol="BTCUSDT", interval="1d", limit=365):
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol" : symbol,
        "interval" : interval,
        "limit" : limit
    }

    logging.info(f"Starting Binance API request... Target: {symbol}, Interval: {interval}")

    try:
        response = requests.get(url, params=params, timeout=10)
        
        # Raise an exception for bad HTTP status codes (e.g., 404, 500)
        response.raise_for_status() 
        
        data = response.json()
        logging.info(f"Successfully fetched {len(data)} records!")
        return data
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch data due to network error or API limits: {e}")
        return None
    

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
    binance_data = fetch_data(symbol="BTCUSDT", interval="1d", limit=100)
    save_to_local(binance_data)