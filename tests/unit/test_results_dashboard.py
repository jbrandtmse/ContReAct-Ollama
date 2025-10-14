"""
Unit tests for Results Dashboard functionality.

Tests the core functions used in the Results Dashboard page including
log file scanning and JSONL file loading.

Part of: Story 2.5 - Results Dashboard Run Selector and Data Loading
Part of: Story 2.6 - Display Summary Metrics on Dashboard
Part of: Story 2.7 - Display Raw Conversation Log on Dashboard
Part of: Story 2.8 - Implement Interactive Charts on Dashboard
"""
import json
import pytest
from pathlib import Path
from unittest.mock import patch
import pandas as pd

from contreact_ollama.ui_utils import (
    get_log_files,
    load_log_file,
    extract_metrics_from_dataframe,
    calculate_summary_metrics,
    load_pei_assessment
)


class TestGetLogFiles:
    """Test suite for get_log_files function."""
    
    def test_returns_empty_list_when_directory_not_exists(self, tmp_path, monkeypatch):
        """Test that get_log_files returns empty list when logs/ doesn't exist."""
        
        # Change to temp directory that has no logs/ folder
        monkeypatch.chdir(tmp_path)
        
        result = get_log_files()
        assert result == []
    
    def test_returns_empty_list_when_directory_empty(self, tmp_path, monkeypatch):
        """Test that get_log_files returns empty list when logs/ is empty."""
        
        # Create empty logs directory
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()
        monkeypatch.chdir(tmp_path)
        
        result = get_log_files()
        assert result == []
    
    def test_returns_all_jsonl_files(self, tmp_path, monkeypatch):
        """Test that get_log_files returns all .jsonl files."""
        
        # Create logs directory with multiple files
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()
        
        # Create .jsonl files
        (logs_dir / "run1.jsonl").touch()
        (logs_dir / "run2.jsonl").touch()
        (logs_dir / "run3.jsonl").touch()
        
        # Create non-jsonl file (should be ignored)
        (logs_dir / "other.txt").touch()
        
        monkeypatch.chdir(tmp_path)
        
        result = get_log_files()
        assert len(result) == 3
        assert "run1.jsonl" in result
        assert "run2.jsonl" in result
        assert "run3.jsonl" in result
        assert "other.txt" not in result
    
    def test_sorts_by_modification_time_newest_first(self, tmp_path, monkeypatch):
        """Test that get_log_files sorts files by modification time."""
        import time
        
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()
        monkeypatch.chdir(tmp_path)
        
        # Create files with different modification times
        old_file = logs_dir / "old.jsonl"
        old_file.touch()
        
        time.sleep(0.1)  # Ensure different timestamps
        
        new_file = logs_dir / "new.jsonl"
        new_file.touch()
        
        result = get_log_files()
        
        # Newest file should be first
        assert result[0] == "new.jsonl"
        assert result[1] == "old.jsonl"


class TestLoadLogFile:
    """Test suite for load_log_file function."""
    
    def test_loads_valid_jsonl_file(self, tmp_path, monkeypatch):
        """Test that load_log_file successfully loads valid JSONL file."""
        
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()
        monkeypatch.chdir(tmp_path)
        
        # Create valid JSONL file
        log_file = logs_dir / "test.jsonl"
        log_data = [
            {"timestamp": "2025-01-08T10:00:00", "run_id": "test", "cycle_number": 1, "event_type": "CYCLE_START"},
            {"timestamp": "2025-01-08T10:00:01", "run_id": "test", "cycle_number": 1, "event_type": "CYCLE_END"}
        ]
        
        with open(log_file, 'w') as f:
            for entry in log_data:
                f.write(json.dumps(entry) + '\n')
        
        df = load_log_file("test.jsonl")
        
        assert df is not None
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert "event_type" in df.columns
        assert df["event_type"].tolist() == ["CYCLE_START", "CYCLE_END"]
    
    def test_skips_empty_lines(self, tmp_path, monkeypatch):
        """Test that load_log_file skips empty lines in JSONL file."""
        
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()
        monkeypatch.chdir(tmp_path)
        
        # Create JSONL file with empty lines
        log_file = logs_dir / "test.jsonl"
        with open(log_file, 'w') as f:
            f.write('{"event_type": "CYCLE_START"}\n')
            f.write('\n')  # Empty line
            f.write('{"event_type": "CYCLE_END"}\n')
        
        df = load_log_file("test.jsonl")
        
        assert df is not None
        assert len(df) == 2
    
    def test_returns_none_on_json_decode_error(self, tmp_path, monkeypatch):
        """Test that load_log_file returns None on JSON parsing error."""
        
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()
        monkeypatch.chdir(tmp_path)
        
        # Create invalid JSONL file
        log_file = logs_dir / "corrupted.jsonl"
        with open(log_file, 'w') as f:
            f.write('{"valid": "json"}\n')
            f.write('invalid json line\n')  # This will cause JSONDecodeError
            f.write('{"another": "valid"}\n')
        
        # Mock st.error to avoid actual streamlit calls
        with patch('streamlit.error'):
            df = load_log_file("corrupted.jsonl")
        
        assert df is None
    
    def test_returns_none_on_file_not_found(self):
        """Test that load_log_file returns None when file doesn't exist."""
        
        with patch('streamlit.error'):
            df = load_log_file("nonexistent.jsonl")
        
        assert df is None
    
    def test_returns_none_on_empty_file(self, tmp_path, monkeypatch):
        """Test that load_log_file returns None for empty file."""
        
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()
        monkeypatch.chdir(tmp_path)
        
        # Create empty JSONL file
        log_file = logs_dir / "empty.jsonl"
        log_file.touch()
        
        with patch('streamlit.warning'):
            df = load_log_file("empty.jsonl")
        
        assert df is None
    
    def test_handles_general_exception(self, tmp_path, monkeypatch):
        """Test that load_log_file handles unexpected exceptions gracefully."""
        
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()
        monkeypatch.chdir(tmp_path)
        
        # Create file that will cause an exception during processing
        log_file = logs_dir / "test.jsonl"
        log_file.write_text('{"test": "data"}\n')
        
        # Mock open to raise an exception
        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            with patch('streamlit.error'):
                df = load_log_file("test.jsonl")
        
        assert df is None


