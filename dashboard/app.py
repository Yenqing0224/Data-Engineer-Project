import streamlit as st
import pandas as pd

# Setup
st.set_page_config(page_title="Crypto Analytics Dashboard", layout="wide")
st.title("Multi-Asset Crypto Intelligence Dashboard")
st.markdown("---")

# Init connection
conn = st.connection("snowflake", type="snowflake")

# Fetch deduplicated data from Marts layer
@st.cache_data(ttl=3600) # Cache
def load_data():
    query = """
        SELECT 
            COIN_ID,
            DATE_TIME, 
            PRICE, 
            MARKET_CAP, 
            TOTAL_VOLUME, 
            MOVING_AVG_PRICE_7D 
        FROM CRYPTO_DB.MARTS.FACT_CRYPTO_PRICE 
        ORDER BY DATE_TIME ASC
    """
    df = conn.query(query)
    # Ensure timestamp is in datetime format for better plotting
    df['DATE_TIME'] = pd.to_datetime(df['DATE_TIME'])
    return df

try:
    with st.spinner("Syncing data from Snowflake..."):
        data = load_data()

    st.sidebar.header("Coin Selection")
    available_coins = data['COIN_ID'].unique().tolist()
    selected_coin = st.sidebar.selectbox(
        "Select the cryptocurrency to analyze:",
        options=available_coins,
        index=0,
        format_func=lambda x: x.upper() # Capitalize coin ID
    )
    coin_data = data[data['COIN_ID'] == selected_coin].reset_index(drop=True)

    if not coin_data.empty and len(coin_data) >= 2:
        # Extract latest row and previous row to calculate changes (Delta)
        latest_row = coin_data.iloc[-1]
        prev_row = coin_data.iloc[-2]

        # Core Metrics Row (KPI Cards)
        st.subheader(f"{selected_coin.upper()} Daily Snapshot")
        m1, m2, m3, m4 = st.columns(4)

        # Price KPI Card (with absolute change)
        price_delta = latest_row['PRICE'] - prev_row['PRICE']
        m1.metric(
            label="Latest Price (USD)", 
            value=f"${latest_row['PRICE']:,.2f}", 
            delta=f"${price_delta:,.2f}"
        )

        # 7-Day Moving Average Card
        m2.metric(
            label="7-Day Moving Average (7D MA)", 
            value=f"${latest_row['MOVING_AVG_PRICE_7D']:,.2f}"
        )

        # Market Cap Card (with delta change)
        cap_delta = latest_row['MARKET_CAP'] - prev_row['MARKET_CAP']
        m3.metric(
            label="Market Capitalization", 
            value=f"${latest_row['MARKET_CAP']:,.0f}",
            delta=f"${cap_delta:,.0f}"
        )

        # 24-Hour Trading Volume Card
        m4.metric(
            label="24h Trading Volume", 
            value=f"${latest_row['TOTAL_VOLUME']:,.0f}"
        )
        
        st.markdown("---")

        # Time-Series Charts (Tabs View)
        st.subheader("Historical Multi-Dimensional Trends")
        tab_price, tab_cap, tab_volume = st.tabs(["Price & MA", "Market Cap", "Trading Volume"])

        with tab_price:
            st.markdown("#### Spot Price vs 7-Day Moving Average Trend")
            price_chart_df = coin_data.set_index('DATE_TIME')[['PRICE', 'MOVING_AVG_PRICE_7D']]
            st.line_chart(price_chart_df)

        with tab_cap:
            st.markdown("#### Market Capitalization Over Time (Area Chart)")
            cap_chart_df = coin_data.set_index('DATE_TIME')['MARKET_CAP']
            st.area_chart(cap_chart_df, color="#29b5e8")

        with tab_volume:
            st.markdown("#### 24h Trading Volume Distribution (Bar Chart)")
            volume_chart_df = coin_data.set_index('DATE_TIME')['TOTAL_VOLUME']
            st.bar_chart(volume_chart_df, color="#ff4b4b")

        st.markdown("---")

        # 🌟 6. Raw Data Explorer
        with st.expander("Expand to View Raw Structured Data from Snowflake Marts Layer"):
            st.markdown("You can sort, filter, or manually inspect the structured data below:")
            # Sort descending to show the newest records first
            st.dataframe(coin_data.sort_values(by='DATE_TIME', ascending=False), use_container_width=True)
    else:
        st.warning("Insufficient time-series data found in the warehouse for rendering.")

except Exception as e:
    st.error(f"Failed to connect or fetch data: {e}")
