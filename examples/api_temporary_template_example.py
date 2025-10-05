#!/usr/bin/env python3
"""Example using direct API calls to execute a temporary workflow template.

This example demonstrates how to use the Chatter API directly with the
requests library to execute a workflow template without storing it in
the database first.
"""

import json
import os
import sys
from datetime import datetime

try:
    import requests
except ImportError:
    print("Error: requests library not installed")
    print("Install it with: pip install requests")
    sys.exit(1)


def login_and_get_token(base_url):
    """Login to the API and get access token."""
    # Get credentials from environment or use defaults for examples
    username = os.getenv("CHATTER_USERNAME", "user@example.com")
    password = os.getenv("CHATTER_PASSWORD", "secure_password")
    
    login_endpoint = f"{base_url}/api/v1/auth/login"
    login_data = {
        "username": username,
        "password": password
    }
    
    print("\n" + "-" * 80)
    print("Logging in to Chatter API...")
    print("-" * 80)
    print(f"Login Endpoint: {login_endpoint}")
    print(f"Username: {username}")
    
    try:
        response = requests.post(
            login_endpoint,
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            access_token = result.get("access_token")
            print("✅ Login Successful!")
            print(f"Token expires in: {result.get('expires_in', 'N/A')} seconds")
            return access_token
        else:
            print(f"❌ Login Failed! Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            print("\nPlease set CHATTER_USERNAME and CHATTER_PASSWORD environment variables")
            return None
            
    except Exception as e:
        print(f"❌ Login Error: {str(e)}")
        print("\nPlease ensure the Chatter API server is running and credentials are correct")
        return None


def execute_temporary_template_with_api():
    """Execute a temporary template using direct API calls."""
    
    # Configuration
    base_url = os.getenv("CHATTER_API_BASE_URL", "http://localhost:8000")
    endpoint = f"{base_url}/api/v1/workflows/templates/execute"
    
    print("=" * 80)
    print("Executing Temporary Template with Direct API Calls")
    print("=" * 80)
    print(f"\nAPI Base URL: {base_url}")
    print(f"Endpoint: {endpoint}")
    
    # Login to get access token
    api_key = login_and_get_token(base_url)
    if not api_key:
        print("\n❌ Cannot proceed without authentication")
        return
    
    print(f"\nUsing API Key: {api_key[:10]}..." if len(api_key) > 10 else f"\nUsing API Key: {api_key}")
    
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
    request_body = {
        "template": template_data,
        "input_data": input_data,
        "debug_mode": False
    }
    
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
    print("Request Body (JSON):")
    print("-" * 80)
    print(json.dumps(request_body, indent=2))
    
    print("\n" + "-" * 80)
    print("Executing Temporary Template...")
    print("-" * 80)
    
    # Set up headers
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        # Make the POST request
        response = requests.post(
            endpoint,
            headers=headers,
            json=request_body,
            timeout=30
        )
        
        # Check the response
        if response.status_code == 200:
            print("\n✅ Execution Successful!")
            print("-" * 80)
            
            result = response.json()
            print(f"Execution ID: {result.get('id', 'N/A')}")
            print(f"Status: {result.get('status', 'N/A')}")
            print(f"Created At: {result.get('created_at', 'N/A')}")
            
            if 'completed_at' in result and result['completed_at']:
                print(f"Completed At: {result['completed_at']}")
            
            if 'output_data' in result and result['output_data']:
                print(f"\nOutput Data:")
                print(json.dumps(result['output_data'], indent=2))
            
            print("\n" + "-" * 80)
            print("Full Response:")
            print("-" * 80)
            print(json.dumps(result, indent=2))
            
        elif response.status_code == 401:
            print("\n❌ Authentication Failed!")
            print("-" * 80)
            print("Error: Invalid or missing API key")
            print("Please set the CHATTER_API_KEY environment variable with a valid API key")
            
        elif response.status_code == 422:
            print("\n❌ Validation Error!")
            print("-" * 80)
            print("Error: Invalid request body")
            try:
                error_detail = response.json()
                print(json.dumps(error_detail, indent=2))
            except:
                print(response.text)
            
        else:
            print(f"\n❌ Request Failed!")
            print("-" * 80)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection Failed!")
        print("-" * 80)
        print(f"Could not connect to {base_url}")
        print("Please ensure the Chatter API server is running")
        
    except requests.exceptions.Timeout:
        print("\n❌ Request Timeout!")
        print("-" * 80)
        print("The request took too long to complete")
        
    except Exception as e:
        print(f"\n❌ Unexpected Error!")
        print("-" * 80)
        print(f"Error: {str(e)}")
    
    print("\n" + "=" * 80)


def compare_with_stored_template():
    """Show the difference between temporary and stored template execution."""
    
    print("\n" + "=" * 80)
    print("COMPARISON: Temporary vs Stored Template Execution")
    print("=" * 80)
    
    base_url = os.getenv("CHATTER_API_BASE_URL", "http://localhost:8000")
    
    print("\n1. STORED TEMPLATE EXECUTION (existing approach):")
    print("-" * 80)
    print("Step 1: Create and save template")
    print(f"   POST {base_url}/api/v1/workflows/templates")
    
    template_create = {
        "name": "Customer Support Assistant",
        "description": "Template for customer support",
        "category": "customer_support",
        "default_params": {"model": "gpt-4", "temperature": 0.7}
    }
    print(json.dumps(template_create, indent=2))
    print("\n   Response: { \"id\": \"template_123\", ... }")
    
    print("\nStep 2: Execute the stored template")
    print(f"   POST {base_url}/api/v1/workflows/templates/template_123/execute")
    
    execution_request = {
        "input_data": {"customer_query": "How do I reset my password?"},
        "debug_mode": False
    }
    print(json.dumps(execution_request, indent=2))
    
    print("\n" + "=" * 80)
    print("\n2. TEMPORARY TEMPLATE EXECUTION (new approach):")
    print("-" * 80)
    print("Single step: Execute template directly without saving")
    print(f"   POST {base_url}/api/v1/workflows/templates/execute")
    
    temp_execution_request = {
        "template": {
            "name": "One-time Support Query",
            "description": "Temporary template for a specific query",
            "category": "custom",
            "default_params": {"model": "gpt-4", "temperature": 0.7}
        },
        "input_data": {"customer_query": "How do I reset my password?"},
        "debug_mode": False
    }
    print(json.dumps(temp_execution_request, indent=2))
    
    print("\n" + "=" * 80)
    print("\nBENEFITS OF TEMPORARY TEMPLATE EXECUTION:")
    print("-" * 80)
    print("✓ No database clutter - template is not persisted")
    print("✓ Faster for one-time use cases (single API call)")
    print("✓ Ideal for testing and development")
    print("✓ Perfect for dynamic, programmatically generated templates")
    print("✓ Same execution capabilities as stored templates")
    print("\n" + "=" * 80)


def main():
    """Main entry point."""
    print("\n" + "=" * 80)
    print("Temporary Template Execution - Direct API Example")
    print("=" * 80)
    print("\nThis example demonstrates executing a workflow template")
    print("without storing it in the database using direct API calls.")
    print("\nPrerequisites:")
    print("- Chatter API server running (default: http://localhost:8000)")
    print("- Valid credentials set in CHATTER_USERNAME and CHATTER_PASSWORD")
    print("  environment variables (or uses defaults: user@example.com/secure_password)")
    print("- requests library installed (pip install requests)")
    print("=" * 80 + "\n")
    
    # Execute the temporary template
    execute_temporary_template_with_api()
    
    # Show comparison
    compare_with_stored_template()
    
    print("\n" + "=" * 80)
    print("Example Complete")
    print("=" * 80)
    print("\nFor more information, see TEMPORARY_TEMPLATE_EXECUTION.md")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
