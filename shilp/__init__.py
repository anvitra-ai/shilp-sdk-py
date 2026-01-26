"""Shilp Python SDK - Official Python SDK for the Shilp Vector Database API."""

from shilp.client import Client
from shilp.discovery_client import DiscoveryClient
from shilp.models import (
    # Request models
    AddCollectionRequest,
    InsertRecordRequest,
    IngestRequest,
    SearchRequest,
    UpdateReplicaLSNRequest,
    RegisterReplicaRequest,
    UnRegisterReplicaRequest,
    FileReaderOptions,
    # Response models
    GenericResponse,
    HealthResponse,
    ListCollectionsResponse,
    Collection,
    MetadataSupportInfo,
    InsertRecordResponse,
    IngestResponse,
    ListIngestionSourcesResponse,
    SearchResponse,
    ListStorageResponse,
    ReadDocumentResponse,
    ListEmbeddingModelsResponse,
    OplogStatusResponse,
    GetOplogResponse,
    UpdateReplicaLSNResponse,
    # Debug models
    DebugDistanceResponse,
    DebugNodeInfoResponse,
    DebugLevelsResponse,
    DebugNodesAtLevelResponse,
    DebugReferenceNodeResponse,
    # Enums and types
    AttrType,
    FilterOp,
    SortOrder,
    StorageBackendType,
    IngestSourceType,
    OpType,
    SyncStatus,
    ReplicaType,
    # Filter and Sort expressions
    FilterExpression,
    CompoundFilter,
    SortExpression,
    CompoundSort,
    # Discovery and Replica models
    Replica,
    Status,
    ProxyStats,
    DiscoveryStats,
)

__version__ = "0.1.0"
__all__ = [
    "Client",
    "DiscoveryClient",
    # Request models
    "AddCollectionRequest",
    "InsertRecordRequest",
    "IngestRequest",
    "SearchRequest",
    "UpdateReplicaLSNRequest",
    "RegisterReplicaRequest",
    "UnRegisterReplicaRequest",
    "FileReaderOptions",
    # Response models
    "GenericResponse",
    "HealthResponse",
    "ListCollectionsResponse",
    "Collection",
    "MetadataSupportInfo",
    "InsertRecordResponse",
    "IngestResponse",
    "ListIngestionSourcesResponse",
    "SearchResponse",
    "ListStorageResponse",
    "ReadDocumentResponse",
    "ListEmbeddingModelsResponse",
    "OplogStatusResponse",
    "GetOplogResponse",
    "UpdateReplicaLSNResponse",
    # Debug models
    "DebugDistanceResponse",
    "DebugNodeInfoResponse",
    "DebugLevelsResponse",
    "DebugNodesAtLevelResponse",
    "DebugReferenceNodeResponse",
    # Enums and types
    "AttrType",
    "FilterOp",
    "SortOrder",
    "StorageBackendType",
    "IngestSourceType",
    "OpType",
    "SyncStatus",
    "ReplicaType",
    # Filter and Sort expressions
    "FilterExpression",
    "CompoundFilter",
    "SortExpression",
    "CompoundSort",
    # Discovery and Replica models
    "Replica",
    "Status",
    "ProxyStats",
    "DiscoveryStats",
]
