# tests/test_config.py

import pytest
from pathlib import Path


def test_config_imports():
    """Test that config module can be imported."""
    from src.core import config
    assert config is not None


def test_embedding_model_updated():
    """Test that embedding model is the updated version."""
    from src.core import config
    assert config.EMBEDDING_MODEL == "models/text-embedding-004"
    assert "embedding-001" not in config.EMBEDDING_MODEL


def test_llm_model_configured():
    """Test that LLM model is configured."""
    from src.core import config
    assert config.LLM_MODEL == "gemini-2.0-flash"


def test_faiss_path_is_path():
    """Test that FAISS path is a Path object."""
    from src.core import config
    assert isinstance(config.FAISS_INDEX_PATH, Path)


def test_log_level_default():
    """Test that LOG_LEVEL has a default value."""
    from src.core import config
    assert config.LOG_LEVEL in ["DEBUG", "INFO", "WARNING", "ERROR"]


def test_langchain_tracing_default():
    """Test that LangChain tracing has a default value."""
    from src.core import config
    assert config.LANGCHAIN_TRACING_V2 in ["true", "false"]
