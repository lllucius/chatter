#!/usr/bin/env python3
"""
RFC 9457 Problem Details Demo

This script demonstrates the new RFC 9457 compliant error responses
implemented in the Chatter API. Run this script to see examples of
the new error format.

Usage:
    python demo_rfc9457.py
"""

import json

from fastapi.testclient import TestClient

from chatter.main import create_app


def demo_rfc9457():
    """Demonstrate RFC 9457 error responses."""
    
    print("🚀 Chatter API - RFC 9457 Problem Details Demo")
    print("=" * 60)
    print()
    print("The Chatter API now returns RFC 9457 compliant error responses")
    print("with proper content-type 'application/problem+json' and structured")
    print("error information for better API client integration.")
    print()
    
    app = create_app()
    client = TestClient(app, base_url="http://localhost:8000")
    
    examples = [
        {
            "title": "Resource Not Found (404)",
            "description": "When a requested resource doesn't exist",
            "method": "GET",
            "url": "/api/v1/documents/nonexistent-id",
            "highlights": ["type URI", "instance reference", "detailed error info"]
        },
        {
            "title": "Authentication Required (403)", 
            "description": "When accessing protected endpoints without auth",
            "method": "GET",
            "url": "/api/v1/auth/me",
            "highlights": ["WWW-Authenticate header", "access-forbidden type"]
        },
        {
            "title": "Method Not Allowed (405)",
            "description": "When using wrong HTTP method",
            "method": "DELETE", 
            "url": "/healthz",
            "highlights": ["method-not-allowed type", "clear error message"]
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example['title']}")
        print(f"   {example['description']}")
        print(f"   Request: {example['method']} {example['url']}")
        print()
        
        # Make the request
        if example['method'] == 'GET':
            response = client.get(example['url'])
        elif example['method'] == 'DELETE':
            response = client.delete(example['url'])
        
        # Show the response
        print(f"   Response:")
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type')}")
        print()
        
        if response.headers.get('content-type') == 'application/problem+json':
            data = response.json()
            print(f"   RFC 9457 Problem Details:")
            print(f"   {json.dumps(data, indent=3)}")
            print()
            
            print(f"   Key highlights:")
            for highlight in example['highlights']:
                if 'type URI' in highlight:
                    print(f"   • Problem type URI: {data.get('type')}")
                elif 'instance' in highlight:
                    print(f"   • Specific instance: {data.get('instance')}")
                elif 'WWW-Authenticate' in highlight:
                    auth_header = response.headers.get('www-authenticate')
                    if auth_header:
                        print(f"   • WWW-Authenticate header: {auth_header}")
                else:
                    print(f"   • {highlight}")
        
        print("\n" + "-" * 50 + "\n")
    
    # Show a successful response for comparison
    print("✅ Successful Response (for comparison)")
    print("   Normal responses still use standard JSON format")
    print()
    
    response = client.get("/")
    print(f"   Request: GET /")
    print(f"   Status: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('content-type')}")
    print(f"   Response: {json.dumps(response.json(), indent=3)}")
    print()
    
    print("=" * 60)
    print("🎯 Benefits of RFC 9457 Implementation:")
    print()
    print("• Standardized error format across all endpoints")
    print("• Machine-readable problem types with URIs")
    print("• Consistent error structure for API clients")
    print("• Better debugging with instance references")
    print("• Compliance with modern API standards")
    print("• Improved developer experience")
    print()
    print("📚 Learn more about RFC 9457:")
    print("   https://www.rfc-editor.org/rfc/rfc9457.html")

if __name__ == "__main__":
    demo_rfc9457()