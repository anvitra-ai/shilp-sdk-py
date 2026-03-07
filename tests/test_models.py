"""
Unit tests for Shilp SDK models and validation.
"""

import pytest
from shilp.models import (
    FilterExpression,
    FilterOp,
    SortExpression,
    SortOrder,
    CompoundFilter,
    CompoundSort,
    AttrType,
    IndexType,
    AttributeType,
    DebugDistanceData,
    DebugDistanceResponse,
    DebugGetEmbeddingsRequest,
    DebugGetEmbeddingsResponse,
    CollectionDataRecord,
    GetCollectionDataResponse,
    Attribute,
    CategoryValue,
    CategorySchema,
    CollectionSchema,
    GetCollectionSchemaResponse,
    VerticalInfo,
    ListNLIVerticalsResponse,
    Collection,
    ListCollectionsResponse,
    SearchRequest,
    StorageBackendType,
)


class TestFilterExpression:
    """Test FilterExpression validation."""

    def test_valid_equals_filter(self):
        """Test valid equals filter expression."""
        expr = FilterExpression(
            attribute="status",
            op=FilterOp.EQUALS,
            value="active"
        )
        expr.validate()  # Should not raise

    def test_valid_in_filter(self):
        """Test valid IN filter expression."""
        expr = FilterExpression(
            attribute="category",
            op=FilterOp.IN,
            values=["tech", "science"]
        )
        expr.validate()  # Should not raise

    def test_empty_attribute_fails(self):
        """Test that empty attribute name fails validation."""
        expr = FilterExpression(
            attribute="",
            op=FilterOp.EQUALS,
            value="test"
        )
        with pytest.raises(ValueError, match="attribute name cannot be empty"):
            expr.validate()

    def test_in_without_values_fails(self):
        """Test that IN operation without values fails validation."""
        expr = FilterExpression(
            attribute="category",
            op=FilterOp.IN,
            values=[]
        )
        with pytest.raises(ValueError, match="IN/NOT IN operations require at least one value"):
            expr.validate()

    def test_equals_without_value_fails(self):
        """Test that equals operation without value fails validation."""
        expr = FilterExpression(
            attribute="status",
            op=FilterOp.EQUALS,
            value=None
        )
        with pytest.raises(ValueError, match="value cannot be None"):
            expr.validate()


class TestSortExpression:
    """Test SortExpression validation."""

    def test_valid_ascending_sort(self):
        """Test valid ascending sort expression."""
        expr = SortExpression(
            attribute="created_at",
            order=SortOrder.ASCENDING
        )
        expr.validate()  # Should not raise

    def test_valid_descending_sort(self):
        """Test valid descending sort expression."""
        expr = SortExpression(
            attribute="updated_at",
            order=SortOrder.DESCENDING
        )
        expr.validate()  # Should not raise

    def test_empty_attribute_fails(self):
        """Test that empty attribute name fails validation."""
        expr = SortExpression(
            attribute="",
            order=SortOrder.ASCENDING
        )
        with pytest.raises(ValueError, match="sort attribute cannot be empty"):
            expr.validate()


class TestCompoundFilter:
    """Test CompoundFilter serialization."""

    def test_to_dict_with_filters(self):
        """Test conversion to dictionary with filters."""
        compound = CompoundFilter(and_filters=[
            FilterExpression(attribute="age", op=FilterOp.GREATER_THAN, value=25),
            FilterExpression(attribute="status", op=FilterOp.EQUALS, value="active"),
        ])
        
        result = compound.to_dict()
        assert "and" in result
        assert len(result["and"]) == 2
        assert result["and"][0]["attribute"] == "age"
        assert result["and"][0]["op"] == FilterOp.GREATER_THAN
        assert result["and"][0]["value"] == 25

    def test_to_dict_empty(self):
        """Test conversion to dictionary with no filters."""
        compound = CompoundFilter()
        result = compound.to_dict()
        assert result == {}


