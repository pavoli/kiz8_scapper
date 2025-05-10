import os
import json
import tempfile
import shutil
import sys
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock

sibling_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'utils'))
sys.path.append(sibling_dir)

# Import functions from your module
from work_json import (
    read_json_file,
    read_json_file_all,
    parse_json_pinecone,
    parse_json_postgres_question,
    parse_json_postgres_answer,
)

# Patch the logger to avoid cluttering test output
@pytest.fixture(autouse=True)
def patch_logger():
    with patch("work_json.logger") as mock_logger:
        yield mock_logger

@pytest.fixture
def temp_json_dir():
    """Creates a temporary directory with sample JSON files."""
    temp_dir = tempfile.mkdtemp()
    files = []
    # Create 2 JSON files with minimal data
    for i in range(2):
        data = {
            "data": [
                {
                    "id": f"id_{i}_1",
                    "title": f"title_{i}_1",
                    "keywords": [f"kw_{i}_1"],
                    "shortAnswer": f"short_{i}_1",
                    "createdAt": f"2024-01-0{i+1}",
                },
                {
                    "id": f"id_{i}_2",
                    "title": f"title_{i}_2",
                    "keywords": [f"kw_{i}_2"],
                    "shortAnswer": f"short_{i}_2",
                    "createdAt": f"2024-01-0{i+2}",
                },
            ]
        }
        file_path = os.path.join(temp_dir, f"file_{i}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        files.append(file_path)
    yield temp_dir, files
    shutil.rmtree(temp_dir)

def test_read_json_file_success(temp_json_dir):
    _, files = temp_json_dir
    data = read_json_file(files[0])
    assert isinstance(data, dict)
    assert "data" in data
    assert len(data["data"]) == 2

def test_read_json_file_not_found():
    assert read_json_file("nonexistent_file.json") is None

def test_read_json_file_invalid_json(tmp_path):
    file_path = tmp_path / "bad.json"
    file_path.write_text("{invalid json", encoding="utf-8")
    assert read_json_file(str(file_path)) is None

def test_read_json_file_permission_error(tmp_path):
    file_path = tmp_path / "no_perm.json"
    file_path.write_text("{}", encoding="utf-8")
    os.chmod(file_path, 0)  # Remove all permissions
    try:
        assert read_json_file(str(file_path)) is None
    finally:
        os.chmod(file_path, 0o644)  # Restore permissions so pytest can clean up

def test_read_json_file_all_prints_and_logs(temp_json_dir, capsys):
    _, files = temp_json_dir
    # Only first 10 items, but our test files have 2 items each
    read_json_file_all(files[0])
    captured = capsys.readouterr()
    assert "id" in captured.out
    # No assertion on logs, as logger is patched

@patch("work_json.get_all_json_files")
@patch("work_json.read_json_file")
def test_parse_json_pinecone_success(mock_read_json, mock_get_files):
    # Simulate two files with data
    mock_get_files.return_value = ["file1.json", "file2.json"]
    mock_read_json.side_effect = [
        {
            "data": [
                {"id": 1, "title": "T1", "keywords": ["a"]},
                {"id": 2, "title": "T2", "keywords": ["b"]},
            ]
        },
        {
            "data": [
                {"id": 3, "title": "T3", "keywords": ["c"]},
            ]
        },
    ]
    with patch("work_json.QUESTION_URL", "http://q/{0}"):
        results = parse_json_pinecone("dummy_dir")
        assert isinstance(results, list)
        assert results[0]["_id"] == "1"
        assert results[0]["url"] == "http://q/1"
        assert results[2]["_id"] == "3"

@patch("work_json.get_all_json_files")
@patch("work_json.read_json_file")
def test_parse_json_pinecone_empty_files(mock_read_json, mock_get_files):
    mock_get_files.return_value = []
    assert parse_json_pinecone("dummy_dir") is None

@patch("work_json.get_all_json_files")
@patch("work_json.read_json_file")
def test_parse_json_postgres_question_success(mock_read_json, mock_get_files):
    mock_get_files.return_value = ["file1.json"]
    mock_read_json.return_value = {
        "data": [
            {"id": 1, "title": "T1", "createdAt": "2024-01-01"},
            {"id": 2, "title": "T2", "createdAt": "2024-01-02"},
        ]
    }
    results = parse_json_postgres_question("dummy_dir")
    assert isinstance(results, list)
    assert results[0] == (1, "T1", "2024-01-01")

@patch("work_json.get_all_json_files")
@patch("work_json.read_json_file")
def test_parse_json_postgres_answer_success(mock_read_json, mock_get_files):
    mock_get_files.return_value = ["file1.json"]
    mock_read_json.return_value = {
        "data": [
            {"id": 1, "shortAnswer": "A1"},
            {"id": 2, "shortAnswer": "A2"},
        ]
    }
    results = parse_json_postgres_answer("dummy_dir")
    assert isinstance(results, list)
    assert results[0] == (1, "A1")
    assert results[1] == (2, "A2")

@patch("work_json.get_all_json_files")
@patch("work_json.read_json_file")
def test_parse_json_postgres_answer_empty_files(mock_read_json, mock_get_files):
    mock_get_files.return_value = []
    assert parse_json_postgres_answer("dummy_dir") is None