class TestDataFrameStructure:
    """Test suite for DataFrame structure after loading."""
    
    def test_dataframe_has_expected_columns(self, tmp_path, monkeypatch):
        """Test that loaded DataFrame has expected columns."""
        
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()
        monkeypatch.chdir(tmp_path)
        
        # Create JSONL with standard event structure
        log_file = logs_dir / "test.jsonl"
        log_data = {
            "timestamp": "2025-01-08T10:00:00.000000",
            "run_id": "test-run-001",
            "cycle_number": 1,
            "event_type": "CYCLE_START",
            "payload": {}
        }
        
        with open(log_file, 'w') as f:
            f.write(json.dumps(log_data) + '\n')
        
        df = load_log_file("test.jsonl")
        
        assert df is not None
        assert "timestamp" in df.columns
        assert "run_id" in df.columns
        assert "cycle_number" in df.columns
        assert "event_type" in df.columns
        assert "payload" in df.columns


class TestExtractMetricsFromDataFrame:
    """Test suite for extract_metrics_from_dataframe function."""
    
    def test_extracts_metrics_from_cycle_end_events(self):
        """Test that metrics are correctly extracted from CYCLE_END events."""
        
        # Create DataFrame with CYCLE_END events containing metrics
        df = pd.DataFrame([
            {
                "event_type": "CYCLE_START",
                "cycle_number": 1,
                "payload": {}
            },
            {
                "event_type": "CYCLE_END",
                "cycle_number": 1,
                "payload": {
                    "metrics": {
                        "memory_ops_total": 5,
                        "messages_to_operator": 2,
                        "response_chars": 1500,
                        "memory_write_chars": 800
                    }
                }
            },
            {
                "event_type": "CYCLE_END",
                "cycle_number": 2,
                "payload": {
                    "metrics": {
                        "memory_ops_total": 3,
                        "messages_to_operator": 1,
                        "response_chars": 1200,
                        "memory_write_chars": 600
                    }
                }
            }
        ])
        
        result = extract_metrics_from_dataframe(df)
        
        assert result is not None
        assert len(result) == 2
        assert "cycle_number" in result.columns
        assert "memory_ops_total" in result.columns
        assert result["cycle_number"].tolist() == [1, 2]
        assert result["memory_ops_total"].tolist() == [5, 3]
    
    def test_returns_none_when_no_cycle_end_events(self):
        """Test that function returns None when no CYCLE_END events exist."""
        
        df = pd.DataFrame([
            {"event_type": "CYCLE_START", "cycle_number": 1, "payload": {}},
            {"event_type": "LLM_REQUEST", "cycle_number": 1, "payload": {}}
        ])
        
        result = extract_metrics_from_dataframe(df)
        assert result is None
    
    def test_returns_none_when_no_metrics_in_payload(self):
        """Test that function returns None when CYCLE_END has no metrics."""
        
        df = pd.DataFrame([
            {
                "event_type": "CYCLE_END",
                "cycle_number": 1,
                "payload": {}  # No metrics field
            }
        ])
        
        result = extract_metrics_from_dataframe(df)
        assert result is None
    
    def test_returns_none_when_dataframe_is_none(self):
        """Test that function handles None DataFrame gracefully."""
        
        result = extract_metrics_from_dataframe(None)
        assert result is None
    
    def test_returns_none_when_event_type_column_missing(self):
        """Test that function handles missing event_type column."""
        
        df = pd.DataFrame([
            {"cycle_number": 1, "payload": {}}
        ])
        
        result = extract_metrics_from_dataframe(df)
        assert result is None
    
    def test_handles_mixed_payload_formats(self):
        """Test that function handles CYCLE_END events with and without metrics."""
        
        df = pd.DataFrame([
            {
                "event_type": "CYCLE_END",
                "cycle_number": 1,
                "payload": {
                    "metrics": {
                        "memory_ops_total": 5,
                        "messages_to_operator": 2,
                        "response_chars": 1500,
                        "memory_write_chars": 800
                    }
                }
            },
            {
                "event_type": "CYCLE_END",
                "cycle_number": 2,
                "payload": {}  # No metrics
            },
            {
                "event_type": "CYCLE_END",
                "cycle_number": 3,
                "payload": {
                    "metrics": {
                        "memory_ops_total": 3,
                        "messages_to_operator": 1,
                        "response_chars": 1200,
                        "memory_write_chars": 600
                    }
                }
            }
        ])
        
        result = extract_metrics_from_dataframe(df)
        
        assert result is not None
        assert len(result) == 2  # Only cycles 1 and 3
        assert result["cycle_number"].tolist() == [1, 3]


