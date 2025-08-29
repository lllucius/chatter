"""Workflow templates for common use cases.

This module provides pre-configured workflow templates that make it easy to set up
workflows for common scenarios like customer support, code assistance, and research.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from chatter.core.exceptions import WorkflowConfigurationError


@dataclass
class WorkflowTemplate:
    """Pre-configured workflow template."""
    name: str
    workflow_type: str
    description: str
    default_params: Dict[str, Any]
    required_tools: Optional[List[str]] = None
    required_retrievers: Optional[List[str]] = None


# Built-in workflow templates
WORKFLOW_TEMPLATES = {
    "customer_support": WorkflowTemplate(
        name="customer_support",
        workflow_type="full",
        description="Customer support with knowledge base and tools",
        default_params={
            "enable_memory": True,
            "memory_window": 50,
            "max_tool_calls": 5,
            "system_message": "You are a helpful customer support assistant. Use the knowledge base to find relevant information and available tools to help resolve customer issues. Always be polite, professional, and thorough in your responses."
        },
        required_tools=["search_kb", "create_ticket", "escalate"],
        required_retrievers=["support_docs"]
    ),
    
    "code_assistant": WorkflowTemplate(
        name="code_assistant",
        workflow_type="tools",
        description="Programming assistant with code tools",
        default_params={
            "enable_memory": True,
            "memory_window": 100,
            "max_tool_calls": 10,
            "system_message": "You are an expert programming assistant. Help users with coding tasks, debugging, code review, and software development best practices. Use available tools to execute code, run tests, and access documentation when needed."
        },
        required_tools=["execute_code", "search_docs", "generate_tests"]
    ),
    
    "research_assistant": WorkflowTemplate(
        name="research_assistant",
        workflow_type="rag",
        description="Research assistant with document retrieval",
        default_params={
            "enable_memory": True,
            "memory_window": 30,
            "max_documents": 10,
            "system_message": "You are a research assistant. Use the provided documents to answer questions accurately and thoroughly. Always cite your sources and explain your reasoning. If information is not available in the documents, clearly state this limitation."
        },
        required_retrievers=["research_docs"]
    ),
    
    "general_chat": WorkflowTemplate(
        name="general_chat",
        workflow_type="plain",
        description="General conversation assistant",
        default_params={
            "enable_memory": True,
            "memory_window": 20,
            "system_message": "You are a helpful, harmless, and honest AI assistant. Engage in natural conversation while being informative and supportive."
        }
    ),
    
    "document_qa": WorkflowTemplate(
        name="document_qa",
        workflow_type="rag",
        description="Document question answering with retrieval",
        default_params={
            "enable_memory": False,  # Each question should be independent
            "max_documents": 15,
            "similarity_threshold": 0.7,
            "system_message": "You are a document analysis assistant. Answer questions based solely on the provided documents. Be precise and cite specific sections when possible."
        },
        required_retrievers=["document_store"]
    ),
    
    "data_analyst": WorkflowTemplate(
        name="data_analyst",
        workflow_type="tools",
        description="Data analysis assistant with computation tools",
        default_params={
            "enable_memory": True,
            "memory_window": 50,
            "max_tool_calls": 15,
            "system_message": "You are a data analyst assistant. Help users analyze data, create visualizations, and derive insights. Use computational tools to perform calculations and generate charts."
        },
        required_tools=["execute_python", "create_chart", "analyze_data"]
    )
}


class WorkflowTemplateManager:
    """Manages workflow templates and template-based workflow creation."""
    
    @classmethod
    def get_template(cls, template_name: str) -> WorkflowTemplate:
        """Get a workflow template by name.
        
        Args:
            template_name: Name of the template to retrieve
            
        Returns:
            WorkflowTemplate: The requested template
            
        Raises:
            WorkflowConfigurationError: If template is not found
        """
        if template_name not in WORKFLOW_TEMPLATES:
            available = ", ".join(WORKFLOW_TEMPLATES.keys())
            raise WorkflowConfigurationError(
                f"Template '{template_name}' not found. Available templates: {available}"
            )
        return WORKFLOW_TEMPLATES[template_name]
    
    @classmethod
    def list_templates(cls) -> List[str]:
        """List available template names.
        
        Returns:
            List of template names
        """
        return list(WORKFLOW_TEMPLATES.keys())
    
    @classmethod
    def get_template_info(cls) -> Dict[str, Dict[str, Any]]:
        """Get information about all available templates.
        
        Returns:
            Dictionary mapping template names to their information
        """
        return {
            name: {
                "name": template.name,
                "workflow_type": template.workflow_type,
                "description": template.description,
                "required_tools": template.required_tools or [],
                "required_retrievers": template.required_retrievers or [],
                "default_params": template.default_params
            }
            for name, template in WORKFLOW_TEMPLATES.items()
        }
    
    @classmethod
    async def create_workflow_from_template(
        cls, 
        template_name: str, 
        llm_service: Any,
        provider_name: str,
        overrides: Optional[Dict[str, Any]] = None,
        retriever: Any = None,
        tools: Optional[List[Any]] = None
    ):
        """Create a workflow from a template.
        
        Args:
            template_name: Name of the template to use
            llm_service: LLM service instance
            provider_name: LLM provider name
            overrides: Parameter overrides for the template
            retriever: Retriever instance (if required by template)
            tools: List of tools (if required by template)
            
        Returns:
            Configured workflow instance
            
        Raises:
            WorkflowConfigurationError: If template requirements are not met
        """
        template = cls.get_template(template_name)
        params = template.default_params.copy()
        
        # Apply overrides
        if overrides:
            params.update(overrides)
        
        # Validate requirements
        if template.required_tools and not tools:
            raise WorkflowConfigurationError(
                f"Template '{template_name}' requires tools: {template.required_tools}"
            )
        
        if template.required_retrievers and not retriever:
            raise WorkflowConfigurationError(
                f"Template '{template_name}' requires retrievers: {template.required_retrievers}"
            )
        
        # Create workflow with template parameters
        workflow_kwargs = {
            "provider_name": provider_name,
            "workflow_type": template.workflow_type,
            **params
        }
        
        # Add retriever and tools if provided
        if retriever:
            workflow_kwargs["retriever"] = retriever
        if tools:
            workflow_kwargs["tools"] = tools
        
        return await llm_service.create_langgraph_workflow(**workflow_kwargs)
    
    @classmethod
    def validate_template_requirements(
        cls,
        template_name: str,
        available_tools: Optional[List[str]] = None,
        available_retrievers: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Validate if template requirements can be satisfied.
        
        Args:
            template_name: Name of the template to validate
            available_tools: List of available tool names
            available_retrievers: List of available retriever names
            
        Returns:
            Dictionary with validation results
        """
        template = cls.get_template(template_name)
        
        result = {
            "valid": True,
            "missing_tools": [],
            "missing_retrievers": [],
            "requirements_met": True
        }
        
        # Check tool requirements
        if template.required_tools:
            available_tools = available_tools or []
            missing_tools = [
                tool for tool in template.required_tools 
                if tool not in available_tools
            ]
            if missing_tools:
                result["missing_tools"] = missing_tools
                result["requirements_met"] = False
        
        # Check retriever requirements
        if template.required_retrievers:
            available_retrievers = available_retrievers or []
            missing_retrievers = [
                retriever for retriever in template.required_retrievers
                if retriever not in available_retrievers
            ]
            if missing_retrievers:
                result["missing_retrievers"] = missing_retrievers
                result["requirements_met"] = False
        
        result["valid"] = result["requirements_met"]
        return result