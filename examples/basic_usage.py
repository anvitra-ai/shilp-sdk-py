"""
Basic usage example for Shilp Python SDK.

This example demonstrates:
- Connecting to Shilp server
- Creating and managing collections
- Inserting records
- Searching for data
- Cleaning up resources
"""

from shilp import Client, AddCollectionRequest, InsertRecordRequest, SearchRequest, StorageBackendType


def main():
    # Initialize the client
    print("Connecting to Shilp server...")
    client = Client("http://localhost:3000")

    # Check health
    health = client.health_check()
    print(f"✓ Health check: {health.success}, Version: {health.version}\n")

    # List existing collections
    collections = client.list_collections()
    print(f"Existing collections: {[c.name for c in collections.data]}\n")

    # Drop collection if it already exists
    collection_name = "example-collection"
    try:
        client.drop_collection(collection_name)
        print(f"Dropped existing collection: {collection_name}")
    except Exception:
        print(f"Collection {collection_name} doesn't exist (OK)")

    # Create a new collection
    print(f"\nCreating collection: {collection_name}")
    response = client.add_collection(AddCollectionRequest(name=collection_name, storage_type=StorageBackendType.FILE, reference_storage_type=StorageBackendType.FILE))
    print(f"✓ Collection created: {response.success}")

    # Insert records
    print(f"\nInserting records into {collection_name}...")
    
    records = [
        {
            "id": "doc-1",
            "title": "Introduction to Vector Databases",
            "content": "Vector databases are specialized databases for storing and querying high-dimensional vectors.",
        },
        {
            "id": "doc-2",
            "title": "Machine Learning Basics",
            "content": "Machine learning is a subset of artificial intelligence that focuses on learning from data.",
        },
        {
            "id": "doc-3",
            "title": "Building Search Systems",
            "content": "Search systems use various algorithms to find relevant information quickly and efficiently.",
        },
    ]

    for record in records:
        response = client.insert_record(
            InsertRecordRequest(
                collection=collection_name,
                id=record["id"],
                record={
                    "title": record["title"],
                    "content": record["content"],
                },
                fields=["title", "content"],
            )
        )
        print(f"  ✓ Inserted record: {record['id']}")

    # Flush collection to ensure all records are persisted
    print(f"\nFlushing collection...")
    client.flush_collection(collection_name)
    print(f"✓ Collection flushed")

    # Search for data
    print(f"\nSearching for 'vector database'...")
    search_results = client.search_data(
        SearchRequest(
            collection=collection_name,
            query="vector database",
            fields=["title", "content"],
            limit=10,
        )
    )
    
    print(f"Found {len(search_results.data)} results:")
    for i, result in enumerate(search_results.data, 1):
        print(f"\n  Result {i}:")
        print(f"    ID: {result.get('id', 'N/A')}")
        print(f"    Title: {result.get('title', 'N/A')}")
        print(f"    Content: {result.get('content', 'N/A')[:100]}...")

    # Advanced search with max distance
    print(f"\n\nAdvanced search with max_distance=0.5...")
    advanced_results = client.search_data(
        SearchRequest(
            collection=collection_name,
            query="machine learning",
            fields=["title", "content"],
            limit=5,
            max_distance=0.5,
        )
    )
    
    print(f"Found {len(advanced_results.data)} results within distance threshold:")
    for i, result in enumerate(advanced_results.data, 1):
        print(f"  {i}. {result.get('title', 'N/A')}")

    # Delete a record
    print(f"\n\nDeleting record 'doc-2'...")
    client.delete_record(collection_name, "doc-2")
    print(f"✓ Record deleted")

    # List collections again
    collections = client.list_collections()
    collection = next((c for c in collections.data if c.name == collection_name), None)
    if collection:
        print(f"\n\nCollection info:")
        print(f"  Name: {collection.name}")
        print(f"  Loaded: {collection.is_loaded}")
        print(f"  Fields: {collection.fields}")
        print(f"  Searchable Fields: {collection.searchable_fields}")

    # Clean up - drop the collection
    print(f"\n\nCleaning up...")
    client.drop_collection(collection_name)
    print(f"✓ Collection {collection_name} dropped")
    
    print("\n✓ Example completed successfully!")


if __name__ == "__main__":
    main()
