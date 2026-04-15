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
    DebugGetEmbeddingsRequest,
    DebugDistanceData,
    DebugDistanceResponse,
    GetCollectionDataResponse,
    CollectionDataRecord,
    GetCollectionSchemaResponse,
    ListNLIVerticalsResponse,
    VerticalInfo,
    EnableMetadataStoreRequest,
    MetadataColumnSchema,
    AttrType,
    EnableMetadataStoreResponse,
    FuzzyAlgo,
    GetSettingsResponse,
    SettingsUpdateRequest,
    SettingsAuth,
    SettingsAvailableProvidersResponse,
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

    @patch("shilp.client.requests.Session")
    def test_client_auth_header(self, mock_session_class):
        """Test Authorization header when auth token is configured."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "version": "1.0.0"}
        mock_response.content = b'{"success": true, "version": "1.0.0"}'
        mock_session.request.return_value = mock_response

        client = Client("http://localhost:3000", auth_token="token-123")
        client.health_check()

        call_args = mock_session.request.call_args
        assert call_args[1]["headers"]["Authorization"] == "Bearer token-123"

    @patch("shilp.client.requests.Session")
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

    @patch("shilp.client.requests.Session")
    def test_add_collection(self, mock_session_class):
        """Test add collection method."""
        # Setup mock
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "message": "Collection created",
        }
        mock_response.content = b'{"success": true}'
        mock_session.request.return_value = mock_response

        # Create client and call add_collection
        client = Client("http://localhost:3000")
        request = AddCollectionRequest(
            name="test-collection",
            storage_type=StorageBackendType.FILE,
            reference_storage_type=StorageBackendType.FILE,
        )
        result = client.add_collection(request)

        # Verify
        assert isinstance(result, GenericResponse)
        assert result.success is True
        mock_session.request.assert_called_once()

        # Verify request parameters
        call_args = mock_session.request.call_args
        assert call_args[1]["method"] == "POST"
        assert "/api/collections/v1/" in call_args[1]["url"]

    @patch("shilp.client.requests.Session")
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
            client.read_document(
                "/some/path", options=FileReaderOptions(limit=-1, skip=0)
            )

        # Negative skip should raise ValueError
        with pytest.raises(ValueError, match="skip cannot be negative"):
            client.read_document(
                "/some/path", options=FileReaderOptions(limit=10, skip=-1)
            )


class TestClientRequestBuilding:
    """Test Client request building logic."""

    @patch("shilp.client.requests.Session")
    def test_request_with_query_params(self, mock_session_class):
        """Test request with query parameters."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "message": "OK",
            "data": {"items": []},
        }
        mock_response.content = b'{"success": true}'
        mock_session.request.return_value = mock_response

        client = Client("http://localhost:3000")
        client.list_storage("/some/path")

        # Verify query params were included
        call_args = mock_session.request.call_args
        assert call_args[1]["params"]["path"] == "/some/path"

    @patch("shilp.client.requests.Session")
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
        request = AddCollectionRequest(
            name="test-collection", has_metadata_storage=True
        )
        client.add_collection(request)

        # Verify JSON data was sent
        call_args = mock_session.request.call_args
        assert call_args[1]["json"]["name"] == "test-collection"
        assert call_args[1]["json"]["has_metadata_storage"] is True


