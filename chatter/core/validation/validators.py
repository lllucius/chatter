"""Base validator classes and concrete validator implementations."""

import re
import html
import json
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

from .context import ValidationContext, ValidationMode
from .exceptions import ValidationError, SecurityValidationError, BusinessValidationError


class BaseValidator(ABC):
    """Base class for all validators."""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.supported_rules: List[str] = []
        
    @abstractmethod
    def validate(
        self, 
        value: Any, 
        rule: str, 
        context: ValidationContext
    ) -> 'ValidationResult':
        """Validate a value according to the specified rule."""
        pass
        
    def sanitize(self, value: Any, context: ValidationContext) -> Any:
        """Sanitize a value. Override in subclasses if needed."""
        return value


class ValidationRule:
    """Represents a validation rule configuration."""
    
    def __init__(
        self,
        name: str,
        pattern: Optional[str] = None,
        max_length: Optional[int] = None,
        min_length: Optional[int] = None,
        required: bool = False,
        allowed_chars: Optional[str] = None,
        forbidden_patterns: Optional[List[str]] = None,
        sanitize: bool = False,
        custom_validator: Optional[callable] = None
    ):
        self.name = name
        self.pattern = pattern
        self.max_length = max_length
        self.min_length = min_length
        self.required = required
        self.allowed_chars = allowed_chars
        self.forbidden_patterns = forbidden_patterns or []
        self.sanitize = sanitize
        self.custom_validator = custom_validator


class InputValidator(BaseValidator):
    """Validates and sanitizes user input."""
    
    def __init__(self):
        super().__init__("input", "Validates user input according to predefined rules")
        self.rules: Dict[str, ValidationRule] = {}
        self._setup_default_rules()
        self.supported_rules = list(self.rules.keys())
        
    def _setup_default_rules(self):
        """Setup default validation rules."""
        self.rules.update({
            "text": ValidationRule(
                name="text",
                max_length=10000,
                forbidden_patterns=[
                    r"<script.*?>.*?</script>",
                    r"javascript:",
                    r"on\w+\s*=",
                ],
                sanitize=True
            ),
            "message": ValidationRule(
                name="message", 
                max_length=5000,
                min_length=1,
                required=True,
                forbidden_patterns=[
                    r"<script.*?>.*?</script>",
                    r"javascript:",
                    r"on\w+\s*=",
                ],
                sanitize=True
            ),
            "username": ValidationRule(
                name="username",
                pattern=r"^[a-zA-Z0-9_-]{3,50}$",
                max_length=50,
                min_length=3,
                required=True,
                allowed_chars="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
            ),
            "email": ValidationRule(
                name="email",
                pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                max_length=254,
                required=True
            ),
            "password": ValidationRule(
                name="password",
                min_length=8,
                max_length=128,
                required=True
            ),
            "url": ValidationRule(
                name="url",
                pattern=r"^https?://[^\s/$.?#].[^\s]*$",
                max_length=2048,
                sanitize=True
            ),
            "filename": ValidationRule(
                name="filename",
                pattern=r"^[a-zA-Z0-9._-]+\.[a-zA-Z0-9]+$",
                max_length=255,
                forbidden_patterns=[r"\.\./", r"\\", r"/"],
                sanitize=True
            ),
            "api_key": ValidationRule(
                name="api_key",
                pattern=r"^[a-zA-Z0-9_-]{16,128}$",
                min_length=16,
                max_length=128,
                required=True
            )
        })
        
    def validate(self, value: Any, rule: str, context: ValidationContext) -> 'ValidationResult':
        """Validate input according to the specified rule.""" 
        from .engine import ValidationResult
        
        if rule not in self.rules:
            return ValidationResult(
                is_valid=False,
                errors=[ValidationError(f"Unknown validation rule: {rule}")]
            )
            
        validation_rule = self.rules[rule]
        
        # Convert to string
        if value is None:
            if validation_rule.required:
                return ValidationResult(
                    is_valid=False,
                    errors=[ValidationError(f"{rule} is required")]
                )
            return ValidationResult(is_valid=True, value="")
            
        str_value = str(value)
        
        # Check required and length
        if validation_rule.required and not str_value.strip():
            return ValidationResult(
                is_valid=False,
                errors=[ValidationError(f"{rule} is required")]
            )
            
        # Apply context overrides for max length
        max_length = context.get_max_length(rule, validation_rule.max_length)
        if max_length and len(str_value) > max_length:
            return ValidationResult(
                is_valid=False,
                errors=[ValidationError(f"{rule} exceeds maximum length of {max_length}")]
            )
            
        if validation_rule.min_length and len(str_value) < validation_rule.min_length:
            return ValidationResult(
                is_valid=False,
                errors=[ValidationError(f"{rule} is below minimum length of {validation_rule.min_length}")]
            )
            
        # Check pattern
        pattern = context.get_custom_pattern(rule) or validation_rule.pattern
        if pattern and not re.match(pattern, str_value):
            return ValidationResult(
                is_valid=False,
                errors=[ValidationError(f"{rule} does not match required pattern")]
            )
            
        # Check allowed characters
        if validation_rule.allowed_chars:
            for char in str_value:
                if char not in validation_rule.allowed_chars:
                    return ValidationResult(
                        is_valid=False,
                        errors=[ValidationError(f"{rule} contains invalid character: {char}")]
                    )
                    
        # Check forbidden patterns
        for pattern in validation_rule.forbidden_patterns:
            if re.search(pattern, str_value, re.IGNORECASE):
                return ValidationResult(
                    is_valid=False,
                    errors=[SecurityValidationError(f"{rule} contains forbidden pattern")]
                )
                
        # Sanitize if needed and enabled
        if validation_rule.sanitize and context.sanitize_input:
            str_value = self._sanitize_value(str_value)
            
        return ValidationResult(is_valid=True, value=str_value)
        
    def _sanitize_value(self, value: str) -> str:
        """Sanitize input value."""
        # Remove HTML tags
        value = re.sub(r'<[^>]+>', '', value)
        # Remove null bytes
        value = value.replace('\x00', '')
        # Remove control characters except newlines and tabs
        value = re.sub(r'[\x01-\x08\x0B\x0C\x0E-\x1F\x7F]', '', value)
        # Normalize whitespace
        value = re.sub(r'\s+', ' ', value).strip()
        return value


