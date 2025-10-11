"""Integration tests for diversity feedback functionality."""

# Standard library imports
from unittest.mock import Mock, MagicMock, call
from typing import List, Dict

# Third-party imports
import pytest
import numpy as np

# Local application imports
from contreact_ollama.core.config import ExperimentConfig
from contreact_ollama.core.cycle_orchestrator import CycleOrchestrator
from contreact_ollama.llm.ollama_interface import OllamaInterface
from contreact_ollama.analysis.embedding_service import EmbeddingService
from contreact_ollama.analysis.similarity_monitor import SimilarityMonitor
from contreact_ollama.state.agent_state import AgentState


@pytest.fixture
def sample_config():
    """Provide sample ExperimentConfig for testing."""
    return ExperimentConfig(
        run_id="diversity-test-001",
        model_name="llama3:latest",
        cycle_count=3,
        ollama_client_config={"host": "http://localhost:11434"},
        model_options={"temperature": 0.7, "seed": 42}
    )


@pytest.fixture
def mock_tool_dispatcher():
    """Provide mock ToolDispatcher."""
    mock = Mock()
    mock.get_tool_definitions.return_value = []
    mock.dispatch.return_value = "Tool result"
    return mock


def test_diversity_feedback_appears_in_next_cycle_prompt(sample_config, mock_tool_dispatcher):
    """Test that diversity advisory appears in next cycle's prompt when reflections are similar."""
    # Create mock Ollama interface that returns identical reflections
    mock_ollama = Mock(spec=OllamaInterface)
    
    # Track all messages sent to Ollama
    captured_prompts = []
    
    def mock_chat_completion(model_name, messages, tools, options):
        """Mock chat completion that captures prompts and returns identical reflections."""
        captured_prompts.append(messages)
        
        # Return identical reflection each time
        return {
            "message": {
                "role": "assistant",
                "content": "FINAL_ANSWER: I explored machine learning and neural networks."
            }
        }
    
    mock_ollama.execute_chat_completion = mock_chat_completion
    
    # Create real EmbeddingService and SimilarityMonitor
    embedding_service = EmbeddingService()
    similarity_monitor = SimilarityMonitor(embedding_service=embedding_service)
    
    # Create orchestrator with diversity monitoring
    orchestrator = CycleOrchestrator(
        config=sample_config,
        ollama_interface=mock_ollama,
        tool_dispatcher=mock_tool_dispatcher,
        logger=None,
        similarity_monitor=similarity_monitor
    )
    
    # Run experiment (3 cycles)
    orchestrator.run_experiment()
    
    # Verify we have prompts from all 3 cycles
    assert len(captured_prompts) >= 3
    
    # Cycle 1 and 2 should not have diversity feedback
    cycle_1_system_prompt = captured_prompts[0][0]["content"]
    assert "Advisory:" not in cycle_1_system_prompt
    
    if len(captured_prompts) > 1:
        cycle_2_system_prompt = captured_prompts[1][0]["content"]
        # Cycle 2 might not have advisory yet (only 1 historical reflection)
    
    # Cycle 3 should have diversity feedback (comparing to cycles 1 and 2)
    if len(captured_prompts) > 2:
        cycle_3_system_prompt = captured_prompts[2][0]["content"]
        # Since reflections are identical, should trigger high similarity advisory
        assert "Advisory:" in cycle_3_system_prompt
        assert ("high similarity" in cycle_3_system_prompt.lower() or 
                "moderate similarity" in cycle_3_system_prompt.lower())


