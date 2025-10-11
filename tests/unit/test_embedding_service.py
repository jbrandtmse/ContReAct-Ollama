"""Unit tests for EmbeddingService."""

# Third-party imports
import numpy as np
import pytest

# Local application imports
from contreact_ollama.analysis.embedding_service import EmbeddingService


def test_init_loads_model():
    """Test that EmbeddingService initializes and loads model successfully."""
    service = EmbeddingService()
    
    assert service.model is not None
    assert service.model_name == 'all-MiniLM-L6-v2'


def test_get_embedding_returns_correct_dimensions():
    """Test that get_embedding returns 384-dimensional vector for all-MiniLM-L6-v2."""
    service = EmbeddingService()
    text = "This is a sample text for testing."
    
    embedding = service.get_embedding(text)
    
    assert isinstance(embedding, np.ndarray)
    assert embedding.shape == (384,)


def test_get_embedding_produces_different_vectors_for_different_text():
    """Test that different texts produce different embedding vectors."""
    service = EmbeddingService()
    text1 = "The quick brown fox jumps over the lazy dog."
    text2 = "Python is a programming language."
    
    embedding1 = service.get_embedding(text1)
    embedding2 = service.get_embedding(text2)
    
    # Vectors should not be identical
    assert not np.allclose(embedding1, embedding2)


def test_get_embedding_produces_similar_vectors_for_similar_text():
    """Test that very similar texts produce similar embedding vectors."""
    service = EmbeddingService()
    text1 = "I am exploring artificial intelligence."
    text2 = "I am exploring artificial intelligence today."
    
    embedding1 = service.get_embedding(text1)
    embedding2 = service.get_embedding(text2)
    
    # Calculate cosine similarity
    similarity = np.dot(embedding1, embedding2) / (
        np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
    )
    
    # Similar texts should have high similarity (>0.9)
    assert similarity > 0.9


def test_get_embedding_handles_empty_string():
    """Test that get_embedding handles empty string gracefully."""
    service = EmbeddingService()
    
    embedding = service.get_embedding("")
    
    assert isinstance(embedding, np.ndarray)
    assert embedding.shape == (384,)
