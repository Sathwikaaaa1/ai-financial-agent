from sec_edgar_downloader import Downloader
import os
import shutil
import glob

# We copied this list directly from your clean50.py script!
TARGET_TICKERS = [
    "NVDA","AAPL","GOOG","MSFT","AMZN","META","TSLA","AVGO","BRK-B",
    "WMT","LLY","JPM","XOM","V","JNJ","MU","MA","ORCL","COST",
    "ABBV","HD","BAC","PG","CVX","CAT","KO","AMD","GE","NFLX",
    "PLTR","CSCO","MRK","LRCX","PM","AMAT","GS","WFC","MS",
    "RTX","UNH","TMUS","IBM","MCD","INTC","AXP","PEP","GEV",
    "VZ","TXN","T"
]

def download_target_10ks():
    # --- CONFIGURATION ---
    # SEC requires a User-Agent formatted as "Name email@domain.com"
    # Please replace these with your actual details to avoid being blocked.
    USER_NAME = "YourName"
    USER_EMAIL = "your.email@example.com" 
    
    DOWNLOAD_FOLDER = "sec-edgar-filings" # Temp folder created by the library
    TARGET_FOLDER = "html10k"
    # ---------------------
    
    if not os.path.exists(TARGET_FOLDER):
        os.makedirs(TARGET_FOLDER)
        print(f"Created directory: {TARGET_FOLDER}")
        
    # Initialize the downloader
    dl = Downloader(USER_NAME, USER_EMAIL)

    print(f"Found {len(TARGET_TICKERS)} target companies. Starting download...")

    for ticker in TARGET_TICKERS:
        # SEC tickers often use hyphen instead of dot (e.g., BRK.B -> BRK-B)
        formatted_ticker = ticker.replace('.', '-')
        
        print(f"\nProcessing: {ticker}...")
        
        try:
            # Download the latest 10-K (limit=1)
            # download_details=True ensures we get the readable HTML file
            count = dl.get("10-K", formatted_ticker, limit=1, download_details=True)
            
            if count == 0:
                print(f"No 10-K found for {ticker}")
                continue

            # Construct the path pattern to find the .htm files
            search_path = os.path.join(DOWNLOAD_FOLDER, formatted_ticker, "10-K", "*", "*.htm*")
            files = glob.glob(search_path)
            
            if files:
                # The main 10-K is usually the largest HTML file in the folder
                main_file = max(files, key=os.path.getsize)
                
                # Define the new filename (e.g., AAPL.html)
                new_filename = f"{ticker}.html"
                
                destination_path = os.path.join(TARGET_FOLDER, new_filename) 
                
                # Move and rename
                shutil.move(main_file, destination_path)
                print(f"-> Saved as {new_filename}")
                
            else:
                print(f"-> Downloaded, but could not locate HTML file for {ticker}")

        except Exception as e:
            print(f"-> Failed: {e}")

    # Cleanup the 'sec-edgar-filings' temp folder after finishing
    if os.path.exists(DOWNLOAD_FOLDER):
        shutil.rmtree(DOWNLOAD_FOLDER) 
        print("\nCleanup complete.")

if __name__ == "__main__":
    download_target_10ks()