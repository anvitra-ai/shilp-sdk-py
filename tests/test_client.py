"""
Unit tests for Shilp SDK Client.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from shilp.client import Client
from shilp.models import (
    AddCollectionRequest,
    FileReaderOptions,
    InsertRecordRequest,
    SearchRequest,
    HealthResponse,
    GenericResponse,
    StorageBackendType,
)


class TestClient:
    """Test Client initialization and basic methods."""

    def test_client_initialization(self):
        """Test client initialization with base URL."""
        client = Client("http://localhost:3000")
        assert client.base_url == "http://localhost:3000"
        assert client.timeout == 30

    def test_client_strips_trailing_slash(self):
        """Test that trailing slash is removed from base URL."""
        client = Client("http://localhost:3000/")
        assert client.base_url == "http://localhost:3000"

    def test_client_custom_timeout(self):
        """Test client initialization with custom timeout."""
        client = Client("http://localhost:3000", timeout=60)
        assert client.timeout == 60

    @patch('shilp.client.requests.Session')
    def test_health_check(self, mock_session_class):
        """Test health check method."""
        # Setup mock
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "version": "1.0.0"}
        mock_response.content = b'{"success": true, "version": "1.0.0"}'
        mock_session.request.return_value = mock_response
        
        # Create client and call health_check
        client = Client("http://localhost:3000")
        result = client.health_check()
        
        # Verify
        assert isinstance(result, HealthResponse)
        assert result.success is True
        assert result.version == "1.0.0"
        mock_session.request.assert_called_once()

    @patch('shilp.client.requests.Session')
    def test_add_collection(self, mock_session_class):
        """Test add collection method."""
        # Setup mock
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "message": "Collection created"}
        mock_response.content = b'{"success": true}'
        mock_session.request.return_value = mock_response
        
        # Create client and call add_collection
        client = Client("http://localhost:3000")
        request = AddCollectionRequest(name="test-collection", storage_type=StorageBackendType.FILE, reference_storage_type=StorageBackendType.FILE)
        result = client.add_collection(request)
        
        # Verify
        assert isinstance(result, GenericResponse)
        assert result.success is True
        mock_session.request.assert_called_once()
        
        # Verify request parameters
        call_args = mock_session.request.call_args
        assert call_args[1]['method'] == 'POST'
        assert '/api/collections/v1/' in call_args[1]['url']

    @patch('shilp.client.requests.Session')
    def test_request_error_handling(self, mock_session_class):
        """Test error handling for failed requests."""
        # Setup mock
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_session.request.return_value = mock_response
        
        # Create client and expect error
        client = Client("http://localhost:3000")
        
        with pytest.raises(Exception):  # Should raise HTTPError
            client.health_check()

    def test_read_document_validation(self):
        """Test read_document parameter validation."""
        client = Client("http://localhost:3000")

        options = FileReaderOptions(limit=10, skip=0)
        
        # Empty path should raise ValueError
        with pytest.raises(ValueError, match="path cannot be empty"):
            client.read_document("", options=options)
        
        # Negative rows should raise ValueError
        with pytest.raises(ValueError, match="limit cannot be negative"):
            client.read_document("/some/path", options=FileReaderOptions(limit=-1, skip=0))
        
        # Negative skip should raise ValueError
        with pytest.raises(ValueError, match="skip cannot be negative"):
            client.read_document("/some/path", options=FileReaderOptions(limit=10, skip=-1))
class TestClientRequestBuilding:
    """Test Client request building logic."""

    @patch('shilp.client.requests.Session')
    def test_request_with_query_params(self, mock_session_class):
        """Test request with query parameters."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "message": "OK",
            "data": {"items": []}
        }
        mock_response.content = b'{"success": true}'
        mock_session.request.return_value = mock_response
        
        client = Client("http://localhost:3000")
        client.list_storage("/some/path")
        
        # Verify query params were included
        call_args = mock_session.request.call_args
        assert call_args[1]['params']['path'] == '/some/path'

    @patch('shilp.client.requests.Session')
    def test_request_with_json_body(self, mock_session_class):
        """Test request with JSON body."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "message": "OK"}
        mock_response.content = b'{"success": true}'
        mock_session.request.return_value = mock_response
        
        client = Client("http://localhost:3000")
        request = AddCollectionRequest(name="test-collection", has_metadata_storage=True)
        client.add_collection(request)
        
        # Verify JSON data was sent
        call_args = mock_session.request.call_args
        assert call_args[1]['json']['name'] == 'test-collection'
        assert call_args[1]['json']['has_metadata_storage'] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
