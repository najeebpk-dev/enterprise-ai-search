"""
Enterprise AI Search - Intelligent Document Search with RAG

This package provides enterprise-grade document search capabilities
combining Azure Cognitive Search and Azure OpenAI.
"""

__version__ = "1.0.0"
__author__ = "Enterprise AI Search Contributors"
__email__ = "contact@example.com"

from src.config import (
    SEARCH_ENDPOINT,
    SEARCH_KEY,
    INDEX_NAME,
    OPENAI_ENDPOINT,
    OPENAI_KEY,
    EMBEDDING_MODEL,
    CHAT_MODEL
)

__all__ = [
    "SEARCH_ENDPOINT",
    "SEARCH_KEY",
    "INDEX_NAME",
    "OPENAI_ENDPOINT",
    "OPENAI_KEY",
    "EMBEDDING_MODEL",
    "CHAT_MODEL"
]
