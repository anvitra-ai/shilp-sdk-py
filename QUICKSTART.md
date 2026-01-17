# Shilp Python SDK - Quick Reference

## Installation

```bash
pip install shilp-sdk
```

## Basic Usage

```python
from shilp import Client, AddCollectionRequest, InsertRecordRequest, SearchRequest

# Initialize client
client = Client("http://localhost:3000")

# Health check
health = client.health_check()

# Create collection
client.add_collection(AddCollectionRequest(name="my-collection"))

# Insert record
client.insert_record(InsertRecordRequest(
    collection="my-collection",
    id="doc-1",
    record={"title": "Example", "vector": [0.1, 0.2, 0.3]}
))

# Flush collection
client.flush_collection("my-collection")

# Search
results = client.search_data(SearchRequest(
    collection="my-collection",
    query="search term",
    fields=["title"],
    limit=10
))

# Clean up
client.drop_collection("my-collection")
```

## Collection Management

| Method | Description |
|--------|-------------|
| `list_collections()` | List all collections |
| `add_collection(request)` | Create a new collection |
| `drop_collection(name)` | Delete a collection |
| `rename_collection(old, new)` | Rename a collection |
| `load_collection(name)` | Load collection into memory |
| `unload_collection(name)` | Unload collection from memory |
| `flush_collection(name)` | Flush collection to disk |
| `reindex_collection(name)` | Re-index a collection |
| `export_collection(name)` | Export collection to file stream |
| `import_collection(path)` | Import collection from file |

## Data Operations

| Method | Description |
|--------|-------------|
| `insert_record(request)` | Insert a single record |
| `delete_record(collection, id)` | Delete a record by ID |
| `ingest_data(request)` | Batch ingest from file |
| `search_data(request)` | Search for records |
| `expiry_cleanup(collection)` | Remove expired records |

## Storage Operations

| Method | Description |
|--------|-------------|
| `list_storage(path)` | List files in storage |
| `read_document(path, rows, skip)` | Read CSV document |
| `list_embedding_models()` | List available embedding models |
| `stream_ingest_stats(collection, callback)` | Stream ingestion stats via SSE |

## Debug Operations

| Method | Description |
|--------|-------------|
| `get_collection_levels(collection)` | Get graph levels |
| `get_collection_nodes_at_level(collection, level)` | Get nodes at level |
| `get_collection_node_info(collection, field, node_id)` | Get node details |
| `get_collection_node_neighbors_at_level(...)` | Get node neighbors |
| `get_collection_distance(collection, field, node_id, text)` | Calculate distance |
| `get_collection_node_by_reference_node_id(...)` | Get node by reference ID |

## Oplog Operations

| Method | Description |
|--------|-------------|
| `register_replica(replica_id)` | Register a replica |
| `unregister_replica(replica_id)` | Unregister a replica |
| `get_oplog_entries(collection, after_lsn, limit)` | Get oplog entries |
| `get_oplog_status(collection)` | Get oplog status |
| `update_replica_lsn(collection, replica_id, lsn)` | Update replica LSN (heartbeat) |

## Data Models

### Enums

```python
from shilp import AttrType, FilterOp, SortOrder

# Attribute types for metadata
AttrType.INT64, AttrType.FLOAT64, AttrType.STRING, AttrType.BOOL

# Filter operations
FilterOp.EQUALS, FilterOp.NOT_EQUALS, FilterOp.GREATER_THAN, 
FilterOp.LESS_THAN, FilterOp.IN, FilterOp.NOT_IN

# Sort orders
SortOrder.ASCENDING, SortOrder.DESCENDING
```

### Filtering

```python
from shilp import FilterExpression, CompoundFilter, FilterOp

filters = CompoundFilter(and_filters=[
    FilterExpression(attribute="age", op=FilterOp.GREATER_THAN, value=25),
    FilterExpression(attribute="status", op=FilterOp.EQUALS, value="active"),
])

results = client.search_data(SearchRequest(
    collection="my-collection",
    query="search term",
    filters=filters,
))
```

### Sorting

```python
from shilp import SortExpression, CompoundSort, SortOrder

sort = CompoundSort(sorts=[
    SortExpression(attribute="created_at", order=SortOrder.DESCENDING),
    SortExpression(attribute="name", order=SortOrder.ASCENDING),
])

results = client.search_data(SearchRequest(
    collection="my-collection",
    query="search term",
    sort=sort,
))
```

### Metadata Fields

```python
from shilp import InsertRecordRequest, AttrType

client.insert_record(InsertRecordRequest(
    collection="my-collection",
    id="doc-1",
    record={
        "title": "Example Document",
        "vector": [0.1, 0.2, 0.3],
    },
    metadata_fields={
        "category": AttrType.STRING,
        "rating": AttrType.FLOAT64,
        "views": AttrType.INT64,
        "published": AttrType.BOOL,
    }
))
```

## Error Handling

```python
import requests

try:
    client.add_collection(AddCollectionRequest(name="test"))
except requests.HTTPError as e:
    print(f"API error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Configuration

```python
import requests

# Custom timeout
client = Client("http://localhost:3000", timeout=60)

# Custom session (for advanced use cases like connection pooling)
session = requests.Session()
session.headers.update({"User-Agent": "MyApp/1.0"})
client = Client("http://localhost:3000", session=session)
```

## Examples

See the `examples/` directory for complete working examples:
- `basic_usage.py` - Basic operations
- `advanced_usage.py` - Advanced features including filtering, sorting, metadata, oplog, etc.

## Testing

```bash
# Install test dependencies
pip install pytest

# Run tests
pytest

# Run with coverage
pytest --cov=shilp
```

## More Information

- Full documentation: [README.md](README.md)
- Go SDK (reference implementation): https://github.com/anvitra-ai/shilp-sdk-go
- Issues: https://github.com/anvitra-ai/shilp-sdk-py/issues
