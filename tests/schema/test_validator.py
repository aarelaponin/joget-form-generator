"""Unit tests for SchemaValidator."""

import pytest
from joget_form_generator.schema.validator import SchemaValidator, ValidationResult


@pytest.fixture
def validator():
    """Fixture providing SchemaValidator instance."""
    return SchemaValidator()


def test_valid_simple_form(validator):
    """Test validation of simple valid form."""
    spec = {
        "form": {"id": "testForm", "name": "Test Form", "tableName": "testForm"},
        "fields": [{"id": "name", "label": "Name", "type": "textField"}],
    }

    result = validator.validate(spec)
    assert result.valid
    assert len(result.errors) == 0


def test_missing_required_field(validator):
    """Test validation fails when required field missing."""
    spec = {
        "form": {
            "id": "testForm",
            "name": "Test Form"
            # Missing: tableName (required)
        },
        "fields": [],
    }

    result = validator.validate(spec)
    assert not result.valid
    assert any("tableName" in error for error in result.errors)


def test_invalid_field_type(validator):
    """Test validation fails for invalid field type."""
    spec = {
        "form": {"id": "test", "name": "Test", "tableName": "test"},
        "fields": [{"id": "field1", "label": "Field 1", "type": "invalidType"}],
    }

    result = validator.validate(spec)
    assert not result.valid
    assert any("is not one of" in error for error in result.errors)


def test_selectbox_needs_options_or_source(validator):
    """Test selectBox requires either options or optionsSource."""
    spec = {
        "form": {"id": "test", "name": "Test", "tableName": "test"},
        "fields": [
            {
                "id": "category",
                "label": "Category",
                "type": "selectBox"
                # Missing: options AND optionsSource
            }
        ],
    }

    result = validator.validate(spec)
    assert not result.valid


def test_valid_selectbox_with_static_options(validator):
    """Test selectBox with static options is valid."""
    spec = {
        "form": {"id": "test", "name": "Test", "tableName": "test"},
        "fields": [
            {
                "id": "category",
                "label": "Category",
                "type": "selectBox",
                "options": [
                    {"value": "cat1", "label": "Category 1"},
                    {"value": "cat2", "label": "Category 2"},
                ],
            }
        ],
    }

    result = validator.validate(spec)
    assert result.valid


def test_valid_selectbox_with_dynamic_options(validator):
    """Test selectBox with optionsSource is valid."""
    spec = {
        "form": {"id": "test", "name": "Test", "tableName": "test"},
        "fields": [
            {
                "id": "category",
                "label": "Category",
                "type": "selectBox",
                "optionsSource": {"type": "formData", "formId": "categories"},
            }
        ],
    }

    result = validator.validate(spec)
    assert result.valid


def test_warning_for_id_tablename_mismatch(validator):
    """Test warning when id and tableName don't match."""
    spec = {
        "form": {"id": "testForm", "name": "Test Form", "tableName": "differentName"},
        "fields": [{"id": "field1", "label": "Field 1", "type": "textField"}],
    }

    result = validator.validate(spec)
    assert result.valid  # Still valid
    assert len(result.warnings) > 0
    assert any("match" in warning.lower() for warning in result.warnings)


def test_warning_for_cascading_without_parent(validator):
    """Test warning for cascading dropdown without parentField."""
    spec = {
        "form": {"id": "test", "name": "Test", "tableName": "test"},
        "fields": [
            {
                "id": "category",
                "label": "Category",
                "type": "selectBox",
                "optionsSource": {
                    "type": "formData",
                    "formId": "categories"
                    # Missing: parentField (may or may not be intentional)
                },
            }
        ],
    }

    result = validator.validate(spec)
    assert result.valid
    assert any("parentField" in warning for warning in result.warnings)


def test_duplicate_field_ids_warning(validator):
    """Test warning for duplicate field IDs."""
    spec = {
        "form": {"id": "test", "name": "Test", "tableName": "test"},
        "fields": [
            {"id": "name", "label": "Name 1", "type": "textField"},
            {"id": "name", "label": "Name 2", "type": "textField"},  # Duplicate!
        ],
    }

    result = validator.validate(spec)
    assert result.valid  # Structurally valid
    assert any("duplicate" in warning.lower() for warning in result.warnings)


def test_checkbox_requires_options(validator):
    """Test checkBox requires options array."""
    spec = {
        "form": {"id": "test", "name": "Test", "tableName": "test"},
        "fields": [
            {
                "id": "agree",
                "label": "I Agree",
                "type": "checkBox"
                # Missing: options (required for checkBox)
            }
        ],
    }

    result = validator.validate(spec)
    assert not result.valid


def test_radio_requires_options(validator):
    """Test radio requires options array."""
    spec = {
        "form": {"id": "test", "name": "Test", "tableName": "test"},
        "fields": [
            {
                "id": "gender",
                "label": "Gender",
                "type": "radio"
                # Missing: options (required for radio)
            }
        ],
    }

    result = validator.validate(spec)
    assert not result.valid


def test_invalid_form_id_pattern(validator):
    """Test form ID must match pattern."""
    spec = {
        "form": {
            "id": "123invalid",  # Must start with letter
            "name": "Test",
            "tableName": "123invalid",
        },
        "fields": [{"id": "field1", "label": "Field 1", "type": "textField"}],
    }

    result = validator.validate(spec)
    assert not result.valid
    assert any("does not match" in error for error in result.errors)


def test_form_id_too_long(validator):
    """Test form ID must be max 20 chars."""
    spec = {
        "form": {
            "id": "a" * 21,  # 21 characters - too long
            "name": "Test",
            "tableName": "a" * 21,
        },
        "fields": [{"id": "field1", "label": "Field 1", "type": "textField"}],
    }

    result = validator.validate(spec)
    assert not result.valid


def test_empty_fields_array_invalid(validator):
    """Test form must have at least one field."""
    spec = {
        "form": {"id": "test", "name": "Test", "tableName": "test"},
        "fields": [],  # Empty - invalid
    }

    result = validator.validate(spec)
    assert not result.valid


def test_all_9_field_types_valid(validator):
    """Test that all 9 Phase 1 field types are recognized."""
    field_types = [
        "hiddenField",
        "textField",
        "passwordField",
        "textArea",
        "selectBox",
        "checkBox",
        "radio",
        "datePicker",
        "fileUpload",
    ]

    for field_type in field_types:
        spec = {
            "form": {"id": "test", "name": "Test", "tableName": "test"},
            "fields": [{"id": "field1", "label": "Field 1", "type": field_type}],
        }

        # Add required properties for specific types
        if field_type in ["selectBox", "checkBox", "radio"]:
            spec["fields"][0]["options"] = [{"value": "opt1", "label": "Option 1"}]

        result = validator.validate(spec)
        assert result.valid, f"Field type '{field_type}' should be valid but got errors: {result.errors}"
