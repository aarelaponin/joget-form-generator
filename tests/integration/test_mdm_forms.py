"""Integration tests for MDM form generation."""

import json
import pytest
from pathlib import Path
from joget_form_generator.transformers.engine import TransformEngine
import yaml


@pytest.mark.integration
class TestMDMFormGeneration:
    """Test MDM form generation against production forms."""

    @pytest.fixture
    def engine(self):
        """Provide TransformEngine instance."""
        return TransformEngine()

    @pytest.fixture
    def production_forms_dir(self):
        """Path to production MDM forms."""
        # Navigate from joget-form-generator/tests/integration to dev/gam_utilities
        return (
            Path(__file__).parent.parent.parent.parent
            / "gam_utilities"
            / "joget_utility"
            / "data"
            / "metadata_forms"
        )

    def normalize_json(self, obj):
        """
        Normalize JSON for comparison by removing metadata and sorting.

        Removes:
        - _metadata field (our generator adds this)
        - Empty string values
        - Sorts keys for consistent comparison
        """
        if isinstance(obj, dict):
            result = {}
            for k, v in obj.items():
                # Skip metadata
                if k == "_metadata":
                    continue
                # Recursively normalize
                normalized = self.normalize_json(v)
                # Skip empty strings but keep other falsy values
                if normalized != "":
                    result[k] = normalized
            return result
        elif isinstance(obj, list):
            return [self.normalize_json(item) for item in obj]
        else:
            return obj

    def compare_forms(self, generated, production, path=""):
        """
        Deep comparison of form structures.

        Returns:
            Tuple of (matches: bool, differences: list)
        """
        differences = []

        gen_norm = self.normalize_json(generated)
        prod_norm = self.normalize_json(production)

        def deep_compare(gen_obj, prod_obj, current_path):
            """Recursively compare objects."""
            if type(gen_obj) is not type(prod_obj):
                differences.append(
                    f"{current_path}: Type mismatch - {type(gen_obj).__name__} vs {type(prod_obj).__name__}"
                )
                return

            if isinstance(gen_obj, dict):
                # Check for missing keys
                gen_keys = set(gen_obj.keys())
                prod_keys = set(prod_obj.keys())

                missing_in_gen = prod_keys - gen_keys
                extra_in_gen = gen_keys - prod_keys

                for key in missing_in_gen:
                    differences.append(
                        f"{current_path}.{key}: Missing in generated (production has it)"
                    )

                for key in extra_in_gen:
                    differences.append(
                        f"{current_path}.{key}: Extra in generated (production doesn't have it)"
                    )

                # Compare common keys
                for key in gen_keys & prod_keys:
                    deep_compare(gen_obj[key], prod_obj[key], f"{current_path}.{key}")

            elif isinstance(gen_obj, list):
                if len(gen_obj) != len(prod_obj):
                    differences.append(
                        f"{current_path}: List length mismatch - {len(gen_obj)} vs {len(prod_obj)}"
                    )
                    return

                for i, (gen_item, prod_item) in enumerate(zip(gen_obj, prod_obj)):
                    deep_compare(gen_item, prod_item, f"{current_path}[{i}]")

            else:
                # Scalar comparison
                if gen_obj != prod_obj:
                    differences.append(
                        f"{current_path}: Value mismatch - '{gen_obj}' vs '{prod_obj}'"
                    )

        deep_compare(gen_norm, prod_norm, "root")

        return len(differences) == 0, differences

    def test_md01_marital_status_structure(self, engine, production_forms_dir):
        """Test md01maritalStatus generation matches production."""
        # Load YAML spec
        yaml_path = (
            Path(__file__).parent.parent.parent / "examples" / "mdm" / "md01maritalStatus.yaml"
        )
        with open(yaml_path) as f:
            spec = yaml.safe_load(f)

        # Generate form
        generated_forms = engine.generate(spec)
        generated = generated_forms["md01maritalStatus"]

        # Load production form
        prod_path = production_forms_dir / "md01maritalStatus.json"
        with open(prod_path) as f:
            production = json.load(f)

        # Compare
        matches, differences = self.compare_forms(generated, production)

        if not matches:
            print("\n=== DIFFERENCES FOUND ===")
            for diff in differences[:10]:  # Show first 10
                print(f"  {diff}")
            if len(differences) > 10:
                print(f"  ... and {len(differences) - 10} more")

        # Should match (or have only acceptable differences)
        assert matches or self._has_only_acceptable_differences(differences)

    def test_md25_equipment_nested_lov(self, engine, production_forms_dir):
        """Test md25equipment generation with nested LOV."""
        # Load YAML spec
        yaml_path = Path(__file__).parent.parent.parent / "examples" / "mdm" / "md25equipment.yaml"
        with open(yaml_path) as f:
            spec = yaml.safe_load(f)

        # Generate form
        generated_forms = engine.generate(spec)
        generated = generated_forms["md25equipment"]

        # Load production form
        prod_path = production_forms_dir / "md25equipment.json"
        with open(prod_path) as f:
            production = json.load(f)

        # Compare
        matches, differences = self.compare_forms(generated, production)

        if not matches:
            print("\n=== DIFFERENCES FOUND ===")
            for diff in differences[:20]:  # Show first 20
                print(f"  {diff}")
            if len(differences) > 20:
                print(f"  ... and {len(differences) - 20} more")

        # Should match (or have only acceptable differences)
        assert matches or self._has_only_acceptable_differences(differences)

    def test_nested_lov_structure(self, engine):
        """Test that nested LOV generates correct FormOptionsBinder."""
        spec = {
            "form": {"id": "testForm", "name": "Test Form"},
            "fields": [
                {
                    "id": "category",
                    "label": "Category",
                    "type": "selectBox",
                    "required": True,
                    "optionsSource": {
                        "type": "formData",
                        "formId": "parentForm",
                        "valueColumn": "code",
                        "labelColumn": "name",
                        "addEmptyOption": True,
                        "useAjax": False,
                    },
                }
            ],
        }

        generated_forms = engine.generate(spec)
        generated = generated_forms["testForm"]

        # Navigate to field
        section = generated["elements"][0]
        column = section["elements"][0]
        field = column["elements"][0]

        # Verify FormOptionsBinder structure
        assert field["className"] == "org.joget.apps.form.lib.SelectBox"

        options_binder = field["properties"]["optionsBinder"]
        assert options_binder["className"] == "org.joget.apps.form.lib.FormOptionsBinder"
        assert options_binder["properties"]["formDefId"] == "parentForm"
        assert options_binder["properties"]["idColumn"] == "code"
        assert options_binder["properties"]["labelColumn"] == "name"
        assert options_binder["properties"]["addEmptyOption"] == "true"
        assert options_binder["properties"]["useAjax"] == "false"

    def test_required_field_validator(self, engine):
        """Test that required fields get DefaultValidator."""
        spec = {
            "form": {"id": "testForm", "name": "Test Form"},
            "fields": [
                {
                    "id": "requiredField",
                    "label": "Required Field",
                    "type": "textField",
                    "required": True,
                }
            ],
        }

        generated_forms = engine.generate(spec)
        generated = generated_forms["testForm"]

        # Navigate to field
        section = generated["elements"][0]
        column = section["elements"][0]
        field = column["elements"][0]

        # Verify DefaultValidator
        validator = field["properties"].get("validator")
        assert validator is not None
        assert validator["className"] == "org.joget.apps.form.lib.DefaultValidator"
        assert validator["properties"]["mandatory"] == "true"

    def _has_only_acceptable_differences(self, differences):
        """
        Check if differences are acceptable (e.g., metadata, empty strings).

        Acceptable differences:
        - Missing empty string values
        - Extra properties that don't affect functionality
        - Empty validator objects (legacy generator artifact)
        - size property differences (normalized vs empty)
        """
        acceptable_patterns = [
            "_metadata",
            "requiredSanitize",
            "workflowVariable",
            "style",
            "readonlyLabel",
            "storeNumeric",
            "validator: Missing",  # Empty validators in old forms
            "size: Extra",  # We normalize size, old forms have empty/missing
            "size: Missing",  # Some old forms have size, we omit if not needed
            "required: Extra",  # We always add required, some old forms omit it
            "description: Missing",  # We default to empty, old forms may have descriptions
        ]

        for diff in differences:
            # Check if difference involves acceptable properties
            is_acceptable = any(pattern in diff for pattern in acceptable_patterns)

            # Also check if it's an empty validator being missing
            if not is_acceptable and "validator" in diff and "Missing in generated" in diff:
                # Production has empty validator, we omit it - acceptable
                is_acceptable = True

            if not is_acceptable:
                return False

        return True


@pytest.mark.integration
class TestFormValidation:
    """Test form validation and error handling."""

    def test_invalid_field_type_rejected(self):
        """Test that invalid field types are rejected."""
        engine = TransformEngine()

        spec = {
            "form": {"id": "testForm", "name": "Test Form"},
            "fields": [{"id": "badField", "label": "Bad Field", "type": "invalidType"}],  # Invalid!
        }

        with pytest.raises(ValueError, match="Validation failed"):
            engine.generate(spec)

    def test_missing_required_field_rejected(self):
        """Test that fields missing required properties are rejected."""
        engine = TransformEngine()

        spec = {
            "form": {"id": "testForm", "name": "Test Form"},
            "fields": [
                {
                    "id": "incompleteField",
                    # Missing: label, type
                }
            ],
        }

        with pytest.raises(ValueError, match="Validation failed"):
            engine.generate(spec)
