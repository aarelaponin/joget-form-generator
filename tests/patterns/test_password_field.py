"""Unit tests for PasswordFieldPattern."""

import pytest
from joget_form_generator.patterns.password_field import PasswordFieldPattern


@pytest.fixture
def pattern():
    """Fixture providing PasswordFieldPattern instance."""
    return PasswordFieldPattern()


def test_basic_password_field(pattern):
    """Test basic password field rendering."""
    field = {
        "id": "password",
        "label": "Password",
        "type": "passwordField",
    }
    context = {}

    result = pattern.render(field, context)

    assert result["className"] == "org.joget.apps.form.lib.PasswordField"
    assert result["properties"]["id"] == "password"
    assert result["properties"]["label"] == "Password"


def test_required_password_field(pattern):
    """Test required password field with validation."""
    field = {
        "id": "password",
        "label": "Password",
        "type": "passwordField",
        "required": True,
    }
    context = {}

    result = pattern.render(field, context)

    assert "validator" in result["properties"]
    validator = result["properties"]["validator"]
    assert validator["className"] == "org.joget.apps.form.lib.DefaultValidator"
    assert validator["properties"]["mandatory"] == "true"


def test_password_field_with_placeholder(pattern):
    """Test password field with placeholder."""
    field = {
        "id": "password",
        "label": "Password",
        "type": "passwordField",
        "placeholder": "Enter secure password",
    }
    context = {}

    result = pattern.render(field, context)

    assert result["properties"]["placeholder"] == "Enter secure password"


def test_password_field_readonly(pattern):
    """Test readonly password field (edge case)."""
    field = {
        "id": "apiKey",
        "label": "API Key",
        "type": "passwordField",
        "readonly": True,
    }
    context = {}

    result = pattern.render(field, context)

    assert result["properties"]["readonly"] == "true"
