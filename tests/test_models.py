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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
