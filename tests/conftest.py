"""Minimal working conftest.py to build upon."""

import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from chatter.utils.database import Base, get_session_generator
from chatter.main import create_app


@pytest.fixture
def minimal_fixture():
    """Minimal fixture for testing."""
    return "minimal_value"