class SecurityValidator(BaseValidator):
    """Validates input for security threats."""
    
    def __init__(self):
        super().__init__("security", "Validates input for security threats")
        self.supported_rules = ["security_check", "xss_check", "sql_injection_check", "path_traversal_check"]
        
        self.sql_injection_patterns = [
            r"(\%27)|(\')|(\-\-)|(%23)|(#)",
            r"((\\%3D)|(=))[^\n]*((\\%27)|(\')|(\-\-)|(%23)|(#))",
            r"/\*(.|\n)*?\*/",
        ]
        
        self.xss_patterns = [
            r"<script.*?>.*?</script>",
            r"javascript:",
            r"vbscript:",
            r"on\w+\s*=",
            r"<iframe.*?>",
            r"<object.*?>",
            r"<embed.*?>",
        ]
        
        self.path_traversal_patterns = [
            r"\.\./",
            r"\.\.\\",
            r"%2e%2e%2f",
            r"%2e%2e\\",
        ]
        
    def validate(self, value: Any, rule: str, context: ValidationContext) -> 'ValidationResult':
        """Validate input for security threats."""
        from .engine import ValidationResult
        
        if not isinstance(value, str):
            return ValidationResult(is_valid=True, value=value)
            
        errors = []
        
        if rule in ["security_check", "sql_injection_check"]:
            if self._detect_sql_injection(value):
                errors.append(SecurityValidationError(
                    "Potential SQL injection detected",
                    threat_type="sql_injection"
                ))
                
        if rule in ["security_check", "xss_check"]:
            if self._detect_xss(value):
                errors.append(SecurityValidationError(
                    "Potential XSS attempt detected",
                    threat_type="xss"
                ))
                
        if rule in ["security_check", "path_traversal_check"]:
            if self._detect_path_traversal(value):
                errors.append(SecurityValidationError(
                    "Potential path traversal detected",
                    threat_type="path_traversal"
                ))
                
        if errors:
            return ValidationResult(is_valid=False, errors=errors)
            
        # Sanitize if enabled
        sanitized_value = value
        if context.sanitize_input:
            sanitized_value = self._sanitize_security_threats(value)
            
        return ValidationResult(is_valid=True, value=sanitized_value)
        
    def _detect_sql_injection(self, value: str) -> bool:
        """Detect potential SQL injection attempts."""
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False
        
    def _detect_xss(self, value: str) -> bool:
        """Detect potential XSS attempts."""
        for pattern in self.xss_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False
        
    def _detect_path_traversal(self, value: str) -> bool:
        """Detect potential path traversal attempts."""
        for pattern in self.path_traversal_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False
        
    def _sanitize_security_threats(self, value: str) -> str:
        """Remove security threats from input."""
        # Remove script tags
        value = re.sub(r'<script[^>]*>.*?</script>', '', value, flags=re.IGNORECASE | re.DOTALL)
        # Remove javascript: URLs
        value = re.sub(r'javascript\s*:', '', value, flags=re.IGNORECASE)
        # Remove event handlers
        value = re.sub(r'on\w+\s*=\s*["\'][^"\']*["\']', '', value, flags=re.IGNORECASE)
        # Remove path traversal
        value = re.sub(r'\.\./', '', value)
        return value


