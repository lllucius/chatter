"""Workflow templates for common use cases.

This module provides basic workflow template definitions.
Template management functionality has been moved to unified_template_manager.py
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class WorkflowTemplate:
    """Pre-configured workflow template."""

    name: str
    workflow_type: str
    description: str
    default_params: dict[str, Any]
    required_tools: list[str] | None = None
    required_retrievers: list[str] | None = None


# Built-in workflow templates (kept for backward compatibility)
WORKFLOW_TEMPLATES = {
    "customer_support": WorkflowTemplate(
        name="customer_support",
        workflow_type="full",
        description="Customer support with knowledge base and tools",
        default_params={
            "enable_memory": True,
            "memory_window": 50,
            "max_tool_calls": 5,
            "system_message": "You are a helpful customer support assistant. Use the knowledge base to find relevant information and available tools to help resolve customer issues. Always be polite, professional, and thorough in your responses.",
        },
        required_tools=["search_kb", "create_ticket", "escalate"],
        required_retrievers=["support_docs"],
    ),
    "code_assistant": WorkflowTemplate(
        name="code_assistant",
        workflow_type="tools",
        description="Programming assistant with code tools",
        default_params={
            "enable_memory": True,
            "memory_window": 100,
            "max_tool_calls": 10,
            "system_message": "You are an expert programming assistant. Help users with coding tasks, debugging, code review, and software development best practices. Use available tools to execute code, run tests, and access documentation when needed.",
        },
        required_tools=[
            "execute_code",
            "search_docs",
            "generate_tests",
        ],
    ),
    "research_assistant": WorkflowTemplate(
        name="research_assistant",
        workflow_type="rag",
        description="Research assistant with document retrieval",
        default_params={
            "enable_memory": True,
            "memory_window": 30,
            "max_documents": 10,
            "system_message": "You are a research assistant. Use the provided documents to answer questions accurately and thoroughly. Always cite your sources and explain your reasoning. If information is not available in the documents, clearly state this limitation.",
        },
        required_retrievers=["research_docs"],
    ),
    "general_chat": WorkflowTemplate(
        name="general_chat",
        workflow_type="plain",
        description="General conversation assistant",
        default_params={
            "enable_memory": True,
            "memory_window": 20,
            "system_message": "You are a helpful, harmless, and honest AI assistant. Engage in natural conversation while being informative and supportive.",
        },
    ),
    "document_qa": WorkflowTemplate(
        name="document_qa",
        workflow_type="rag",
        description="Document question answering with retrieval",
        default_params={
            "enable_memory": False,  # Each question should be independent
            "max_documents": 15,
            "similarity_threshold": 0.7,
            "system_message": "You are a document analysis assistant. Answer questions based solely on the provided documents. Be precise and cite specific sections when possible.",
        },
        required_retrievers=["document_store"],
    ),
    "data_analyst": WorkflowTemplate(
        name="data_analyst",
        workflow_type="tools",
        description="Data analysis assistant with computation tools",
        default_params={
            "enable_memory": True,
            "memory_window": 50,
            "max_tool_calls": 15,
            "system_message": "You are a data analyst assistant. Help users analyze data, create visualizations, and derive insights. Use computational tools to perform calculations and generate charts.",
        },
        required_tools=[
            "execute_python",
            "create_chart",
            "analyze_data",
        ],
    ),
}
