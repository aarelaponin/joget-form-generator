"""Capability mixins for shared pattern functionality."""

from typing import Any


class ReadOnlyMixin:
    """Mixin for readonly/required properties (used by all fields)."""

    def get_readonly_props(self, field: dict[str, Any]) -> dict[str, str]:
        """
        Get readonly and required properties in Joget format.

        Returns:
            Dict with 'required' and 'readonly' keys (Joget boolean strings)
        """
        return {
            "required": "true" if field.get("required", False) else "",
            "readonly": "true" if field.get("readonly", False) else "",
        }


class ValidationMixin:
    """Mixin for building Joget validators."""

    def build_validator(self, field: dict[str, Any]) -> dict[str, Any] | None:
        """
        Build Joget validator configuration from validation spec.

        Uses DefaultValidator which is the standard validator in Joget DX.
        DefaultValidator requires all three properties:
        - mandatory: "true" for required fields, "" otherwise
        - type: "regex" for custom regex validation, "" otherwise
        - message: error message for validation failure, "" if none

        Note: Joget does NOT have separate RegexValidator or MultiValidator classes.
        All validation is done through DefaultValidator with appropriate properties.

        Args:
            field: Field specification with optional 'validation' key and 'required' flag

        Returns:
            Joget validator dict or None if no validation
        """
        is_required = field.get("required", False)
        validation = field.get("validation")

        # No validation needed
        if not is_required and not validation:
            return None

        # Build DefaultValidator properties - always include all three
        props: dict[str, Any] = {
            "mandatory": "true" if is_required else "",
            "type": "",
            "message": "",
        }

        # Check for additional validation rules
        if validation:
            # Regex pattern validator
            if pattern := validation.get("pattern"):
                props["type"] = "regex"
                props["regex"] = pattern
                props["message"] = validation.get("message", "Invalid format")

            # Min/max length - implemented via regex pattern
            min_len = validation.get("minLength")
            max_len = validation.get("maxLength")

            if min_len is not None or max_len is not None:
                # If we already have a pattern, we can't add length validation easily
                # Only add length validation if no explicit pattern
                if "regex" not in props:
                    if min_len is not None and max_len is not None:
                        props["type"] = "regex"
                        props["regex"] = f"^.{{{min_len},{max_len}}}$"
                        props["message"] = validation.get(
                            "message", f"Must be between {min_len} and {max_len} characters"
                        )
                    elif min_len is not None:
                        props["type"] = "regex"
                        props["regex"] = f"^.{{{min_len},}}$"
                        props["message"] = validation.get(
                            "message", f"Minimum {min_len} characters required"
                        )
                    elif max_len is not None:
                        props["type"] = "regex"
                        props["regex"] = f"^.{{0,{max_len}}}$"
                        props["message"] = validation.get(
                            "message", f"Maximum {max_len} characters allowed"
                        )

        return {
            "className": "org.joget.apps.form.lib.DefaultValidator",
            "properties": props,
        }