class BusinessValidator(BaseValidator):
    """Validates business logic rules."""
    
    def __init__(self):
        super().__init__("business", "Validates business logic rules")
        self.supported_rules = ["model_consistency", "embedding_space", "provider_rules"]
        
    def validate(self, value: Any, rule: Union[str, List[str]], context: ValidationContext) -> 'ValidationResult':
        """Validate business logic rules."""
        from .engine import ValidationResult
        
        # Handle multiple rules
        if isinstance(rule, list):
            errors = []
            for single_rule in rule:
                result = self._validate_single_rule(value, single_rule, context)
                if not result.is_valid:
                    errors.extend(result.errors)
            return ValidationResult(
                is_valid=len(errors) == 0,
                value=value,
                errors=errors
            )
        else:
            return self._validate_single_rule(value, rule, context)
            
    def _validate_single_rule(self, value: Any, rule: str, context: ValidationContext) -> 'ValidationResult':
        """Validate a single business rule."""
        from .engine import ValidationResult
        
        if rule == "model_consistency":
            return self._validate_model_consistency(value, context)
        elif rule == "embedding_space":
            return self._validate_embedding_space(value, context)
        elif rule == "provider_rules":
            return self._validate_provider_rules(value, context)
        else:
            return ValidationResult(
                is_valid=False,
                errors=[BusinessValidationError(f"Unknown business rule: {rule}")]
            )
            
    def _validate_model_consistency(self, data: Dict[str, Any], context: ValidationContext) -> 'ValidationResult':
        """Validate model configuration consistency."""
        from .engine import ValidationResult
        
        errors = []
        model_type = data.get("model_type")
        dimensions = data.get("dimensions")
        max_tokens = data.get("max_tokens")
        supports_batch = data.get("supports_batch")
        max_batch_size = data.get("max_batch_size")
        
        # Embedding models must have dimensions
        if model_type == "EMBEDDING" and not dimensions:
            errors.append(BusinessValidationError(
                "Embedding models must specify dimensions > 0",
                rule_name="model_consistency"
            ))
            
        # LLM models should not have dimensions
        if model_type == "LLM" and dimensions:
            errors.append(BusinessValidationError(
                "LLM models should not specify dimensions",
                rule_name="model_consistency"
            ))
            
        # Validate batch configuration
        if max_batch_size and not supports_batch:
            errors.append(BusinessValidationError(
                "max_batch_size specified but supports_batch is False",
                rule_name="model_consistency"
            ))
            
        return ValidationResult(
            is_valid=len(errors) == 0,
            value=data,
            errors=errors
        )
        
    def _validate_embedding_space(self, data: Dict[str, Any], context: ValidationContext) -> 'ValidationResult':
        """Validate embedding space consistency.""" 
        from .engine import ValidationResult
        
        errors = []
        model_dimensions = data.get("model_dimensions")
        base_dimensions = data.get("base_dimensions")
        effective_dimensions = data.get("effective_dimensions")
        
        if base_dimensions != model_dimensions:
            errors.append(BusinessValidationError(
                f"Base dimensions ({base_dimensions}) must match model dimensions ({model_dimensions})",
                rule_name="embedding_space"
            ))
            
        if effective_dimensions and effective_dimensions > base_dimensions:
            errors.append(BusinessValidationError(
                "Effective dimensions cannot be greater than base dimensions",
                rule_name="embedding_space"
            ))
            
        return ValidationResult(
            is_valid=len(errors) == 0,
            value=data,
            errors=errors
        )
        
    def _validate_provider_rules(self, data: Dict[str, Any], context: ValidationContext) -> 'ValidationResult':
        """Validate provider-specific rules."""
        from .engine import ValidationResult, BusinessValidationError
        
        errors = []
        provider_name = data.get("name", "").lower()
        api_key = data.get("api_key", "")
        
        # Provider-specific validation rules
        if provider_name == "openai":
            if api_key and not api_key.startswith("sk-"):
                errors.append(BusinessValidationError(
                    "OpenAI API keys must start with 'sk-'",
                    rule_name="provider_rules"
                ))
        elif provider_name == "anthropic":
            if api_key and not api_key.startswith("sk-ant-"):
                errors.append(BusinessValidationError(
                    "Anthropic API keys must start with 'sk-ant-'",
                    rule_name="provider_rules"
                ))
        elif provider_name in ["cohere", "cohereai"]:
            if api_key and len(api_key) < 32:
                errors.append(BusinessValidationError(
                    "Cohere API keys must be at least 32 characters",
                    rule_name="provider_rules"
                ))
        
        # General validations for all providers
        if "api_key" in data and not api_key:
            errors.append(BusinessValidationError(
                "API key cannot be empty",
                rule_name="provider_rules"
            ))
            
        # Check required fields based on provider
        required_fields = data.get("required_fields", [])
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(BusinessValidationError(
                    f"Required field '{field}' is missing or empty",
                    rule_name="provider_rules"
                ))
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            value=data,
            errors=errors
        )


