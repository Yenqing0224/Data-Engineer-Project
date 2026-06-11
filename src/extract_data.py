import requests
import json
import logging
import os
from dotenv import load_dotenv


load_dotenv()

# Init logging
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
        
        # Raise exception
        response.raise_for_status() 
        
        data = response.json()
        prices = data.get("prices", [])
        
        logging.info(f"Successfully fetched {len(prices)} records!")
        return prices

    # Error handling    
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch data due to network error or API limits: {e}")
        return None
    

# Function to test
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
    save_to_local(cryptocurrency, symbol="bitcoin")