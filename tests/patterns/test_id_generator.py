"""Unit tests for IDGeneratorPattern."""

import pytest
from joget_form_generator.patterns.id_generator import IDGeneratorPattern


@pytest.fixture
def pattern():
    """Fixture providing IDGeneratorPattern instance."""
    return IDGeneratorPattern()


def test_basic_id_generator(pattern):
    """Test basic ID generator rendering."""
    field = {
        "id": "recordId",
        "label": "Record ID",
        "type": "idGenerator",
    }
    context = {}

    result = pattern.render(field, context)

    assert result["className"] == "org.joget.apps.form.lib.IdGeneratorField"
    assert result["properties"]["id"] == "recordId"
    assert result["properties"]["label"] == "Record ID"
    assert result["properties"]["readonly"] == "true"


def test_id_generator_with_prefix(pattern):
    """Test ID generator with prefix."""
    field = {
        "id": "invoiceId",
        "label": "Invoice ID",
        "type": "idGenerator",
        "prefix": "INV-",
    }
    context = {}

    result = pattern.render(field, context)

    assert result["properties"]["prefix"] == "INV-"


def test_id_generator_with_postfix(pattern):
    """Test ID generator with postfix."""
    field = {
        "id": "orderId",
        "label": "Order ID",
        "type": "idGenerator",
        "postfix": "-ORD",
    }
    context = {}

    result = pattern.render(field, context)

    assert result["properties"]["postfix"] == "-ORD"


def test_id_generator_with_prefix_and_postfix(pattern):
    """Test ID generator with both prefix and postfix."""
    field = {
        "id": "ticketId",
        "label": "Ticket ID",
        "type": "idGenerator",
        "prefix": "TKT-",
        "postfix": "-2025",
    }
    context = {}

    result = pattern.render(field, context)

    assert result["properties"]["prefix"] == "TKT-"
    assert result["properties"]["postfix"] == "-2025"


def test_id_generator_with_custom_format(pattern):
    """Test ID generator with custom format."""
    field = {
        "id": "customId",
        "label": "Custom ID",
        "type": "idGenerator",
        "prefix": "CUST",
        "format": "{prefix}-{count:08d}",
    }
    context = {}

    result = pattern.render(field, context)

    assert result["properties"]["format"] == "{prefix}-{count:08d}"
    assert result["properties"]["prefix"] == "CUST"


def test_id_generator_default_format(pattern):
    """Test ID generator uses default format."""
    field = {
        "id": "autoId",
        "label": "Auto ID",
        "type": "idGenerator",
    }
    context = {}

    result = pattern.render(field, context)

    # Default format should be present
    assert "format" in result["properties"]
    assert "{count" in result["properties"]["format"]