class TestCompoundSort:
    """Test CompoundSort serialization."""

    def test_to_dict_with_sorts(self):
        """Test conversion to dictionary with sorts."""
        compound = CompoundSort(sorts=[
            SortExpression(attribute="created_at", order=SortOrder.DESCENDING),
            SortExpression(attribute="name", order=SortOrder.ASCENDING),
        ])
        
        result = compound.to_dict()
        assert "sorts" in result
        assert len(result["sorts"]) == 2
        assert result["sorts"][0]["attribute"] == "created_at"
        assert result["sorts"][0]["order"] == SortOrder.DESCENDING

    def test_to_dict_empty(self):
        """Test conversion to dictionary with no sorts."""
        compound = CompoundSort()
        result = compound.to_dict()
        assert result == {}


class TestAttrType:
    """Test AttrType enum."""

    def test_attr_types_defined(self):
        """Test that all attribute types are defined."""
        assert AttrType.INT64 == 0
        assert AttrType.FLOAT64 == 1
        assert AttrType.STRING == 2
        assert AttrType.BOOL == 3


class TestFilterOp:
    """Test FilterOp enum."""

    def test_filter_ops_defined(self):
        """Test that all filter operations are defined."""
        assert FilterOp.EQUALS == 0
        assert FilterOp.NOT_EQUALS == 1
        assert FilterOp.GREATER_THAN == 2
        assert FilterOp.GREATER_THAN_OR_EQUAL == 3
        assert FilterOp.LESS_THAN == 4
        assert FilterOp.LESS_THAN_OR_EQUAL == 5
        assert FilterOp.IN == 6
        assert FilterOp.NOT_IN == 7


class TestSortOrder:
    """Test SortOrder enum."""

    def test_sort_orders_defined(self):
        """Test that all sort orders are defined."""
        assert SortOrder.ASCENDING == 0
        assert SortOrder.DESCENDING == 1


class TestIndexType:
    """Test IndexType constants."""

    def test_index_types_defined(self):
        """Test that all index types are defined."""
        assert IndexType.HNSW == "hnsw"
        assert IndexType.INVERTED == "inverted"
        assert IndexType.METADATA == "metadata"


class TestAttributeType:
    """Test AttributeType enum."""

    def test_attribute_types_defined(self):
        """Test that all attribute types are defined."""
        assert AttributeType.NUMERICAL == 1
        assert AttributeType.STRING == 2


class TestDebugDistanceData:
    """Test DebugDistanceData dataclass."""

    def test_debug_distance_data_creation(self):
        """Test creating a DebugDistanceData instance."""
        d = DebugDistanceData(distance=0.5, vector=[0.1, 0.2, 0.3])
        assert d.distance == 0.5
        assert d.vector == [0.1, 0.2, 0.3]
        assert d.custom_matcher_distance is None

    def test_debug_distance_data_with_custom_matcher(self):
        """Test DebugDistanceData with custom_matcher_distance."""
        d = DebugDistanceData(distance=0.5, vector=[0.1], custom_matcher_distance=0.3)
        assert d.custom_matcher_distance == 0.3

    def test_debug_distance_response_with_data(self):
        """Test DebugDistanceResponse with DebugDistanceData."""
        data = DebugDistanceData(distance=0.7, vector=[0.1, 0.2])
        resp = DebugDistanceResponse(success=True, message="OK", data=data)
        assert isinstance(resp.data, DebugDistanceData)
        assert resp.data.distance == 0.7


class TestDebugEmbeddings:
    """Test debug embeddings request/response models."""

    def test_embeddings_request_creation(self):
        """Test DebugGetEmbeddingsRequest creation."""
        req = DebugGetEmbeddingsRequest(texts=["hello", "world"])
        assert req.texts == ["hello", "world"]

    def test_embeddings_response_creation(self):
        """Test DebugGetEmbeddingsResponse creation."""
        resp = DebugGetEmbeddingsResponse(
            success=True, message="OK", data=[[0.1, 0.2], [0.3, 0.4]]
        )
        assert resp.success is True
        assert len(resp.data) == 2
        assert resp.data[0] == [0.1, 0.2]


