"""Secure template rendering utilities."""

import re
import string
from typing import Any

from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class SecureTemplateRenderer:
    """Secure template renderer that prevents code injection."""

    # Safe characters for template variables
    SAFE_VARIABLE_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")

    # Maximum depth for nested variable access
    MAX_VARIABLE_DEPTH = 3

    # Maximum length for variable values
    MAX_VARIABLE_LENGTH = 10000

    @classmethod
    def render_secure_f_string(
        cls, template: str, variables: dict[str, Any]
    ) -> str:
        """Render f-string template securely without code injection risks.

        This uses string.Template which is safe from code injection,
        unlike str.format() which can execute arbitrary code.

        Args:
            template: Template string with ${variable} placeholders
            variables: Variables to substitute

        Returns:
            Rendered template string

        Raises:
            ValueError: If template or variables are invalid
        """
        try:
            # Validate and sanitize variables
            sanitized_vars = cls._sanitize_variables(variables)

            # Convert f-string style {var} to Template style ${var}
            template_converted = cls._convert_f_string_to_template(
                template
            )

            # Use string.Template for safe substitution
            template_obj = string.Template(template_converted)
            return template_obj.safe_substitute(sanitized_vars)

        except Exception as e:
            logger.error(f"Template rendering failed: {str(e)}")
            raise ValueError(
                f"Template rendering failed: {str(e)}"
            ) from e

    @classmethod
    def render_jinja2_secure(
        cls, template: str, variables: dict[str, Any]
    ) -> str:
        """Render Jinja2 template securely.

        Args:
            template: Jinja2 template string
            variables: Variables to substitute

        Returns:
            Rendered template string

        Raises:
            ValueError: If template rendering fails
        """
        try:
            from jinja2 import meta, select_autoescape
            from jinja2.sandbox import SandboxedEnvironment

            # Use sandboxed environment to prevent code execution
            env = SandboxedEnvironment(
                autoescape=select_autoescape(["html", "xml"]),
                enable_async=False,
            )

            # Validate and sanitize variables
            sanitized_vars = cls._sanitize_variables(variables)

            # Parse template and validate variables
            parsed = env.parse(template)
            required_vars = meta.find_undeclared_variables(parsed)

            # Check if all required variables are provided
            missing_vars = required_vars - set(sanitized_vars.keys())
            if missing_vars:
                raise ValueError(
                    f"Missing required variables: {missing_vars}"
                )

            # Render template
            template_obj = env.from_string(template)
            return template_obj.render(sanitized_vars)

        except ImportError as e:
            raise ValueError(
                "Jinja2 not installed for template rendering"
            ) from e
        except Exception as e:
            logger.error(f"Jinja2 template rendering failed: {str(e)}")
            raise ValueError(
                f"Template rendering failed: {str(e)}"
            ) from e

    @classmethod
    def render_mustache_secure(
        cls, template: str, variables: dict[str, Any]
    ) -> str:
        """Render Mustache template securely.

        Args:
            template: Mustache template string
            variables: Variables to substitute

        Returns:
            Rendered template string

        Raises:
            ValueError: If template rendering fails
        """
        try:
            import pystache

            # Validate and sanitize variables
            sanitized_vars = cls._sanitize_variables(variables)

            # Render with pystache (inherently safer than f-strings)
            return pystache.render(template, sanitized_vars)

        except ImportError as e:
            raise ValueError(
                "Pystache not installed for mustache template rendering"
            ) from e
        except Exception as e:
            logger.error(
                f"Mustache template rendering failed: {str(e)}"
            )
            raise ValueError(
                f"Template rendering failed: {str(e)}"
            ) from e

    @classmethod
    def _sanitize_variables(
        cls, variables: dict[str, Any]
    ) -> dict[str, str]:
        """Sanitize template variables to prevent injection attacks.

        Args:
            variables: Raw variables dictionary

        Returns:
            Sanitized variables dictionary

        Raises:
            ValueError: If variables are invalid
        """
        sanitized = {}

        for key, value in variables.items():
            # Validate variable name
            if not cls.SAFE_VARIABLE_PATTERN.match(key):
                raise ValueError(f"Invalid variable name: {key}")

            # Convert value to string and validate length
            str_value = str(value)
            if len(str_value) > cls.MAX_VARIABLE_LENGTH:
                raise ValueError(
                    f"Variable '{key}' value too long (max {cls.MAX_VARIABLE_LENGTH} chars)"
                )

            # Basic HTML/script sanitization for security
            sanitized_value = cls._sanitize_content(str_value)
            sanitized[key] = sanitized_value

        return sanitized

    @classmethod
    def _sanitize_content(cls, content: str) -> str:
        """Basic content sanitization to prevent XSS and code injection.

        Args:
            content: Raw content string

        Returns:
            Sanitized content string
        """
        # Remove or escape potentially dangerous patterns
        dangerous_patterns = [
            (
                r"<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>",
                "",
            ),  # Remove script tags
            (r"javascript:", ""),  # Remove javascript: protocols
            (r"on\w+\s*=", ""),  # Remove event handlers like onclick=
            (r"eval\s*\(", ""),  # Remove eval calls
            (r"exec\s*\(", ""),  # Remove exec calls
        ]

        sanitized = content
        for pattern, replacement in dangerous_patterns:
            sanitized = re.sub(
                pattern, replacement, sanitized, flags=re.IGNORECASE
            )

        return sanitized

    @classmethod
    def _convert_f_string_to_template(
        cls, f_string_template: str
    ) -> str:
        """Convert f-string style {var} to Template style ${var}.

        Args:
            f_string_template: Template with {var} placeholders

        Returns:
            Template with ${var} placeholders
        """

        # Simple conversion from {var} to ${var}
        # This handles basic cases - more complex f-string features are not supported
        def replace_placeholder(match):
            var_name = match.group(1)
            # Validate variable name
            if not cls.SAFE_VARIABLE_PATTERN.match(var_name):
                raise ValueError(
                    f"Invalid variable name in template: {var_name}"
                )
            return f"${{{var_name}}}"

        # Match {variable_name} patterns
        pattern = r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}"
        return re.sub(pattern, replace_placeholder, f_string_template)

    @classmethod
    def validate_template_syntax(
        cls, template: str, template_format: str
    ) -> dict[str, Any]:
        """Validate template syntax and extract variables.

        Args:
            template: Template string
            template_format: Template format (f-string, jinja2, mustache)

        Returns:
            Dictionary with validation results and extracted variables
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "variables": [],
        }

        try:
            if template_format == "f-string":
                # Extract variables from f-string template
                variables = re.findall(
                    r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}", template
                )
                result["variables"] = list(set(variables))

                # Validate variable names
                for var in variables:
                    if not cls.SAFE_VARIABLE_PATTERN.match(var):
                        result["valid"] = False
                        result["errors"].append(
                            f"Invalid variable name: {var}"
                        )

            elif template_format == "jinja2":
                try:
                    from jinja2 import Environment, meta

                    env = Environment()
                    parsed = env.parse(template)
                    variables = meta.find_undeclared_variables(parsed)
                    result["variables"] = list(variables)
                except ImportError:
                    result["warnings"].append(
                        "Jinja2 not available for validation"
                    )
                except Exception as e:
                    result["valid"] = False
                    result["errors"].append(
                        f"Jinja2 syntax error: {str(e)}"
                    )

            elif template_format == "mustache":
                # Basic mustache variable extraction
                variables = re.findall(r"\{\{([^}]+)\}\}", template)
                result["variables"] = list(set(variables))

        except Exception as e:
            result["valid"] = False
            result["errors"].append(
                f"Template validation failed: {str(e)}"
            )

        return result
