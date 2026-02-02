"""Shilp API Client implementation."""

import json
import requests
from typing import Any, Dict, List, Optional, BinaryIO, Callable
from io import IOBase
from urllib.parse import urljoin

from shilp.models import (
    GenericResponse,
    HealthResponse,
    ListCollectionsResponse,
    Collection,
    MetadataSupportInfo,
    AddCollectionRequest,
    InsertRecordRequest,
    InsertRecordResponse,
    IngestRequest,
    IngestResponse,
    ListIngestionSourcesResponse,
    FileReaderOptions,
    SearchRequest,
    SearchResponse,
    ListStorageResponse,
    ReadDocumentResponse,
    ListEmbeddingModelsResponse,
    DebugDistanceResponse,
    DebugNodeInfoResponse,
    DebugLevelsResponse,
    DebugNodesAtLevelResponse,
    DebugReferenceNodeResponse,
    OplogStatusResponse,
    GetOplogResponse,
    UpdateReplicaLSNRequest,
    UpdateReplicaLSNResponse,
    RegisterReplicaRequest,
    UnRegisterReplicaRequest,
    StorageBackendType,
)


class Client:
    """Client for the Shilp API."""

    def __init__(self, base_url: str, timeout: int = 30, session: Optional[requests.Session] = None):
        """
        Initialize the Shilp API client.

        Args:
            base_url: Base URL of the Shilp server (e.g., "http://localhost:3000")
            timeout: Request timeout in seconds (default: 30)
            session: Optional custom requests.Session instance
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()

    def _request(
        self,
        method: str,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Perform an HTTP request.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API endpoint path
            json_data: JSON data to send in request body
            params: Query parameters

        Returns:
            Response JSON as dictionary

        Raises:
            requests.HTTPError: If the request fails
        """
        url = urljoin(self.base_url, path)
        
        response = self.session.request(
            method=method,
            url=url,
            json=json_data,
            params=params,
            timeout=self.timeout,
        )

        if response.status_code >= 400:
            raise requests.HTTPError(
                f"API error: {response.text} (status: {response.status_code})",
                response=response,
            )

        return response.json() if response.content else {}

    def _request_file_response(
        self,
        method: str,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> BinaryIO:
        """
        Perform an HTTP request and return file response.

        Args:
            method: HTTP method
            path: API endpoint path
            json_data: JSON data to send in request body
            params: Query parameters

        Returns:
            Response content as binary stream

        Raises:
            requests.HTTPError: If the request fails
        """
        url = urljoin(self.base_url, path)
        
        response = self.session.request(
            method=method,
            url=url,
            json=json_data,
            params=params,
            timeout=self.timeout,
            stream=True,
        )

        if response.status_code >= 400:
            raise requests.HTTPError(
                f"API error: {response.text} (status: {response.status_code})",
                response=response,
            )

        return response.raw

    def _upload_file(self, path: str, file_path: str) -> Dict[str, Any]:
        """
        Upload a file to the API.

        Args:
            path: API endpoint path
            file_path: Path to the file to upload

        Returns:
            Response JSON as dictionary

        Raises:
            requests.HTTPError: If the request fails
        """
        url = urljoin(self.base_url, path)
        
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = self.session.post(
                url=url,
                files=files,
                timeout=self.timeout,
            )

        if response.status_code >= 400:
            raise requests.HTTPError(
                f"API error: {response.text} (status: {response.status_code})",
                response=response,
            )

        return response.json() if response.content else {}

    # Health Check
    def health_check(self) -> HealthResponse:
        """
        Perform a health check on the API.

        Returns:
            HealthResponse with success status and version
        """
        data = self._request("GET", "/health")
        return HealthResponse(**data)

    # Collection Management
    def list_collections(self) -> ListCollectionsResponse:
        """
        List all collections.

        Returns:
            ListCollectionsResponse containing list of collections
        """
        data = self._request("GET", "/api/collections/v1/")
        # Convert nested collections
        if 'data' in data:
            data['data'] = [
                Collection(
                    name=c['name'],
                    is_loaded=c['is_loaded'],
                    fields=c['fields'],
                    searchable_fields=c['searchable_fields'],
                    metadata=c.get('metadata'),
                    has_metadata_enabled=c.get('has_metadata_enabled', False),
                    no_reference_storage=c.get('no_reference_storage', False),
                    storage_type=StorageBackendType(c.get('storage_type', 0)),
                    reference_storage_type=StorageBackendType(c.get('reference_storage_type', 0)),
                    is_pq_enabled=c.get('is_pq_enabled', False),
                )
                for c in data['data']
            ]
        # Convert metadata_info
        if 'metadata_info' in data and data['metadata_info']:
            data['metadata_info'] = [
                MetadataSupportInfo(
                    support_metadata=m['support_metadata'],
                    name=m['name'],
                    type=StorageBackendType(m['type']),
                    is_default=m['is_default'],
                )
                for m in data['metadata_info']
            ]
        return ListCollectionsResponse(**data)

    def add_collection(self, request: AddCollectionRequest) -> GenericResponse:
        """
        Add a new collection.

        Args:
            request: AddCollectionRequest with collection details

        Returns:
            GenericResponse indicating success or failure
        """
        json_data = {
            "name": request.name,
            "no_reference_storage": request.no_reference_storage,
            "has_metadata_storage": request.has_metadata_storage,
        }
        if request.storage_type is not None:
            json_data["storage_type"] = request.storage_type
        if request.reference_storage_type is not None:
            json_data["reference_storage_type"] = request.reference_storage_type
        if request.enable_pq:
            json_data["enable_pq"] = request.enable_pq
        data = self._request("POST", "/api/collections/v1/", json_data=json_data)
        return GenericResponse(**data)

    def drop_collection(self, name: str) -> GenericResponse:
        """
        Drop an existing collection.

        Args:
            name: Name of the collection to drop

        Returns:
            GenericResponse indicating success or failure
        """
        data = self._request("DELETE", f"/api/collections/v1/{name}")
        return GenericResponse(**data)

    def rename_collection(self, old_name: str, new_name: str) -> GenericResponse:
        """
        Rename an existing collection.

        Args:
            old_name: Current name of the collection
            new_name: New name for the collection

        Returns:
            GenericResponse indicating success or failure
        """
        data = self._request("PUT", f"/api/collections/v1/{old_name}/rename/{new_name}")
        return GenericResponse(**data)

    def load_collection(self, name: str) -> GenericResponse:
        """
        Load a collection into memory.

        Args:
            name: Name of the collection to load

        Returns:
            GenericResponse indicating success or failure
        """
        data = self._request("POST", f"/api/collections/v1/{name}/load")
        return GenericResponse(**data)

    def unload_collection(self, name: str) -> GenericResponse:
        """
        Unload a collection from memory.

        Args:
            name: Name of the collection to unload

        Returns:
            GenericResponse indicating success or failure
        """
        data = self._request("POST", f"/api/collections/v1/{name}/unload")
        return GenericResponse(**data)

    def flush_collection(self, name: str) -> GenericResponse:
        """
        Flush a collection to disk.

        Args:
            name: Name of the collection to flush

        Returns:
            GenericResponse indicating success or failure
        """
        data = self._request("POST", f"/api/collections/v1/{name}/flush")
        return GenericResponse(**data)

    def reindex_collection(self, name: str) -> GenericResponse:
        """
        Re-index a collection for debug purposes.

        Args:
            name: Name of the collection to reindex

        Returns:
            GenericResponse indicating success or failure
        """
        data = self._request("PUT", f"/api/collections/v1/{name}/reindex")
        return GenericResponse(**data)

    def pq_train(self, collection_name: str) -> GenericResponse:
        """
        Perform Product Quantization training for an existing collection.

        Args:
            collection_name: Name of the collection to train PQ on

        Returns:
            GenericResponse indicating success or failure
        """
        data = self._request("POST", f"/api/collections/v1/{collection_name}/pq-train")
        return GenericResponse(**data)

    def delete_record(self, collection_name: str, record_id: str) -> GenericResponse:
        """
        Delete a record from a collection.

        Args:
            collection_name: Name of the collection
            record_id: ID of the record to delete

        Returns:
            GenericResponse indicating success or failure
        """
        data = self._request("DELETE", f"/api/collections/v1/{collection_name}/{record_id}")
        return GenericResponse(**data)

    def expiry_cleanup(self, collection_name: str) -> GenericResponse:
        """
        Perform expiry cleanup on a collection.

        Args:
            collection_name: Name of the collection

        Returns:
            GenericResponse indicating success or failure
        """
        data = self._request("POST", f"/api/collections/v1/{collection_name}/expiry-cleanup")
        return GenericResponse(**data)

    def export_collection(self, name: str) -> BinaryIO:
        """
        Export a collection and return a file stream.

        Args:
            name: Name of the collection to export

        Returns:
            Binary file stream that can be saved to disk

        Example:
            with client.export_collection("my-collection") as f:
                with open("export.bin", "wb") as out:
                    out.write(f.read())
        """
        return self._request_file_response("POST", f"/api/collections/v1/{name}/export")

    def import_collection(self, file_path: str) -> GenericResponse:
        """
        Import a collection from a file.

        Args:
            file_path: Path to the exported collection file

        Returns:
            GenericResponse indicating success or failure
        """
        data = self._upload_file("/api/collections/v1/import", file_path)
        return GenericResponse(**data)

    # Data Operations
    def insert_record(self, request: InsertRecordRequest) -> InsertRecordResponse:
        """
        Insert a new record into a collection.

        Args:
            request: InsertRecordRequest with record details

        Returns:
            InsertRecordResponse with inserted record details
        """
        json_data = {
            "collection": request.collection,
            "record": request.record,
        }
        if request.expiry is not None:
            json_data["expiry"] = request.expiry
        if request.id is not None:
            json_data["id"] = request.id
        if request.metadata_fields is not None:
            json_data["metadata_fields"] = request.metadata_fields
        if request.embedding_provider is not None:
            json_data["embedding_provider"] = request.embedding_provider
        if request.fields is not None:
            json_data["fields"] = request.fields
        if request.keyword_fields is not None:
            json_data["keyword_fields"] = request.keyword_fields
        if request.model is not None:
            json_data["model"] = request.model

        data = self._request("POST", "/api/collections/v1/record", json_data=json_data)
        return InsertRecordResponse(**data)

    def ingest_data(self, request: IngestRequest) -> IngestResponse:
        """
        Ingest data into a collection.

        Args:
            request: IngestRequest with ingestion details

        Returns:
            IngestResponse indicating success or failure
        """
        json_data = {
            "collection_name": request.collection_name,
        }
        # Source configuration
        if request.file_path is not None:
            json_data["file_path"] = request.file_path
        if request.source_type is not None:
            json_data["source_type"] = request.source_type
        
        # MongoDB source configuration
        if request.database_name is not None:
            json_data["database_name"] = request.database_name
        if request.mongo_collection is not None:
            json_data["mongo_collection"] = request.mongo_collection
        if request.query is not None:
            json_data["query"] = request.query
        if request.mongo_fetch_batch_size is not None:
            json_data["mongo_fetch_batch_size"] = request.mongo_fetch_batch_size
        
        # Common configuration
        if request.fields is not None:
            json_data["fields"] = request.fields
        if request.keyword_fields is not None:
            json_data["keyword_fields"] = request.keyword_fields
        if request.metadata_fields is not None:
            json_data["metadata_fields"] = request.metadata_fields
        if request.id_field is not None:
            json_data["id_field"] = request.id_field
        if request.expiry_field is not None:
            json_data["expiry_field"] = request.expiry_field
        if request.embedding_provider is not None:
            json_data["embedding_provider"] = request.embedding_provider
        if request.embedding_model is not None:
            json_data["embedding_model"] = request.embedding_model
        if request.ingestion_batch_size is not None:
            json_data["ingestion_batch_size"] = request.ingestion_batch_size

        data = self._request("POST", "/api/data/v1/ingest", json_data=json_data)
        return IngestResponse(**data)

    def search_data(self, request: SearchRequest) -> SearchResponse:
        """
        Search for data in a collection using POST request.

        Args:
            request: SearchRequest with search parameters

        Returns:
            SearchResponse with search results

        Raises:
            ValueError: If collection name is empty or both query and vector_query are empty
        """
        if not request.collection:
            raise ValueError("collection name cannot be empty")
        if not request.query and not request.vector_query:
            raise ValueError("both vector_query and query cannot be empty")

        json_data = {
            "collection": request.collection,
            "query": request.query,
        }
        if request.fields is not None:
            json_data["fields"] = request.fields
        if request.limit is not None:
            json_data["limit"] = request.limit
        if request.weights is not None:
            json_data["weights"] = request.weights
        if request.max_distance is not None:
            json_data["max_distance"] = request.max_distance
        if request.filters is not None:
            json_data["filters"] = request.filters.to_dict()
        if request.sort is not None:
            json_data["sort"] = request.sort.to_dict()
        if request.vector_query is not None:
            json_data["vector_query"] = request.vector_query

        data = self._request("POST", "/api/data/v1/search", json_data=json_data)
        return SearchResponse(**data)

    # Storage Operations
    def upload_data_file(self, file_path: str) -> GenericResponse:
        """
        Upload a data file to storage.

        Args:
            file_path: Path to the file to upload

        Returns:
            GenericResponse indicating success or failure
        """
        data = self._upload_file("/api/data/v1/storage/upload", file_path)
        return GenericResponse(**data)

    def list_storage(self, path: str = "", source: Optional[str] = None) -> ListStorageResponse:
        """
        List contents of a directory in uploads storage.
        If the source is mongodb, then empty path lists all DBs. If path is a DB, lists all collections in that DB.

        Args:
            path: Directory path (optional)
            source: Source type ("file" or "mongodb", optional)

        Returns:
            ListStorageResponse with storage items
        """
        params = {}
        if path:
            params["path"] = path
        if source:
            params["source"] = source
        
        data = self._request("GET", "/api/data/v1/storage/list", params=params)
        return ListStorageResponse(**data)

    def read_document(self, path: str, options: Optional[FileReaderOptions] = None) -> ReadDocumentResponse:
        """
        Read the first few rows of a CSV document or MongoDB collection.
        If the source is mongodb, then path is in the format "database/collection".
        options.mongo_filter can be used to filter the documents returned in case of mongodb.

        Args:
            path: Path to the document or "database/collection" for MongoDB
            options: FileReaderOptions with read parameters (optional)

        Returns:
            ReadDocumentResponse with document data

        Raises:
            ValueError: If path is empty or rows/skip are negative
        """
        if not path:
            raise ValueError("path cannot be empty")
        
        if options is None:
            options = FileReaderOptions()
        
        if options.limit < 0:
            raise ValueError("limit cannot be negative")
        if options.skip < 0:
            raise ValueError("skip cannot be negative")

        params = {"path": path}
        if options.source:
            params["source"] = options.source
        if options.limit > 0:
            params["rows"] = str(options.limit)
        if options.skip > 0:
            params["skip"] = str(options.skip)
        if options.source == "mongodb" and options.mongo_filter:
            import json
            params["mongo_filter"] = json.dumps(options.mongo_filter)

        data = self._request("GET", "/api/data/v1/storage/read", params=params)
        return ReadDocumentResponse(**data)
    
    def list_embedding_models(self) -> ListEmbeddingModelsResponse:
        """
        List all available embedding providers and their models.

        Returns:
            ListEmbeddingModelsResponse with embedding models
        """
        data = self._request("GET", "/api/data/v1/embedding/models")
        return ListEmbeddingModelsResponse(**data)

    def list_ingest_sources(self) -> ListIngestionSourcesResponse:
        """
        List all available ingestion sources.

        Returns:
            ListIngestionSourcesResponse with available ingestion sources
        """
        data = self._request("GET", "/api/data/v1/ingest/sources")
        return ListIngestionSourcesResponse(**data)

    def stream_ingest_stats(self, collection: str, callback: Callable[[str], None]) -> None:
        """
        Stream ingestion statistics via SSE.

        Args:
            collection: Collection name
            callback: Function to call for each event line

        Note:
            This is a blocking call that streams events until connection closes.
        """
        url = urljoin(self.base_url, f"/api/data/v1/ingest/stats?collection={collection}")
        response = self.session.get(url, stream=True, timeout=self.timeout)
        
        if response.status_code >= 400:
            raise requests.HTTPError(
                f"API error: {response.text} (status: {response.status_code})",
                response=response,
            )

        for line in response.iter_lines():
            if line:
                callback(line.decode('utf-8'))

    # Debug Operations
    def get_collection_distance(
        self, collection_name: str, field: str, node_id: int, text: str
    ) -> DebugDistanceResponse:
        """
        Get the distance of a node in a collection for debug purposes.

        Args:
            collection_name: Name of the collection
            field: Field name
            node_id: Node ID
            text: Text to calculate distance from

        Returns:
            DebugDistanceResponse with distance information
        """
        params = {"text": text}
        data = self._request(
            "GET",
            f"/api/collections/v1/debug/{collection_name}/{field}/distance/{node_id}",
            params=params,
        )
        return DebugDistanceResponse(**data)

    def get_collection_node_info(
        self, collection_name: str, field: str, node_id: int
    ) -> DebugNodeInfoResponse:
        """
        Get node info of a collection for debug purposes.

        Args:
            collection_name: Name of the collection
            field: Field name
            node_id: Node ID

        Returns:
            DebugNodeInfoResponse with node information
        """
        data = self._request(
            "GET",
            f"/api/collections/v1/debug/{collection_name}/{field}/nodes/{node_id}",
        )
        return DebugNodeInfoResponse(**data)

    def get_collection_node_neighbors_at_level(
        self,
        collection_name: str,
        field: str,
        node_id: int,
        level: int,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> DebugNodeInfoResponse:
        """
        Get node neighbors at a level of a collection for debug purposes.

        Args:
            collection_name: Name of the collection
            field: Field name
            node_id: Node ID
            level: Level in the graph
            limit: Maximum number of neighbors to return (optional)
            offset: Offset for pagination (optional)

        Returns:
            DebugNodeInfoResponse with neighbor information
        """
        params = {}
        if limit is not None:
            params["limit"] = str(limit)
        if offset is not None:
            params["offset"] = str(offset)

        data = self._request(
            "GET",
            f"/api/collections/v1/debug/{collection_name}/{field}/nodes/{node_id}/neighbors/{level}",
            params=params,
        )
        return DebugNodeInfoResponse(**data)

    def get_collection_levels(self, collection_name: str) -> DebugLevelsResponse:
        """
        Get levels of a collection for debug purposes.

        Args:
            collection_name: Name of the collection

        Returns:
            DebugLevelsResponse with level information
        """
        data = self._request("GET", f"/api/collections/v1/debug/{collection_name}/levels")
        return DebugLevelsResponse(**data)

    def get_collection_nodes_at_level(
        self, collection_name: str, level: int
    ) -> DebugNodesAtLevelResponse:
        """
        Get nodes at a level of a collection for debug purposes.

        Args:
            collection_name: Name of the collection
            level: Level in the graph

        Returns:
            DebugNodesAtLevelResponse with nodes at the level
        """
        data = self._request(
            "GET",
            f"/api/collections/v1/debug/{collection_name}/levels/{level}",
        )
        return DebugNodesAtLevelResponse(**data)

    def get_collection_node_by_reference_node_id(
        self, collection_name: str, node_id: int
    ) -> DebugReferenceNodeResponse:
        """
        Get node by reference node ID of a collection for debug purposes.

        Args:
            collection_name: Name of the collection
            node_id: Reference node ID

        Returns:
            DebugReferenceNodeResponse with reference node information
        """
        data = self._request(
            "GET",
            f"/api/collections/v1/debug/{collection_name}/nodes/reference_node/{node_id}",
        )
        return DebugReferenceNodeResponse(**data)

    # Oplog Operations
    def get_oplog_entries(
        self, collection: str, after_lsn: int, limit: int = 0
    ) -> GetOplogResponse:
        """
        Retrieve oplog entries after a specific LSN for replica synchronization.

        Args:
            collection: Collection name (empty string for all collections)
            after_lsn: LSN after which to retrieve oplog entries
            limit: Maximum number of oplog entries to retrieve (optional)

        Returns:
            GetOplogResponse with oplog entries
        """
        params = {"after_lsn": str(after_lsn)}
        if collection:
            params["collection"] = collection
        if limit > 0:
            params["limit"] = str(limit)

        data = self._request("GET", "/api/oplog/v1/", params=params)
        return GetOplogResponse(**data)

    def update_replica_lsn(
        self, collection: str, replica_id: str, lsn: int
    ) -> UpdateReplicaLSNResponse:
        """
        Update the last applied LSN for a replica (heartbeat).

        Args:
            collection: Collection name
            replica_id: Replica identifier
            lsn: Last applied LSN

        Returns:
            UpdateReplicaLSNResponse indicating success or failure
        """
        json_data = {
            "collection": collection,
            "replica_id": replica_id,
            "lsn": lsn,
        }
        data = self._request("POST", "/api/oplog/v1/heartbeat", json_data=json_data)
        return UpdateReplicaLSNResponse(**data)

    def register_replica(self, replica_id: str) -> GenericResponse:
        """
        Register a replica for oplog retention tracking.

        Args:
            replica_id: Replica identifier

        Returns:
            GenericResponse indicating success or failure
        """
        json_data = {"replica_id": replica_id}
        data = self._request("POST", "/api/oplog/v1/register", json_data=json_data)
        return GenericResponse(**data)

    def unregister_replica(self, replica_id: str) -> GenericResponse:
        """
        Unregister a replica for oplog retention tracking.

        Args:
            replica_id: Replica identifier

        Returns:
            GenericResponse indicating success or failure
        """
        json_data = {"replica_id": replica_id}
        data = self._request("POST", "/api/oplog/v1/unregister", json_data=json_data)
        return GenericResponse(**data)

    def get_oplog_status(self, collection: str) -> OplogStatusResponse:
        """
        Retrieve current oplog status and statistics for a collection.

        Args:
            collection: Collection name

        Returns:
            OplogStatusResponse with oplog status
        """
        params = {"collection": collection}
        data = self._request("GET", "/api/oplog/v1/status", params=params)
        return OplogStatusResponse(**data)
