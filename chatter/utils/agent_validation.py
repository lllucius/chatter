"""Agent-specific input validation and sanitization."""

import re
import uuid
from typing import Any

from chatter.utils.logging import get_logger
from chatter.utils.problem import InternalServerProblem
from chatter.schemas.agents import AgentType

logger = get_logger(__name__)


class AgentInputValidator:
    """Validator for agent-related inputs."""

    @staticmethod
    def validate_agent_id(agent_id: str) -> str:
        """Validate and sanitize agent ID.
        
        Args:
            agent_id: Agent ID to validate
            
        Returns:
            Validated agent ID
            
        Raises:
            InternalServerProblem: If validation fails
        """
        if not agent_id or not isinstance(agent_id, str):
            raise InternalServerProblem(detail="Agent ID is required")
        
        agent_id = agent_id.strip()
        
        # Check if it's a valid UUID
        try:
            uuid.UUID(agent_id)
        except ValueError:
            raise InternalServerProblem(detail="Invalid agent ID format")
        
        return agent_id

    @staticmethod
    def validate_conversation_id(conversation_id: str) -> str:
        """Validate and sanitize conversation ID.
        
        Args:
            conversation_id: Conversation ID to validate
            
        Returns:
            Validated conversation ID
            
        Raises:
            InternalServerProblem: If validation fails
        """
        if not conversation_id or not isinstance(conversation_id, str):
            raise InternalServerProblem(detail="Conversation ID is required")
        
        conversation_id = conversation_id.strip()
        
        # Check if it's a valid UUID
        try:
            uuid.UUID(conversation_id)
        except ValueError:
            raise InternalServerProblem(detail="Invalid conversation ID format")
        
        return conversation_id

    @staticmethod
    def validate_agent_name(name: str) -> str:
        """Validate and sanitize agent name.
        
        Args:
            name: Agent name to validate
            
        Returns:
            Validated agent name
            
        Raises:
            InternalServerProblem: If validation fails
        """
        if not name or not isinstance(name, str):
            raise InternalServerProblem(detail="Agent name is required")
        
        name = name.strip()
        
        # Check length
        if len(name) < 1:
            raise InternalServerProblem(detail="Agent name cannot be empty")
        if len(name) > 100:
            raise InternalServerProblem(detail="Agent name too long (max 100 characters)")
        
        # Check for dangerous patterns
        dangerous_patterns = [
            r"<script.*?>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe.*?>.*?</iframe>",
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, name, re.IGNORECASE):
                raise InternalServerProblem(detail="Agent name contains invalid characters")
        
        return name

    @staticmethod
    def validate_agent_message(message: str) -> str:
        """Validate and sanitize agent interaction message.
        
        Args:
            message: Message to validate
            
        Returns:
            Validated message
            
        Raises:
            InternalServerProblem: If validation fails
        """
        if not message or not isinstance(message, str):
            raise InternalServerProblem(detail="Message is required")
        
        message = message.strip()
        
        # Check length
        if len(message) < 1:
            raise InternalServerProblem(detail="Message cannot be empty")
        if len(message) > 10000:
            raise InternalServerProblem(detail="Message too long (max 10000 characters)")
        
        # Check for dangerous patterns
        dangerous_patterns = [
            r"<script.*?>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe.*?>.*?</iframe>",
            r"<object.*?>.*?</object>",
            r"<embed.*?>.*?</embed>",
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                logger.warning("Dangerous pattern detected in message", pattern=pattern)
                # Remove the dangerous content instead of rejecting
                message = re.sub(pattern, "", message, flags=re.IGNORECASE)
        
        return message

    @staticmethod
    def validate_agent_type(agent_type: str | AgentType) -> AgentType:
        """Validate agent type.
        
        Args:
            agent_type: Agent type to validate
            
        Returns:
            Validated agent type
            
        Raises:
            InternalServerProblem: If validation fails
        """
        if isinstance(agent_type, AgentType):
            return agent_type
        
        if not agent_type or not isinstance(agent_type, str):
            raise InternalServerProblem(detail="Agent type is required")
        
        try:
            return AgentType(agent_type)
        except ValueError:
            valid_types = [t.value for t in AgentType]
            raise InternalServerProblem(
                detail=f"Invalid agent type. Valid types: {', '.join(valid_types)}"
            )

    @staticmethod
    def validate_pagination_params(offset: int, limit: int) -> tuple[int, int]:
        """Validate pagination parameters.
        
        Args:
            offset: Offset value
            limit: Limit value
            
        Returns:
            Tuple of validated (offset, limit)
        """
        # Ensure offset is non-negative
        offset = max(0, offset) if isinstance(offset, int) else 0
        
        # Ensure limit is within reasonable bounds
        if not isinstance(limit, int) or limit < 1:
            limit = 10
        elif limit > 100:
            limit = 100
        
        return offset, limit

    @staticmethod
    def validate_temperature(temperature: float) -> float:
        """Validate temperature parameter.
        
        Args:
            temperature: Temperature value
            
        Returns:
            Validated temperature
            
        Raises:
            InternalServerProblem: If validation fails
        """
        if not isinstance(temperature, (int, float)):
            raise InternalServerProblem(detail="Temperature must be a number")
        
        temperature = float(temperature)
        
        if temperature < 0.0 or temperature > 2.0:
            raise InternalServerProblem(detail="Temperature must be between 0.0 and 2.0")
        
        return temperature

    @staticmethod
    def validate_max_tokens(max_tokens: int) -> int:
        """Validate max tokens parameter.
        
        Args:
            max_tokens: Max tokens value
            
        Returns:
            Validated max tokens
            
        Raises:
            InternalServerProblem: If validation fails
        """
        if not isinstance(max_tokens, int):
            raise InternalServerProblem(detail="Max tokens must be an integer")
        
        if max_tokens < 1 or max_tokens > 32000:
            raise InternalServerProblem(detail="Max tokens must be between 1 and 32000")
        
        return max_tokens

    @staticmethod
    def sanitize_agent_context(context: dict[str, Any] | None) -> dict[str, Any]:
        """Sanitize agent interaction context.
        
        Args:
            context: Context dictionary
            
        Returns:
            Sanitized context
        """
        if not context:
            return {}
        
        if not isinstance(context, dict):
            logger.warning("Invalid context type, ignoring")
            return {}
        
        sanitized = {}
        
        for key, value in context.items():
            # Sanitize keys
            if not isinstance(key, str) or len(key) > 100:
                continue
            
            # Sanitize string values
            if isinstance(value, str):
                if len(value) > 1000:  # Limit value length
                    value = value[:1000]
                
                # Remove dangerous patterns
                dangerous_patterns = [
                    r"<script.*?>.*?</script>",
                    r"javascript:",
                    r"on\w+\s*=",
                ]
                
                for pattern in dangerous_patterns:
                    value = re.sub(pattern, "", value, flags=re.IGNORECASE)
            
            # Only allow basic types
            if isinstance(value, (str, int, float, bool)):
                sanitized[key] = value
        
        return sanitized