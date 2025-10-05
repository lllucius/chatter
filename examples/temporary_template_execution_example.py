#!/usr/bin/env python3
"""Example script demonstrating the temporary template execution API.

This script shows how to execute a workflow template without storing it
in the database first.
"""

import asyncio
import json

# Uncomment these imports when using with actual SDK
# from chatter_sdk import ChatterClient
# from chatter_sdk.models import WorkflowTemplateDirectExecutionRequest


async def example_temporary_template_execution():
    """Example of executing a temporary template."""
    
    # This would be the actual usage with the SDK
    # client = ChatterClient(base_url="http://localhost:8000", api_key="your-api-key")
    
    # Define a temporary template
    template_data = {
        "name": "Quick Search Assistant",
        "description": "A simple search assistant that uses tools",
        "category": "custom",
        "default_params": {
            "model": "gpt-4",
            "temperature": 0.7,
            "system_prompt": "You are a helpful search assistant. Use the available tools to find information and provide accurate answers.",
        },
        "required_tools": ["search"],
        "required_retrievers": None,
    }
    
    # Define input data for this execution
    input_data = {
        "temperature": 0.9,  # Override the default temperature
        "max_tokens": 1000,
        "user_query": "What are the latest developments in quantum computing?",
    }
    
    # Create the execution request
    execution_request = {
        "template": template_data,
        "input_data": input_data,
        "debug_mode": False,
    }
    
    print("Temporary Template Execution Request:")
    print(json.dumps(execution_request, indent=2))
    print("\nThis request would be sent to: POST /api/v1/workflows/templates/execute")
    
    # With the actual SDK, you would do:
    # response = await client.workflows.execute_temporary_template(
    #     WorkflowTemplateDirectExecutionRequest(**execution_request)
    # )
    # print(f"Execution ID: {response.id}")
    # print(f"Status: {response.status}")
    # print(f"Result: {response.output_data}")


async def example_vs_stored_template():
    """Example showing the difference between temporary and stored template execution."""
    
    print("=" * 80)
    print("COMPARISON: Temporary vs Stored Template Execution")
    print("=" * 80)
    
    print("\n1. STORED TEMPLATE EXECUTION (existing approach):")
    print("-" * 80)
    print("Step 1: Create and save template")
    template_create = {
        "name": "Customer Support Assistant",
        "description": "Template for customer support",
        "category": "customer_support",
        "default_params": {"model": "gpt-4", "temperature": 0.7},
    }
    print(f"POST /api/v1/workflows/templates")
    print(json.dumps(template_create, indent=2))
    print("\nResponse: { id: 'template_123', ... }")
    
    print("\nStep 2: Execute the stored template")
    execution_request = {
        "input_data": {"customer_query": "How do I reset my password?"},
        "debug_mode": False,
    }
    print(f"POST /api/v1/workflows/templates/template_123/execute")
    print(json.dumps(execution_request, indent=2))
    
    print("\n" + "=" * 80)
    print("\n2. TEMPORARY TEMPLATE EXECUTION (new approach):")
    print("-" * 80)
    print("Single step: Execute template directly without saving")
    temp_execution_request = {
        "template": {
            "name": "One-time Support Query",
            "description": "Temporary template for a specific query",
            "category": "custom",
            "default_params": {"model": "gpt-4", "temperature": 0.7},
        },
        "input_data": {"customer_query": "How do I reset my password?"},
        "debug_mode": False,
    }
    print(f"POST /api/v1/workflows/templates/execute")
    print(json.dumps(temp_execution_request, indent=2))
    
    print("\n" + "=" * 80)
    print("\nBENEFITS OF TEMPORARY TEMPLATE EXECUTION:")
    print("-" * 80)
    print("✓ No database clutter - template is not persisted")
    print("✓ Faster for one-time use cases")
    print("✓ Ideal for testing and development")
    print("✓ Perfect for dynamic, programmatically generated templates")
    print("✓ Same execution capabilities as stored templates")
    print("\n" + "=" * 80)


async def example_testing_workflow():
    """Example of using temporary templates for testing."""
    
    print("\n" + "=" * 80)
    print("USE CASE: Testing Different Template Configurations")
    print("=" * 80)
    
    # Test different temperatures
    for temp in [0.3, 0.7, 0.9]:
        template_data = {
            "name": f"Test Template - Temp {temp}",
            "description": f"Testing with temperature {temp}",
            "category": "custom",
            "default_params": {
                "model": "gpt-4",
                "temperature": temp,
                "system_prompt": "You are a creative writing assistant.",
            },
        }
        
        execution_request = {
            "template": template_data,
            "input_data": {
                "prompt": "Write a short poem about the ocean.",
            },
            "debug_mode": True,  # Enable debug mode for testing
        }
        
        print(f"\nTest {temp}:")
        print(f"POST /api/v1/workflows/templates/execute")
        print(f"Temperature: {temp}, Debug: True")
        # In practice, you would execute and compare results


if __name__ == "__main__":
    print("=" * 80)
    print("Temporary Template Execution Examples")
    print("=" * 80)
    
    asyncio.run(example_temporary_template_execution())
    print("\n")
    asyncio.run(example_vs_stored_template())
    print("\n")
    asyncio.run(example_testing_workflow())
    
    print("\n" + "=" * 80)
    print("For more information, see TEMPORARY_TEMPLATE_EXECUTION.md")
    print("=" * 80)