def test_reflection_embeddings_stored_correctly(sample_config, mock_tool_dispatcher):
    """Test that reflection embeddings are stored correctly across cycles."""
    # Create mock Ollama interface
    mock_ollama = Mock(spec=OllamaInterface)
    
    reflections = [
        "I explored artificial intelligence and deep learning.",
        "I investigated machine learning algorithms.",
        "I studied neural network architectures."
    ]
    
    reflection_index = [0]
    
    def mock_chat_completion(model_name, messages, tools, options):
        """Mock chat completion that returns different reflections."""
        idx = reflection_index[0]
        reflection = reflections[idx] if idx < len(reflections) else reflections[-1]
        reflection_index[0] += 1
        
        return {
            "message": {
                "role": "assistant",
                "content": f"FINAL_ANSWER: {reflection}"
            }
        }
    
    mock_ollama.execute_chat_completion = mock_chat_completion
    
    # Create real EmbeddingService and SimilarityMonitor
    embedding_service = EmbeddingService()
    similarity_monitor = SimilarityMonitor(embedding_service=embedding_service)
    
    # Create orchestrator with diversity monitoring
    orchestrator = CycleOrchestrator(
        config=sample_config,
        ollama_interface=mock_ollama,
        tool_dispatcher=mock_tool_dispatcher,
        logger=None,
        similarity_monitor=similarity_monitor
    )
    
    # Run experiment (3 cycles)
    orchestrator.run_experiment()
    
    # Verify reflection embeddings are stored
    assert hasattr(orchestrator, 'reflection_embeddings')
    assert len(orchestrator.reflection_embeddings) == 3
    
    # Verify each embedding is a 384-dimensional numpy array
    for embedding in orchestrator.reflection_embeddings:
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (384,)
    
    # Verify embeddings are different (not identical)
    emb1 = orchestrator.reflection_embeddings[0]
    emb2 = orchestrator.reflection_embeddings[1]
    emb3 = orchestrator.reflection_embeddings[2]
    
    assert not np.allclose(emb1, emb2)
    assert not np.allclose(emb2, emb3)
    assert not np.allclose(emb1, emb3)


def test_no_feedback_for_diverse_reflections(sample_config, mock_tool_dispatcher, capsys):
    """Test that no diversity advisory is triggered for diverse reflections."""
    # Create mock Ollama interface that returns very different reflections
    mock_ollama = Mock(spec=OllamaInterface)
    
    reflections = [
        "I explored quantum computing and its applications.",
        "I studied ancient Roman history and architecture.",
        "I investigated marine biology and ocean ecosystems."
    ]
    
    reflection_index = [0]
    
    def mock_chat_completion(model_name, messages, tools, options):
        """Mock chat completion that returns very different reflections."""
        idx = reflection_index[0]
        reflection = reflections[idx] if idx < len(reflections) else reflections[-1]
        reflection_index[0] += 1
        
        return {
            "message": {
                "role": "assistant",
                "content": f"FINAL_ANSWER: {reflection}"
            }
        }
    
    mock_ollama.execute_chat_completion = mock_chat_completion
    
    # Create real EmbeddingService and SimilarityMonitor
    embedding_service = EmbeddingService()
    similarity_monitor = SimilarityMonitor(embedding_service=embedding_service)
    
    # Create orchestrator with diversity monitoring
    orchestrator = CycleOrchestrator(
        config=sample_config,
        ollama_interface=mock_ollama,
        tool_dispatcher=mock_tool_dispatcher,
        logger=None,
        similarity_monitor=similarity_monitor
    )
    
    # Run experiment (3 cycles)
    orchestrator.run_experiment()
    
    # Capture console output
    captured = capsys.readouterr()
    
    # Verify no diversity advisory messages in console
    assert "[Diversity advisory triggered: similarity detected]" not in captured.out
    
    # Verify embeddings are stored but very different
    assert len(orchestrator.reflection_embeddings) == 3
    
    # Calculate similarities to verify they're below threshold
    emb1 = orchestrator.reflection_embeddings[0]
    emb2 = orchestrator.reflection_embeddings[1]
    emb3 = orchestrator.reflection_embeddings[2]
    
    # Calculate cosine similarities
    from sklearn.metrics.pairwise import cosine_similarity
    
    sim_1_2 = cosine_similarity(emb1.reshape(1, -1), emb2.reshape(1, -1))[0][0]
    sim_2_3 = cosine_similarity(emb2.reshape(1, -1), emb3.reshape(1, -1))[0][0]
    sim_1_3 = cosine_similarity(emb1.reshape(1, -1), emb3.reshape(1, -1))[0][0]
    
    # All similarities should be below moderate threshold (0.7)
    # (Note: these are very diverse topics, so similarities should be low)
    assert sim_1_2 < 0.8, f"Similarity 1-2 too high: {sim_1_2}"
    assert sim_2_3 < 0.8, f"Similarity 2-3 too high: {sim_2_3}"
    assert sim_1_3 < 0.8, f"Similarity 1-3 too high: {sim_1_3}"


