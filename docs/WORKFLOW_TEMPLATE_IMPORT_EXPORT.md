# Workflow Template Import/Export Documentation

## Overview

This feature adds the ability to import, export, validate, load, and execute workflow templates. It allows users to share templates, create backups, and migrate templates between environments.

## API Endpoints

### Export Template

**Endpoint:** `GET /api/v1/workflows/templates/{template_id}/export`

**Description:** Export a workflow template as JSON.

**Response:**
```json
{
  "template": {
    "name": "My Template",
    "description": "Template description",
    "category": "custom",
    "default_params": {},
    "tags": ["tag1", "tag2"],
    "is_public": false,
    "version": 1,
    "metadata": {
      "config_hash": "abc123...",
      "estimated_complexity": 5,
      "export_version": "1.0"
    }
  },
  "export_format": "json",
  "exported_at": "2024-01-01T12:00:00Z"
}
```

### Import Template

**Endpoint:** `POST /api/v1/workflows/templates/import`

**Description:** Import a workflow template from JSON.

**Request:**
```json
{
  "template": {
    "name": "My Template",
    "description": "Template description",
    "category": "custom",
    "default_params": {}
  },
  "override_name": "New Template Name",  // Optional
  "merge_with_existing": false            // Optional
}
```

**Response:** Returns the imported template as `WorkflowTemplateResponse`.

### Load Template

**Endpoint:** `GET /api/v1/workflows/templates/{template_id}/load`

**Description:** Load a workflow template with full details. This is similar to getting a template but explicitly meant for loading purposes.

**Response:** Returns `WorkflowTemplateResponse` with complete template data.

### Validate Template

**Endpoint:** `POST /api/v1/workflows/templates/validate`

**Description:** Validate a workflow template structure before import.

**Request:**
```json
{
  "template": {
    "name": "Template to Validate",
    "description": "...",
    "category": "custom"
  }
}
```

**Response:**
```json
{
  "is_valid": true,
  "errors": [],
  "warnings": ["Template with name 'Template to Validate' already exists"],
  "template_info": {
    "name": "Template to Validate",
    "description": "...",
    "category": "custom",
    "tags": []
  }
}
```

### Execute Template

**Endpoint:** `POST /api/v1/workflows/templates/{template_id}/execute`

**Description:** Execute a workflow template directly by creating a temporary workflow definition and running it.

**Request:**
```json
{
  "input_data": {
    "message": "Hello, world!",
    "options": {
      "temperature": 0.7
    }
  },
  "debug_mode": false
}
```

**Response:** Returns `WorkflowExecutionResponse` with execution results.

## Usage Examples

### Exporting a Template

```typescript
const sdk = await getSDK();
const response = await sdk.workflows.exportWorkflowTemplateApiV1WorkflowsTemplatesTemplateIdExport(
  templateId
);

// Download as file
const blob = new Blob([JSON.stringify(response.template, null, 2)], {
  type: 'application/json',
});
const url = URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = `template_${templateId}.json`;
a.click();
```

### Importing a Template

```typescript
const sdk = await getSDK();
const importedTemplate = await sdk.workflows.importWorkflowTemplateApiV1WorkflowsTemplatesImport({
  template: templateData,
  override_name: "My Imported Template",
  merge_with_existing: false,
});
```

### Validating Before Import

```typescript
const sdk = await getSDK();
const validation = await sdk.workflows.validateWorkflowTemplateApiV1WorkflowsTemplatesValidate({
  template: templateData,
});

if (validation.is_valid) {
  // Proceed with import
} else {
  console.error("Validation errors:", validation.errors);
}
```

### Executing a Template

```typescript
const sdk = await getSDK();
const execution = await sdk.workflows.executeWorkflowTemplateApiV1WorkflowsTemplatesTemplateIdExecute(
  templateId,
  {
    input_data: { message: "Process this" },
    debug_mode: true,
  }
);

console.log("Execution result:", execution.output_data);
```

## Frontend UI

The Workflow Templates page includes:

1. **Export Button**: Each template row has an export action that downloads the template as a JSON file.

2. **Import Button**: In the toolbar, an import button allows users to upload a JSON file containing template data.

3. **Import Dialog**: When importing, users can:
   - Review the imported template JSON
   - Optionally override the template name
   - Choose whether to merge with existing templates

## Template Format

Templates are exported in the following JSON format:

```json
{
  "name": "Template Name",
  "description": "Template description",
  "category": "custom",
  "default_params": {
    "temperature": 0.7,
    "max_tokens": 1000
  },
  "required_tools": ["tool1", "tool2"],
  "required_retrievers": ["retriever1"],
  "tags": ["tag1", "tag2"],
  "is_public": false,
  "version": 1,
  "metadata": {
    "config_hash": "hash_value",
    "estimated_complexity": 5,
    "export_version": "1.0"
  }
}
```

## Security Considerations

1. **Validation**: All imported templates are validated before being created in the database.
2. **Ownership**: Imported templates are always owned by the importing user.
3. **Access Control**: Users can only export templates they own or that are public.
4. **Sanitization**: Template data is sanitized during import to prevent injection attacks.

## Migration and Backup

Templates can be used for:

1. **Backup**: Export templates regularly for backup purposes
2. **Migration**: Move templates between environments (dev, staging, production)
3. **Sharing**: Share templates with team members or the community
4. **Version Control**: Store templates in version control systems

## Best Practices

1. **Naming**: Use descriptive names when importing templates to avoid conflicts
2. **Validation**: Always validate templates before importing
3. **Documentation**: Include comprehensive descriptions in templates
4. **Versioning**: Track template versions when making changes
5. **Testing**: Execute templates in a test environment before production use
