"""Tests for Multi Paged Form pattern (Enterprise Edition)."""

from joget_form_generator.patterns.multi_paged_form import MultiPagedFormPattern


def test_basic_multi_paged_form():
    """Test basic multi paged form rendering."""
    pattern = MultiPagedFormPattern()
    field = {
        "id": "wizard",
        "label": "Registration Wizard",
        "type": "multiPagedForm",
        "pages": [
            {"formId": "personalInfo", "label": "Personal Information"},
            {"formId": "addressInfo", "label": "Address"},
        ],
    }

    result = pattern.render(field, {})

    assert result["className"] == "org.joget.plugin.enterprise.PageFormElement"
    assert result["properties"]["id"] == "wizard"
    assert result["properties"]["label"] == "Registration Wizard"
    assert len(result["properties"]["pages"]) == 2
    assert result["properties"]["pages"][0]["formDefId"] == "personalInfo"
    assert result["properties"]["pages"][0]["label"] == "Personal Information"
    assert result["properties"]["showNavigation"] == "true"  # default
    assert result["properties"]["showProgressBar"] == "true"  # default


def test_multi_paged_form_with_descriptions():
    """Test multi paged form with page descriptions."""
    pattern = MultiPagedFormPattern()
    field = {
        "id": "onboarding",
        "type": "multiPagedForm",
        "pages": [
            {
                "formId": "step1",
                "label": "Step 1",
                "description": "Enter your basic information",
            },
            {
                "formId": "step2",
                "label": "Step 2",
                "description": "Review and confirm",
            },
        ],
    }

    result = pattern.render(field, {})

    assert result["properties"]["pages"][0]["description"] == "Enter your basic information"
    assert result["properties"]["pages"][1]["description"] == "Review and confirm"


def test_multi_paged_form_without_navigation():
    """Test multi paged form with navigation hidden."""
    pattern = MultiPagedFormPattern()
    field = {
        "id": "survey",
        "type": "multiPagedForm",
        "pages": [
            {"formId": "page1", "label": "Page 1"},
            {"formId": "page2", "label": "Page 2"},
        ],
        "showNavigation": False,
    }

    result = pattern.render(field, {})

    assert result["properties"]["showNavigation"] == "false"


def test_multi_paged_form_without_progress_bar():
    """Test multi paged form with progress bar hidden."""
    pattern = MultiPagedFormPattern()
    field = {
        "id": "form",
        "type": "multiPagedForm",
        "pages": [
            {"formId": "page1", "label": "Page 1"},
        ],
        "showProgressBar": False,
    }

    result = pattern.render(field, {})

    assert result["properties"]["showProgressBar"] == "false"


def test_multi_paged_form_readonly():
    """Test readonly multi paged form."""
    pattern = MultiPagedFormPattern()
    field = {
        "id": "review",
        "label": "Review Form",
        "type": "multiPagedForm",
        "pages": [
            {"formId": "details", "label": "Details"},
        ],
        "readonly": True,
    }

    result = pattern.render(field, {})

    assert result["properties"]["readonly"] == "true"


def test_multi_paged_form_three_pages():
    """Test multi paged form with three pages."""
    pattern = MultiPagedFormPattern()
    field = {
        "id": "application",
        "type": "multiPagedForm",
        "pages": [
            {"formId": "applicantInfo", "label": "Applicant", "description": "Your information"},
            {
                "formId": "documents",
                "label": "Documents",
                "description": "Upload required documents",
            },
            {"formId": "confirmation", "label": "Confirmation", "description": "Review and submit"},
        ],
    }

    result = pattern.render(field, {})

    assert len(result["properties"]["pages"]) == 3
    assert result["properties"]["pages"][2]["formDefId"] == "confirmation"
