#!/usr/bin/env python3
"""Generate Pydantic models from JSON Schema."""

import subprocess
from pathlib import Path


def generate_models():
    """Generate Pydantic models from JSON Schema."""

    project_root = Path(__file__).parent.parent
    schema_file = project_root / "src/joget_form_generator/schema/form_spec_schema.json"
    output_file = project_root / "src/joget_form_generator/models/spec.py"

    print(f"Generating Pydantic models...")
    print(f"  Schema: {schema_file}")
    print(f"  Output: {output_file}")

    cmd = [
        "datamodel-codegen",
        "--input", str(schema_file),
        "--output", str(output_file),
        "--input-file-type", "jsonschema",
        "--use-schema-description",
        "--use-field-description",
        "--field-constraints",
        "--use-default",
        "--target-python-version", "3.10",
        "--use-standard-collections",
        "--use-union-operator",
        "--output-model-type", "pydantic_v2.BaseModel",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ Generation failed:")
        print(result.stderr)
        return False

    print(f"✓ Generated: {output_file}")

    # Add header comment to generated file
    with open(output_file, 'r') as f:
        content = f.read()

    header = '''"""
Pydantic models for form specifications.

⚠️  AUTO-GENERATED FROM JSON SCHEMA - DO NOT EDIT MANUALLY
Source: src/joget_form_generator/schema/form_spec_schema.json
Regenerate: python scripts/generate_models.py
"""

'''

    with open(output_file, 'w') as f:
        f.write(header + content)

    print("✓ Added header comment")
    return True


if __name__ == "__main__":
    success = generate_models()
    exit(0 if success else 1)
