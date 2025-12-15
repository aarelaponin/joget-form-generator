# Form Specifications

This folder contains YAML specifications for Joget DX forms.

## Usage

Place your `.yaml` form specification files here, then generate Joget JSON:

```bash
# Generate a single form
joget-form-gen generate specs/my_form.yaml -o output/

# Generate all specs in a subfolder
joget-form-gen generate specs/mdm/*.yaml -o output/mdm/
```

## Folder Structure

Organize specs by module or domain:

```
specs/
├── mdm/              # Master Data Management forms
├── hr/               # Human Resources forms
├── finance/          # Finance forms
└── ...
```

## Naming Convention

- Use descriptive names: `employee_registration.yaml`, `leave_request.yaml`
- For MDM forms: `md01_marital_status.yaml`, `md25_equipment.yaml`
- Keep form ID and filename aligned for easy reference

## Specification Reference

See [YAML Specification Reference](../docs/YAML_SPECIFICATION.md) for complete documentation on:
- Form metadata requirements
- All 17 supported field types
- Options sources (static, formData, api, database)
- Validation rules
- Examples
