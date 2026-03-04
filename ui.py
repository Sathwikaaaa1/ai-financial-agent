import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from agent import app, llm # We import 'llm' to generate the insight

# --- Page Config ---
st.set_page_config(page_title="AI Financial Analyst", layout="wide")
st.title("📈 AI Financial Analyst Agent")

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar: Stock Watchlist with Analytics (Selectbox Search) ---
with st.sidebar:
    st.header("Watchlist")
    

    all_tickers = [
        "NVDA","AAPL","GOOG","MSFT","AMZN","META","TSLA","AVGO","BRK-B",
        "WMT","LLY","JPM","XOM","V","JNJ","MU","MA","ORCL","COST",
        "ABBV","HD","BAC","PG","CVX","CAT","KO","AMD","GE","NFLX",
        "PLTR","CSCO","MRK","LRCX","PM","AMAT","GS","WFC","MS",
        "RTX","UNH","TMUS","IBM","MCD","INTC","AXP","PEP","GEV",
        "VZ","TXN","T"
    ] 
    
    # Selectbox allows typing to filter (Search based on first character)
    ticker_input = st.selectbox("Search Ticker:", options=all_tickers, index=0)
    
    if st.button("Show Chart"):
        df = yf.Ticker(ticker_input).history(period="1mo")
        
        if not df.empty:
            st.subheader(f"{ticker_input} 30D")
            fig = go.Figure(data=[go.Candlestick(x=df.index,
                            open=df['Open'], high=df['High'],
                            low=df['Low'], close=df['Close'])])
            fig.update_layout(template="plotly_dark", showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)

            # --- Calculation Logic ---
            start_price = df['Close'].iloc[0]
            end_price = df['Close'].iloc[-1]
            pct_change = ((end_price - start_price) / start_price) * 100
            high_val = df['High'].max()
            low_val = df['Low'].min()
            volatility = df['Close'].pct_change().std() * 100
            vol_label = "High" if volatility > 2 else "Low" if volatility < 1 else "Moderate"
            sentiment = "Bullish" if pct_change > 0 else "Bearish"

            # Generate Insight
            insight_prompt = f"Stock: {ticker_input}. 30-day Trend: {pct_change:.1f}%. Range: ${low_val:.2f}-${high_val:.2f}. Volatility: {vol_label}. Provide a one-sentence investor insight."
            insight = llm.invoke([SystemMessage(content=insight_prompt)]).content

            st.markdown(f"**Trend:** {pct_change:+.1f}% ({sentiment})")
            st.markdown(f"**Range:** Low of ${low_val:.2f} to High of ${high_val:.2f}")
            st.markdown(f"**Volatility:** {vol_label} (daily swings)")
            st.markdown(f"**Insight:** {insight}")
        else:
            st.error("Data not available for this ticker.")

# --- Chat Interface ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Show me a chart for NVDA"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Prepare history for the agent
        history = []
        for m in st.session_state.messages:
            role = HumanMessage if m["role"] == "user" else AIMessage
            history.append(role(content=m["content"]))

        with st.spinner("Analyzing..."):
            result = app.invoke({"messages": history})
            full_response = result["messages"][-1].content
            
            # --- ANALYTICS LOGIC ---
            if "HISTORICAL_DATA_READY" in full_response:
                ticker = full_response.split("|")[1]
                df = yf.Ticker(ticker).history(period="1mo")
                
                # 1. Render Chart
                st.subheader(f"📊 {ticker} 30-Day Performance")
                fig = go.Figure(data=[go.Candlestick(x=df.index,
                                open=df['Open'], high=df['High'],
                                low=df['Low'], close=df['Close'])])
                st.plotly_chart(fig, use_container_width=True)
                
                # 2. Calculate Metrics
                start_price = df['Close'].iloc[0]
                end_price = df['Close'].iloc[-1]
                pct_change = ((end_price - start_price) / start_price) * 100
                high_val = df['High'].max()
                low_val = df['Low'].min()
                # Volatility calculation (Standard Deviation of daily returns)
                volatility = df['Close'].pct_change().std() * 100
                vol_label = "High" if volatility > 2 else "Low" if volatility < 1 else "Moderate"
                
                # 3. Generate AI Insight
                insight_prompt = f"The stock {ticker} has a 30-day trend of {pct_change:.1f}%, a range of ${low_val:.2f} to ${high_val:.2f}, and {vol_label} volatility. Provide a one-sentence investor insight."
                insight = llm.invoke([SystemMessage(content=insight_prompt)]).content
                
                # 4. Display Analytics
                sentiment = "Bullish" if pct_change > 0 else "Bearish"
                st.markdown(f"**Trend:** {pct_change:+.1f}% ({sentiment})")
                st.markdown(f"**Range:** Low of ${low_val:.2f} to High of ${high_val:.2f}")
                st.markdown(f"**Volatility:** {vol_label} (daily swings)")
                st.success(f"**Insight:** {insight}")
                
                full_response = f"I have generated the chart and technical analysis for {ticker} above."

        st.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})