class TestNewV013Methods:
    """Test new v0.13.1 methods."""

    @patch("shilp.client.requests.Session")
    def test_get_collection_distance_with_custom_matcher_text(self, mock_session_class):
        """Test get_collection_distance with custom_matcher_text parameter."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "message": "OK",
            "data": {
                "distance": 0.5,
                "vector": [0.1, 0.2, 0.3],
                "custom_matcher_distance": 0.3,
            },
        }
        mock_response.content = b'{"success": true}'
        mock_session.request.return_value = mock_response

        client = Client("http://localhost:3000")
        result = client.get_collection_distance(
            "my-collection",
            "field1",
            42,
            "hello world",
            custom_matcher_text="custom text",
        )

        assert isinstance(result, DebugDistanceResponse)
        assert isinstance(result.data, DebugDistanceData)
        assert result.data.distance == 0.5
        assert result.data.custom_matcher_distance == 0.3
        assert result.data.vector == [0.1, 0.2, 0.3]

        call_args = mock_session.request.call_args
        assert call_args[1]["params"]["text"] == "hello world"
        assert call_args[1]["params"]["custom_matcher_text"] == "custom text"

    @patch("shilp.client.requests.Session")
    def test_get_collection_distance_without_custom_matcher_text(
        self, mock_session_class
    ):
        """Test get_collection_distance without custom_matcher_text uses no extra param."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "message": "OK",
            "data": {
                "distance": 0.7,
                "vector": [0.4, 0.5],
                "custom_matcher_distance": None,
            },
        }
        mock_response.content = b'{"success": true}'
        mock_session.request.return_value = mock_response

        client = Client("http://localhost:3000")
        result = client.get_collection_distance("my-collection", "field1", 1, "text")

        call_args = mock_session.request.call_args
        assert "custom_matcher_text" not in call_args[1]["params"]

    @patch("shilp.client.requests.Session")
    def test_get_collection_embeddings(self, mock_session_class):
        """Test get_collection_embeddings method."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "message": "OK",
            "data": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
        }
        mock_response.content = b'{"success": true}'
        mock_session.request.return_value = mock_response

        client = Client("http://localhost:3000")
        req = DebugGetEmbeddingsRequest(texts=["hello", "world"])
        result = client.get_collection_embeddings("my-collection", req)

        assert result.success is True
        assert result.data == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]

        call_args = mock_session.request.call_args
        assert call_args[1]["method"] == "POST"
        assert (
            "/api/collections/v1/debug/my-collection/embedding" in call_args[1]["url"]
        )
        assert call_args[1]["json"]["texts"] == ["hello", "world"]

    @patch("shilp.client.requests.Session")
    def test_get_collection_data(self, mock_session_class):
        """Test get_collection_data method."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "message": "OK",
            "data": [
                {"id": "1", "data": {"field": "value"}, "vectors": None},
                {"id": "2", "data": {"field": "value2"}},
            ],
            "total": 2,
        }
        mock_response.content = b'{"success": true}'
        mock_session.request.return_value = mock_response

        client = Client("http://localhost:3000")
        result = client.get_collection_data("my-collection", 0, 10)

        assert isinstance(result, GetCollectionDataResponse)
        assert result.total == 2
        assert len(result.data) == 2
        assert isinstance(result.data[0], CollectionDataRecord)
        assert result.data[0].id == "1"

        call_args = mock_session.request.call_args
        assert call_args[1]["params"]["offset"] == 0
        assert call_args[1]["params"]["limit"] == 10

    @patch("shilp.client.requests.Session")
    def test_get_collection_schema(self, mock_session_class):
        """Test get_collection_schema method."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "message": "OK",
            "data": {
                "attributes": [
                    {
                        "name": "color",
                        "type": 2,
                        "index_type": "inverted",
                        "is_metadata": False,
                    }
                ],
                "value_schema": [
                    {
                        "name": "color",
                        "index_type": "inverted",
                        "values": [{"value": "red", "count": 10}],
                        "synonyms": ["hue"],
                    }
                ],
            },
        }
        mock_response.content = b'{"success": true}'
        mock_session.request.return_value = mock_response

        client = Client("http://localhost:3000")
        result = client.get_collection_schema("my-collection")

        assert isinstance(result, GetCollectionSchemaResponse)
        assert result.data is not None
        assert len(result.data.attributes) == 1
        assert result.data.attributes[0].name == "color"
        assert len(result.data.value_schema) == 1
        assert result.data.value_schema[0].values[0].value == "red"

    @patch("shilp.client.requests.Session")
    def test_list_nli_verticals(self, mock_session_class):
        """Test list_nli_verticals method."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "message": "OK",
            "data": [
                {"name": "ecommerce", "label": "E-Commerce", "is_native": True},
                {"name": "custom", "label": "Custom", "is_native": False},
            ],
        }
        mock_response.content = b'{"success": true}'
        mock_session.request.return_value = mock_response

        client = Client("http://localhost:3000")
        result = client.list_nli_verticals()

        assert isinstance(result, ListNLIVerticalsResponse)
        assert result.success is True
        assert len(result.data) == 2
        assert isinstance(result.data[0], VerticalInfo)
        assert result.data[0].name == "ecommerce"
        assert result.data[0].is_native is True

        call_args = mock_session.request.call_args
        assert "/api/data/v1/nli/verticals" in call_args[1]["url"]

    @patch("shilp.client.requests.Session")
    def test_search_with_use_nli(self, mock_session_class):
        """Test search_data includes use_nli when set."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "data": [], "message": "OK"}
        mock_response.content = b'{"success": true}'
        mock_session.request.return_value = mock_response

        client = Client("http://localhost:3000")
        request = SearchRequest(
            collection="my-collection", query="search text", use_nli=True
        )
        client.search_data(request)

        call_args = mock_session.request.call_args
        assert call_args[1]["json"]["use_nli"] is True

    @patch("shilp.client.requests.Session")
    def test_list_collections_with_nli_fields(self, mock_session_class):
        """Test list_collections handles new NLI fields in Collection."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "message": "OK",
            "data": [
                {
                    "name": "test",
                    "is_loaded": True,
                    "fields": ["f1"],
                    "searchable_fields": ["f1"],
                    "storage_type": 1,
                    "reference_storage_type": 1,
                    "field_config": {"f1": "hnsw"},
                    "is_nli_enabled": True,
                    "nli_domain": "ecommerce",
                    "total_no_of_documents": 25,
                }
            ],
            "is_nli_supported": True,
        }
        mock_response.content = b'{"success": true}'
        mock_session.request.return_value = mock_response

        client = Client("http://localhost:3000")
        result = client.list_collections()

        assert result.is_nli_supported is True
        assert result.data[0].field_config == {"f1": "hnsw"}
        assert result.data[0].is_nli_enabled is True
        assert result.data[0].nli_domain == "ecommerce"
        assert result.data[0].total_no_of_documents == 25

    @patch("shilp.client.requests.Session")
    def test_search_with_invalid_fuzzy_algo(self, mock_session_class):
        """Test search_data validates fuzzy_algo."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        client = Client("http://localhost:3000")
        request = SearchRequest(
            collection="my-collection", query="search text", fuzzy_algo="bad_algo"
        )
        with pytest.raises(ValueError, match="invalid fuzzy algorithm - bad_algo"):
            client.search_data(request)

    @patch("shilp.client.requests.Session")
    def test_search_with_valid_fuzzy_algo(self, mock_session_class):
        """Test search_data includes fuzzy_algo when valid."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "data": [], "message": "OK"}
        mock_response.content = b'{"success": true}'
        mock_session.request.return_value = mock_response

        client = Client("http://localhost:3000")
        request = SearchRequest(
            collection="my-collection",
            query="search text",
            fuzzy_algo=FuzzyAlgo.LEVENSHTEIN,
        )
        client.search_data(request)

        call_args = mock_session.request.call_args
        assert call_args[1]["json"]["fuzzy_algo"] == FuzzyAlgo.LEVENSHTEIN

    @patch("shilp.client.requests.Session")
    def test_enable_metadata_store(self, mock_session_class):
        """Test enable_metadata_store endpoint."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "message": "enabled",
            "records_indexed": 3,
        }
        mock_response.content = b'{"success": true}'
        mock_session.request.return_value = mock_response

        client = Client("http://localhost:3000")
        req = EnableMetadataStoreRequest(
            fields=[MetadataColumnSchema(name="color", type=AttrType.STRING)]
        )
        result = client.enable_metadata_store("my-collection", req)

        assert isinstance(result, EnableMetadataStoreResponse)
        assert result.records_indexed == 3
        call_args = mock_session.request.call_args
        assert call_args[1]["method"] == "POST"
        assert (
            "/api/collections/v1/my-collection/metadata/enable" in call_args[1]["url"]
        )

    @patch("shilp.client.requests.Session")
    def test_get_settings(self, mock_session_class):
        """Test get_settings endpoint parsing."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "message": "ok",
            "data": {
                "auth": {"enable": True, "tested": True, "name": "jwt"},
                "allowedOrigins": ["*"],
                "integrations": [],
            },
        }
        mock_response.content = b'{"success": true}'
        mock_session.request.return_value = mock_response

        client = Client("http://localhost:3000")
        result = client.get_settings()

        assert isinstance(result, GetSettingsResponse)
        assert result.data is not None
        assert result.data.auth.enable is True

    @patch("shilp.client.requests.Session")
    def test_update_settings(self, mock_session_class):
        """Test update_settings endpoint."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "message": "updated"}
        mock_response.content = b'{"success": true}'
        mock_session.request.return_value = mock_response

        client = Client("http://localhost:3000")
        req = SettingsUpdateRequest(
            auth=SettingsAuth(enable=True, tested=True, name="jwt")
        )
        result = client.update_settings(req)

        assert result.success is True
        call_args = mock_session.request.call_args
        assert call_args[1]["method"] == "PUT"
        assert "/api/settings/v1/" in call_args[1]["url"]
        assert call_args[1]["json"]["auth"]["name"] == "jwt"

    @patch("shilp.client.requests.Session")
    def test_list_providers(self, mock_session_class):
        """Test list_providers endpoint parsing."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "message": "ok",
            "data": {
                "auth": [{"name": "jwt", "type": "auth", "arguments": []}],
                "integrations": [{"name": "x", "type": "data-source", "arguments": []}],
            },
        }
        mock_response.content = b'{"success": true}'
        mock_session.request.return_value = mock_response

        client = Client("http://localhost:3000")
        result = client.list_providers()

        assert isinstance(result, SettingsAvailableProvidersResponse)
        assert result.data is not None
        assert result.data.auth[0].name == "jwt"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
