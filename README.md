# Shilp Python SDK

Official Python SDK for the Shilp Vector Database API.

## Installation

```bash
pip install shilp-sdk
```

Or install from source:

```bash
git clone https://github.com/anvitra-ai/shilp-sdk-py.git
cd shilp-sdk-py
pip install -e .
```

## Usage

```python
from shilp import Client, AddCollectionRequest, InsertRecordRequest, SearchRequest

# Initialize the client
client = Client("http://localhost:3000")

# Check health
health = client.health_check()
print(f"Health: {health.success}, Version: {health.version}")

# List collections
collections = client.list_collections()
print(f"Collections: {[c.name for c in collections.data]}")

# Drop collection if exists
try:
    client.drop_collection("my-collection")
except:
    pass

# Create a new collection
client.add_collection(
    AddCollectionRequest(
        name="my-collection",
        storage_type=StorageBackendType.FILE,
        reference_storage_type=StorageBackendType.FILE
    )
)

# Insert a record
client.insert_record(InsertRecordRequest(
    collection="my-collection",
    id="record-1",
    record={
        "title": "Hello World",
        "content": "This my test description"
    },
    fields=["title", "content"],
))

# Flush collection (important after inserting records)
client.flush_collection("my-collection")

# Search
results = client.search_data(SearchRequest(
    collection="my-collection",
    query="Hello",
    fields=["title"],
    limit=10,
))
print(f"Search results: {results.data}")

# Advanced search with max distance filter
results = client.search_data(SearchRequest(
    collection="my-collection",
    query="Hello",
    fields=["title"],
    limit=10,
    max_distance=0.5,
))
print(f"Advanced search results: {results.data}")

# Clean up
client.drop_collection("my-collection")
```

## Features

- **Collection Management**: List, add, drop, rename, load, unload, flush, reindex
- **Data Ingestion & Search**: Insert records, ingest data, search with keyword fields support
- **Record Management**: Insert, delete, expiry cleanup
- **Debug Collection Operations**: Distance, node info, levels, neighbors
- **Oplog Operations**: Replica registration, heartbeat, get entries, status
- **Storage Listing**: List and read storage files
- **Health Check**: Monitor API health and version

### Debug Operations

The SDK provides debug endpoints for inspecting collection internals:

```python
# Re-index a collection
client.reindex_collection("my-collection")

# Get collection levels
levels = client.get_collection_levels("my-collection")

# Get nodes at a specific level
nodes = client.get_collection_nodes_at_level("my-collection", 0)

# Get node information
node_info = client.get_collection_node_info("my-collection", "title", 123)

# Get node neighbors at a level
neighbors = client.get_collection_node_neighbors_at_level(
    "my-collection", "title", 123, 0, limit=10, offset=0
)

# Get distance calculation
distance = client.get_collection_distance("my-collection", "title", 123, "some text")

# Get node by reference ID
ref_node = client.get_collection_node_by_reference_node_id("my-collection", 456)
```

### Oplog Operations

The SDK provides oplog (operation log) endpoints for replica synchronization:

```python
# Register a replica for oplog tracking
register_resp = client.register_replica("replica-1")
print(f"Registered replica: {register_resp.success}")

# Get oplog status for a collection
status = client.get_oplog_status("my-collection")
print(f"Oplog status - Last LSN: {status.last_lsn}, "
      f"Retention LSN: {status.retention_lsn}, "
      f"Replicas: {status.replica_count}")

# Get oplog entries after a specific LSN
entries = client.get_oplog_entries("my-collection", after_lsn=1000, limit=100)
print(f"Retrieved {entries.count} oplog entries, last LSN: {entries.last_lsn}")

# Get oplog entries for all collections
all_entries = client.get_oplog_entries("", after_lsn=1000, limit=100)

# Update replica LSN (heartbeat)
update_resp = client.update_replica_lsn("my-collection", "replica-1", 1050)
print(f"Updated replica LSN: {update_resp.success}")

# Unregister replica
client.unregister_replica("replica-1")
```

### Filtering and Sorting

The SDK supports advanced filtering and sorting:

