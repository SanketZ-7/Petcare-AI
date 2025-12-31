import os
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_tavily import TavilySearchResults

from src.core import config

def get_broad_pet_life_urls(num_results_per_query=1):
    """
    Fetch URLs covering the most essential aspects of pet ownership using Tavily via LangChain tool.
    Only include URLs from trusted domains.
    """
    queries = [
        "pet care basics",
        # "pet adoption tips",
        # "pet training techniques",
        # "pet health care",
        # "pet nutrition advice",
        "pet food types"
    ]
    allowed_domains = [
        "akc.org", "aspca.org", "humanesociety.org", "petmd.com", "petfinder.com",
        ".edu", ".gov"
    ]
    tavily_tool = TavilySearchResults(k=num_results_per_query)
    urls = set()
    for query in queries:
        try:
            results = tavily_tool.invoke({"query": query})
            # TavilySearchResults returns a list of dicts with 'url' keys
            for item in results:
                url = item.get('url')
                if url and any(domain in url for domain in allowed_domains):
                    urls.add(url)
                if len(urls) >= num_results_per_query * len(queries):
                    break
        except Exception as e:
            print(f"Error fetching URLs for query '{query}': {e}")
            
    return list(urls)

def main():
    """
    Main function to load data, split it, and store it in a vector database.
    """
    print("--- Starting Data Ingestion ---")

    # 1. Discover Broad Pet Life URLs
    print("Fetching broad pet life URLs using Tavily API...")
    urls = get_broad_pet_life_urls(num_results_per_query=1)
    print(f"Found {len(urls)} unique URLs.")

    all_docs = []
    for url in urls:
        print(f"Loading documents from {url}...")
        try:
            loader = WebBaseLoader(url)
            docs = loader.load()
            print(f"Loaded {len(docs)} document(s) from {url}.")
            all_docs.extend(docs)
        except Exception as e:
            print(f"Failed to load {url}: {e}")

    if not all_docs:
        print("No documents loaded. Exiting.")
        return

    # 2. Split Documents
    print("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.INGEST_CHUNK_SIZE, 
        chunk_overlap=config.INGEST_CHUNK_OVERLAP
    )
    splits = text_splitter.split_documents(all_docs)
    print(f"Split into {len(splits)} chunks.")

    # 3. Create Embeddings and Store in FAISS
    print(f"Creating vector store at {config.FAISS_INDEX_PATH}...")
    try:
        embeddings = GoogleGenerativeAIEmbeddings(
            model=config.EMBEDDING_MODEL,
            google_api_key=config.GOOGLE_API_KEY
        )
        vectorstore = FAISS.from_documents(
            documents=splits,
            embedding=embeddings
        )
        vectorstore.save_local(str(config.FAISS_INDEX_PATH))
        print("--- Data Ingestion Complete ---")
        print(f"Total vectors in store: {vectorstore.index.ntotal}")
    except Exception as e:
        print(f"FAILED to ingest due to embedding error: {e}")

if __name__ == "__main__":
    main()