class ConfigValidator(BaseValidator):
    """Validates configuration settings."""
    
    def __init__(self):
        super().__init__("config", "Validates configuration settings")
        self.supported_rules = ["database_config", "api_keys", "security_config"]
        
    def validate(self, value: Any, rule: str, context: ValidationContext) -> 'ValidationResult':
        """Validate configuration settings."""
        from .engine import ValidationResult
        
        if rule == "database_config":
            return self._validate_database_config(value, context)
        elif rule == "api_keys":
            return self._validate_api_keys(value, context)
        elif rule == "security_config":
            return self._validate_security_config(value, context)
        else:
            return ValidationResult(is_valid=True, value=value)
            
    def _validate_database_config(self, config: Dict[str, Any], context: ValidationContext) -> 'ValidationResult':
        """Validate database configuration."""
        from .engine import ValidationResult
        
        errors = []
        database_url = config.get('DATABASE_URL', '')
        
        if not database_url:
            errors.append(ValidationError("DATABASE_URL is required"))
        else:
            try:
                parsed = urlparse(database_url)
                if not parsed.scheme or not parsed.hostname:
                    errors.append(ValidationError("DATABASE_URL format is invalid"))
            except Exception as e:
                errors.append(ValidationError(f"DATABASE_URL parsing failed: {str(e)}"))
                
        return ValidationResult(
            is_valid=len(errors) == 0,
            value=config,
            errors=errors
        )
        
    def _validate_api_keys(self, config: Dict[str, Any], context: ValidationContext) -> 'ValidationResult':
        """Validate API keys."""
        from .engine import ValidationResult
        
        errors = []
        
        for key_name in ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY']:
            if key_name in config:
                api_key = config[key_name]
                if not api_key or len(api_key) < 10:
                    errors.append(ValidationError(f"{key_name} appears too short"))
                elif api_key in ["your-api-key", "sk-test", "test-key"]:
                    errors.append(ValidationError(f"{key_name} appears to be a placeholder"))
                    
        return ValidationResult(
            is_valid=len(errors) == 0,
            value=config,
            errors=errors
        )
        
    def _validate_security_config(self, config: Dict[str, Any], context: ValidationContext) -> 'ValidationResult':
        """Validate security configuration."""
        from .engine import ValidationResult
        
        errors = []
        secret_key = config.get('SECRET_KEY', '')
        
        if len(secret_key) < 32:
            errors.append(ValidationError("SECRET_KEY too short (minimum 32 characters)"))
            
        return ValidationResult(
            is_valid=len(errors) == 0,
            value=config,
            errors=errors
        )


