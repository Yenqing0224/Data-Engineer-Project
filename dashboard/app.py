import streamlit as st
import pandas as pd

# Setup
st.set_page_config(page_title="Crypto Analytics Dashboard", layout="wide")
st.title("📈 Bitcoin 7-Day Moving Average Trend")

# Init connection
conn = st.connection("snowflake", type="snowflake")

# Fetch deduplicated data from Marts layer
@st.cache_data(ttl=3600) # Cache
def load_data():
    query = """
        SELECT PRICE_TIMESTAMP, PRICE_USD, MOVING_AVG_PRICE_7D 
        FROM CRYPTO_DB.MARTS.mart_bitcoin_trends 
        ORDER BY PRICE_TIMESTAMP ASC
    """
    df = conn.query(query)
    # Ensure timestamp is in datetime format for better plotting
    df['PRICE_TIMESTAMP'] = pd.to_datetime(df['PRICE_TIMESTAMP'])
    return df

try:
    with st.spinner("Fetching data from Snowflake..."):
        data = load_data()

    # Layout: Metrics Display
    latest_row = data.iloc[-1]
    col1, col2 = st.columns(2)
    col1.metric("Latest Price (USD)", f"${latest_row['PRICE_USD']:,.2f}")
    col2.metric("7-Day Moving Avg", f"${latest_row['MOVING_AVG_PRICE_7D']:,.2f}")

    # Layout: Dual-line Chart
    st.subheader("Price vs 7-Day Moving Average")
    # Prepare dataframe for st.line_chart by setting index
    chart_data = data.set_index('PRICE_TIMESTAMP')[['PRICE_USD', 'MOVING_AVG_PRICE_7D']]
    st.line_chart(chart_data)

except Exception as e:
    st.error(f"Failed to connect or fetch data: {e}")