class OptionsMixin:
    """Mixin for building options (SelectBox, Radio, CheckBox)."""

    def build_options_binder(
        self, field: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Build optionsBinder for fields with options.

        Args:
            field: Field specification
            context: Global context

        Returns:
            Joget optionsBinder configuration
        """
        # Check for dynamic options source
        if options_source := field.get("optionsSource"):
            return self._build_dynamic_options(options_source, context)

        # Static options
        options = field.get("options", [])
        return self._build_static_options(options)

    def _build_static_options(self, options: list[dict]) -> dict[str, Any]:
        """Build FormOptionsBinder for static options."""
        # Joget requires grouping field in each option
        option_list = [
            {"value": opt["value"], "label": opt["label"], "grouping": ""}
            for opt in options
        ]

        return {
            "className": "",
            "properties": {},
        }

    def build_static_options_array(self, options: list[dict]) -> list[dict[str, str]]:
        """Build static options array with grouping field for CheckBox/Radio/SelectBox."""
        return [
            {"value": opt["value"], "label": opt["label"], "grouping": ""}
            for opt in options
        ]

    def _build_dynamic_options(
        self, options_source: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Build options binder for dynamic/cascading options."""

        source_type = options_source["type"]

        if source_type == "formData":
            # Nested LOV: get options from another form (parent form reference)
            # Uses FormOptionsBinder for simple parent-child relationships
            add_empty = options_source.get("addEmptyOption", True)
            use_ajax = options_source.get("useAjax", False)

            props = {
                "formDefId": options_source["formId"],
                "idColumn": options_source.get("valueColumn", "code"),
                "labelColumn": options_source.get("labelColumn", "name"),
                "groupingColumn": options_source.get("groupingColumn", ""),
                "extraCondition": options_source.get("extraCondition", ""),
                "addEmptyOption": "true" if add_empty else "",
                "emptyLabel": options_source.get("emptyLabel", ""),
                "useAjax": "true" if use_ajax else "",
                "cacheInterval": "",
            }

            # Cascading dropdown support
            if parent_field := options_source.get("parentField"):
                props["parentField"] = parent_field
            if filter_field := options_source.get("filterField"):
                props["filterField"] = filter_field

            return {
                "className": "org.joget.apps.form.lib.FormOptionsBinder",
                "properties": props,
            }

        elif source_type == "api":
            # JSON API-based options (JsonApiFormOptionsBinder)
            props = {
                "jsonUrl": options_source["jsonUrl"],
                "requestType": options_source.get("requestType", "GET").lower(),
                "idColumn": options_source["idColumn"],
                "labelColumn": options_source["labelColumn"],
                "addEmptyOption": "true" if options_source.get("addEmptyOption", True) else "false",
                "emptyLabel": options_source.get("emptyLabel", ""),
                "useAjax": "true" if options_source.get("useAjax", False) else "false",
            }

            # Optional grouping column
            if grouping := options_source.get("groupingColumn"):
                props["groupingColumn"] = grouping

            # Optional base object for array extraction
            if base_obj := options_source.get("multirowBaseObject"):
                props["multirowBaseObject"] = base_obj

            # POST/PUT specific options
            if props["requestType"] in ["post", "put"]:
                props["postMethod"] = options_source.get("postMethod", "parameters")

                if props["postMethod"] == "custom" and "customPayload" in options_source:
                    props["customPayload"] = options_source["customPayload"]
                elif "params" in options_source:
                    props["params"] = options_source["params"]

            # HTTP headers
            if "headers" in options_source:
                props["headers"] = options_source["headers"]

            return {
                "className": "org.joget.apps.form.lib.JsonApiFormOptionsBinder",
                "properties": props,
            }

        elif source_type == "database":
            # Database wizard options binder (Enterprise Edition)
            props = {
                "jdbcDatasource": options_source.get("jdbcDatasource", "default"),
                "tableName": options_source["tableName"],
                "valueColumn": options_source["valueColumn"],
                "labelColumn": options_source["labelColumn"],
                "addEmpty": "true" if options_source.get("addEmpty", True) else "false",
                "emptyLabel": options_source.get("emptyLabel", ""),
                "useAjax": "true" if options_source.get("useAjax", False) else "false",
                "joins": [],
                "filters": [],
            }

            # Optional grouping column
            if grouping := options_source.get("groupingColumn"):
                props["groupingColumn"] = grouping
            else:
                props["groupingColumn"] = ""

            # Optional extra SQL condition
            if extra := options_source.get("extraCondition"):
                props["extraCondition"] = extra
            else:
                props["extraCondition"] = ""

            return {
                "className": "org.joget.plugin.enterprise.DatabaseWizardOptionsBinder",
                "properties": props,
            }

        else:
            # Fallback to empty static options
            return self._build_static_options([])
