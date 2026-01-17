"""Shilp Python SDK - Official Python SDK for the Shilp Vector Database API."""

from shilp.client import Client
from shilp.models import (
    # Request models
    AddCollectionRequest,
    InsertRecordRequest,
    IngestRequest,
    SearchRequest,
    UpdateReplicaLSNRequest,
    RegisterReplicaRequest,
    UnRegisterReplicaRequest,
    # Response models
    GenericResponse,
    HealthResponse,
    ListCollectionsResponse,
    Collection,
    InsertRecordResponse,
    IngestResponse,
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
    OpType,
    # Filter and Sort expressions
    FilterExpression,
    CompoundFilter,
    SortExpression,
    CompoundSort,
)

__version__ = "0.1.0"
__all__ = [
    "Client",
    # Request models
    "AddCollectionRequest",
    "InsertRecordRequest",
    "IngestRequest",
    "SearchRequest",
    "UpdateReplicaLSNRequest",
    "RegisterReplicaRequest",
    "UnRegisterReplicaRequest",
    # Response models
    "GenericResponse",
    "HealthResponse",
    "ListCollectionsResponse",
    "Collection",
    "InsertRecordResponse",
    "IngestResponse",
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
    "OpType",
    # Filter and Sort expressions
    "FilterExpression",
    "CompoundFilter",
    "SortExpression",
    "CompoundSort",
]
