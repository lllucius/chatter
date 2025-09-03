"""Comprehensive tests for prompts API."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.models.prompt import Prompt, PromptType, PromptCategory
from chatter.schemas.prompt import PromptCreate, PromptUpdate
from chatter.core.prompts import PromptService, PromptError


class TestPromptsAPI:
    """Test cases for prompts API endpoints."""

    @pytest.mark.asyncio
    async def test_create_prompt_success(self, client: AsyncClient, auth_headers: dict):
        """Test successful prompt creation."""
        prompt_data = {
            "name": "Test Prompt",
            "description": "A test prompt",
            "content": "Hello {name}, how are you?",
            "variables": ["name"],
            "prompt_type": "template",
            "category": "general",
            "template_format": "f-string"
        }
        
        response = await client.post(
            "/api/v1/prompts/",
            json=prompt_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == prompt_data["name"]
        assert data["content"] == prompt_data["content"]
        assert data["variables"] == prompt_data["variables"]

    @pytest.mark.asyncio
    async def test_create_prompt_validation_error(self, client: AsyncClient, auth_headers: dict):
        """Test prompt creation with validation errors."""
        # Test with dangerous content
        prompt_data = {
            "name": "Malicious Prompt",
            "content": "Hello {name}, let's exec('rm -rf /')",
            "variables": ["name"],
            "template_format": "f-string"
        }
        
        response = await client.post(
            "/api/v1/prompts/",
            json=prompt_data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "dangerous pattern" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_create_prompt_chain_validation(self, client: AsyncClient, auth_headers: dict):
        """Test chain prompt validation."""
        # Test chain prompt without chain_steps
        prompt_data = {
            "name": "Invalid Chain",
            "content": "Step 1: {input}",
            "is_chain": True,
            "template_format": "f-string"
        }
        
        response = await client.post(
            "/api/v1/prompts/",
            json=prompt_data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "chain_steps" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_list_prompts_with_valid_sort(self, client: AsyncClient, auth_headers: dict):
        """Test listing prompts with valid sort parameters."""
        response = await client.get(
            "/api/v1/prompts/?sort_by=created_at&sort_order=desc",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "prompts" in data
        assert "total_count" in data

    @pytest.mark.asyncio
    async def test_list_prompts_invalid_sort_column(self, client: AsyncClient, auth_headers: dict):
        """Test listing prompts with invalid sort column."""
        response = await client.get(
            "/api/v1/prompts/?sort_by=malicious_column",
            headers=auth_headers
        )
        
        # Should return 422 validation error due to pattern validation
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_prompt_success(self, client: AsyncClient, auth_headers: dict):
        """Test getting a prompt successfully."""
        # First create a prompt
        prompt_data = {
            "name": "Get Test Prompt",
            "content": "Test content for {variable}",
            "variables": ["variable"],
            "template_format": "f-string"
        }
        
        create_response = await client.post(
            "/api/v1/prompts/",
            json=prompt_data,
            headers=auth_headers
        )
        prompt_id = create_response.json()["id"]
        
        # Now get the prompt
        response = await client.get(
            f"/api/v1/prompts/{prompt_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == prompt_id
        assert data["name"] == prompt_data["name"]

    @pytest.mark.asyncio
    async def test_update_prompt_success(self, client: AsyncClient, auth_headers: dict):
        """Test updating a prompt successfully."""
        # First create a prompt
        prompt_data = {
            "name": "Update Test Prompt",
            "content": "Original content",
            "template_format": "f-string"
        }
        
        create_response = await client.post(
            "/api/v1/prompts/",
            json=prompt_data,
            headers=auth_headers
        )
        prompt_id = create_response.json()["id"]
        
        # Update the prompt
        update_data = {
            "name": "Updated Prompt Name",
            "content": "Updated content for {user}"
        }
        
        response = await client.put(
            f"/api/v1/prompts/{prompt_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["content"] == update_data["content"]

    @pytest.mark.asyncio
    async def test_delete_prompt_success(self, client: AsyncClient, auth_headers: dict):
        """Test deleting a prompt successfully."""
        # First create a prompt
        prompt_data = {
            "name": "Delete Test Prompt",
            "content": "Content to be deleted",
            "template_format": "f-string"
        }
        
        create_response = await client.post(
            "/api/v1/prompts/",
            json=prompt_data,
            headers=auth_headers
        )
        prompt_id = create_response.json()["id"]
        
        # Delete the prompt
        response = await client.delete(
            f"/api/v1/prompts/{prompt_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]

    @pytest.mark.asyncio
    async def test_test_prompt_success(self, client: AsyncClient, auth_headers: dict):
        """Test prompt testing functionality."""
        # First create a prompt
        prompt_data = {
            "name": "Test Render Prompt",
            "content": "Hello {name}, your age is {age}",
            "variables": ["name", "age"],
            "required_variables": ["name"],
            "template_format": "f-string"
        }
        
        create_response = await client.post(
            "/api/v1/prompts/",
            json=prompt_data,
            headers=auth_headers
        )
        prompt_id = create_response.json()["id"]
        
        # Test the prompt
        test_data = {
            "variables": {"name": "John", "age": "25"},
            "validate_only": False
        }
        
        response = await client.post(
            f"/api/v1/prompts/{prompt_id}/test",
            json=test_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "rendered_content" in data
        assert "validation_result" in data
        assert data["validation_result"]["valid"] is True

    @pytest.mark.asyncio
    async def test_clone_prompt_success(self, client: AsyncClient, auth_headers: dict):
        """Test cloning a prompt successfully."""
        # First create a prompt
        prompt_data = {
            "name": "Original Prompt",
            "content": "Original content for {variable}",
            "variables": ["variable"],
            "template_format": "f-string"
        }
        
        create_response = await client.post(
            "/api/v1/prompts/",
            json=prompt_data,
            headers=auth_headers
        )
        prompt_id = create_response.json()["id"]
        
        # Clone the prompt
        clone_data = {
            "name": "Cloned Prompt",
            "description": "A cloned version"
        }
        
        response = await client.post(
            f"/api/v1/prompts/{prompt_id}/clone",
            json=clone_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == clone_data["name"]
        assert data["description"] == clone_data["description"]
        assert data["content"] == prompt_data["content"]

    @pytest.mark.asyncio
    async def test_get_prompt_stats(self, client: AsyncClient, auth_headers: dict):
        """Test getting prompt statistics."""
        response = await client.get(
            "/api/v1/prompts/stats/overview",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_prompts" in data
        assert "prompts_by_type" in data
        assert "prompts_by_category" in data
        assert "usage_stats" in data


class TestPromptService:
    """Test cases for PromptService class."""

    @pytest.mark.asyncio
    async def test_safe_sort_column(self, db_session: AsyncSession):
        """Test safe sort column validation."""
        service = PromptService(db_session)
        
        # Test valid sort column
        column = service._get_safe_sort_column("created_at")
        assert column is not None
        
        # Test invalid sort column (should default to created_at)
        column = service._get_safe_sort_column("malicious_column")
        assert column is not None  # Should default to a safe column

    @pytest.mark.asyncio
    async def test_create_prompt_duplicate_name(self, db_session: AsyncSession, test_user):
        """Test creating prompt with duplicate name."""
        service = PromptService(db_session)
        
        prompt_data = PromptCreate(
            name="Duplicate Test",
            content="First prompt content",
            template_format="f-string"
        )
        
        # Create first prompt
        await service.create_prompt(test_user.id, prompt_data)
        
        # Try to create second prompt with same name
        with pytest.raises(PromptError, match="already exists"):
            await service.create_prompt(test_user.id, prompt_data)


class TestTemplateRendering:
    """Test cases for template rendering security."""

    def test_safe_template_rendering(self):
        """Test that template rendering is secure."""
        prompt = Prompt(
            name="Test",
            content="Hello {name}",
            template_format="f-string",
            owner_id="test_user",
            content_hash="test_hash"
        )
        
        # Test normal rendering
        result = prompt.render(name="John")
        assert "Hello John" in result
        
        # Test with potentially dangerous input
        try:
            result = prompt.render(name="<script>alert('xss')</script>")
            # Should be escaped
            assert "&lt;script&gt;" in result or "alert" not in result
        except ValueError:
            # Or should raise an error
            pass

    def test_template_variable_validation(self):
        """Test template variable validation."""
        prompt = Prompt(
            name="Test",
            content="Hello {name}",
            template_format="f-string",
            owner_id="test_user",
            content_hash="test_hash",
            required_variables=["name"]
        )
        
        # Test validation with missing required variable
        result = prompt.validate_variables()
        assert not result["valid"]
        assert "name" in result["missing_required"]
        
        # Test validation with all required variables
        result = prompt.validate_variables(name="John")
        assert result["valid"]


class TestSecurityValidation:
    """Test cases for security validation."""

    def test_content_sanitization(self):
        """Test that dangerous content is rejected."""
        with pytest.raises(ValueError, match="dangerous pattern"):
            PromptCreate(
                name="Malicious",
                content="Let's exec('rm -rf /')",
                template_format="f-string"
            )

    def test_variable_name_validation(self):
        """Test that invalid variable names are rejected."""
        with pytest.raises(ValueError, match="Invalid variable name"):
            PromptCreate(
                name="Test",
                content="Hello {name}",
                variables=["invalid-variable-name"],
                template_format="f-string"
            )

    def test_template_format_validation(self):
        """Test that invalid template formats are rejected."""
        with pytest.raises(ValueError, match="Template format must be one of"):
            PromptCreate(
                name="Test",
                content="Hello {name}",
                template_format="invalid_format"
            )


class TestPerformanceOptimizations:
    """Test cases for performance optimizations."""

    @pytest.mark.asyncio
    async def test_optimized_stats_query(self, db_session: AsyncSession, test_user):
        """Test that stats collection is optimized."""
        service = PromptService(db_session)
        
        # Create multiple prompts
        for i in range(5):
            prompt_data = PromptCreate(
                name=f"Test Prompt {i}",
                content=f"Content {i}",
                prompt_type=PromptType.TEMPLATE,
                category=PromptCategory.GENERAL,
                template_format="f-string"
            )
            await service.create_prompt(test_user.id, prompt_data)
        
        # Get stats - should be efficient
        stats = await service.get_prompt_stats(test_user.id)
        
        assert stats["total_prompts"] == 5
        assert "prompts_by_type" in stats
        assert "prompts_by_category" in stats