class TestCollectionDataModels:
    """Test collection data models."""

    def test_collection_data_record_creation(self):
        """Test CollectionDataRecord creation."""
        rec = CollectionDataRecord(id="abc", data={"field": "value"})
        assert rec.id == "abc"
        assert rec.data == {"field": "value"}
        assert rec.vectors is None

    def test_get_collection_data_response_creation(self):
        """Test GetCollectionDataResponse creation."""
        rec = CollectionDataRecord(id="1", data={})
        resp = GetCollectionDataResponse(success=True, message="OK", data=[rec], total=1)
        assert resp.total == 1
        assert len(resp.data) == 1


class TestCollectionSchemaModels:
    """Test collection schema models."""

    def test_attribute_creation(self):
        """Test Attribute creation."""
        attr = Attribute(name="color", type=AttributeType.STRING, index_type="inverted")
        assert attr.name == "color"
        assert attr.type == AttributeType.STRING
        assert attr.index_type == "inverted"

    def test_category_value_creation(self):
        """Test CategoryValue creation."""
        cv = CategoryValue(value="red", count=10)
        assert cv.value == "red"
        assert cv.count == 10

    def test_category_schema_creation(self):
        """Test CategorySchema creation."""
        cs = CategorySchema(
            name="color",
            index_type="inverted",
            values=[CategoryValue(value="red", count=5)],
            synonyms=["hue"],
        )
        assert cs.name == "color"
        assert len(cs.values) == 1
        assert cs.synonyms == ["hue"]

    def test_collection_schema_creation(self):
        """Test CollectionSchema creation."""
        schema = CollectionSchema(
            attributes=[Attribute(name="color")],
            value_schema=[CategorySchema(name="color")],
        )
        assert len(schema.attributes) == 1
        assert len(schema.value_schema) == 1

    def test_get_collection_schema_response(self):
        """Test GetCollectionSchemaResponse creation."""
        resp = GetCollectionSchemaResponse(success=True, message="OK", data=CollectionSchema())
        assert resp.success is True
        assert isinstance(resp.data, CollectionSchema)


class TestNLIModels:
    """Test NLI-related models."""

    def test_vertical_info_creation(self):
        """Test VerticalInfo creation."""
        v = VerticalInfo(name="ecommerce", label="E-Commerce", is_native=True)
        assert v.name == "ecommerce"
        assert v.is_native is True

    def test_list_nli_verticals_response(self):
        """Test ListNLIVerticalsResponse creation."""
        resp = ListNLIVerticalsResponse(
            success=True,
            data=[VerticalInfo(name="ecommerce")],
            message="OK",
        )
        assert resp.success is True
        assert len(resp.data) == 1


class TestCollectionNLIFields:
    """Test Collection and ListCollectionsResponse with NLI fields."""

    def test_collection_with_nli_fields(self):
        """Test Collection includes NLI fields."""
        col = Collection(
            name="test",
            is_loaded=True,
            fields=["f1"],
            searchable_fields=["f1"],
            field_config={"f1": "hnsw"},
            is_nli_enabled=True,
            nli_domain="ecommerce",
        )
        assert col.field_config == {"f1": "hnsw"}
        assert col.is_nli_enabled is True
        assert col.nli_domain == "ecommerce"

    def test_list_collections_response_nli_supported(self):
        """Test ListCollectionsResponse includes is_nli_supported."""
        col = Collection(
            name="test", is_loaded=True, fields=[], searchable_fields=[]
        )
        resp = ListCollectionsResponse(
            success=True, message="OK", data=[col], is_nli_supported=True
        )
        assert resp.is_nli_supported is True


class TestSearchRequestUseNLI:
    """Test SearchRequest with use_nli field."""

    def test_search_request_with_use_nli(self):
        """Test SearchRequest includes use_nli field."""
        req = SearchRequest(collection="test", query="hello", use_nli=True)
        assert req.use_nli is True

    def test_search_request_use_nli_defaults_none(self):
        """Test SearchRequest use_nli defaults to None."""
        req = SearchRequest(collection="test", query="hello")
        assert req.use_nli is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
