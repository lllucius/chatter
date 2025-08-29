"""
Chatter Python SDK - Mock Implementation
This is a minimal implementation for testing purposes.
"""

__version__ = "0.1.0"

from .client import ChatterClient
from .models import HealthResponse

__all__ = ["ChatterClient", "HealthResponse"]
