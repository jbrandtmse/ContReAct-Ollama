"""Similarity monitoring for tracking reflection diversity."""

# Standard library imports
from typing import List, Optional

# Third-party imports
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Local application imports
from contreact_ollama.analysis.embedding_service import EmbeddingService


class SimilarityMonitor:
    """Track reflection similarity and generate advisory feedback."""
    
    def __init__(self, embedding_service: EmbeddingService):
        """
        Initialize with embedding service instance.
        
        Args:
            embedding_service: Service for generating text embeddings
        """
        self.embedding_service = embedding_service
        
    def check_similarity(
        self, 
        new_reflection_embedding: np.ndarray, 
        historical_embeddings: List[np.ndarray]
    ) -> Optional[str]:
        """
        Check similarity of new reflection against historical reflections.
        
        Args:
            new_reflection_embedding: Embedding vector of latest reflection (384-dim)
            historical_embeddings: List of embedding vectors from previous reflections
            
        Returns:
            Advisory feedback string if similarity exceeds threshold, None otherwise
            
        Similarity Thresholds:
            - > 0.8 (high): Returns strong advisory to explore new topics
            - > 0.7 (moderate): Returns mild advisory to consider diversification
            - <= 0.7: No feedback, returns None
            
        Example:
            >>> monitor = SimilarityMonitor(embedding_service)
            >>> feedback = monitor.check_similarity(new_emb, historical_embs)
            >>> if feedback:
            ...     print(feedback)
            'Advisory: Your current line of reflection shows high similarity...'
        """
        if not historical_embeddings:
            # No history to compare against
            return None
        
        # Calculate cosine similarity against all historical embeddings
        # Reshape for sklearn compatibility
        new_emb_2d = new_reflection_embedding.reshape(1, -1)
        historical_embs_2d = np.array(historical_embeddings)
        
        # Compute similarities
        similarities = cosine_similarity(new_emb_2d, historical_embs_2d)[0]
        
        # Find maximum similarity
        max_similarity = np.max(similarities)
        
        # Apply thresholds and return appropriate feedback
        if max_similarity > 0.8:
            return (
                "Advisory: Your current line of reflection shows high similarity "
                "to a previous cycle. Consider exploring a distinctly different topic, "
                "problem space, or mode of inquiry to diversify your exploration."
            )
        elif max_similarity > 0.7:
            return (
                "Advisory: Your current line of reflection shows moderate similarity "
                "to a previous cycle. You might consider branching into a related but "
                "distinct area to expand the breadth of your exploration."
            )
        else:
            # Similarity is acceptable, no feedback needed
            return None
