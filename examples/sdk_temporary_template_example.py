#!/usr/bin/env python3
"""Example using Python SDK to execute a temporary workflow template.

This example demonstrates how to use the Chatter Python SDK to execute
a workflow template without storing it in the database first.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add SDK to path
sdk_path = Path(__file__).parent.parent / "sdk" / "python"
if str(sdk_path) not in sys.path:
    sys.path.insert(0, str(sdk_path))

from chatter_sdk import ApiClient, Configuration, WorkflowsApi
from chatter_sdk.models import WorkflowTemplateDirectExecutionRequest


async def execute_temporary_template_with_sdk():
    """Execute a temporary template using the Python SDK."""
    
    # Configuration
    api_key = os.getenv("CHATTER_API_KEY", "your-api-key-here")
    base_url = os.getenv("CHATTER_API_BASE_URL", "http://localhost:8000")
    
    # Configure the SDK
    configuration = Configuration(
        host=base_url,
        api_key={"HTTPBearer": api_key}
    )
    
    print("=" * 80)
    print("Executing Temporary Template with Python SDK")
    print("=" * 80)
    print(f"\nAPI Base URL: {base_url}")
    print(f"Using API Key: {api_key[:10]}..." if len(api_key) > 10 else f"Using API Key: {api_key}")
    
    # Create the API client
    async with ApiClient(configuration) as api_client:
        # Create the workflows API instance
        workflows_api = WorkflowsApi(api_client)
        
        # Define the temporary template
        template_data = {
            "name": "Quick Search Assistant",
            "description": "A simple search assistant for one-time use",
            "category": "custom",
            "default_params": {
                "model": "gpt-4",
                "temperature": 0.7,
                "system_prompt": "You are a helpful search assistant. Use available tools to find information and provide accurate answers."
            },
            "required_tools": ["search"],
            "required_retrievers": None
        }
        
        # Define input data for this execution
        input_data = {
            "temperature": 0.9,  # Override default temperature
            "max_tokens": 1000,
            "user_query": "What are the latest developments in quantum computing?"
        }
        
        # Create the execution request
        execution_request = WorkflowTemplateDirectExecutionRequest(
            template=template_data,
            input_data=input_data,
            debug_mode=False
        )
        
        print("\n" + "-" * 80)
        print("Template Configuration:")
        print("-" * 80)
        print(f"Name: {template_data['name']}")
        print(f"Description: {template_data['description']}")
        print(f"Category: {template_data['category']}")
        print(f"Model: {template_data['default_params']['model']}")
        print(f"Temperature (default): {template_data['default_params']['temperature']}")
        print(f"Temperature (override): {input_data['temperature']}")
        print(f"Required Tools: {template_data['required_tools']}")
        
        print("\n" + "-" * 80)
        print("Executing Temporary Template...")
        print("-" * 80)
        
        try:
            # Execute the temporary template
            response = await workflows_api.execute_temporary_workflow_template_api_v1_workflows_templates_execute_post(
                workflow_template_direct_execution_request=execution_request
            )
            
            print("\n✅ Execution Successful!")
            print("-" * 80)
            print(f"Execution ID: {response.id}")
            print(f"Status: {response.status}")
            print(f"Created At: {response.created_at}")
            
            if hasattr(response, 'completed_at') and response.completed_at:
                print(f"Completed At: {response.completed_at}")
            
            if hasattr(response, 'output_data') and response.output_data:
                print(f"\nOutput Data:")
                print(response.output_data)
            
        except Exception as e:
            print(f"\n❌ Execution Failed!")
            print("-" * 80)
            print(f"Error: {str(e)}")
            if hasattr(e, 'body'):
                print(f"Details: {e.body}")
    
    print("\n" + "=" * 80)


async def main():
    """Main entry point."""
    print("\n" + "=" * 80)
    print("Temporary Template Execution - Python SDK Example")
    print("=" * 80)
    print("\nThis example demonstrates executing a workflow template")
    print("without storing it in the database using the Python SDK.")
    print("\nPrerequisites:")
    print("- Chatter API server running (default: http://localhost:8000)")
    print("- Valid API key set in CHATTER_API_KEY environment variable")
    print("=" * 80 + "\n")
    
    await execute_temporary_template_with_sdk()
    
    print("\n" + "=" * 80)
    print("Example Complete")
    print("=" * 80)
    print("\nKey Benefits of Temporary Template Execution:")
    print("✓ No database clutter - template is not persisted")
    print("✓ Faster for one-time use cases")
    print("✓ Ideal for testing and development")
    print("✓ Perfect for dynamic, programmatically generated templates")
    print("✓ Same execution capabilities as stored templates")
    print("\nFor more information, see TEMPORARY_TEMPLATE_EXECUTION.md")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
