"""
Unit tests for Results Dashboard functionality.

Tests the core functions used in the Results Dashboard page including
log file scanning and JSONL file loading.

Part of: Story 2.5 - Results Dashboard Run Selector and Data Loading
Part of: Story 2.6 - Display Summary Metrics on Dashboard
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
