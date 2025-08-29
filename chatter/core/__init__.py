"""Core business logic."""

# Conditional imports to avoid dependency issues during testing
try:
    from .agents import agent_manager
except ImportError:
    agent_manager = None

try:
    from .langchain import orchestrator
except ImportError:
    orchestrator = None

try:
    from .langgraph import workflow_manager
except ImportError:
    workflow_manager = None

try:
    from .vector_store import vector_store_manager
except ImportError:
    vector_store_manager = None

__all__ = [
    "agent_manager",
    "orchestrator", 
    "workflow_manager",
    "vector_store_manager"
]
