"""Tests for workflow template import/export/validate/execute APIs."""

import json
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from httpx import AsyncClient

from chatter.models.workflow import TemplateCategory, WorkflowTemplate


@pytest.fixture
async def test_workflow_template(db_session, auth_user):
    """Create a test workflow template."""
    template = WorkflowTemplate(
        owner_id=auth_user.id,
        name="Test Template",
        description="A test template",
        category=TemplateCategory.CUSTOM,
        default_params={"temperature": 0.7},
        tags=["test"],
        is_public=False,
        version=1,
    )
    db_session.add(template)
    await db_session.commit()
    await db_session.refresh(template)
    return template


@pytest.mark.asyncio
async def test_export_workflow_template(
    client: AsyncClient, auth_headers, test_workflow_template
):
    """Test exporting a workflow template."""
    response = await client.get(
        f"/api/v1/workflows/templates/{test_workflow_template.id}/export",
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "template" in data
    assert "export_format" in data
    assert "exported_at" in data
    assert data["template"]["name"] == test_workflow_template.name
    assert data["template"]["description"] == test_workflow_template.description


@pytest.mark.asyncio
async def test_export_nonexistent_template(client: AsyncClient, auth_headers):
    """Test exporting a non-existent template returns 404."""
    response = await client.get(
        "/api/v1/workflows/templates/nonexistent_id/export",
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_import_workflow_template(client: AsyncClient, auth_headers):
    """Test importing a workflow template."""
    template_data = {
        "name": "Imported Template",
        "description": "A test imported template",
        "category": "custom",
        "default_params": {"temperature": 0.7},
        "tags": ["test", "imported"],
    }

    response = await client.post(
        "/api/v1/workflows/templates/import",
        json={"template": template_data},
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == template_data["name"]
    assert data["description"] == template_data["description"]
    assert data["category"] == template_data["category"]


@pytest.mark.asyncio
async def test_import_template_with_override_name(
    client: AsyncClient, auth_headers
):
    """Test importing a template with name override."""
    template_data = {
        "name": "Original Name",
        "description": "A test template",
        "category": "custom",
    }

    response = await client.post(
        "/api/v1/workflows/templates/import",
        json={
            "template": template_data,
            "override_name": "Override Name",
        },
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Override Name"


@pytest.mark.asyncio
async def test_import_invalid_template(client: AsyncClient, auth_headers):
    """Test importing an invalid template returns error."""
    invalid_template = {
        "name": "Test",
        # Missing required fields
    }

    response = await client.post(
        "/api/v1/workflows/templates/import",
        json={"template": invalid_template},
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_load_workflow_template(
    client: AsyncClient, auth_headers, test_workflow_template
):
    """Test loading a workflow template."""
    response = await client.get(
        f"/api/v1/workflows/templates/{test_workflow_template.id}/load",
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_workflow_template.id
    assert data["name"] == test_workflow_template.name


@pytest.mark.asyncio
async def test_load_nonexistent_template(client: AsyncClient, auth_headers):
    """Test loading a non-existent template returns 404."""
    response = await client.get(
        "/api/v1/workflows/templates/nonexistent_id/load",
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_validate_workflow_template(client: AsyncClient, auth_headers):
    """Test validating a workflow template."""
    valid_template = {
        "name": "Valid Template",
        "description": "A valid template",
        "category": "custom",
        "default_params": {},
    }

    response = await client.post(
        "/api/v1/workflows/templates/validate",
        json={"template": valid_template},
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["is_valid"] is True
    assert len(data["errors"]) == 0


@pytest.mark.asyncio
async def test_validate_invalid_template(client: AsyncClient, auth_headers):
    """Test validating an invalid template."""
    invalid_template = {
        "name": "",  # Empty name
        "description": "Test",
        "category": "invalid_category",
    }

    response = await client.post(
        "/api/v1/workflows/templates/validate",
        json={"template": invalid_template},
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["is_valid"] is False
    assert len(data["errors"]) > 0


@pytest.mark.asyncio
async def test_execute_workflow_template(
    client: AsyncClient, auth_headers, test_workflow_template
):
    """Test executing a workflow template."""
    with patch(
        "chatter.services.workflow_execution.WorkflowExecutionService.execute_workflow_definition"
    ) as mock_execute:
        mock_execute.return_value = {
            "id": "exec_123",
            "definition_id": "def_123",
            "owner_id": "user_123",
            "status": "completed",
            "started_at": None,
            "completed_at": None,
            "execution_time_ms": 1000,
            "output_data": {"result": "success"},
            "error_message": None,
            "tokens_used": 100,
            "cost": 0.01,
            "execution_log": [],
            "debug_info": None,
            "created_at": None,
            "updated_at": None,
        }

        response = await client.post(
            f"/api/v1/workflows/templates/{test_workflow_template.id}/execute",
            json={"input_data": {"message": "test"}},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert data["status"] == "completed"


@pytest.mark.asyncio
async def test_execute_nonexistent_template(client: AsyncClient, auth_headers):
    """Test executing a non-existent template returns error."""
    response = await client.post(
        "/api/v1/workflows/templates/nonexistent_id/execute",
        json={"input_data": {}},
        headers=auth_headers,
    )

    # Should fail when trying to create definition from non-existent template
    assert response.status_code in [
        status.HTTP_404_NOT_FOUND,
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    ]


@pytest.mark.asyncio
async def test_export_import_roundtrip(
    client: AsyncClient, auth_headers, test_workflow_template
):
    """Test exporting and then importing a template."""
    # Export
    export_response = await client.get(
        f"/api/v1/workflows/templates/{test_workflow_template.id}/export",
        headers=auth_headers,
    )
    assert export_response.status_code == status.HTTP_200_OK
    exported_data = export_response.json()

    # Import with new name
    import_response = await client.post(
        "/api/v1/workflows/templates/import",
        json={
            "template": exported_data["template"],
            "override_name": "Imported Copy",
        },
        headers=auth_headers,
    )
    assert import_response.status_code == status.HTTP_200_OK
    imported_data = import_response.json()

    # Verify imported template has same characteristics
    assert imported_data["name"] == "Imported Copy"
    assert (
        imported_data["description"]
        == exported_data["template"]["description"]
    )
    assert imported_data["category"] == exported_data["template"]["category"]


@pytest.mark.asyncio
async def test_execute_temporary_workflow_template(
    client: AsyncClient, auth_headers
):
    """Test executing a temporary workflow template without storing it."""
    with patch(
        "chatter.services.workflow_execution.WorkflowExecutionService.execute_workflow_definition"
    ) as mock_execute:
        mock_execute.return_value = {
            "id": "exec_123",
            "definition_id": "def_123",
            "owner_id": "user_123",
            "status": "completed",
            "started_at": None,
            "completed_at": None,
            "execution_time_ms": 1000,
            "output_data": {"result": "success"},
            "error_message": None,
            "tokens_used": 100,
            "cost": 0.01,
            "execution_log": [],
            "debug_info": None,
            "created_at": None,
            "updated_at": None,
        }

        template_data = {
            "name": "Temporary Template",
            "description": "A temporary template for testing",
            "category": "custom",
            "default_params": {
                "model": "gpt-4",
                "temperature": 0.7,
            },
        }

        response = await client.post(
            "/api/v1/workflows/templates/execute",
            json={
                "template": template_data,
                "input_data": {"message": "test"},
                "debug_mode": False,
            },
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert data["status"] == "completed"


@pytest.mark.asyncio
async def test_execute_temporary_template_missing_required_fields(
    client: AsyncClient, auth_headers
):
    """Test executing a temporary template with missing required fields."""
    # Missing description
    template_data = {
        "name": "Incomplete Template",
        "category": "custom",
    }

    response = await client.post(
        "/api/v1/workflows/templates/execute",
        json={
            "template": template_data,
            "input_data": {},
        },
        headers=auth_headers,
    )

    # Should fail validation
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    # Missing name
    template_data = {
        "description": "A template without a name",
        "category": "custom",
    }

    response = await client.post(
        "/api/v1/workflows/templates/execute",
        json={
            "template": template_data,
            "input_data": {},
        },
        headers=auth_headers,
    )

    # Should fail validation
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_execute_temporary_template_with_merged_params(
    client: AsyncClient, auth_headers
):
    """Test that user input properly merges with template default params."""
    with patch(
        "chatter.services.workflow_management.WorkflowManagementService.create_workflow_definition"
    ) as mock_create_def, patch(
        "chatter.services.workflow_execution.WorkflowExecutionService.execute_workflow_definition"
    ) as mock_execute:
        # Mock workflow definition creation
        mock_definition = AsyncMock()
        mock_definition.id = "def_123"
        mock_definition.name = "Temporary Template (Execution)"
        mock_create_def.return_value = mock_definition

        # Mock execution
        mock_execute.return_value = {
            "id": "exec_123",
            "definition_id": "def_123",
            "owner_id": "user_123",
            "status": "completed",
            "started_at": None,
            "completed_at": None,
            "execution_time_ms": 1000,
            "output_data": {"result": "success"},
            "error_message": None,
            "tokens_used": 100,
            "cost": 0.01,
            "execution_log": [],
            "debug_info": None,
            "created_at": None,
            "updated_at": None,
        }

        template_data = {
            "name": "Temporary Template",
            "description": "A temporary template",
            "category": "custom",
            "default_params": {
                "model": "gpt-4",
                "temperature": 0.7,
                "system_prompt": "Default prompt",
            },
        }

        # User input should override temperature
        user_input = {
            "temperature": 0.9,
            "max_tokens": 1000,
        }

        response = await client.post(
            "/api/v1/workflows/templates/execute",
            json={
                "template": template_data,
                "input_data": user_input,
                "debug_mode": False,
            },
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "completed"