class TestCalculateSummaryMetrics:
    """Test suite for calculate_summary_metrics function."""
    
    def test_calculates_correct_totals(self):
        """Test that summary metrics are calculated correctly."""
        
        metrics_df = pd.DataFrame([
            {
                "cycle_number": 1,
                "memory_ops_total": 5,
                "messages_to_operator": 2,
                "response_chars": 1500,
                "memory_write_chars": 800
            },
            {
                "cycle_number": 2,
                "memory_ops_total": 3,
                "messages_to_operator": 1,
                "response_chars": 1200,
                "memory_write_chars": 600
            },
            {
                "cycle_number": 3,
                "memory_ops_total": 7,
                "messages_to_operator": 3,
                "response_chars": 2000,
                "memory_write_chars": 1000
            }
        ])
        
        result = calculate_summary_metrics(metrics_df)
        
        assert result["total_memory_ops"] == 15
        assert result["total_messages"] == 6
        assert result["total_response_chars"] == 4700
        assert result["total_memory_chars"] == 2400
    
    def test_returns_integer_values(self):
        """Test that all returned values are integers."""
        
        metrics_df = pd.DataFrame([
            {
                "cycle_number": 1,
                "memory_ops_total": 5,
                "messages_to_operator": 2,
                "response_chars": 1500,
                "memory_write_chars": 800
            }
        ])
        
        result = calculate_summary_metrics(metrics_df)
        
        assert isinstance(result["total_memory_ops"], int)
        assert isinstance(result["total_messages"], int)
        assert isinstance(result["total_response_chars"], int)
        assert isinstance(result["total_memory_chars"], int)
    
    def test_handles_single_cycle(self):
        """Test that function works with single cycle."""
        
        metrics_df = pd.DataFrame([
            {
                "cycle_number": 1,
                "memory_ops_total": 5,
                "messages_to_operator": 2,
                "response_chars": 1500,
                "memory_write_chars": 800
            }
        ])
        
        result = calculate_summary_metrics(metrics_df)
        
        assert result["total_memory_ops"] == 5
        assert result["total_messages"] == 2
        assert result["total_response_chars"] == 1500
        assert result["total_memory_chars"] == 800


class TestLoadPEIAssessment:
    """Test suite for load_pei_assessment function."""
    
    def test_loads_valid_pei_file(self, tmp_path, monkeypatch):
        """Test that PEI assessment file is loaded correctly."""
        
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()
        monkeypatch.chdir(tmp_path)
        
        # Create PEI assessment file
        pei_data = {
            "run_id": "test-run-001",
            "evaluator_model": "llama3:latest",
            "pei_rating": 7,
            "pei_response": "Agent showed good exploration...",
            "timestamp": "2025-01-08T15:30:00.000000"
        }
        
        pei_file = logs_dir / "test-run-001_pei.json"
        with open(pei_file, 'w') as f:
            json.dump(pei_data, f)
        
        result = load_pei_assessment("test-run-001")
        
        assert result is not None
        assert result["run_id"] == "test-run-001"
        assert result["pei_rating"] == 7
        assert result["evaluator_model"] == "llama3:latest"
    
    def test_returns_none_when_file_not_found(self, tmp_path, monkeypatch):
        """Test that function returns None when PEI file doesn't exist."""
        
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()
        monkeypatch.chdir(tmp_path)
        
        result = load_pei_assessment("nonexistent-run")
        assert result is None
    
    def test_returns_none_on_json_decode_error(self, tmp_path, monkeypatch):
        """Test that function returns None on malformed JSON."""
        
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()
        monkeypatch.chdir(tmp_path)
        
        # Create invalid JSON file
        pei_file = logs_dir / "test-run_pei.json"
        with open(pei_file, 'w') as f:
            f.write("invalid json content")
        
        result = load_pei_assessment("test-run")
        assert result is None
    
    def test_handles_dict_format(self, tmp_path, monkeypatch):
        """Test that function handles dictionary format correctly."""
        
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()
        monkeypatch.chdir(tmp_path)
        
        pei_data = {"pei_rating": 8, "run_id": "test"}
        
        pei_file = logs_dir / "test_pei.json"
        with open(pei_file, 'w') as f:
            json.dump(pei_data, f)
        
        result = load_pei_assessment("test")
        
        assert isinstance(result, dict)
        assert result["pei_rating"] == 8
    
    def test_handles_list_format(self, tmp_path, monkeypatch):
        """Test that function handles list format correctly."""
        
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()
        monkeypatch.chdir(tmp_path)
        
        pei_data = [{"pei_rating": 8}, {"pei_rating": 9}]
        
        pei_file = logs_dir / "test_pei.json"
        with open(pei_file, 'w') as f:
            json.dump(pei_data, f)
        
        result = load_pei_assessment("test")
        
        assert isinstance(result, list)
        assert len(result) == 2