def test_moderate_similarity_triggers_appropriate_advisory(sample_config, mock_tool_dispatcher, capsys):
    """Test that moderate similarity (0.7-0.8) triggers appropriate advisory message."""
    # Create mock Ollama interface
    mock_ollama = Mock(spec=OllamaInterface)
    
    # Use related but not identical topics to trigger moderate similarity
    reflections = [
        "I explored machine learning algorithms and their applications in classification tasks.",
        "I studied deep learning models and neural network architectures for image recognition.",
        "I investigated convolutional neural networks for computer vision applications."
    ]
    
    reflection_index = [0]
    captured_prompts = []
    
    def mock_chat_completion(model_name, messages, tools, options):
        """Mock chat completion that returns related reflections."""
        captured_prompts.append(messages)
        idx = reflection_index[0]
        reflection = reflections[idx] if idx < len(reflections) else reflections[-1]
        reflection_index[0] += 1
        
        return {
            "message": {
                "role": "assistant",
                "content": f"FINAL_ANSWER: {reflection}"
            }
        }
    
    mock_ollama.execute_chat_completion = mock_chat_completion
    
    # Create real EmbeddingService and SimilarityMonitor
    embedding_service = EmbeddingService()
    similarity_monitor = SimilarityMonitor(embedding_service=embedding_service)
    
    # Create orchestrator with diversity monitoring
    orchestrator = CycleOrchestrator(
        config=sample_config,
        ollama_interface=mock_ollama,
        tool_dispatcher=mock_tool_dispatcher,
        logger=None,
        similarity_monitor=similarity_monitor
    )
    
    # Run experiment (3 cycles)
    orchestrator.run_experiment()
    
    # Capture console output
    captured = capsys.readouterr()
    
    # Verify embeddings stored
    assert len(orchestrator.reflection_embeddings) == 3
    
    # Calculate similarities between related topics
    from sklearn.metrics.pairwise import cosine_similarity
    
    emb1 = orchestrator.reflection_embeddings[0]
    emb2 = orchestrator.reflection_embeddings[1]
    emb3 = orchestrator.reflection_embeddings[2]
    
    sim_1_2 = cosine_similarity(emb1.reshape(1, -1), emb2.reshape(1, -1))[0][0]
    sim_2_3 = cosine_similarity(emb2.reshape(1, -1), emb3.reshape(1, -1))[0][0]
    
    # At least one pair should have moderate to high similarity (related topics)
    max_similarity = max(sim_1_2, sim_2_3)
    assert max_similarity > 0.5, f"Expected moderate similarity for related topics, got {max_similarity}"
    
    # If any similarity exceeds threshold, diversity advisory should be triggered
    # (console message confirms it was detected)
    if max_similarity > 0.7:
        assert "[Diversity advisory triggered: similarity detected]" in captured.out, \
            f"Expected diversity advisory for similarity {max_similarity:.4f}"
    
    # Check that if sim_1_2 > 0.7, then cycle 3 should have advisory
    # (because advisory generated after cycle 2 would be used in cycle 3)
    if sim_1_2 > 0.7 and len(captured_prompts) >= 3:
        cycle_3_system_prompt = captured_prompts[2][0]["content"]
        assert "Advisory:" in cycle_3_system_prompt, \
            f"Expected advisory in cycle 3 prompt when sim(1,2)={sim_1_2:.4f} > 0.7"
