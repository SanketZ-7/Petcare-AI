# PetCare Assistant with LangChain

A Retrieval-Augmented Generation (RAG) assistant for pet care, built using LangChain, LangGraph, FAISS, and Mistral AI.

## Features

- **RAG Pipeline**: Retrieves relevant pet care information from a FAISS vector store
- **Web Search Fallback**: Falls back to Tavily web search when no relevant documents found
- **Async Support**: All agent nodes use async/await for better performance
- **Domain Guardrails**: Filters out non-pet related queries before processing
- **Structured Logging**: Uses structlog for production-grade observability
- **Modern Python**: Follows modern Python packaging standards

## Project Structure

```
pet-care-assistant/
├── main.py                 # CLI entry point
├── requirements.txt        # Dependencies with pinned versions
├── pyproject.toml          # Modern Python project config
├── src/
│   ├── agent/
│   │   ├── graph.py        # LangGraph workflow definition
│   │   └── nodes.py        # Async agent node functions
│   ├── core/
│   │   └── config.py       # Configuration and environment settings
│   └── pipeline/
│       └── ingest.py       # Data ingestion pipeline
├── tests/                  # Test suite
│   ├── conftest.py         # Pytest fixtures
│   └── test_config.py      # Configuration tests
└── data/
    └── faiss_index/        # Vector store (generated)
```

## Setup

1. **Create a `.env` file** with your API keys:
   ```
   MISTRAL_API_KEY=your_mistral_api_key
   TAVILY_API_KEY=your_tavily_api_key
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the ingestion pipeline** (optional, builds vector store):
   ```bash
   python -m src.pipeline.ingest
   ```

4. **Start the chatbot**:
   ```bash
   python main.py
   ```

## Configuration

Key settings in `src/core/config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `EMBEDDING_MODEL` | `mistral-embed` | Mistral embedding model |
| `LLM_MODEL` | `mistral-small-latest` | Mistral LLM for generation |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

### Optional: LangSmith Tracing

Add to `.env` to enable:
```
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=pet-care-assistant
```

## Testing

```bash
pytest
```

## Requirements

- Python 3.9+
- Mistral API key (for LLM & Embeddings)
- Tavily API key (for web search)

## Deployment

The project is configured for deployment on **Netlify** using the `mangum` adapter.
See `NETLIFY_GUIDE.md` for detailed instructions.

## Notes

- Do not commit your `.env` file or any secrets to version control
- The FAISS vector store is generated in `data/faiss_index/` and should not be committed