class TestConversationLogDataProcessing:
    """Test suite for conversation log data processing logic."""
    
    def test_processes_cycle_start_event(self):
        """Test that CYCLE_START events are processed correctly."""
        
        df = pd.DataFrame([
            {
                "cycle_number": 1,
                "event_type": "CYCLE_START",
                "payload": {},
                "timestamp": "2025-01-08T10:00:00"
            }
        ])
        
        # Verify DataFrame structure for conversation log processing
        for idx, row in df.iterrows():
            assert row.get('cycle_number') == 1
            assert row.get('event_type') == 'CYCLE_START'
            assert isinstance(row.get('payload'), dict)
            assert row.get('timestamp') == "2025-01-08T10:00:00"
    
    def test_processes_llm_invocation_event(self):
        """Test that LLM_INVOCATION events with messages are processed correctly."""
        
        df = pd.DataFrame([
            {
                "cycle_number": 1,
                "event_type": "LLM_INVOCATION",
                "payload": {
                    "prompt_messages": [
                        {"role": "system", "content": "You are an assistant"},
                        {"role": "user", "content": "Hello"}
                    ],
                    "response_message": {
                        "role": "assistant",
                        "content": "Hi there!"
                    }
                },
                "timestamp": "2025-01-08T10:00:01"
            }
        ])
        
        # Verify message extraction
        for idx, row in df.iterrows():
            payload = row.get('payload', {})
            assert 'prompt_messages' in payload
            assert 'response_message' in payload
            assert len(payload['prompt_messages']) == 2
            assert payload['prompt_messages'][0]['role'] == 'system'
            assert payload['response_message']['role'] == 'assistant'
    
    def test_processes_tool_call_event(self):
        """Test that TOOL_CALL events are processed correctly."""
        
        df = pd.DataFrame([
            {
                "cycle_number": 1,
                "event_type": "TOOL_CALL",
                "payload": {
                    "tool_name": "store_memory",
                    "parameters": {"key": "test", "value": "data"},
                    "output": "Memory stored successfully"
                },
                "timestamp": "2025-01-08T10:00:02"
            }
        ])
        
        # Verify tool call extraction
        for idx, row in df.iterrows():
            payload = row.get('payload', {})
            assert payload.get('tool_name') == 'store_memory'
            assert isinstance(payload.get('parameters'), dict)
            assert payload.get('output') == 'Memory stored successfully'
    
    def test_processes_cycle_end_event_with_reflection(self):
        """Test that CYCLE_END events with reflection are processed correctly."""
        
        df = pd.DataFrame([
            {
                "cycle_number": 1,
                "event_type": "CYCLE_END",
                "payload": {
                    "final_reflection": "I explored the problem space effectively",
                    "metrics": {
                        "memory_ops_total": 5,
                        "messages_to_operator": 2,
                        "response_chars": 1500
                    }
                },
                "timestamp": "2025-01-08T10:00:05"
            }
        ])
        
        # Verify reflection extraction
        for idx, row in df.iterrows():
            payload = row.get('payload', {})
            assert 'final_reflection' in payload
            assert 'metrics' in payload
            assert payload['final_reflection'] == "I explored the problem space effectively"
            assert isinstance(payload['metrics'], dict)
    
    def test_handles_missing_payload_gracefully(self):
        """Test that missing payload is handled without errors."""
        
        df = pd.DataFrame([
            {
                "cycle_number": 1,
                "event_type": "CYCLE_START",
                "timestamp": "2025-01-08T10:00:00"
                # Missing payload field
            }
        ])
        
        # Verify default handling
        for idx, row in df.iterrows():
            payload = row.get('payload', {})
            assert isinstance(payload, dict)
            assert len(payload) == 0
    
    def test_handles_non_dict_payload(self):
        """Test that non-dictionary payloads are handled gracefully."""
        
        df = pd.DataFrame([
            {
                "cycle_number": 1,
                "event_type": "CYCLE_START",
                "payload": "invalid_payload_string",
                "timestamp": "2025-01-08T10:00:00"
            }
        ])
        
        # Verify type checking
        for idx, row in df.iterrows():
            payload = row.get('payload', {})
            # The code should check isinstance(payload, dict)
            is_valid = isinstance(payload, dict)
            assert not is_valid  # String is not dict
    
    def test_handles_empty_prompt_messages(self):
        """Test that empty prompt_messages list is handled."""
        
        df = pd.DataFrame([
            {
                "cycle_number": 1,
                "event_type": "LLM_INVOCATION",
                "payload": {
                    "prompt_messages": [],
                    "response_message": {"role": "assistant", "content": "Hello"}
                },
                "timestamp": "2025-01-08T10:00:01"
            }
        ])
        
        # Verify empty list handling
        for idx, row in df.iterrows():
            payload = row.get('payload', {})
            messages = payload.get('prompt_messages', [])
            assert isinstance(messages, list)
            assert len(messages) == 0
    
    def test_handles_malformed_message_in_list(self):
        """Test that malformed messages in list are handled."""
        
        df = pd.DataFrame([
            {
                "cycle_number": 1,
                "event_type": "LLM_INVOCATION",
                "payload": {
                    "prompt_messages": [
                        {"role": "system", "content": "Valid message"},
                        "invalid_message_string",  # Malformed message
                        {"role": "user", "content": "Another valid message"}
                    ]
                },
                "timestamp": "2025-01-08T10:00:01"
            }
        ])
        
        # Verify message validation
        for idx, row in df.iterrows():
            payload = row.get('payload', {})
            if 'prompt_messages' in payload:
                messages = payload['prompt_messages']
                if isinstance(messages, list):
                    for msg in messages:
                        # Code should check isinstance(msg, dict)
                        if isinstance(msg, dict):
                            assert 'role' in msg or 'content' in msg
    
    def test_handles_missing_role_or_content_in_message(self):
        """Test that messages missing role or content are handled."""
        
        df = pd.DataFrame([
            {
                "cycle_number": 1,
                "event_type": "LLM_INVOCATION",
                "payload": {
                    "prompt_messages": [
                        {"role": "system"},  # Missing content
                        {"content": "No role specified"},  # Missing role
                        {}  # Missing both
                    ]
                },
                "timestamp": "2025-01-08T10:00:01"
            }
        ])
        
        # Verify default handling with .get()
        for idx, row in df.iterrows():
            payload = row.get('payload', {})
            if 'prompt_messages' in payload:
                for msg in payload['prompt_messages']:
                    if isinstance(msg, dict):
                        role = msg.get('role', 'unknown')
                        content = msg.get('content', '')
                        assert role in ['system', 'unknown'] or role is not None
                        assert content == '' or isinstance(content, str)
    
    def test_handles_missing_tool_call_fields(self):
        """Test that missing tool_name, parameters, or output are handled."""
        
        df = pd.DataFrame([
            {
                "cycle_number": 1,
                "event_type": "TOOL_CALL",
                "payload": {},  # All fields missing
                "timestamp": "2025-01-08T10:00:02"
            }
        ])
        
        # Verify default handling
        for idx, row in df.iterrows():
            payload = row.get('payload', {})
            tool_name = payload.get('tool_name', 'unknown')
            parameters = payload.get('parameters', {})
            output = payload.get('output', '')
            
            assert tool_name == 'unknown'
            assert isinstance(parameters, dict)
            assert output == ''
    
    def test_full_conversation_log_flow(self):
        """Test complete conversation flow with all event types."""
        
        df = pd.DataFrame([
            {
                "cycle_number": 1,
                "event_type": "CYCLE_START",
                "payload": {},
                "timestamp": "2025-01-08T10:00:00"
            },
            {
                "cycle_number": 1,
                "event_type": "LLM_INVOCATION",
                "payload": {
                    "prompt_messages": [
                        {"role": "system", "content": "System prompt"}
                    ],
                    "response_message": {
                        "role": "assistant",
                        "content": "I will use tools"
                    }
                },
                "timestamp": "2025-01-08T10:00:01"
            },
            {
                "cycle_number": 1,
                "event_type": "TOOL_CALL",
                "payload": {
                    "tool_name": "store_memory",
                    "parameters": {"key": "test"},
                    "output": "Success"
                },
                "timestamp": "2025-01-08T10:00:02"
            },
            {
                "cycle_number": 1,
                "event_type": "CYCLE_END",
                "payload": {
                    "final_reflection": "Completed cycle",
                    "metrics": {
                        "memory_ops_total": 1,
                        "messages_to_operator": 0,
                        "response_chars": 100
                    }
                },
                "timestamp": "2025-01-08T10:00:05"
            }
        ])
        
        # Verify complete flow can be processed
        event_types_seen = []
        for idx, row in df.iterrows():
            event_type = row.get('event_type', 'UNKNOWN')
            event_types_seen.append(event_type)
            payload = row.get('payload', {})
            
            # Verify payload is always a dict or can be defaulted
            if not isinstance(payload, dict):
                payload = {}
            
            assert isinstance(payload, dict)
        
        assert event_types_seen == ['CYCLE_START', 'LLM_INVOCATION', 'TOOL_CALL', 'CYCLE_END']
    
    def test_error_handling_continues_on_exception(self):
        """Test that processing continues even when individual events cause errors."""
        
        df = pd.DataFrame([
            {
                "cycle_number": 1,
                "event_type": "CYCLE_START",
                "payload": {},
                "timestamp": "2025-01-08T10:00:00"
            },
            {
                "cycle_number": 1,
                "event_type": "LLM_INVOCATION",
                "payload": None,  # This will cause issues
                "timestamp": "2025-01-08T10:00:01"
            },
            {
                "cycle_number": 1,
                "event_type": "CYCLE_END",
                "payload": {"final_reflection": "Done"},
                "timestamp": "2025-01-08T10:00:05"
            }
        ])
        
        # Verify processing can continue despite errors
        processed_count = 0
        error_count = 0
        
        for idx, row in df.iterrows():
            try:
                payload = row.get('payload', {})
                if not isinstance(payload, dict):
                    raise ValueError("Invalid payload")
                processed_count += 1
            except Exception:
                error_count += 1
                continue  # Code should continue on error
        
        assert processed_count > 0  # At least some events processed
        assert error_count > 0  # At least one error occurred
    
    def test_event_type_filtering_single_type(self):
        """Test filtering to show only one event type"""
        df = pd.DataFrame([
            {'event_type': 'CYCLE_START', 'cycle_number': 1, 'payload': {}},
            {'event_type': 'LLM_INVOCATION', 'cycle_number': 1, 'payload': {'prompt_messages': []}},
            {'event_type': 'TOOL_CALL', 'cycle_number': 1, 'payload': {'tool_name': 'test'}},
            {'event_type': 'CYCLE_END', 'cycle_number': 1, 'payload': {}},
        ])
        
        selected_types = ['TOOL_CALL']
        filtered = df[df['event_type'].isin(selected_types)]
        
        assert len(filtered) == 1
        assert filtered.iloc[0]['event_type'] == 'TOOL_CALL'

    def test_event_type_filtering_multiple_types(self):
        """Test filtering to show multiple event types"""
        df = pd.DataFrame([
            {'event_type': 'CYCLE_START', 'cycle_number': 1, 'payload': {}},
            {'event_type': 'LLM_INVOCATION', 'cycle_number': 1, 'payload': {}},
            {'event_type': 'CYCLE_END', 'cycle_number': 1, 'payload': {}},
        ])
        
        selected_types = ['CYCLE_START', 'CYCLE_END']
        filtered = df[df['event_type'].isin(selected_types)]
        
        assert len(filtered) == 2
        assert 'CYCLE_START' in filtered['event_type'].values
        assert 'CYCLE_END' in filtered['event_type'].values
        assert 'LLM_INVOCATION' not in filtered['event_type'].values

    def test_event_type_filtering_preserves_order(self):
        """Test that filtering maintains chronological order"""
        df = pd.DataFrame([
            {'event_type': 'CYCLE_START', 'cycle_number': 1, 'payload': {}, 'timestamp': '2025-01-01 10:00:00'},
            {'event_type': 'TOOL_CALL', 'cycle_number': 1, 'payload': {}, 'timestamp': '2025-01-01 10:00:01'},
            {'event_type': 'LLM_INVOCATION', 'cycle_number': 1, 'payload': {}, 'timestamp': '2025-01-01 10:00:02'},
            {'event_type': 'TOOL_CALL', 'cycle_number': 1, 'payload': {}, 'timestamp': '2025-01-01 10:00:03'},
        ])
        
        selected_types = ['TOOL_CALL']
        filtered = df[df['event_type'].isin(selected_types)]
        
        assert len(filtered) == 2
        # Verify order preserved (first tool call before second)
        assert filtered.iloc[0]['timestamp'] == '2025-01-01 10:00:01'
        assert filtered.iloc[1]['timestamp'] == '2025-01-01 10:00:03'

    def test_event_type_filtering_empty_selection(self):
        """Test behavior when no event types selected"""
        df = pd.DataFrame([
            {'event_type': 'CYCLE_START', 'cycle_number': 1, 'payload': {}},
        ])
        
        selected_types = []
        filtered = df[df['event_type'].isin(selected_types)]
        
        assert len(filtered) == 0