class WorkflowValidator(BaseValidator):
    """Validates workflow configurations."""
    
    def __init__(self):
        super().__init__("workflow", "Validates workflow configurations")
        self.supported_rules = ["workflow_config", "workflow_request", "workflow_parameters"]
        
    def validate(self, value: Any, rule: str, context: ValidationContext) -> 'ValidationResult':
        """Validate workflow configurations."""
        from .engine import ValidationResult
        
        if rule == "workflow_config":
            return self._validate_workflow_config(value, context)
        elif rule == "workflow_request":
            return self._validate_workflow_request(value, context)
        elif rule == "workflow_parameters":
            return self._validate_workflow_parameters(value, context)
        else:
            return ValidationResult(is_valid=True, value=value)
            
    def _validate_workflow_config(self, config: Dict[str, Any], context: ValidationContext) -> 'ValidationResult':
        """Validate workflow configuration."""
        from .engine import ValidationResult
        
        errors = []
        
        # Handle simple workflow type validation (for workflow execution service)
        if "workflow_type" in config and len(config) == 1:
            workflow_type = config["workflow_type"]
            valid_types = ["plain", "rag", "tools", "full"]
            if workflow_type not in valid_types:
                errors.append(ValidationError(f"Invalid workflow type: {workflow_type}. Must be one of {valid_types}"))
        else:
            # Handle full workflow configuration validation
            required_fields = ['id', 'name', 'steps']
            
            for field in required_fields:
                if field not in config:
                    errors.append(ValidationError(f"Workflow config missing required field: {field}"))
                
        return ValidationResult(
            is_valid=len(errors) == 0,
            value=config,
            errors=errors
        )
        
    def _validate_workflow_request(self, request: Dict[str, Any], context: ValidationContext) -> 'ValidationResult':
        """Validate workflow request."""
        from .engine import ValidationResult
        
        errors = []
        message = request.get('message', '')
        
        if not message or not message.strip():
            errors.append(ValidationError("Message cannot be empty"))
            
        if len(message) > 10000:
            errors.append(ValidationError("Message too long (maximum 10000 characters)"))
            
        return ValidationResult(
            is_valid=len(errors) == 0,
            value=request,
            errors=errors
        )
        
    def _validate_workflow_parameters(self, params: Dict[str, Any], context: ValidationContext) -> 'ValidationResult':
        """Validate workflow parameters."""
        from .engine import ValidationResult
        
        errors = []
        
        # Validate temperature
        if 'temperature' in params:
            temp = params['temperature']
            if not isinstance(temp, (int, float)) or temp < 0.0 or temp > 1.0:
                errors.append(ValidationError("Temperature must be between 0.0 and 1.0"))
                
        # Validate max_tokens
        if 'max_tokens' in params:
            tokens = params['max_tokens']
            if not isinstance(tokens, int) or tokens < 1:
                errors.append(ValidationError("max_tokens must be a positive integer"))
                
        return ValidationResult(
            is_valid=len(errors) == 0,
            value=params,
            errors=errors
        )


