"""
Mock data models for testing.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class HealthResponse:
    """Health check response model."""

    status: str
    timestamp: str


@dataclass
class UserCreate:
    """User creation model."""

    email: str
    username: str
    password: str


@dataclass
class ChatRequest:
    """Chat request model."""

    message: str
    conversation_id: Optional[str] = None