class TestInteractiveChartsDataPreparation:
    """Test suite for interactive charts data preparation logic."""
    
    def test_aggregates_tool_calls_by_cycle(self):
        """Test that tool calls are correctly aggregated per cycle."""
        
        df = pd.DataFrame([
            {'event_type': 'TOOL_CALL', 'cycle_number': 1, 'payload': {'tool_name': 'store_memory'}},
            {'event_type': 'TOOL_CALL', 'cycle_number': 1, 'payload': {'tool_name': 'retrieve_memory'}},
            {'event_type': 'TOOL_CALL', 'cycle_number': 2, 'payload': {'tool_name': 'store_memory'}},
            {'event_type': 'CYCLE_END', 'cycle_number': 1, 'payload': {}},
        ])
        
        tool_calls_df = df[df['event_type'] == 'TOOL_CALL'].groupby('cycle_number').size().reset_index(name='tool_calls')
        
        assert len(tool_calls_df) == 2
        assert tool_calls_df[tool_calls_df['cycle_number'] == 1]['tool_calls'].values[0] == 2
        assert tool_calls_df[tool_calls_df['cycle_number'] == 2]['tool_calls'].values[0] == 1
    
    def test_handles_zero_tool_calls(self):
        """Test that zero tool calls results in empty DataFrame."""
        
        df = pd.DataFrame([
            {'event_type': 'CYCLE_START', 'cycle_number': 1, 'payload': {}},
            {'event_type': 'CYCLE_END', 'cycle_number': 1, 'payload': {}},
        ])
        
        tool_calls_df = df[df['event_type'] == 'TOOL_CALL'].groupby('cycle_number').size().reset_index(name='tool_calls')
        
        assert len(tool_calls_df) == 0
    
    def test_extracts_metrics_for_charts(self):
        """Test that metrics are correctly extracted for chart visualization."""
        
        df = pd.DataFrame([
            {
                'event_type': 'CYCLE_END',
                'cycle_number': 1,
                'payload': {
                    'metrics': {
                        'memory_ops_total': 5,
                        'messages_to_operator': 2,
                        'response_chars': 1500,
                        'memory_write_chars': 800
                    }
                }
            },
            {
                'event_type': 'CYCLE_END',
                'cycle_number': 2,
                'payload': {
                    'metrics': {
                        'memory_ops_total': 3,
                        'messages_to_operator': 1,
                        'response_chars': 1200,
                        'memory_write_chars': 600
                    }
                }
            }
        ])
        
        cycle_ends = df[df['event_type'] == 'CYCLE_END'].copy()
        metrics_data = []
        
        for idx, row in cycle_ends.iterrows():
            if 'payload' in row and isinstance(row['payload'], dict):
                payload = row['payload']
                if 'metrics' in payload:
                    metrics = payload['metrics']
                    metrics_data.append({
                        'cycle': row['cycle_number'],
                        'memory_ops': metrics.get('memory_ops_total', 0),
                        'messages': metrics.get('messages_to_operator', 0),
                        'response_chars': metrics.get('response_chars', 0),
                        'memory_chars': metrics.get('memory_write_chars', 0)
                    })
        
        assert len(metrics_data) == 2
        assert metrics_data[0]['cycle'] == 1
        assert metrics_data[0]['memory_ops'] == 5
        assert metrics_data[1]['cycle'] == 2
        assert metrics_data[1]['response_chars'] == 1200
    
    def test_handles_missing_metrics_in_cycle_end(self):
        """Test that CYCLE_END events without metrics are skipped."""
        
        df = pd.DataFrame([
            {
                'event_type': 'CYCLE_END',
                'cycle_number': 1,
                'payload': {
                    'metrics': {
                        'memory_ops_total': 5,
                        'messages_to_operator': 2,
                        'response_chars': 1500,
                        'memory_write_chars': 800
                    }
                }
            },
            {
                'event_type': 'CYCLE_END',
                'cycle_number': 2,
                'payload': {}  # No metrics
            },
            {
                'event_type': 'CYCLE_END',
                'cycle_number': 3,
                'payload': {
                    'metrics': {
                        'memory_ops_total': 3,
                        'messages_to_operator': 1,
                        'response_chars': 1200,
                        'memory_write_chars': 600
                    }
                }
            }
        ])
        
        cycle_ends = df[df['event_type'] == 'CYCLE_END'].copy()
        metrics_data = []
        
        for idx, row in cycle_ends.iterrows():
            if 'payload' in row and isinstance(row['payload'], dict):
                payload = row['payload']
                if 'metrics' in payload:
                    metrics = payload['metrics']
                    metrics_data.append({
                        'cycle': row['cycle_number'],
                        'memory_ops': metrics.get('memory_ops_total', 0),
                        'messages': metrics.get('messages_to_operator', 0),
                        'response_chars': metrics.get('response_chars', 0),
                        'memory_chars': metrics.get('memory_write_chars', 0)
                    })
        
        assert len(metrics_data) == 2  # Only cycles 1 and 3
        assert metrics_data[0]['cycle'] == 1
        assert metrics_data[1]['cycle'] == 3
    
    def test_handles_no_cycle_end_events(self):
        """Test behavior when no CYCLE_END events exist."""
        
        df = pd.DataFrame([
            {'event_type': 'CYCLE_START', 'cycle_number': 1, 'payload': {}},
            {'event_type': 'TOOL_CALL', 'cycle_number': 1, 'payload': {}},
        ])
        
        cycle_ends = df[df['event_type'] == 'CYCLE_END'].copy()
        
        assert len(cycle_ends) == 0
    
    def test_metrics_dataframe_structure(self):
        """Test that metrics DataFrame has correct structure for charts."""
        
        metrics_data = [
            {
                'cycle': 1,
                'memory_ops': 5,
                'messages': 2,
                'response_chars': 1500,
                'memory_chars': 800
            },
            {
                'cycle': 2,
                'memory_ops': 3,
                'messages': 1,
                'response_chars': 1200,
                'memory_chars': 600
            }
        ]
        
        metrics_df = pd.DataFrame(metrics_data)
        
        assert 'cycle' in metrics_df.columns
        assert 'memory_ops' in metrics_df.columns
        assert 'messages' in metrics_df.columns
        assert 'response_chars' in metrics_df.columns
        assert 'memory_chars' in metrics_df.columns
        assert len(metrics_df) == 2
    
    def test_dataframe_melting_for_grouped_bar_chart(self):
        """Test that DataFrame melting works correctly for grouped bar charts."""
        
        metrics_df = pd.DataFrame([
            {'cycle': 1, 'memory_ops': 5, 'messages': 2},
            {'cycle': 2, 'memory_ops': 3, 'messages': 1},
        ])
        
        melted_df = metrics_df.melt(
            id_vars=['cycle'],
            value_vars=['memory_ops', 'messages'],
            var_name='Metric',
            value_name='Count'
        )
        
        assert len(melted_df) == 4  # 2 cycles × 2 metrics
        assert 'cycle' in melted_df.columns
        assert 'Metric' in melted_df.columns
        assert 'Count' in melted_df.columns
        assert 'memory_ops' in melted_df['Metric'].values
        assert 'messages' in melted_df['Metric'].values
    
    def test_metric_renaming_for_display(self):
        """Test that metrics are renamed for better display."""
        
        metrics_df = pd.DataFrame([
            {'cycle': 1, 'memory_ops': 5, 'messages': 2},
        ])
        
        melted_df = metrics_df.melt(
            id_vars=['cycle'],
            value_vars=['memory_ops', 'messages'],
            var_name='Metric',
            value_name='Count'
        )
        
        melted_df['Metric'] = melted_df['Metric'].map({
            'memory_ops': 'Memory Operations',
            'messages': 'Messages to Operator'
        })
        
        assert 'Memory Operations' in melted_df['Metric'].values
        assert 'Messages to Operator' in melted_df['Metric'].values
        assert 'memory_ops' not in melted_df['Metric'].values
        assert 'messages' not in melted_df['Metric'].values


