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

        Args:
            field: Field specification with optional 'validation' key

        Returns:
            Joget validator dict or None if no validation
        """
        validation = field.get("validation")
        if not validation:
            return None

        validators = []

        # Regex pattern validator
        if pattern := validation.get("pattern"):
            validators.append(
                {
                    "className": "org.joget.apps.form.lib.RegexValidator",
                    "properties": {
                        "regex": pattern,
                        "message": validation.get("message", "Invalid format"),
                    },
                }
            )

        # Minimum length validator
        if (min_len := validation.get("minLength")) is not None:
            validators.append(
                {
                    "className": "org.joget.apps.form.lib.TextFieldLengthValidator",
                    "properties": {
                        "minLength": str(min_len),
                        "message": validation.get(
                            "message", f"Minimum {min_len} characters required"
                        ),
                    },
                }
            )

        # Maximum length validator
        if (max_len := validation.get("maxLength")) is not None:
            validators.append(
                {
                    "className": "org.joget.apps.form.lib.TextFieldLengthValidator",
                    "properties": {
                        "maxLength": str(max_len),
                        "message": validation.get(
                            "message", f"Maximum {max_len} characters allowed"
                        ),
                    },
                }
            )

        # Return single validator or multi-validator
        if len(validators) == 0:
            return None
        elif len(validators) == 1:
            return validators[0]
        else:
            return {
                "className": "org.joget.apps.form.lib.MultiValidator",
                "properties": {"validators": validators},
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
        option_list = [
            {"value": opt["value"], "label": opt["label"]} for opt in options
        ]

        return {
            "className": "org.joget.apps.form.lib.FormOptionsBinder",
            "properties": {"formDefId": "", "options": option_list},
        }

    def _build_dynamic_options(
        self, options_source: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Build options binder for dynamic/cascading options."""

        source_type = options_source["type"]

        if source_type == "formData":
            # Cascading dropdown (get options from another form)
            return {
                "className": "org.joget.apps.form.model.FormLoadBinder",
                "properties": {
                    "formDefId": options_source["formId"],
                    "keyColumn": options_source.get("valueColumn", "id"),
                    "labelColumn": options_source.get("labelColumn", "name"),
                    # Cascading configuration
                    "parentFieldId": options_source.get("parentField", ""),
                    "filterField": options_source.get("filterField", ""),
                    "extraCondition": options_source.get("extraCondition", ""),
                },
            }

        elif source_type == "api":
            # API-based options
            return {
                "className": "org.joget.apps.form.lib.RestApiFormBinder",
                "properties": {
                    "url": options_source["url"],
                    "method": options_source.get("method", "GET"),
                    "valueJsonPath": options_source.get("valueJsonPath", "$.value"),
                    "labelJsonPath": options_source.get("labelJsonPath", "$.label"),
                },
            }

        elif source_type == "database":
            # Direct database query
            return {
                "className": "org.joget.apps.form.lib.JdbcOptionsBinder",
                "properties": {
                    "datasource": options_source.get("datasource", "default"),
                    "sql": options_source.get("sql", ""),
                    "useAjax": "true",
                },
            }

        else:
            # Fallback to empty static options
            return self._build_static_options([])
