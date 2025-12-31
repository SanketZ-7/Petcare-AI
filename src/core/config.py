# src/core/config.py

import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory
BASE_DIR = Path(__file__).parent.parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

# API Keys
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


EMBEDDING_MODEL = "mistral-embed"
LLM_MODEL = "mistral-small-latest"
TEMPERATURE = 0


FAISS_INDEX_PATH = BASE_DIR / "data" / "faiss_index"


SEARCH_K = 3


INGEST_CHUNK_SIZE = 1000
INGEST_CHUNK_OVERLAP = 150


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


