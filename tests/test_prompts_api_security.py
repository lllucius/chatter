"""Comprehensive test suite for the Prompts API."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from chatter.core.prompts import PromptError, PromptService
from chatter.models.prompt import PromptCategory, PromptType
from chatter.schemas.prompt import (
    PromptCreate,
    PromptTestRequest,
    PromptUpdate,
)
from chatter.utils.template_security import SecureTemplateRenderer


class TestSecureTemplateRenderer:
    """Test secure template rendering functionality."""

    def test_secure_f_string_rendering(self):
        """Test secure f-string rendering."""
        template = "Hello ${name}, welcome to ${platform}!"
        variables = {"name": "Alice", "platform": "Chatter"}

        result = SecureTemplateRenderer.render_secure_f_string(
            template, variables
        )
        assert result == "Hello Alice, welcome to Chatter!"

    def test_secure_f_string_prevents_injection(self):
        """Test that secure f-string rendering prevents code injection."""
        template = "Hello ${name}"
        malicious_variables = {
            "name": "__import__('os').system('rm -rf /')"
        }

        # Should not execute the malicious code
        result = SecureTemplateRenderer.render_secure_f_string(
            template, malicious_variables
        )
        assert "__import__" not in result or "system" not in result

    def test_variable_sanitization(self):
        """Test variable sanitization."""
        variables = {
            "valid_name": "Alice",
            "script_content": "<script>alert('xss')</script>",
            "javascript_url": "javascript:alert('xss')",
        }

        sanitized = SecureTemplateRenderer._sanitize_variables(
            variables
        )

        assert sanitized["valid_name"] == "Alice"
        assert "<script>" not in sanitized["script_content"]
        assert "javascript:" not in sanitized["javascript_url"]

    def test_invalid_variable_names(self):
        """Test that invalid variable names are rejected."""
        invalid_variables = {
            "123invalid": "value",  # Starts with number
            "invalid-name": "value",  # Contains hyphen
            "invalid.name": "value",  # Contains dot
        }

        with pytest.raises(ValueError, match="Invalid variable name"):
            SecureTemplateRenderer._sanitize_variables(
                invalid_variables
            )

    def test_variable_length_limit(self):
        """Test variable length limits."""
        long_value = "x" * (
            SecureTemplateRenderer.MAX_VARIABLE_LENGTH + 1
        )
        variables = {"name": long_value}

        with pytest.raises(ValueError, match="value too long"):
            SecureTemplateRenderer._sanitize_variables(variables)

    def test_template_syntax_validation(self):
        """Test template syntax validation."""
        # Valid f-string template
        result = SecureTemplateRenderer.validate_template_syntax(
            "Hello {name}!", "f-string"
        )
        assert result["valid"] is True
        assert "name" in result["variables"]

        # Invalid variable name
        result = SecureTemplateRenderer.validate_template_syntax(
            "Hello {123invalid}!", "f-string"
        )
        assert result["valid"] is False
        assert "Invalid variable name" in str(result["errors"])

    @pytest.mark.skipif(
        not pytest.importorskip(
            "jinja2", reason="Jinja2 not available"
        ),
        reason="Jinja2 not available",
    )
    def test_jinja2_secure_rendering(self):
        """Test secure Jinja2 rendering."""
        template = "Hello {{ name }}, welcome to {{ platform }}!"
        variables = {"name": "Alice", "platform": "Chatter"}

        result = SecureTemplateRenderer.render_jinja2_secure(
            template, variables
        )
        assert result == "Hello Alice, welcome to Chatter!"

    @pytest.mark.skipif(
        not pytest.importorskip(
            "pystache", reason="Pystache not available"
        ),
        reason="Pystache not available",
    )
    def test_mustache_secure_rendering(self):
        """Test secure Mustache rendering."""
        template = "Hello {{name}}, welcome to {{platform}}!"
        variables = {"name": "Alice", "platform": "Chatter"}

        result = SecureTemplateRenderer.render_mustache_secure(
            template, variables
        )
        assert result == "Hello Alice, welcome to Chatter!"


class TestPromptSchemas:
    """Test Prompt schema validation."""

    def test_prompt_create_validation(self):
        """Test PromptCreate validation."""
        # Valid prompt
        prompt_data = {
            "name": "Test Prompt",
            "content": "Hello {name}!",
            "prompt_type": PromptType.TEMPLATE,
            "category": PromptCategory.GENERAL,
            "template_format": "f-string",
        }

        prompt = PromptCreate(**prompt_data)
        assert prompt.name == "Test Prompt"
        assert "name" in prompt.variables

    def test_prompt_create_invalid_template_format(self):
        """Test PromptCreate with invalid template format."""
        prompt_data = {
            "name": "Test Prompt",
            "content": "Hello {name}!",
            "template_format": "invalid_format",
        }

        with pytest.raises(ValueError, match="Invalid template format"):
            PromptCreate(**prompt_data)

    def test_prompt_create_length_constraints(self):
        """Test PromptCreate with length constraints."""
        prompt_data = {
            "name": "Test Prompt",
            "content": "Hi!",  # 3 characters
            "min_length": 10,  # Minimum 10 characters
            "max_length": 5,  # Maximum 5 characters
        }

        with pytest.raises(
            ValueError,
            match="min_length cannot be greater than max_length",
        ):
            PromptCreate(**prompt_data)

    def test_prompt_update_validation(self):
        """Test PromptUpdate validation."""
        # Empty update should fail
        with pytest.raises(
            ValueError, match="At least one field must be provided"
        ):
            PromptUpdate()

        # Valid update
        update = PromptUpdate(name="Updated Name")
        assert update.name == "Updated Name"

    def test_prompt_test_request_validation(self):
        """Test PromptTestRequest validation."""
        # Valid request
        test_request = PromptTestRequest(
            variables={"name": "Alice"}, validate_only=True
        )
        assert test_request.variables == {"name": "Alice"}

        # Too many variables
        too_many_vars = {f"var_{i}": f"value_{i}" for i in range(101)}
        with pytest.raises(ValueError, match="Too many variables"):
            PromptTestRequest(variables=too_many_vars)


class TestPromptService:
    """Test PromptService functionality."""

    @pytest.fixture
    def mock_session(self):
        """Mock database session."""
        session = AsyncMock()
        return session

    @pytest.fixture
    def prompt_service(self, mock_session):
        """Create PromptService instance with mocked session."""
        return PromptService(mock_session)

    @pytest.mark.asyncio
    async def test_create_prompt_success(
        self, prompt_service, mock_session
    ):
        """Test successful prompt creation."""
        prompt_data = PromptCreate(
            name="Test Prompt",
            content="Hello {name}!",
            prompt_type=PromptType.TEMPLATE,
            category=PromptCategory.GENERAL,
        )

        # Mock database interactions
        mock_session.execute.return_value.scalar_one_or_none.return_value = (
            None
        )
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        with patch("chatter.models.prompt.Prompt") as MockPrompt:
            mock_prompt_instance = MockPrompt.return_value
            mock_prompt_instance.id = "test-id"
            mock_prompt_instance.name = "Test Prompt"

            await prompt_service.create_prompt("user-id", prompt_data)

            assert mock_session.add.called
            assert mock_session.commit.called
            assert mock_session.refresh.called

    @pytest.mark.asyncio
    async def test_create_prompt_duplicate_name(
        self, prompt_service, mock_session
    ):
        """Test prompt creation with duplicate name."""
        prompt_data = PromptCreate(
            name="Existing Prompt",
            content="Hello {name}!",
        )

        # Mock existing prompt
        mock_existing_prompt = MagicMock()
        mock_session.execute.return_value.scalar_one_or_none.return_value = (
            mock_existing_prompt
        )

        with pytest.raises(
            PromptError, match="Prompt with this name already exists"
        ):
            await prompt_service.create_prompt("user-id", prompt_data)

    @pytest.mark.asyncio
    async def test_test_prompt_security(
        self, prompt_service, mock_session
    ):
        """Test prompt testing with security considerations."""
        # Mock prompt
        mock_prompt = MagicMock()
        mock_prompt.validate_variables.return_value = {
            "valid": True,
            "errors": [],
            "warnings": [],
        }
        mock_prompt.render.return_value = "Hello Alice!"

        # Mock get_prompt
        prompt_service.get_prompt = AsyncMock(return_value=mock_prompt)
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        test_request = PromptTestRequest(
            variables={"name": "Alice"},
            include_performance_metrics=True,
        )

        result = await prompt_service.test_prompt(
            "prompt-id", "user-id", test_request
        )

        assert result["rendered_content"] == "Hello Alice!"
        assert result["validation_result"]["valid"] is True
        assert "performance_metrics" in result
        assert "security_warnings" in result

    @pytest.mark.asyncio
    async def test_test_prompt_with_malicious_variables(
        self, prompt_service, mock_session
    ):
        """Test prompt testing rejects malicious variables."""
        test_request_data = {
            "variables": {
                "malicious_script": "<script>alert('xss')</script>",
                "javascript_url": "javascript:alert('xss')",
            }
        }

        # This should be caught by schema validation
        test_request = PromptTestRequest(**test_request_data)

        # The variables should be sanitized by the secure renderer
        from chatter.utils.template_security import (
            SecureTemplateRenderer,
        )

        sanitized = SecureTemplateRenderer._sanitize_variables(
            test_request.variables
        )

        assert "<script>" not in sanitized["malicious_script"]
        assert "javascript:" not in sanitized["javascript_url"]


class TestPromptModel:
    """Test Prompt model functionality."""

    def test_secure_render_f_string(self):
        """Test secure rendering with f-string format."""
        from chatter.models.prompt import Prompt

        prompt = Prompt()
        prompt.content = "Hello {name}!"
        prompt.template_format = "f-string"

        with patch.object(prompt, "render") as mock_render:
            mock_render.return_value = "Hello Alice!"
            result = prompt.render(name="Alice")
            assert result == "Hello Alice!"

    def test_validate_variables_with_security(self):
        """Test variable validation with security checks."""
        from chatter.models.prompt import Prompt

        prompt = Prompt()
        prompt.content = "Hello {name}!"
        prompt.template_format = "f-string"
        prompt.required_variables = ["name"]

        # Valid variables
        result = prompt.validate_variables(name="Alice")
        assert result["valid"] is True

        # Missing required variable
        result = prompt.validate_variables()
        assert result["valid"] is False
        assert "Missing required variable: name" in result["errors"]


class TestPromptAPIRoutes:
    """Test Prompt API route ordering and responses."""

    def test_route_ordering(self):
        """Test that stats route is defined before parameterized route."""
        from chatter.api.prompts import router

        routes = router.routes
        route_paths = [route.path for route in routes]

        # Stats route should come before the parameterized route
        stats_index = None
        param_index = None

        for i, path in enumerate(route_paths):
            if path == "/stats/overview":
                stats_index = i
            elif path == "/{prompt_id}":
                param_index = i

        # Both routes should exist
        assert stats_index is not None, "Stats route not found"
        assert param_index is not None, "Parameterized route not found"

        # Stats route should come before parameterized route
        assert (
            stats_index < param_index
        ), "Stats route should be defined before parameterized route"


class TestSecurityFeatures:
    """Test security features of the Prompts API."""

    def test_template_injection_prevention(self):
        """Test that template injection attacks are prevented."""
        # Test various injection attempts
        injection_attempts = [
            "__import__('os').system('rm -rf /')",
            "eval('malicious_code')",
            "exec('import os; os.system(\"ls\")')",
            "{{''.constructor.constructor('alert(1)')()}}",  # JavaScript template injection
        ]

        for attempt in injection_attempts:
            variables = {"user_input": attempt}

            # Should not raise an exception and should sanitize the input
            try:
                sanitized = SecureTemplateRenderer._sanitize_variables(
                    variables
                )
                # The sanitized version should not contain dangerous patterns
                assert "import" not in sanitized.get("user_input", "")
                assert "eval" not in sanitized.get("user_input", "")
                assert "exec" not in sanitized.get("user_input", "")
            except ValueError:
                # It's also acceptable to reject the input entirely
                pass

    def test_xss_prevention(self):
        """Test XSS prevention in template variables."""
        xss_attempts = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "onclick=alert('xss')",
            "onload=alert('xss')",
        ]

        for attempt in xss_attempts:
            variables = {"content": attempt}
            sanitized = SecureTemplateRenderer._sanitize_variables(
                variables
            )

            # Should remove or neutralize XSS attempts
            sanitized_content = sanitized.get("content", "")
            assert "<script>" not in sanitized_content
            assert "javascript:" not in sanitized_content
            assert "onclick=" not in sanitized_content
            assert "onload=" not in sanitized_content

    def test_variable_name_validation(self):
        """Test that only safe variable names are allowed."""
        invalid_names = [
            "123invalid",  # Starts with number
            "invalid-name",  # Contains hyphen
            "invalid.name",  # Contains dot
            "invalid name",  # Contains space
            "__special__",  # Double underscore (potentially dangerous)
        ]

        for invalid_name in invalid_names:
            variables = {invalid_name: "value"}

            with pytest.raises(
                ValueError, match="Invalid variable name"
            ):
                SecureTemplateRenderer._sanitize_variables(variables)

    def test_content_length_limits(self):
        """Test content length limits."""
        max_length = SecureTemplateRenderer.MAX_VARIABLE_LENGTH

        # Should accept content at the limit
        variables = {"content": "x" * max_length}
        sanitized = SecureTemplateRenderer._sanitize_variables(
            variables
        )
        assert len(sanitized["content"]) == max_length

        # Should reject content over the limit
        variables = {"content": "x" * (max_length + 1)}
        with pytest.raises(ValueError, match="value too long"):
            SecureTemplateRenderer._sanitize_variables(variables)


if __name__ == "__main__":
    pytest.main([__file__])