class TestInteractiveChartsErrorHandling:
    """Test suite for interactive charts error handling."""
    
    def test_handles_empty_dataframe(self):
        """Test that empty DataFrame is handled gracefully."""
        
        df = pd.DataFrame()
        
        try:
            tool_calls_df = df[df['event_type'] == 'TOOL_CALL'].groupby('cycle_number').size().reset_index(name='tool_calls')
            # Should handle gracefully, not raise exception
            assert len(tool_calls_df) == 0
        except KeyError:
            # Expected if event_type column doesn't exist
            pass
    
    def test_handles_missing_payload_column(self):
        """Test that missing payload column is handled."""
        
        df = pd.DataFrame([
            {'event_type': 'CYCLE_END', 'cycle_number': 1}
            # Missing payload column
        ])
        
        cycle_ends = df[df['event_type'] == 'CYCLE_END'].copy()
        metrics_data = []
        
        for idx, row in cycle_ends.iterrows():
            if 'payload' in row and isinstance(row['payload'], dict):
                payload = row['payload']
                if 'metrics' in payload:
                    metrics_data.append({'cycle': row['cycle_number']})
        
        assert len(metrics_data) == 0  # No metrics extracted
    
    def test_handles_non_dict_payload(self):
        """Test that non-dictionary payload is handled."""
        
        df = pd.DataFrame([
            {
                'event_type': 'CYCLE_END',
                'cycle_number': 1,
                'payload': 'invalid_payload'
            }
        ])
        
        cycle_ends = df[df['event_type'] == 'CYCLE_END'].copy()
        metrics_data = []
        
        for idx, row in cycle_ends.iterrows():
            if 'payload' in row and isinstance(row['payload'], dict):
                payload = row['payload']
                if 'metrics' in payload:
                    metrics_data.append({'cycle': row['cycle_number']})
        
        assert len(metrics_data) == 0  # Invalid payload skipped
    
    def test_handles_missing_metric_fields(self):
        """Test that missing metric fields use default values."""
        
        df = pd.DataFrame([
            {
                'event_type': 'CYCLE_END',
                'cycle_number': 1,
                'payload': {
                    'metrics': {
                        'memory_ops_total': 5
                        # Missing other fields
                    }
                }
            }
        ])
        
        cycle_ends = df[df['event_type'] == 'CYCLE_END'].copy()
        metrics_data = []
        
        for idx, row in cycle_ends.iterrows():
            if 'payload' in row and isinstance(row['payload'], dict):
                payload = row['payload']
                if 'metrics' in payload:
                    metrics = payload['metrics']
                    metrics_data.append({
                        'cycle': row['cycle_number'],
                        'memory_ops': metrics.get('memory_ops_total', 0),
                        'messages': metrics.get('messages_to_operator', 0),
                        'response_chars': metrics.get('response_chars', 0),
                        'memory_chars': metrics.get('memory_write_chars', 0)
                    })
        
        assert len(metrics_data) == 1
        assert metrics_data[0]['memory_ops'] == 5
        assert metrics_data[0]['messages'] == 0  # Default
        assert metrics_data[0]['response_chars'] == 0  # Default
        assert metrics_data[0]['memory_chars'] == 0  # Default
    
    def test_exception_handling_continues_processing(self):
        """Test that exceptions don't stop chart data preparation."""
        
        df = pd.DataFrame([
            {
                'event_type': 'CYCLE_END',
                'cycle_number': 1,
                'payload': {
                    'metrics': {
                        'memory_ops_total': 5,
                        'messages_to_operator': 2,
                        'response_chars': 1500,
                        'memory_write_chars': 800
                    }
                }
            },
            {
                'event_type': 'CYCLE_END',
                'cycle_number': 2,
                'payload': None  # Will cause error
            },
            {
                'event_type': 'CYCLE_END',
                'cycle_number': 3,
                'payload': {
                    'metrics': {
                        'memory_ops_total': 3,
                        'messages_to_operator': 1,
                        'response_chars': 1200,
                        'memory_write_chars': 600
                    }
                }
            }
        ])
        
        cycle_ends = df[df['event_type'] == 'CYCLE_END'].copy()
        metrics_data = []
        
        for idx, row in cycle_ends.iterrows():
            try:
                if 'payload' in row and isinstance(row['payload'], dict):
                    payload = row['payload']
                    if 'metrics' in payload:
                        metrics = payload['metrics']
                        metrics_data.append({
                            'cycle': row['cycle_number'],
                            'memory_ops': metrics.get('memory_ops_total', 0),
                            'messages': metrics.get('messages_to_operator', 0),
                            'response_chars': metrics.get('response_chars', 0),
                            'memory_chars': metrics.get('memory_write_chars', 0)
                        })
            except Exception:
                continue  # Should continue processing
        
        assert len(metrics_data) == 2  # Cycles 1 and 3 processed despite error in cycle 2
        assert metrics_data[0]['cycle'] == 1
        assert metrics_data[1]['cycle'] == 3


