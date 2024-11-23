import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import date, timedelta
import plotly.express as px
import requests
from bs4 import BeautifulSoup
import json

@st.cache_data
def load_nse_stocks():
    """
    Load list of NSE stocks from a comprehensive source
    """
    try:
        # Get the list of NSE stocks
        url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
        df = pd.read_csv(url)
        # Create a dictionary of stock symbols and names
        stocks_dict = dict(zip(df['SYMBOL'], df['NAME OF COMPANY']))
        return stocks_dict
    except:
        # Fallback list in case the NSE website is not accessible
        return {
            'RELIANCE': 'Reliance Industries Ltd.',
            'TCS': 'Tata Consultancy Services Ltd.',
            'HDFCBANK': 'HDFC Bank Ltd.',
            'INFY': 'Infosys Ltd.',
            'ICICIBANK': 'ICICI Bank Ltd.',
            'HINDUNILVR': 'Hindustan Unilever Ltd.',
            'ITC': 'ITC Ltd.',
            'SBIN': 'State Bank of India',
            'BHARTIARTL': 'Bharti Airtel Ltd.',
            'KOTAKBANK': 'Kotak Mahindra Bank Ltd.',
            'WIPRO': 'Wipro Ltd.',
            'ASIANPAINT': 'Asian Paints Ltd.',
            'MARUTI': 'Maruti Suzuki India Ltd.',
            'TATAMOTORS': 'Tata Motors Ltd.',
            'TECHM': 'Tech Mahindra Ltd.',
            'TITAN': 'Titan Company Ltd.',
            'BAJFINANCE': 'Bajaj Finance Ltd.',
            'TATASTEEL': 'Tata Steel Ltd.',
            'ADANIENT': 'Adani Enterprises Ltd.',
            'ZOMATO': 'Zomato Ltd.',
            'PAYTM': 'Paytm Ltd.',
            'NYKAA': 'FSN E-Commerce Ltd.',
            # Add many more stocks here
        }

def fetch_stock_data(symbol, start_date, end_date):
    """
    Fetch stock data using yfinance
    """
    try:
        ticker = yf.Ticker(f"{symbol}.NS")
        data = ticker.history(start=start_date, end=end_date, interval="1d")
        
        if data.empty:
            st.error(f"No data found for {symbol}")
            return None
            
        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

def create_candlestick_chart(data, symbol):
    """
    Create an interactive candlestick chart using Plotly
    """
    if data is None or len(data) == 0:
        return None
        
    fig = go.Figure(data=[go.Candlestick(x=data.index,
                                        open=data['Open'],
                                        high=data['High'],
                                        low=data['Low'],
                                        close=data['Close'])])
    
    fig.update_layout(
        title=f'{symbol} Stock Price',
        yaxis_title='Price (₹)',
        xaxis_title='Date',
        template='plotly_white'
    )
    
    return fig

def create_volume_chart(data, symbol):
    """
    Create volume chart using Plotly
    """
    fig = px.bar(data, x=data.index, y='Volume',
                 title=f'{symbol} Trading Volume')
    fig.update_layout(template='plotly_white')
    return fig

def calculate_technical_indicators(data):
    """
    Calculate technical indicators
    """
    if data is None or len(data) == 0:
        return None
        
    # Calculate 20-day moving average
    data['MA20'] = data['Close'].rolling(window=20).mean()
    
    # Calculate 50-day moving average
    data['MA50'] = data['Close'].rolling(window=50).mean()
    
    # Calculate RSI
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    
    return data

def main():
    st.set_page_config(page_title="Stock Market Dashboard", layout="wide")
    
    # Add title and description
    st.title("📈 Stock Market Dashboard")
    st.markdown("Select a stock and time period to view the analysis")
    
    # Load stock list
    stocks_dict = load_nse_stocks()
    
    # Create sidebar for inputs
    with st.sidebar:
        st.header("Configure Your Analysis")
        
        # Create a searchable dropdown for stocks
        st.subheader("Select Stock")
        selected_stock = st.selectbox(
            "Search and select a stock",
            options=list(stocks_dict.keys()),
            format_func=lambda x: f"{x} - {stocks_dict[x]}"
        )
        
        symbol = selected_stock if selected_stock else "RELIANCE"
        
        # Date range selection
        st.subheader("Select Time Period")
        end_date = date.today()
        
        date_options = {
            '1 Month': 30,
            '3 Months': 90,
            '6 Months': 180,
            '1 Year': 365,
            '2 Years': 730,
            '5 Years': 1825
        }
        
        selected_period = st.selectbox("Select Time Period", list(date_options.keys()))
        start_date = end_date - timedelta(days=date_options[selected_period])
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("This dashboard shows stock data from NSE (National Stock Exchange of India)")
        
        # Add stock information
        if symbol:
            st.markdown("---")
            st.markdown("### Selected Stock Info")
            st.markdown(f"**Company Name:** {stocks_dict[symbol]}")
            st.markdown(f"**Symbol:** {symbol}")

    if symbol:
        # Show loading message
        with st.spinner(f'Fetching data for {symbol}...'):
            # Fetch and process data
            data = fetch_stock_data(symbol, start_date, end_date)
            
            if data is not None and not data.empty:
                # Calculate technical indicators
                data = calculate_technical_indicators(data)
                
                # Create two columns for charts
                col1, col2 = st.columns(2)
                
                with col1:
                    # Display candlestick chart
                    st.plotly_chart(create_candlestick_chart(data, symbol), use_container_width=True)
                    
                with col2:
                    # Display volume chart
                    st.plotly_chart(create_volume_chart(data, symbol), use_container_width=True)
                
                # Display summary statistics in an expander
                with st.expander("View Summary Statistics"):
                    stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
                    
                    with stats_col1:
                        st.metric("Current Price", f"₹{data['Close'][-1]:.2f}")
                    with stats_col2:
                        st.metric("Average Price", f"₹{data['Close'].mean():.2f}")
                    with stats_col3:
                        st.metric("Highest Price", f"₹{data['High'].max():.2f}")
                    with stats_col4:
                        st.metric("Lowest Price", f"₹{data['Low'].min():.2f}")
                
                # Display technical indicators
                st.subheader("Technical Indicators")
                tech_col1, tech_col2 = st.columns(2)
                
                with tech_col1:
                    st.metric("20-Day MA", f"₹{data['MA20'][-1]:.2f}")
                    st.metric("50-Day MA", f"₹{data['MA50'][-1]:.2f}")
                
                with tech_col2:
                    rsi_value = data['RSI'][-1]
                    st.metric("RSI", f"{rsi_value:.2f}")
                    
                    if rsi_value > 70:
                        st.warning("RSI indicates overbought conditions")
                    elif rsi_value < 30:
                        st.warning("RSI indicates oversold conditions")
                
                # Display raw data in an expander
                with st.expander("View Raw Data"):
                    st.dataframe(data)

if __name__ == "__main__":
    main()