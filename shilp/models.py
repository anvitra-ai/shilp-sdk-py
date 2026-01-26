"""Data models for Shilp SDK."""

from enum import IntEnum
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field


class AttrType(IntEnum):
    """Type of a metadata attribute."""
    INT64 = 0
    FLOAT64 = 1
    STRING = 2
    BOOL = 3


class FilterOp(IntEnum):
    """Filter operation types."""
    EQUALS = 0
    NOT_EQUALS = 1
    GREATER_THAN = 2
    GREATER_THAN_OR_EQUAL = 3
    LESS_THAN = 4
    LESS_THAN_OR_EQUAL = 5
    IN = 6
    NOT_IN = 7


class SortOrder(IntEnum):
    """Sort direction."""
    ASCENDING = 0
    DESCENDING = 1


class StorageBackendType(IntEnum):
    """Type of storage backend for persistence."""
    DOES_NOT_EXIST = -1
    FILE = 1
    S3 = 2


class IngestSourceType:
    """Type of ingestion source."""
    FILE = "file"
    MONGODB = "mongodb"


class OpType:
    """Operation type in the oplog."""
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    DROP_COLLECTION = "drop_collection"
    RENAME_COLLECTION = "rename_collection"


@dataclass
class GenericResponse:
    """Standard response structure."""
    success: bool
    message: str


@dataclass
class MetadataColumnSchema:
    """Metadata column schema."""
    name: str
    type: AttrType


@dataclass
class Collection:
    """Represents a collection in the database."""
    name: str
    is_loaded: bool
    fields: List[str]
    searchable_fields: List[str]
    metadata: Optional[List[MetadataColumnSchema]] = None
    has_metadata_enabled: bool = False
    no_reference_storage: bool = False
    storage_type: StorageBackendType = StorageBackendType.FILE
    reference_storage_type: StorageBackendType = StorageBackendType.FILE


@dataclass
class MetadataSupportInfo:
    """Metadata support information."""
    support_metadata: bool
    name: str
    type: StorageBackendType
    is_default: bool


@dataclass
class ListCollectionsResponse:
    """Response for listing collections."""
    success: bool
    message: str
    data: List[Collection]
    metadata_info: Optional[List[MetadataSupportInfo]] = None


@dataclass
class AddCollectionRequest:
    """Request to add a new collection."""
    name: str
    no_reference_storage: bool = False
    has_metadata_storage: bool = False
    storage_type: Optional[StorageBackendType] = None
    reference_storage_type: Optional[StorageBackendType] = None


@dataclass
class RecordData:
    """Record data in the response."""
    id: str
    expiry: int
    fields: Dict[str, Any]
    keyword_fields: Optional[Dict[str, bool]] = None
    metadata_fields: Optional[Dict[str, int]] = None


@dataclass
class InsertRecordRequest:
    """Request to insert a record."""
    collection: str
    record: Dict[str, Any]
    expiry: Optional[int] = None
    id: Optional[str] = None
    metadata_fields: Optional[Dict[str, AttrType]] = None
    embedding_provider: Optional[str] = None
    fields: Optional[List[str]] = None
    keyword_fields: Optional[List[str]] = None
    model: Optional[str] = None


@dataclass
class InsertRecordResponse:
    """Response for inserting a record."""
    success: bool
    message: str
    record: Optional[RecordData] = None
    remaining_records: Optional[int] = None


@dataclass
class IngestRequest:
    """Request to ingest data."""
    # Source configuration - use either file_path OR MongoDB settings
    # file_path has the path to the file to be ingested or 'database/collection' for MongoDB
    file_path: Optional[str] = None
    source_type: Optional[str] = None  # "file" or "mongodb"
    
    # MongoDB source configuration
    database_name: Optional[str] = None
    mongo_collection: Optional[str] = None
    query: Optional[Dict[str, Any]] = None
    mongo_fetch_batch_size: Optional[int] = None
    
    # Common configuration
    collection_name: str = ""
    fields: Optional[List[str]] = None
    keyword_fields: Optional[List[str]] = None
    metadata_fields: Optional[Dict[str, AttrType]] = None
    id_field: Optional[str] = None
    expiry_field: Optional[str] = None
    embedding_provider: Optional[str] = None
    embedding_model: Optional[str] = None
    ingestion_batch_size: Optional[int] = None