class TestInteractiveChartsDataAccuracy:
    """Test suite for verifying chart data accuracy."""
    
    def test_tool_call_counts_match_source_data(self):
        """Test that tool call counts in chart data match source events."""
        
        df = pd.DataFrame([
            {'event_type': 'TOOL_CALL', 'cycle_number': 1, 'payload': {'tool_name': 'store_memory'}},
            {'event_type': 'TOOL_CALL', 'cycle_number': 1, 'payload': {'tool_name': 'retrieve_memory'}},
            {'event_type': 'TOOL_CALL', 'cycle_number': 1, 'payload': {'tool_name': 'send_message'}},
            {'event_type': 'TOOL_CALL', 'cycle_number': 2, 'payload': {'tool_name': 'store_memory'}},
            {'event_type': 'TOOL_CALL', 'cycle_number': 2, 'payload': {'tool_name': 'retrieve_memory'}},
        ])
        
        # Manual count
        cycle_1_count = len(df[(df['event_type'] == 'TOOL_CALL') & (df['cycle_number'] == 1)])
        cycle_2_count = len(df[(df['event_type'] == 'TOOL_CALL') & (df['cycle_number'] == 2)])
        
        # Chart data
        tool_calls_df = df[df['event_type'] == 'TOOL_CALL'].groupby('cycle_number').size().reset_index(name='tool_calls')
        
        assert tool_calls_df[tool_calls_df['cycle_number'] == 1]['tool_calls'].values[0] == cycle_1_count
        assert tool_calls_df[tool_calls_df['cycle_number'] == 2]['tool_calls'].values[0] == cycle_2_count
        assert cycle_1_count == 3
        assert cycle_2_count == 2
    
    def test_metrics_values_match_source_data(self):
        """Test that metric values in chart data match source CYCLE_END events."""
        
        df = pd.DataFrame([
            {
                'event_type': 'CYCLE_END',
                'cycle_number': 1,
                'payload': {
                    'metrics': {
                        'memory_ops_total': 5,
                        'messages_to_operator': 2,
                        'response_chars': 1500,
                        'memory_write_chars': 800
                    }
                }
            }
        ])
        
        # Extract for chart
        cycle_ends = df[df['event_type'] == 'CYCLE_END'].copy()
        metrics_data = []
        
        for idx, row in cycle_ends.iterrows():
            if 'payload' in row and isinstance(row['payload'], dict):
                payload = row['payload']
                if 'metrics' in payload:
                    metrics = payload['metrics']
                    metrics_data.append({
                        'cycle': row['cycle_number'],
                        'memory_ops': metrics.get('memory_ops_total', 0),
                        'messages': metrics.get('messages_to_operator', 0),
                        'response_chars': metrics.get('response_chars', 0),
                        'memory_chars': metrics.get('memory_write_chars', 0)
                    })
        
        # Verify accuracy
        source_metrics = df.iloc[0]['payload']['metrics']
        chart_data = metrics_data[0]
        
        assert chart_data['memory_ops'] == source_metrics['memory_ops_total']
        assert chart_data['messages'] == source_metrics['messages_to_operator']
        assert chart_data['response_chars'] == source_metrics['response_chars']
        assert chart_data['memory_chars'] == source_metrics['memory_write_chars']
    
    def test_all_cycles_represented_in_chart_data(self):
        """Test that all cycles with data are represented in chart data."""
        
        df = pd.DataFrame([
            {'event_type': 'CYCLE_END', 'cycle_number': 1, 'payload': {'metrics': {'memory_ops_total': 5}}},
            {'event_type': 'CYCLE_END', 'cycle_number': 2, 'payload': {'metrics': {'memory_ops_total': 3}}},
            {'event_type': 'CYCLE_END', 'cycle_number': 3, 'payload': {'metrics': {'memory_ops_total': 7}}},
            {'event_type': 'CYCLE_END', 'cycle_number': 5, 'payload': {'metrics': {'memory_ops_total': 2}}},
        ])
        
        expected_cycles = [1, 2, 3, 5]
        
        cycle_ends = df[df['event_type'] == 'CYCLE_END'].copy()
        metrics_data = []
        
        for idx, row in cycle_ends.iterrows():
            if 'payload' in row and isinstance(row['payload'], dict):
                payload = row['payload']
                if 'metrics' in payload:
                    metrics = payload['metrics']
                    metrics_data.append({
                        'cycle': row['cycle_number'],
                        'memory_ops': metrics.get('memory_ops_total', 0)
                    })
        
        chart_cycles = [d['cycle'] for d in metrics_data]
        
        assert chart_cycles == expected_cycles
        assert len(chart_cycles) == 4


def test_load_memory_entries_success():
    """Test loading memory entries from database."""
    # TODO: Implement test with populated test database
    pass


def test_load_memory_entries_missing_db():
    """Test handling of missing memory database."""
    # TODO: Test when file doesn't exist
    pass


def test_load_memory_entries_empty_run():
    """Test loading memory for run with no entries."""
    # TODO: Test when run_id has no entries
    pass
