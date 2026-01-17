"""
Advanced example demonstrating all features of Shilp Python SDK.

This example shows:
- Collection management
- Data ingestion and search
- Filtering and sorting
- Debug operations
- Oplog operations
- Export/import
"""

from shilp import (
    Client,
    AddCollectionRequest,
    InsertRecordRequest,
    SearchRequest,
    FilterExpression,
    CompoundFilter,
    SortExpression,
    CompoundSort,
    FilterOp,
    SortOrder,
    AttrType,
)


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def main():
    # Initialize client
    client = Client("http://localhost:3000")
    
    print_section("Health Check")
    health = client.health_check()
    print(f"Server Status: {health.success}")
    print(f"Version: {health.version}")

    print_section("Collection Management")
    
    # List collections
    collections = client.list_collections()
    print(f"Total collections: {len(collections.data)}")
    
    # Create a test collection
    collection_name = "advanced-example"
    try:
        client.drop_collection(collection_name)
    except:
        pass
    
    client.add_collection(AddCollectionRequest(
        name=collection_name,
        has_metadata_storage=True
    ))
    print(f"✓ Created collection: {collection_name}")

    print_section("Inserting Records with Metadata")
    
    # Insert records with metadata fields
    records = [
        {
            "id": "tech-1",
            "title": "AI Revolution",
            "content": "Artificial intelligence is transforming industries",
            "category": "technology",
            "rating": 4.5,
            "views": 1000,
            "published": True,
        },
        {
            "id": "tech-2",
            "title": "Cloud Computing",
            "content": "Cloud platforms enable scalable applications",
            "category": "technology",
            "rating": 4.0,
            "views": 750,
            "published": True,
        },
        {
            "id": "sci-1",
            "title": "Space Exploration",
            "content": "New discoveries in deep space",
            "category": "science",
            "rating": 5.0,
            "views": 2000,
            "published": True,
        },
    ]

    for rec in records:
        client.insert_record(InsertRecordRequest(
            collection=collection_name,
            id=rec["id"],
            record={
                "title": rec["title"],
                "content": rec["content"],
                "vector": [0.1, 0.2, 0.3, 0.4, 0.5],  # Example vector
            },
            metadata_fields={
                "category": AttrType.STRING,
                "rating": AttrType.FLOAT64,
                "views": AttrType.INT64,
                "published": AttrType.BOOL,
            }
        ))
        print(f"  ✓ Inserted: {rec['id']}")

    # Flush to persist
    client.flush_collection(collection_name)
    print("\n✓ Collection flushed")

    print_section("Basic Search")
    
    results = client.search_data(SearchRequest(
        collection=collection_name,
        query="artificial intelligence",
        fields=["title", "content"],
        limit=5
    ))
    print(f"Found {len(results.data)} results")
    for i, result in enumerate(results.data, 1):
        print(f"  {i}. {result.get('title', 'N/A')}")

    print_section("Advanced Search with Filtering")
    
    # Search with filters
    filters = CompoundFilter(and_filters=[
        FilterExpression(
            attribute="rating",
            op=FilterOp.GREATER_THAN_OR_EQUAL,
            value=4.0
        ),
        FilterExpression(
            attribute="category",
            op=FilterOp.EQUALS,
            value="technology"
        ),
    ])
    
    sort = CompoundSort(sorts=[
        SortExpression(attribute="views", order=SortOrder.DESCENDING)
    ])
    
    filtered_results = client.search_data(SearchRequest(
        collection=collection_name,
        query="technology",
        fields=["title", "content"],
        limit=10,
        filters=filters,
        sort=sort,
    ))
    
    print(f"Filtered results: {len(filtered_results.data)}")
    for result in filtered_results.data:
        print(f"  - {result.get('title', 'N/A')} (rating: {result.get('rating', 'N/A')})")

    print_section("Collection Operations")
    
    # Unload and load collection
    client.unload_collection(collection_name)
    print("✓ Collection unloaded")
    
    client.load_collection(collection_name)
    print("✓ Collection loaded")
    
    # Reindex
    client.reindex_collection(collection_name)
    print("✓ Collection reindexed")

    print_section("Record Management")
    
    # Delete a record
    client.delete_record(collection_name, "tech-2")
    print("✓ Deleted record: tech-2")
    
    # Perform expiry cleanup
    client.expiry_cleanup(collection_name)
    print("✓ Expiry cleanup completed")

    print_section("Storage Operations")
    
    # List storage (this may be empty in a test environment)
    try:
        storage_items = client.list_storage()
        print(f"Storage items: {len(storage_items.data.get('items', []))}")
    except Exception as e:
        print(f"Storage listing: {e}")

    print_section("Embedding Models")
    
    try:
        embedding_models = client.list_embedding_models()
        print(f"Total providers: {len(embedding_models.data)}")
        for provider in embedding_models.data[:3]:  # Show first 3
            print(f"  - {provider.name} ({'default' if provider.is_default else 'non-default'})")
            for model in provider.models[:2]:  # Show first 2 models
                print(f"      • {model.name}")
    except Exception as e:
        print(f"Embedding models: {e}")

    print_section("Debug Operations")
    
    # Get collection levels
    try:
        levels = client.get_collection_levels(collection_name)
        print(f"✓ Retrieved collection levels")
        if levels.data:
            for field, level_info in list(levels.data.items())[:2]:
                print(f"  Field: {field}")
                for info in level_info[:3]:
                    print(f"    Level {info.level}: {info.node_count} nodes")
    except Exception as e:
        print(f"Debug operations: {e}")

    print_section("Oplog Operations")
    
    try:
        # Register a replica
        replica_id = "test-replica-1"
        client.register_replica(replica_id)
        print(f"✓ Registered replica: {replica_id}")
        
        # Get oplog status
        status = client.get_oplog_status(collection_name)
        print(f"✓ Oplog Status:")
        print(f"  Last LSN: {status.last_lsn}")
        print(f"  Retention LSN: {status.retention_lsn}")
        print(f"  Replica Count: {status.replica_count}")
        
        # Get oplog entries
        if status.last_lsn > 0:
            entries = client.get_oplog_entries(collection_name, after_lsn=0, limit=5)
            print(f"✓ Retrieved {entries.count} oplog entries")
        
        # Unregister replica
        client.unregister_replica(replica_id)
        print(f"✓ Unregistered replica: {replica_id}")
    except Exception as e:
        print(f"Oplog operations: {e}")

    print_section("Export/Import Collection")
    
    try:
        # Export collection
        export_file = "/tmp/test-collection-export.bin"
        with client.export_collection(collection_name) as export_data:
            with open(export_file, "wb") as f:
                content = export_data.read()
                f.write(content)
        print(f"✓ Exported collection to {export_file} ({len(content)} bytes)")
        
        # Import would create a new collection from the export
        # client.import_collection(export_file)
        # print(f"✓ Imported collection from {export_file}")
    except Exception as e:
        print(f"Export/Import: {e}")

    print_section("Rename Collection")
    
    new_name = f"{collection_name}-renamed"
    try:
        client.drop_collection(new_name)
    except:
        pass
    
    client.rename_collection(collection_name, new_name)
    print(f"✓ Renamed {collection_name} to {new_name}")
    collection_name = new_name

    print_section("Cleanup")
    
    # Drop the test collection
    client.drop_collection(collection_name)
    print(f"✓ Dropped collection: {collection_name}")
    
    print("\n✓ All advanced examples completed successfully!\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
