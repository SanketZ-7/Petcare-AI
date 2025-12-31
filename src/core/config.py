# src/core/config.py

import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory
BASE_DIR = Path(__file__).parent.parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

# API Keys
# API Keys
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Model Configurations
EMBEDDING_MODEL = "mistral-embed"
LLM_MODEL = "mistral-small-latest"
TEMPERATURE = 0

# Vector Store Configurations
FAISS_INDEX_PATH = BASE_DIR / "data" / "faiss_index"

# Search Tool Configurations
SEARCH_K = 3

# Data Ingestion Configurations
INGEST_CHUNK_SIZE = 1000
INGEST_CHUNK_OVERLAP = 150

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# LangSmith Tracing (optional - set in .env to enable)
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "pet-care-assistant")
