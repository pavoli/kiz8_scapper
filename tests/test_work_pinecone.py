import os
import pytest
import sys
from unittest.mock import patch, MagicMock

sibling_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'utils'))
sys.path.append(sibling_dir)

from work_pinecone import PineconeClient, MAX_BATCH_SIZE

# Patch environment variables and dependencies at the module level
@pytest.fixture(autouse=True)
def patch_env(monkeypatch):
    monkeypatch.setenv("PINECONE_API_KEY", "test-key")
    monkeypatch.setenv("PINECONE_INDEX_NAME", "test-index")
    monkeypatch.setenv("PINECONE_NAMESPACE", "test-namespace")

@pytest.fixture
def mock_logger():
    with patch("work_pinecone.setup_logger") as logger:
        yield logger

@pytest.fixture
def mock_pinecone():
    with patch("work_pinecone.Pinecone") as pinecone:
        mock_pc = MagicMock()
        pinecone.return_value = mock_pc
        yield mock_pc

@pytest.fixture
def pinecone_client(mock_logger, mock_pinecone):
    # This will use patched env vars and mocked Pinecone
    return PineconeClient()

def test_init_uses_env_vars(pinecone_client):
    assert pinecone_client.api_key == "test-key"
    assert pinecone_client.index_name == "test-index"
    assert pinecone_client.namespace == "test-namespace"
    assert pinecone_client.logger is not None

def test_create_index_creates_when_missing(pinecone_client, mock_pinecone):
    # Simulate index not existing
    mock_pinecone.has_index.return_value = False
    pinecone_client.create_index()
    mock_pinecone.create_index_for_model.assert_called_once()
    pinecone_client.logger.debug.assert_any_call(f"Index `{pinecone_client.index_name}` created.")

def test_create_index_skips_when_exists(pinecone_client, mock_pinecone):
    # Simulate index exists
    mock_pinecone.has_index.return_value = True
    pinecone_client.create_index()
    mock_pinecone.create_index_for_model.assert_not_called()
    pinecone_client.logger.debug.assert_any_call(f"Index `{pinecone_client.index_name}` already exists.")

def test_batch_records_batches_correctly(pinecone_client):
    records = [{"id": i} for i in range(105)]
    batches = list(pinecone_client.batch_records(records, max_batch_size=50))
    assert len(batches) == 3
    assert len(batches[0]) == 50
    assert len(batches[1]) == 50
    assert len(batches[2]) == 5

@patch("work_pinecone.parse_json_pinecone")
def test_upsert_data_success(mock_parse_json, pinecone_client):
    # Mock parse_json_pinecone to return 3 records
    mock_parse_json.return_value = [{"id": i} for i in range(3)]
    pinecone_client.dense_index = MagicMock()
    pinecone_client.batch_records = lambda records, max_batch_size=MAX_BATCH_SIZE: [records]
    pinecone_client.upsert_data("dummy_dir")
    pinecone_client.dense_index.upsert_records.assert_called_once_with(
        pinecone_client.namespace, [{"id": 0}, {"id": 1}, {"id": 2}]
    )
    pinecone_client.logger.info.assert_called_with("All data upserted into Pinecone successfully.")

@patch("work_pinecone.parse_json_pinecone")
def test_upsert_data_raises_on_error(mock_parse_json, pinecone_client):
    mock_parse_json.side_effect = Exception("parse error")
    with pytest.raises(Exception):
        pinecone_client.upsert_data("dummy_dir")
    pinecone_client.logger.error.assert_called()
