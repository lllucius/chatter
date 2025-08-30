"""Advanced workflow features including conditional and composite workflows."""

# Simple logger fallback
import logging
from typing import Any, Literal
from uuid import uuid4

logger = logging.getLogger(__name__)

ExecutionStrategy = Literal["sequential", "parallel", "conditional"]


class ConditionalWorkflowConfig:
    """Configuration for conditional workflow selection."""

    def __init__(
        self,
        conditions: dict[str, Any],
        workflow_configs: dict[str, dict[str, Any]]
    ):
        """Initialize conditional workflow configuration.

        Args:
            conditions: Dictionary of condition names to condition values
            workflow_configs: Dictionary mapping condition results to workflow configs
        """
        self.conditions = conditions
        self.workflow_configs = workflow_configs

    def evaluate_conditions(self, context: dict[str, Any]) -> str | None:
        """Evaluate conditions against context to determine workflow.

        Args:
            context: Context data to evaluate conditions against

        Returns:
            Key of the workflow config to use, or None if no conditions match
        """
        for condition_name, condition_value in self.conditions.items():
            context_value = context.get(condition_name)

            # Simple equality check - can be extended for more complex logic
            if isinstance(condition_value, dict):
                # Handle range conditions
                if "min" in condition_value and "max" in condition_value:
                    if (context_value is not None and
                            condition_value["min"] <= context_value <= condition_value["max"]):
                        return condition_name
                # Handle list membership
                elif "in" in condition_value:
                    if context_value in condition_value["in"]:
                        return condition_name
            elif context_value == condition_value:
                return condition_name

        # Return default if no conditions match
        return self.workflow_configs.get("default", {}).get("key")


class CompositeWorkflowConfig:
    """Configuration for composite workflow execution."""

    def __init__(
        self,
        workflows: list[dict[str, Any]],
        execution_strategy: ExecutionStrategy = "sequential"
    ):
        """Initialize composite workflow configuration.

        Args:
            workflows: List of workflow configurations
            execution_strategy: How to execute the workflows
        """
        self.workflows = workflows
        self.execution_strategy = execution_strategy
        self.workflow_id = str(uuid4())


