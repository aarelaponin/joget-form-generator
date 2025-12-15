"""Unit tests for pattern mixins."""

import pytest
from joget_form_generator.patterns.mixins import ValidationMixin, OptionsMixin


class TestValidationMixin:
    """Test ValidationMixin functionality."""

    def test_build_validator_with_required(self):
        """Test validator generation for required field."""
        mixin = ValidationMixin()
        field = {
            "id": "field1",
            "label": "Field 1",
            "required": True,
        }

        validator = mixin.build_validator(field)

        assert validator is not None
        assert validator["className"] == "org.joget.apps.form.lib.DefaultValidator"
        assert validator["properties"]["mandatory"] == "true"

    def test_build_validator_with_regex(self):
        """Test regex validator generation."""
        mixin = ValidationMixin()
        field = {
            "id": "email",
            "label": "Email",
            "required": True,
            "validation": {
                "pattern": "^[a-zA-Z0-9]+@[a-zA-Z0-9]+\\.[a-zA-Z]{2,}$",
                "message": "Invalid email format",
            },
        }

        validator = mixin.build_validator(field)

        # Should have both required and regex validators
        assert validator is not None

    def test_build_validator_optional_field(self):
        """Test no validator for optional field without validation."""
        mixin = ValidationMixin()
        field = {
            "id": "field1",
            "label": "Field 1",
            "required": False,
        }

        validator = mixin.build_validator(field)

        # Optional field with no validation should have no validator
        assert validator is None or validator == {}


class TestOptionsMixin:
    """Test OptionsMixin functionality."""

    def test_build_static_options(self):
        """Test static options builder."""
        mixin = OptionsMixin()
        options = [
            {"value": "opt1", "label": "Option 1"},
            {"value": "opt2", "label": "Option 2"},
        ]

        options_binder = mixin._build_static_options(options)

        assert options_binder["className"] == "org.joget.apps.form.lib.FormOptionsBinder"
        assert len(options_binder["properties"]["options"]) == 2
        assert options_binder["properties"]["options"][0]["value"] == "opt1"

    def test_build_dynamic_options_form_data(self):
        """Test dynamic options with formData source."""
        mixin = OptionsMixin()
        options_source = {
            "type": "formData",
            "formId": "parentForm",
            "valueColumn": "id",
            "labelColumn": "name",
        }
        context = {}

        options_binder = mixin._build_dynamic_options(options_source, context)

        assert options_binder["className"] == "org.joget.apps.form.lib.FormOptionsBinder"
        assert options_binder["properties"]["formDefId"] == "parentForm"
        assert options_binder["properties"]["idColumn"] == "id"
        assert options_binder["properties"]["labelColumn"] == "name"

    def test_build_dynamic_options_api_get(self):
        """Test API options with GET request."""
        mixin = OptionsMixin()
        options_source = {
            "type": "api",
            "jsonUrl": "https://api.example.com/countries",
            "requestType": "GET",
            "idColumn": "code",
            "labelColumn": "name",
        }
        context = {}

        options_binder = mixin._build_dynamic_options(options_source, context)

        assert options_binder["className"] == "org.joget.apps.form.lib.JsonApiFormOptionsBinder"
        assert options_binder["properties"]["jsonUrl"] == "https://api.example.com/countries"
        assert options_binder["properties"]["requestType"] == "get"
        assert options_binder["properties"]["idColumn"] == "code"
        assert options_binder["properties"]["labelColumn"] == "name"
        assert options_binder["properties"]["addEmptyOption"] == "true"

    def test_build_dynamic_options_api_post_with_params(self):
        """Test API options with POST request and parameters."""
        mixin = OptionsMixin()
        options_source = {
            "type": "api",
            "jsonUrl": "https://api.example.com/search",
            "requestType": "POST",
            "idColumn": "id",
            "labelColumn": "title",
            "postMethod": "parameters",
            "params": [
                {"name": "category", "value": "books"},
                {"name": "limit", "value": "100"}
            ],
            "headers": [
                {"name": "Authorization", "value": "Bearer TOKEN"}
            ],
        }
        context = {}

        options_binder = mixin._build_dynamic_options(options_source, context)

        assert options_binder["className"] == "org.joget.apps.form.lib.JsonApiFormOptionsBinder"
        assert options_binder["properties"]["requestType"] == "post"
        assert options_binder["properties"]["postMethod"] == "parameters"
        assert len(options_binder["properties"]["params"]) == 2
        assert len(options_binder["properties"]["headers"]) == 1

    def test_build_dynamic_options_api_with_grouping(self):
        """Test API options with grouping column."""
        mixin = OptionsMixin()
        options_source = {
            "type": "api",
            "jsonUrl": "https://api.example.com/products",
            "requestType": "GET",
            "idColumn": "sku",
            "labelColumn": "name",
            "groupingColumn": "category",
            "multirowBaseObject": "data.products",
        }
        context = {}

        options_binder = mixin._build_dynamic_options(options_source, context)

        assert options_binder["properties"]["groupingColumn"] == "category"
        assert options_binder["properties"]["multirowBaseObject"] == "data.products"

    def test_build_dynamic_options_database(self):
        """Test database options with table name."""
        mixin = OptionsMixin()
        options_source = {
            "type": "database",
            "tableName": "app_fd_categories",
            "valueColumn": "c_code",
            "labelColumn": "c_name",
        }
        context = {}

        options_binder = mixin._build_dynamic_options(options_source, context)

        assert options_binder["className"] == "org.joget.plugin.enterprise.DatabaseWizardOptionsBinder"
        assert options_binder["properties"]["jdbcDatasource"] == "default"
        assert options_binder["properties"]["tableName"] == "app_fd_categories"
        assert options_binder["properties"]["valueColumn"] == "c_code"
        assert options_binder["properties"]["labelColumn"] == "c_name"
        assert options_binder["properties"]["addEmpty"] == "true"

    def test_build_dynamic_options_database_with_condition(self):
        """Test database options with SQL condition."""
        mixin = OptionsMixin()
        options_source = {
            "type": "database",
            "jdbcDatasource": "hrDatabase",
            "tableName": "departments",
            "valueColumn": "dept_code",
            "labelColumn": "dept_name",
            "extraCondition": "is_active = 1",
            "groupingColumn": "division",
        }
        context = {}

        options_binder = mixin._build_dynamic_options(options_source, context)

        assert options_binder["properties"]["jdbcDatasource"] == "hrDatabase"
        assert options_binder["properties"]["extraCondition"] == "is_active = 1"
        assert options_binder["properties"]["groupingColumn"] == "division"

    def test_build_dynamic_options_api_no_empty_option(self):
        """Test API options without empty option."""
        mixin = OptionsMixin()
        options_source = {
            "type": "api",
            "jsonUrl": "https://api.example.com/data",
            "idColumn": "id",
            "labelColumn": "name",
            "addEmptyOption": False,
        }
        context = {}

        options_binder = mixin._build_dynamic_options(options_source, context)

        assert options_binder["properties"]["addEmptyOption"] == "false"

    def test_build_dynamic_options_database_with_ajax(self):
        """Test database options with AJAX enabled."""
        mixin = OptionsMixin()
        options_source = {
            "type": "database",
            "tableName": "large_table",
            "valueColumn": "id",
            "labelColumn": "name",
            "useAjax": True,
        }
        context = {}

        options_binder = mixin._build_dynamic_options(options_source, context)

        assert options_binder["properties"]["useAjax"] == "true"
