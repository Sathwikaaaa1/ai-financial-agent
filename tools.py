import yfinance as yf
from langchain_core.tools import tool
from retrieval import retrieve_sec_documents

# ---------------------------------------------------------
# Tool 1: Live Stock Price
# ---------------------------------------------------------
@tool
def get_stock_price(ticker: str) -> str:
    """
    Fetches the current live stock price and basic company info for a given ticker symbol.
    Always use this tool when the user asks for the current price or market cap.
    
    Args:
        ticker: The stock ticker symbol (e.g., "AAPL", "MSFT").
    """
    print(f"\n[Tool Executing] Fetching live price for {ticker}...")
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        current_price = info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))
        market_cap = info.get('marketCap', 'N/A')
        
        if current_price == 'N/A':
            return f"Could not find live price data for {ticker}."
            
        return f"The current price of {ticker} is ${current_price}. The market cap is ${market_cap}."
    except Exception as e:
        return f"Error fetching price for {ticker}: {str(e)}"

# ---------------------------------------------------------
# Tool 2: Historical Data (For Charts!)
# ---------------------------------------------------------
@tool
def get_historical_prices(ticker: str, period: str = "1mo") -> str:
    """
    Fetches historical daily stock prices for a given ticker to be used for charts.
    Use this when the user asks to see a chart, graph, or historical trend of the stock.
    
    Args:
        ticker: The stock ticker symbol (e.g., "AAPL").
        period: The time period (e.g., "1mo", "3mo", "1y"). Default is "1mo".
    """
    print(f"\n[Tool Executing] Fetching historical data for {ticker} over {period}...")
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        
        if hist.empty:
            return f"No historical data found for {ticker}."
            
        # We return a specific marker so our Streamlit UI knows to draw a chart later!
        return f"HISTORICAL_DATA_READY|{ticker}|{period}"
    except Exception as e:
        return f"Error fetching historical data: {str(e)}"

# ---------------------------------------------------------
# Tool 3: SEC Document Search (Our RAG Pipeline)
# ---------------------------------------------------------
@tool
def search_sec_filings(query: str, ticker: str) -> str:
    """
    Searches the company's official SEC 10-K financial filings for specific information.
    Use this tool when the user asks about revenue, risks, supply chain, strategy, or financial performance.
    
    Args:
        query: The specific question to search for (e.g., "What are the supply chain risks?").
        ticker: The stock ticker symbol (e.g., "AAPL").
    """
    print(f"\n[Tool Executing] Searching SEC filings for {ticker}...")
    try:
        # We are simply calling the function we wrote in Phase 3!
        return retrieve_sec_documents(query=query, ticker=ticker)
    except Exception as e:
        return f"Error searching database: {str(e)}"

# --- Quick Test ---
if __name__ == "__main__":
    print("Testing Live Price Tool:")
    print(get_stock_price.invoke({"ticker": "AAPL"}))
    
    print("\nTesting Historical Data Tool:")
    print(get_historical_prices.invoke({"ticker": "MSFT", "period": "1mo"}))
    
    # We will skip testing the SEC tool here since we just verified it in Phase 3!