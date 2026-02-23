import os
import glob
from tqdm import tqdm
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector
from sqlalchemy import create_engine, text

# Configuration matching your .env and docker-compose
CONNECTION_STRING = "postgresql+psycopg://admin:password@localhost:5432/financial_agent"
COLLECTION_NAME = "sec_filings"
DATA_FOLDER = "data_prep/mds" 

print("🔌 Initializing Embeddings Model...")
# This will download a small, fast, local embedding model from HuggingFace
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

vector_store = PGVector(
    embeddings=embeddings,
    collection_name=COLLECTION_NAME,
    connection=CONNECTION_STRING,
    use_jsonb=True,
)

def split_markdown(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    # 1. Split by Header (Keeps sections like "Risk Factors" together)
    headers_to_split_on = [("#", "Header 1"), ("##", "Header 2"), ("###", "Header 3")]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    md_header_splits = markdown_splitter.split_text(text)

    # 2. Split by Size (Ensures chunks aren't too massive for the LLM context window)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    return text_splitter.split_documents(md_header_splits)

def main():
    md_files = glob.glob(os.path.join(DATA_FOLDER, "*.md"))
    if not md_files:
        print(f"❌ No markdown files found in '{DATA_FOLDER}/'.")
        return

    print(f"🚀 Starting ingestion for {len(md_files)} files...")
    
    # tqdm creates a nice progress bar in the terminal
    for file_path in tqdm(md_files, desc="Ingesting Files", unit="file"):
        ticker = os.path.basename(file_path).replace(".md", "").upper()
        
        try:
            # Chop the file into chunks
            chunks = split_markdown(file_path)
            
            # Attach metadata (CRITICAL for later)
            for chunk in chunks:
                chunk.metadata["ticker"] = ticker
                chunk.metadata["source"] = file_path

            # Upload to PGVector
            vector_store.add_documents(chunks)
            
        except Exception as e:
            print(f"\n❌ Error processing {ticker}: {e}")
            continue

    print("\n✅ Ingestion Complete!")

if __name__ == "__main__":
    main()