```python
from shilp import FilterExpression, CompoundFilter, SortExpression, CompoundSort, FilterOp, SortOrder, AttrType

# Create filters
filters = CompoundFilter(and_filters=[
    FilterExpression(attribute="age", op=FilterOp.GREATER_THAN, value=25),
    FilterExpression(attribute="status", op=FilterOp.EQUALS, value="active"),
])

# Create sort criteria
sort = CompoundSort(sorts=[
    SortExpression(attribute="created_at", order=SortOrder.DESCENDING),
])

# Search with filters and sorting
results = client.search_data(SearchRequest(
    collection="my-collection",
    query="search term",
    fields=["content"],
    limit=20,
    filters=filters,
    sort=sort,
))
```

### Export and Import Collections

```python
# Export a collection
with client.export_collection("my-collection") as f:
    with open("my-collection-export.bin", "wb") as out:
        out.write(f.read())

# Import a collection
client.import_collection("my-collection-export.bin")
```

### Embedding Models

```python
# List available embedding models
models = client.list_embedding_models()
for provider in models.data:
    print(f"Provider: {provider.name} (default: {provider.is_default})")
    for model in provider.models:
        print(f"  - {model.name} (default: {model.is_default})")
```

## API Reference

### Client

#### `Client(base_url: str, timeout: int = 30, session: Optional[requests.Session] = None)`

Initialize the Shilp API client.

**Parameters:**

- `base_url`: Base URL of the Shilp server (e.g., "http://localhost:3000")
- `timeout`: Request timeout in seconds (default: 30)
- `session`: Optional custom requests.Session instance

### Collection Management Methods

- `list_collections() -> ListCollectionsResponse`
- `add_collection(request: AddCollectionRequest) -> GenericResponse`
- `drop_collection(name: str) -> GenericResponse`
- `rename_collection(old_name: str, new_name: str) -> GenericResponse`
- `load_collection(name: str) -> GenericResponse`
- `unload_collection(name: str) -> GenericResponse`
- `flush_collection(name: str) -> GenericResponse`
- `reindex_collection(name: str) -> GenericResponse`
- `export_collection(name: str) -> BinaryIO`
- `import_collection(file_path: str) -> GenericResponse`

### Data Operations Methods

- `insert_record(request: InsertRecordRequest) -> InsertRecordResponse`
- `delete_record(collection_name: str, record_id: str) -> GenericResponse`
- `expiry_cleanup(collection_name: str) -> GenericResponse`
- `ingest_data(request: IngestRequest) -> IngestResponse`
- `search_data(request: SearchRequest) -> SearchResponse`

### Storage Methods

- `list_storage(path: str = "") -> ListStorageResponse`
- `read_document(path: str, rows: int = 0, skip: int = 0) -> ReadDocumentResponse`
- `list_embedding_models() -> ListEmbeddingModelsResponse`

### Debug Methods

- `get_collection_distance(collection_name: str, field: str, node_id: int, text: str) -> DebugDistanceResponse`
- `get_collection_node_info(collection_name: str, field: str, node_id: int) -> DebugNodeInfoResponse`
- `get_collection_node_neighbors_at_level(...) -> DebugNodeInfoResponse`
- `get_collection_levels(collection_name: str) -> DebugLevelsResponse`
- `get_collection_nodes_at_level(collection_name: str, level: int) -> DebugNodesAtLevelResponse`
- `get_collection_node_by_reference_node_id(collection_name: str, node_id: int) -> DebugReferenceNodeResponse`

### Oplog Methods

- `get_oplog_entries(collection: str, after_lsn: int, limit: int = 0) -> GetOplogResponse`
- `update_replica_lsn(collection: str, replica_id: str, lsn: int) -> UpdateReplicaLSNResponse`
- `register_replica(replica_id: str) -> GenericResponse`
- `unregister_replica(replica_id: str) -> GenericResponse`
- `get_oplog_status(collection: str) -> OplogStatusResponse`

### Health Check

- `health_check() -> HealthResponse`

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black shilp/

# Type checking
mypy shilp/
```

## License

MIT License - see LICENSE file for details.

## Related Projects

- [shilp-sdk-go](https://github.com/anvitra-ai/shilp-sdk-go) - Official Go SDK for Shilp
