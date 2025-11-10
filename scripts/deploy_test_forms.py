#!/usr/bin/env python3
"""Deploy generated MDM test forms to Joget for validation."""

import json
import sys
from pathlib import Path

# Add gam_utilities to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "gam_utilities" / "joget_utility"))

from joget_client import JogetClient
from dotenv import load_dotenv
import os

# Load environment from gam_utilities
env_path = Path(__file__).parent.parent.parent / "gam_utilities" / ".env.3"
load_dotenv(env_path, override=True)

def deploy_form(form_json_path: Path, app_id: str = "farmlandRegistry"):
    """
    Deploy a single form to Joget.

    Args:
        form_json_path: Path to generated form JSON file
        app_id: Target application ID
    """
    # Read form JSON
    with open(form_json_path) as f:
        form_def = json.load(f)

    # Extract form metadata
    form_id = form_def["properties"]["id"]
    form_name = form_def["properties"]["name"]
    table_name = form_def["properties"]["tableName"]

    print(f"\n{'='*60}")
    print(f"Deploying: {form_id}")
    print(f"Name: {form_name}")
    print(f"Table: {table_name}")
    print(f"{'='*60}\n")

    # Prepare payload
    payload = {
        "target_app_id": app_id,
        "target_app_version": "1",
        "form_id": form_id,
        "form_name": form_name,
        "table_name": table_name,
        "form_definition_json": json.dumps(form_def, ensure_ascii=False),
        "create_api_endpoint": "yes",
        "api_name": f"api_{form_id}",
        "create_crud": "yes"
    }

    # Create client
    base_url = os.getenv("JOGET_BASE_URL", "http://localhost:8888/jw/api")
    client = JogetClient(base_url=base_url, debug=True)

    # FormCreator API credentials
    api_id = "API-d248866d-355c-43a5-a973-87fd7de1bc0a"
    api_key = "88d2fb10d08f48d3952dab1023b642fd"

    try:
        # Deploy form
        response = client.create_form(
            payload=payload,
            api_id=api_id,
            api_key=api_key
        )

        print(f"✅ Form deployed successfully!")
        print(f"Response: {json.dumps(response, indent=2)}")

        # Query database for created API
        db_config = {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", 3308)),
            "database": os.getenv("DB_NAME", "jwdb"),
            "user": os.getenv("DB_USER", "root"),
            "password": os.getenv("DB_PASSWORD")
        }

        api_id_created = client.get_api_id_for_form(
            app_id=app_id,
            app_version="1",
            api_name=f"api_{form_id}",
            db_config=db_config
        )

        if api_id_created:
            print(f"✅ API created: {api_id_created}")
        else:
            print(f"⚠️  API not found in database (may need manual verification)")

        return True

    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Deploy test forms."""
    # Forms to deploy
    forms = [
        Path("/tmp/mdm_test/md01maritalStatus.json"),
        Path("/tmp/mdm_test/md25equipment.json")
    ]

    results = {}
    for form_path in forms:
        if not form_path.exists():
            print(f"❌ Form not found: {form_path}")
            results[form_path.stem] = False
            continue

        results[form_path.stem] = deploy_form(form_path)

    # Summary
    print(f"\n{'='*60}")
    print("DEPLOYMENT SUMMARY")
    print(f"{'='*60}")
    for form_id, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{form_id}: {status}")
    print(f"{'='*60}\n")

    # Exit code
    sys.exit(0 if all(results.values()) else 1)

if __name__ == "__main__":
    main()
