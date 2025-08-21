"""
Chatter - Advanced AI Chatbot Backend API Platform

A comprehensive Python-based backend API platform for building advanced AI chatbots,
implemented with FastAPI, LangChain, LangGraph, Postgres, PGVector, and SQLAlchemy.
"""

__version__ = "0.1.0"
__author__ = "Chatter Team"
__email__ = "team@chatter.ai"
__description__ = "Advanced AI Chatbot Backend API Platform"

# Version info tuple for programmatic access
VERSION_INFO = tuple(int(part) for part in __version__.split('.'))

# Public API
__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__description__",
    "VERSION_INFO",
]
