from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector

# 1. Setup (Must match ingest.py)
CONNECTION_STRING = "postgresql+psycopg://admin:password@localhost:5432/financial_agent"
COLLECTION_NAME = "sec_filings"

print("🔌 Connecting to Vector Database...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

vector_store = PGVector(
    embeddings=embeddings,
    collection_name=COLLECTION_NAME,
    connection=CONNECTION_STRING,
    use_jsonb=True,
)

def retrieve_sec_documents(query: str, ticker: str, k: int = 3) -> str:
    """
    Searches the database and RETURNS a string of text for the LLM to read.
    """
    print(f"\n🔎 RAG Search Triggered: '{query}' for {ticker.upper()}")
    
    try:
        # We search the database, strictly filtering by the requested ticker
        results = vector_store.similarity_search(
            query, 
            k=k,
            filter={"ticker": ticker.upper()} 
        )
        
        if not results:
            return f"No SEC filing results found for {ticker}."

        # We glue all the text chunks together into one massive string
        formatted_results = []
        for i, doc in enumerate(results):
            formatted_results.append(f"--- Document {i+1} ---\n{doc.page_content}\n")
            
        # We RETURN the string so the AI agent receives the text
        return "\n".join(formatted_results)
        
    except Exception as e:
        return f"Error during search: {e}"
    
##print(retrieve_sec_documents("What is the revenue growth?", "AAPL"))

'''
if __name__ == "__main__":
    # Test 1: General Concept Search across all companies
    test_query("What are the primary risk factors regarding supply chain?")
    
    # Test 2: Specific Company Search (Ensures we don't mix up Apple with Microsoft)
    test_query("What is the revenue growth?", ticker="AAPL")
'''