@dataclass
class IngestResponse:
    """Response for data ingestion."""
    success: bool
    message: str
    details: Optional[List[str]] = None


@dataclass
class FileReaderOptions:
    """Options for reading files."""
    source: Optional[str] = None  # IngestSourceType
    mongo_filter: Optional[Dict[str, Any]] = None
    skip: int = 0
    limit: int = 0


@dataclass
class ListIngestionSourcesResponse:
    """Response for listing ingestion sources."""
    message: str
    success: bool
    data: Optional[List[str]] = None


@dataclass
class FilterExpression:
    """Single filter condition."""
    attribute: str
    op: FilterOp
    value: Optional[Any] = None
    values: Optional[List[Any]] = None

    def validate(self) -> None:
        """Validate the filter expression."""
        if not self.attribute:
            raise ValueError("attribute name cannot be empty")
        
        if self.op in (FilterOp.IN, FilterOp.NOT_IN):
            if not self.values or len(self.values) == 0:
                raise ValueError("IN/NOT IN operations require at least one value")
        else:
            if self.value is None:
                raise ValueError(f"value cannot be None for operation {self.op}")


@dataclass
class CompoundFilter:
    """Combination of filter expressions."""
    and_filters: Optional[List[FilterExpression]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {}
        if self.and_filters:
            result["and"] = [
                {
                    "attribute": f.attribute,
                    "op": f.op,
                    "value": f.value,
                    "values": f.values
                }
                for f in self.and_filters
            ]
        return result


@dataclass
class SortExpression:
    """Sort criterion."""
    attribute: str
    order: SortOrder

    def validate(self) -> None:
        """Validate the sort expression."""
        if not self.attribute:
            raise ValueError("sort attribute cannot be empty")
        if self.order not in (SortOrder.ASCENDING, SortOrder.DESCENDING):
            raise ValueError(f"invalid sort order: {self.order}")


@dataclass
class CompoundSort:
    """Combination of sort expressions."""
    sorts: Optional[List[SortExpression]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {}
        if self.sorts:
            result["sorts"] = [
                {"attribute": s.attribute, "order": s.order}
                for s in self.sorts
            ]
        return result


@dataclass
class SearchRequest:
    """Request body for POST search."""
    collection: str
    query: str
    fields: Optional[List[str]] = None
    limit: Optional[int] = None
    weights: Optional[Dict[str, float]] = None
    max_distance: Optional[float] = None
    filters: Optional[CompoundFilter] = None
    sort: Optional[CompoundSort] = None


@dataclass
class SearchResponse:
    """Response for searching data."""
    success: bool
    data: List[Dict[str, Any]]
    
    message: Optional[str] = None


@dataclass
class StorageItem:
    """Item in the storage list."""
    name: str
    is_dir: bool


@dataclass
class ListStorageResponse:
    """Response for listing storage."""
    success: bool
    message: str
    data: Dict[str, List[StorageItem]]


@dataclass
class ReadDocumentResponse:
    """Response for reading document contents."""
    success: bool
    message: str
    data: List[Dict[str, str]]


@dataclass
class HealthResponse:
    """Response for health check."""
    success: bool
    version: str


@dataclass
class DebugDistanceResponse:
    """Response for debug distance endpoint."""
    success: bool
    message: str
    data: Dict[str, Any]


@dataclass
class DebugNeighbor:
    """Neighbor node in the graph."""
    node_id: int
    vector_id: str
    field: str
    distance: float
    metadata: Dict[str, Any]


@dataclass
class DebugNodeInfo:
    """Detailed information about a node."""
    node_id: int
    vector_id: str
    field: str
    level: int
    metadata: Dict[str, Any]
    neighbors: List[DebugNeighbor]


@dataclass
class DebugNodeInfoResponse:
    """Response for debug node info endpoint."""
    success: bool
    message: str
    data: Optional[DebugNodeInfo] = None


@dataclass
class DebugLevelInfo:
    """Level information."""
    level: int
    node_count: int


@dataclass
class DebugLevelsResponse:
    """Response for debug levels endpoint."""
    success: bool
    message: str
    data: Dict[str, List[DebugLevelInfo]]


@dataclass
class DebugNodesAtLevelResponse:
    """Response for debug nodes at level endpoint."""
    success: bool
    message: str
    data: Dict[str, List[int]]


@dataclass
class DebugVectorNode:
    """Vector node in the reference node response."""
    id: int
    field: str
    vector: List[float]


@dataclass
class DebugReferenceNode:
    """Reference node with its metadata and vector nodes."""
    id: str
    metadata: Dict[str, Any]
    nodes: List[DebugVectorNode]


@dataclass
class DebugReferenceNodeResponse:
    """Response for debug reference node endpoint."""
    success: bool
    message: str
    data: Optional[DebugReferenceNode] = None


@dataclass
class EmbeddingModel:
    """Embedding model."""
    name: str
    is_default: bool


@dataclass
class EmbeddingProvider:
    """Embedding provider with its models."""
    name: str
    is_default: bool
    models: List[EmbeddingModel]


@dataclass
class ListEmbeddingModelsResponse:
    """Response for listing embedding models."""
    success: bool
    message: str
    data: List[EmbeddingProvider]
    supports_distributed_embedding: bool = False


@dataclass
class OplogStatusResponse:
    """Oplog status response."""
    success: bool
    message: str
    last_lsn: int
    retention_lsn: int
    replica_count: int


@dataclass
class UpdateReplicaLSNRequest:
    """Replica LSN update request."""
    collection: str
    replica_id: str
    lsn: int


@dataclass
class UpdateReplicaLSNResponse:
    """Update response."""
    success: bool
    message: str


@dataclass
class RegisterReplicaRequest:
    """Replica registration request."""
    replica_id: str


@dataclass
class UnRegisterReplicaRequest:
    """Replica unregistration request."""
    replica_id: str


@dataclass
class Record:
    """Record structure."""
    id: str
    fields: Dict[str, Any]
    keyword_fields: Optional[Dict[str, bool]] = None
    metadata_fields: Optional[Dict[str, AttrType]] = None
    vectors: Optional[Dict[str, List[float]]] = None
    dist: Optional[float] = None
    nodes: Optional[List[str]] = None
    expiry: Optional[int] = None


@dataclass
class OplogEntry:
    """Single entry in the operation log."""
    lsn: int
    timestamp: datetime
    collection: str
    doc_id: str
    op_type: str
    vector: Optional[List[float]] = None
    metadata: Optional[Dict[str, Any]] = None
    keywords: Optional[List[str]] = None
    full_doc: Optional[Record] = None
    vectors: Optional[Dict[str, List[float]]] = None
    fields: Optional[Dict[str, Any]] = None
    keyword_fields: Optional[Dict[str, bool]] = None
    metadata_fields: Optional[Dict[str, AttrType]] = None
    expiry: Optional[int] = None
    new_name: Optional[str] = None


@dataclass
class GetOplogResponse:
    """Oplog response."""
    success: bool
    message: str
    entries: List[OplogEntry]
    last_lsn: int
    count: int


class SyncStatus:
    """Sync status for replicas."""
    READY = "ready"
    SYNCING = "syncing"


class ReplicaType(IntEnum):
    """Type of replica."""
    READ_REPLICA = 0
    WRITE_REPLICA = 1
    SINGLE_NODE = 2


@dataclass
class Replica:
    """Replica information."""
    id: str
    address: str
    is_healthy: bool
    is_syncing: bool  # Traffic gate - if true, no traffic sent


@dataclass
class Status:
    """Overall status of the registry."""
    write_replica: Replica
    read_replicas: List[Replica]
    available: int
    total: int


@dataclass
class ProxyStats:
    """Proxy statistics."""
    active_proxies: int
    targets: List[str]


@dataclass
class DiscoveryStats:
    """Discovery statistics."""
    registry: Status
    proxy: ProxyStats


@dataclass
class UpdateSyncStatusRequest:
    """Request to update sync status."""
    account_id: str
    address: str
    status: str  # SyncStatus


@dataclass
class RegisterToDiscoveryRequest:
    """Request to register to discovery service."""
    account_id: str
    address: str
    id: str
    is_read: bool
    is_write: bool