class AdvancedWorkflowManager:
    """Manager for advanced workflow features."""

    def __init__(self):
        """Initialize advanced workflow manager."""
        self.conditional_configs: dict[str, ConditionalWorkflowConfig] = {}
        self.composite_configs: dict[str, CompositeWorkflowConfig] = {}

    async def create_conditional_workflow(
        self,
        llm: Any,
        conditions: dict[str, Any],
        workflow_configs: dict[str, dict[str, Any]],
        context: dict[str, Any] | None = None
    ) -> Any | None:
        """Create a workflow based on conditions.

        Args:
            llm: Language model to use
            conditions: Dictionary of conditions to evaluate
            workflow_configs: Dictionary mapping condition results to workflow configs
            context: Context data for condition evaluation

        Returns:
            Created workflow or None if no conditions match
        """
        config = ConditionalWorkflowConfig(conditions, workflow_configs)

        # Use provided context or empty dict
        eval_context = context or {}

        # Evaluate conditions
        selected_config_key = config.evaluate_conditions(eval_context)

        if not selected_config_key or selected_config_key not in workflow_configs:
            logger.warning(
                "No matching condition found for conditional workflow",
                conditions=conditions,
                context=eval_context
            )
            return None

        selected_config = workflow_configs[selected_config_key]

        logger.info(
            "Creating conditional workflow",
            selected_config=selected_config_key,
            context=eval_context
        )

        # Create workflow with selected configuration
        try:
            # Import here to avoid circular imports
            from chatter.core.langgraph import LangGraphWorkflowManager

            manager = LangGraphWorkflowManager()
            workflow = manager.create_workflow(
                llm=llm,
                mode=selected_config.get("mode", "plain"),
                enable_memory=selected_config.get("enable_memory", False),
                memory_window=selected_config.get("memory_window", 20),
                system_message=selected_config.get("system_message")
            )
            return workflow
        except Exception as e:
            logger.error(f"Failed to create workflow: {e}")
            return None

    async def create_composite_workflow(
        self,
        workflows: list[Any],
        execution_strategy: ExecutionStrategy = "sequential"
    ) -> CompositeWorkflowConfig:
        """Create a composite workflow that combines multiple workflows.

        Note: This creates a configuration object. Actual execution coordination
        would need to be handled by the calling code.

        Args:
            workflows: List of compiled workflows to combine
            execution_strategy: How to execute the workflows

        Returns:
            Composite workflow configuration
        """
        workflow_configs = []
        for i, workflow in enumerate(workflows):
            workflow_configs.append({
                "index": i,
                "workflow": workflow,
                "workflow_id": str(uuid4())
            })

        config = CompositeWorkflowConfig(
            workflows=workflow_configs,
            execution_strategy=execution_strategy
        )

        self.composite_configs[config.workflow_id] = config

        logger.info(
            "Created composite workflow",
            workflow_id=config.workflow_id,
            strategy=execution_strategy,
            workflow_count=len(workflows)
        )

        return config

    async def execute_composite_workflow(
        self,
        config: CompositeWorkflowConfig,
        initial_state: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Execute a composite workflow.

        Args:
            config: Composite workflow configuration
            initial_state: Initial state to pass to workflows

        Returns:
            List of results from each workflow
        """
        results = []
        current_state = initial_state.copy()

        if config.execution_strategy == "sequential":
            # Execute workflows one after another, chaining state
            for workflow_config in config.workflows:
                workflow = workflow_config["workflow"]

                logger.info(
                    "Executing workflow in sequence",
                    composite_id=config.workflow_id,
                    workflow_index=workflow_config["index"]
                )

                try:
                    # Import here to avoid circular imports
                    from chatter.core.langgraph import (
                        LangGraphWorkflowManager,
                    )

                    manager = LangGraphWorkflowManager()
                    result = await manager.run_workflow(
                        workflow=workflow,
                        initial_state=current_state,
                        thread_id=workflow_config["workflow_id"]
                    )
                    results.append(result)

                    # Update state for next workflow (merge results)
                    if isinstance(result, dict):
                        current_state.update(result)

                except Exception as e:
                    logger.error(
                        "Error in composite workflow execution",
                        composite_id=config.workflow_id,
                        workflow_index=workflow_config["index"],
                        error=str(e)
                    )
                    results.append({"error": str(e)})

        elif config.execution_strategy == "parallel":
            # Execute all workflows in parallel with same initial state
            import asyncio

            async def execute_single(workflow_config: dict[str, Any]) -> dict[str, Any]:
                workflow = workflow_config["workflow"]
                try:
                    from chatter.core.langgraph import (
                        LangGraphWorkflowManager,
                    )

                    manager = LangGraphWorkflowManager()
                    return await manager.run_workflow(
                        workflow=workflow,
                        initial_state=initial_state,
                        thread_id=workflow_config["workflow_id"]
                    )
                except Exception as e:
                    logger.error(
                        "Error in parallel workflow execution",
                        composite_id=config.workflow_id,
                        workflow_index=workflow_config["index"],
                        error=str(e)
                    )
                    return {"error": str(e)}

            logger.info(
                "Executing workflows in parallel",
                composite_id=config.workflow_id,
                workflow_count=len(config.workflows)
            )

            results = await asyncio.gather(*[
                execute_single(wf_config) for wf_config in config.workflows
            ])
            results = list(results)

        else:
            raise ValueError(f"Unsupported execution strategy: {config.execution_strategy}")

        logger.info(
            "Completed composite workflow execution",
            composite_id=config.workflow_id,
            strategy=config.execution_strategy,
            results_count=len(results)
        )

        return results

    def register_conditional_config(
        self,
        config_name: str,
        conditions: dict[str, Any],
        workflow_configs: dict[str, dict[str, Any]]
    ) -> None:
        """Register a reusable conditional workflow configuration.

        Args:
            config_name: Name for the configuration
            conditions: Dictionary of conditions to evaluate
            workflow_configs: Dictionary mapping condition results to workflow configs
        """
        self.conditional_configs[config_name] = ConditionalWorkflowConfig(
            conditions, workflow_configs
        )

        logger.info(
            "Registered conditional workflow configuration",
            config_name=config_name,
            conditions=list(conditions.keys())
        )

    async def create_workflow_from_template(
        self,
        llm: Any,
        template_name: str,
        context: dict[str, Any] | None = None
    ) -> Any | None:
        """Create workflow from a registered conditional configuration template.

        Args:
            llm: Language model to use
            template_name: Name of the registered configuration
            context: Context for condition evaluation

        Returns:
            Created workflow or None if template not found or conditions don't match
        """
        if template_name not in self.conditional_configs:
            logger.error(
                "Conditional workflow template not found",
                template_name=template_name
            )
            return None

        config = self.conditional_configs[template_name]

        return await self.create_conditional_workflow(
            llm=llm,
            conditions=config.conditions,
            workflow_configs=config.workflow_configs,
            context=context
        )


# Example predefined configurations
def setup_default_conditional_configs(manager: AdvancedWorkflowManager) -> None:
    """Setup default conditional workflow configurations."""

    # Customer support workflow based on query complexity
    manager.register_conditional_config(
        "customer_support",
        conditions={
            "query_complexity": {"min": 0.7, "max": 1.0},  # High complexity
            "query_type": "technical_support",
            "default": True
        },
        workflow_configs={
            "query_complexity": {
                "mode": "full",
                "enable_memory": True,
                "memory_window": 50
            },
            "query_type": {
                "mode": "tools",
                "enable_memory": True,
                "memory_window": 20
            },
            "default": {
                "mode": "plain",
                "enable_memory": False,
                "key": "default"
            }
        }
    )

    # Document analysis workflow based on document type
    manager.register_conditional_config(
        "document_analysis",
        conditions={
            "document_type": {"in": ["pdf", "docx", "txt"]},
            "has_images": True,
            "default": True
        },
        workflow_configs={
            "document_type": {
                "mode": "rag",
                "enable_memory": False
            },
            "has_images": {
                "mode": "full",
                "enable_memory": True
            },
            "default": {
                "mode": "plain",
                "key": "default"
            }
        }
    )


# Global instance
advanced_workflow_manager = AdvancedWorkflowManager()

# Setup default configurations
setup_default_conditional_configs(advanced_workflow_manager)
