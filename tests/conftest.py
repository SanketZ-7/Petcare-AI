# tests/conftest.py

import pytest
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def sample_question():
    """Sample question for testing."""
    return "What food is best for puppies?"


@pytest.fixture
def sample_state():
    """Sample state dictionary for testing nodes."""
    return {
        "question": "How do I train my cat?",
        "documents": [],
        "generation": "",
        "web_search_needed": False
    }