class AgentValidator(BaseValidator):
    """Validates agent-specific input."""
    
    def __init__(self):
        super().__init__("agent", "Validates agent-specific input")
        self.supported_rules = ["agent_input", "agent_id", "conversation_id", "agent_name"]
        
    def validate(self, value: Any, rule: str, context: ValidationContext) -> 'ValidationResult':
        """Validate agent-specific input."""
        from .engine import ValidationResult
        
        if rule == "agent_id":
            return self._validate_agent_id(value, context)
        elif rule == "conversation_id":
            return self._validate_conversation_id(value, context)
        elif rule == "agent_name":
            return self._validate_agent_name(value, context)
        elif rule == "agent_input":
            return self._validate_agent_input(value, context)
        else:
            return ValidationResult(is_valid=True, value=value)
            
    def _validate_agent_id(self, agent_id: str, context: ValidationContext) -> 'ValidationResult':
        """Validate agent ID."""
        from .engine import ValidationResult
        
        if not agent_id or not isinstance(agent_id, str):
            return ValidationResult(
                is_valid=False,
                errors=[ValidationError("Agent ID is required")]
            )
            
        try:
            uuid.UUID(agent_id.strip())
            return ValidationResult(is_valid=True, value=agent_id.strip())
        except ValueError:
            return ValidationResult(
                is_valid=False,
                errors=[ValidationError("Invalid agent ID format")]
            )
            
    def _validate_conversation_id(self, conversation_id: str, context: ValidationContext) -> 'ValidationResult':
        """Validate conversation ID."""
        from .engine import ValidationResult
        
        if not conversation_id or not isinstance(conversation_id, str):
            return ValidationResult(
                is_valid=False,
                errors=[ValidationError("Conversation ID is required")]
            )
            
        try:
            uuid.UUID(conversation_id.strip())
            return ValidationResult(is_valid=True, value=conversation_id.strip())
        except ValueError:
            return ValidationResult(
                is_valid=False,
                errors=[ValidationError("Invalid conversation ID format")]
            )
            
    def _validate_agent_name(self, name: str, context: ValidationContext) -> 'ValidationResult':
        """Validate agent name."""
        from .engine import ValidationResult
        
        if not name or not isinstance(name, str):
            return ValidationResult(
                is_valid=False,
                errors=[ValidationError("Agent name is required")]
            )
            
        name = name.strip()
        
        if len(name) < 1:
            return ValidationResult(
                is_valid=False,
                errors=[ValidationError("Agent name cannot be empty")]
            )
            
        if len(name) > 100:
            return ValidationResult(
                is_valid=False,
                errors=[ValidationError("Agent name too long (max 100 characters)")]
            )
            
        return ValidationResult(is_valid=True, value=name)
        
    def _validate_agent_input(self, data: Dict[str, Any], context: ValidationContext) -> 'ValidationResult':
        """Validate agent input data."""
        from .engine import ValidationResult
        
        errors = []
        
        if 'agent_id' in data:
            result = self._validate_agent_id(data['agent_id'], context)
            if not result.is_valid:
                errors.extend(result.errors)
                
        if 'name' in data:
            result = self._validate_agent_name(data['name'], context)
            if not result.is_valid:
                errors.extend(result.errors)
                
        return ValidationResult(
            is_valid=len(errors) == 0,
            value=data,
            errors=errors
        )