"""Workflow preparation service - extracts LLM, tools, retriever setup.

This service consolidates the preparation logic previously duplicated across
multiple execution methods in workflow_execution.py.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel

from chatter.core.workflow_graph_builder import create_workflow_definition_from_model
from chatter.core.langgraph import workflow_manager
from chatter.models.workflow import WorkflowDefinition
from chatter.services.llm import LLMService
from chatter.services.workflow_types import WorkflowConfig, WorkflowSource, WorkflowSourceType
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class PreparedWorkflow:
    """Prepared workflow ready for execution.
    
    This encapsulates all the components needed to execute a workflow,
    eliminating the need to pass them around separately.
    """

    workflow: Any  # LangGraph Pregel workflow
    definition: WorkflowDefinition  # For tracking and metadata
    llm: BaseChatModel
    tools: list[Any] | None
    retriever: Any | None
    config: WorkflowConfig


class WorkflowPreparationService:
    """Service for preparing workflows for execution.
    
    This consolidates LLM, tool, and retriever loading logic that was
    previously duplicated across 9 execution methods.
    """

    def __init__(self, llm_service: LLMService, session):
        """Initialize the preparation service."""
        self.llm_service = llm_service
        self.session = session

    async def prepare_workflow(
        self,
        source: WorkflowSource,
        config: WorkflowConfig,
        user_id: str,
        conversation_id: str,
    ) -> PreparedWorkflow:
        """Prepare workflow from any source.
        
        This method consolidates workflow preparation logic from:
        - _execute_with_universal_template()
        - _execute_with_dynamic_workflow()
        - _execute_streaming_with_universal_template()
        - _execute_streaming_with_dynamic_workflow()
        - execute_workflow_definition()
        
        Args:
            source: Source of the workflow (template, definition, or dynamic)
            config: Configuration for the workflow
            user_id: User executing the workflow
            conversation_id: Conversation ID for the workflow
            
        Returns:
            PreparedWorkflow with all components ready for execution
        """
        # Get/create definition based on source type
        if source.source_type == WorkflowSourceType.TEMPLATE:
            definition = await self._prepare_from_template(
                source, config, user_id
            )
        elif source.source_type == WorkflowSourceType.DEFINITION:
            definition = await self._prepare_from_definition(
                source, user_id
            )
        else:  # DYNAMIC
            definition = await self._prepare_dynamic(
                config, user_id, conversation_id
            )

        # Get LLM
        llm = await self.llm_service.get_llm(
            provider=config.provider,
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )

        # Get tools if enabled
        tools = None
        if config.enable_tools:
            tools = await self._get_tools(config, user_id)

        # Get retriever if enabled
        retriever = None
        if config.enable_retrieval and config.document_ids:
            retriever = await self._get_retriever(
                config.document_ids, user_id
            )

        # Create workflow
        workflow = await self._create_workflow(
            definition, llm, tools, retriever, config, user_id, conversation_id
        )

        return PreparedWorkflow(
            workflow=workflow,
            definition=definition,
            llm=llm,
            tools=tools,
            retriever=retriever,
            config=config,
        )

    async def _prepare_from_template(
        self, source: WorkflowSource, config: WorkflowConfig, user_id: str
    ) -> WorkflowDefinition:
        """Prepare workflow from a template.
        
        Consolidates template lookup logic from multiple methods.
        """
        from chatter.services.workflow_management import WorkflowManagementService

        workflow_mgmt = WorkflowManagementService(self.session)
        
        # Get template
        template = await workflow_mgmt.get_workflow_template(
            template_id=source.source_id,
            owner_id=user_id,
        )
        
        if not template:
            raise ValueError(f"Template not found: {source.source_id}")
        
        # Generate definition from template
        definition = await workflow_mgmt._generate_workflow_from_template(
            template=template,
            user_id=user_id,
            save_definition=False,  # Don't persist temporary definitions
        )
        
        logger.info(
            f"Prepared workflow from template: {source.source_id}",
            template_id=template.id,
            definition_id=definition.id,
        )
        
        return definition

    async def _prepare_from_definition(
        self, source: WorkflowSource, user_id: str
    ) -> WorkflowDefinition:
        """Prepare workflow from a stored definition.
        
        Consolidates definition lookup logic.
        """
        from chatter.services.workflow_management import WorkflowManagementService

        workflow_mgmt = WorkflowManagementService(self.session)
        
        # Get definition
        definition = await workflow_mgmt.get_workflow_definition(
            workflow_id=source.source_id,
            owner_id=user_id,
        )
        
        if not definition:
            raise ValueError(f"Definition not found: {source.source_id}")
        
        logger.info(
            f"Prepared workflow from definition: {source.source_id}",
            definition_id=definition.id,
        )
        
        return definition

    async def _prepare_dynamic(
        self, config: WorkflowConfig, user_id: str, conversation_id: str
    ) -> WorkflowDefinition:
        """Prepare dynamic workflow.
        
        Consolidates dynamic workflow creation from _execute_with_dynamic_workflow().
        """
        from chatter.core.workflow_graph_builder import create_simple_workflow_definition

        # Create simple workflow definition
        definition = create_simple_workflow_definition(
            user_id=user_id,
            provider=config.provider,
            model=config.model,
            enable_tools=config.enable_tools,
            enable_retrieval=config.enable_retrieval,
            enable_memory=config.enable_memory,
            system_prompt_override=config.system_prompt_override,
            allowed_tools=config.allowed_tools,
            memory_window=config.memory_window,
            max_tool_calls=config.max_tool_calls,
            user_id=user_id,
            conversation_id=conversation_id,
        )
        
        logger.info(
            "Prepared dynamic workflow",
            definition_id=definition.id,
            provider=config.provider,
            model=config.model,
        )
        
        return definition

    async def _get_tools(
        self, config: WorkflowConfig, user_id: str
    ) -> list[Any]:
        """Get and filter tools.
        
        Consolidates tool loading logic from multiple methods.
        """
        try:
            from chatter.core.tool_registry import tool_registry

            # Get all enabled tools for workspace
            tools = await tool_registry.get_enabled_tools_for_workspace(
                workspace_id=user_id,
                user_permissions=[],  # Future: integrate with WorkflowSecurityManager
                session=self.session,
            )

            # Filter tools by allowed_tools if specified
            if config.allowed_tools:
                allowed_tools_set = set(config.allowed_tools)
                filtered_tools = [
                    tool
                    for tool in tools
                    if tool_registry._get_tool_name(tool) in allowed_tools_set
                ]
                logger.info(
                    f"Filtered {len(tools)} tools down to {len(filtered_tools)} "
                    f"allowed tools: {config.allowed_tools}"
                )
                tools = filtered_tools

            logger.info(f"Loaded {len(tools)} tools for workflow execution")
            return tools

        except Exception as e:
            logger.warning(f"Could not load tools from tool registry: {e}")
            return []

    async def _get_retriever(
        self, document_ids: list[str], user_id: str
    ) -> Any | None:
        """Get retriever for document search.
        
        Consolidates retriever loading logic from multiple methods.
        """
        try:
            from chatter.core.vector_store import get_vector_store_retriever

            retriever = await get_vector_store_retriever(
                user_id=user_id,
                document_ids=document_ids,
            )
            logger.info(
                "Loaded retriever from vector store",
                document_ids=document_ids,
            )
            return retriever

        except Exception as e:
            logger.warning(f"Could not load retriever from vector store: {e}")
            return None

    async def _create_workflow(
        self,
        definition: WorkflowDefinition,
        llm: BaseChatModel,
        tools: list[Any] | None,
        retriever: Any | None,
        config: WorkflowConfig,
        user_id: str,
        conversation_id: str,
    ) -> Any:
        """Create LangGraph workflow.
        
        Consolidates workflow creation from definition.
        """
        # Convert database WorkflowDefinition to graph builder format
        graph_definition = create_workflow_definition_from_model(definition)

        # Create workflow
        workflow = await workflow_manager.create_workflow_from_definition(
            definition=graph_definition,
            llm=llm,
            retriever=retriever,
            tools=tools,
            max_tool_calls=config.max_tool_calls,
            user_id=user_id,
            conversation_id=conversation_id,
        )

        logger.debug(
            "Workflow created from definition",
            definition_id=definition.id,
        )

        return workflow
