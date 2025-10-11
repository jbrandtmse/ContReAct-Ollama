"""Embedding service for generating semantic embeddings from text."""

# Standard library imports
from typing import Optional

# Third-party imports
import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """Generate semantic embeddings for text using sentence-transformers."""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize with specified sentence transformer model.
        
        Args:
            model_name: Name of sentence-transformers model to use.
                       Default is 'all-MiniLM-L6-v2' which produces 384-dimensional embeddings.
                       This model is fast and suitable for semantic similarity tasks.
        
        Note:
            On first use, the model will be downloaded from HuggingFace.
            Subsequent uses will load from cache.
        """
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        
    def get_embedding(self, text: str) -> np.ndarray:
        """
        Convert text to embedding vector.
        
        Args:
            text: Input text to embed (e.g., agent's reflection)
            
        Returns:
            Numpy array of embedding values (384 dimensions for all-MiniLM-L6-v2)
            
        Example:
            >>> service = EmbeddingService()
            >>> embedding = service.get_embedding("I explored topic X")
            >>> embedding.shape
            (384,)
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding
