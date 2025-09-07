"""
Example demonstrating how the frontend workflow editor integrates with the backend APIs.

This shows the typical flow of operations that would occur when a user:
1. Creates a complex workflow in the editor
2. Analyzes the workflow complexity  
3. Saves it as a template
4. Executes the workflow

This is for demonstration purposes and would not be run in production.
"""

import asyncio
from datetime import datetime
from typing import Any

# Simulated API calls that the frontend would make to the backend


def create_sample_workflow_definition() -> dict[str, Any]:
    """Create a sample workflow definition matching the frontend editor format."""
    return {
        "name": "Customer Support RAG Workflow",
        "description": "Advanced customer support workflow with RAG retrieval, error handling, and analytics",
        "nodes": [
            {
                "id": "start-1",
                "type": "start",
                "position": {"x": 100, "y": 100},
                "data": {
                    "label": "Start",
                    "nodeType": "start",
                    "config": {}
                }
            },
            {
                "id": "retrieval-1",
                "type": "retrieval",
                "position": {"x": 300, "y": 100},
                "data": {
                    "label": "Search Knowledge Base",
                    "nodeType": "retrieval",
                    "config": {
                        "query": "customer inquiry",
                        "limit": 5,
                        "threshold": 0.8
                    }
                }
            },
            {
                "id": "conditional-1",
                "type": "conditional",
                "position": {"x": 500, "y": 100},
                "data": {
                    "label": "Results Found?",
                    "nodeType": "conditional",
                    "config": {
                        "condition": "len(retrieval_results) > 0"
                    }
                }
            },
            {
                "id": "model-1",
                "type": "model",
                "position": {"x": 700, "y": 50},
                "data": {
                    "label": "Generate Response",
                    "nodeType": "model",
                    "config": {
                        "model": "gpt-4",
                        "systemMessage": "You are a helpful customer support assistant. Use the provided knowledge base results to answer the customer's question.",
                        "temperature": 0.7,
                        "maxTokens": 500
                    }
                }
            },
            {
                "id": "error-handler-1",
                "type": "error_handler",
                "position": {"x": 700, "y": 150},
                "data": {
                    "label": "Fallback Handler",
                    "nodeType": "error_handler",
                    "config": {
                        "retryCount": 2,
                        "fallbackAction": "escalate_to_human"
                    }
                }
            },
            {
                "id": "variable-1",
                "type": "variable",
                "position": {"x": 900, "y": 100},
                "data": {
                    "label": "Store Response",
                    "nodeType": "variable",
                    "config": {
                        "operation": "set",
                        "variableName": "final_response",
                        "value": "model_output"
                    }
                }
            }
        ],
        "edges": [
            {
                "id": "e1",
                "source": "start-1",
                "target": "retrieval-1",
                "type": "default",
                "data": {}
            },
            {
                "id": "e2",
                "source": "retrieval-1",
                "target": "conditional-1",
                "type": "default",
                "data": {}
            },
            {
                "id": "e3",
                "source": "conditional-1",
                "target": "model-1",
                "type": "default",
                "data": {
                    "condition": "results_found",
                    "label": "Yes"
                }
            },
            {
                "id": "e4",
                "source": "conditional-1",
                "target": "error-handler-1",
                "type": "default",
                "data": {
                    "condition": "no_results",
                    "label": "No"
                }
            },
            {
                "id": "e5",
                "source": "model-1",
                "target": "variable-1",
                "type": "default",
                "data": {}
            },
            {
                "id": "e6",
                "source": "error-handler-1",
                "target": "variable-1",
                "type": "default",
                "data": {}
            }
        ],
        "metadata": {
            "category": "customer_support",
            "tags": ["rag", "customer-support", "error-handling"],
            "complexity_hint": "medium"
        }
    }


async def demonstrate_workflow_backend_integration():
    """Demonstrate the complete workflow from creation to execution."""

    print("🚀 Workflow Editor Backend Integration Demo")
    print("=" * 50)

    # Step 1: Create workflow definition
    print("\n1. Creating workflow definition...")
    workflow_def = create_sample_workflow_definition()
    print(f"   ✓ Created workflow with {len(workflow_def['nodes'])} nodes and {len(workflow_def['edges'])} edges")

    # Step 2: Validate workflow
    print("\n2. Validating workflow...")
    # POST /api/workflows/definitions/validate
    print("   ✓ Validation passed - workflow is structurally sound")
    print("   ✓ All nodes have valid configurations")
    print("   ✓ No orphaned nodes detected")

    # Step 3: Analyze workflow complexity
    print("\n3. Analyzing workflow complexity...")
    # GET /api/workflows/definitions/{id}/analytics
    analytics_result = {
        "complexity": {
            "score": 45,
            "node_count": 6,
            "edge_count": 6,
            "depth": 4,
            "branching_factor": 1.17,
            "loop_complexity": 0,
            "conditional_complexity": 2
        },
        "bottlenecks": [
            {
                "node_id": "conditional-1",
                "node_type": "conditional",
                "reason": "Single decision point for entire workflow",
                "severity": "medium",
                "suggestions": [
                    "Consider adding parallel processing paths",
                    "Cache retrieval results for similar queries"
                ]
            }
        ],
        "optimization_suggestions": [
            {
                "type": "caching",
                "description": "Consider caching results from expensive retrieval operations",
                "impact": "high",
                "node_ids": ["retrieval-1"]
            },
            {
                "type": "parallelization",
                "description": "Model and error handler could run in parallel in some cases",
                "impact": "medium",
                "node_ids": ["model-1", "error-handler-1"]
            }
        ],
        "execution_paths": 2,
        "estimated_execution_time_ms": 3500,
        "risk_factors": [
            "No error handling for model failures",
            "Retrieval timeout not configured"
        ]
    }

    print(f"   ✓ Complexity Score: {analytics_result['complexity']['score']}/100")
    print(f"   ✓ Execution Paths: {analytics_result['execution_paths']}")
    print(f"   ✓ Estimated Time: {analytics_result['estimated_execution_time_ms']}ms")
    print(f"   ✓ Found {len(analytics_result['bottlenecks'])} bottlenecks")
    print(f"   ✓ Generated {len(analytics_result['optimization_suggestions'])} optimization suggestions")

    # Step 4: Save as template
    print("\n4. Saving as reusable template...")
    # POST /api/workflows/templates
    template_data = {
        "name": "Customer Support RAG Template",
        "description": "Template for customer support workflows with RAG and error handling",
        "workflow_type": "rag",
        "category": "customer_support",
        "default_params": {
            "retrieval_limit": 5,
            "model_temperature": 0.7,
            "max_tokens": 500
        },
        "required_tools": ["vector_search"],
        "required_retrievers": ["knowledge_base"],
        "tags": ["rag", "customer-support", "template"],
        "is_public": False
    }
    print("   ✓ Template saved with ID: template_12345")
    print("   ✓ Added to 'Customer Support' category")
    print("   ✓ Available for reuse by team members")

    # Step 5: Execute workflow
    print("\n5. Executing workflow...")
    # POST /api/workflows/definitions/{id}/execute
    execution_request = {
        "input_data": {
            "customer_query": "How do I reset my password?",
            "customer_id": "cust_789",
            "priority": "medium"
        },
        "context": {
            "session_id": "sess_456",
            "timestamp": datetime.utcnow().isoformat()
        }
    }

    # Simulated execution result
    execution_result = {
        "execution_id": "exec_12345",
        "status": "completed",
        "result": {
            "final_response": "To reset your password, please follow these steps: 1) Go to the login page...",
            "confidence": 0.95,
            "sources_used": 2
        },
        "steps": [
            {
                "node_id": "start-1",
                "node_type": "start",
                "status": "completed",
                "execution_time_ms": 5
            },
            {
                "node_id": "retrieval-1",
                "node_type": "retrieval",
                "status": "completed",
                "execution_time_ms": 245,
                "output_data": {"result_count": 3}
            },
            {
                "node_id": "conditional-1",
                "node_type": "conditional",
                "status": "completed",
                "execution_time_ms": 8
            },
            {
                "node_id": "model-1",
                "node_type": "model",
                "status": "completed",
                "execution_time_ms": 1850
            },
            {
                "node_id": "variable-1",
                "node_type": "variable",
                "status": "completed",
                "execution_time_ms": 3
            }
        ],
        "total_execution_time_ms": 2111,
        "started_at": "2025-01-07T10:30:00Z",
        "completed_at": "2025-01-07T10:30:02Z"
    }

    print(f"   ✓ Execution completed in {execution_result['total_execution_time_ms']}ms")
    print(f"   ✓ Status: {execution_result['status']}")
    print(f"   ✓ Processed {len(execution_result['steps'])} steps")
    print(f"   ✓ Generated response with {execution_result['result']['confidence']:.0%} confidence")

    # Step 6: Get node types for editor
    print("\n6. Frontend editor loading node types...")
    # GET /api/workflows/node-types
    print("   ✓ Loaded 10 supported node types")
    print("   ✓ Node properties loaded for editor configuration")

    print("\n🎉 Integration Demo Complete!")
    print("\nThe frontend workflow editor now has full backend support for:")
    print("  • Complex workflow creation and editing")
    print("  • Real-time workflow validation")
    print("  • Advanced analytics and optimization")
    print("  • Template management and reuse")
    print("  • Workflow execution with detailed step tracking")
    print("  • Support for all 10 node types including new advanced nodes")


def print_api_summary():
    """Print summary of all the new API endpoints."""
    print("\n📋 Backend API Endpoints Added")
    print("=" * 40)

    endpoints = [
        ("POST", "/api/workflows/definitions", "Create workflow definition"),
        ("GET", "/api/workflows/definitions", "List workflow definitions"),
        ("GET", "/api/workflows/definitions/{id}", "Get workflow definition"),
        ("PUT", "/api/workflows/definitions/{id}", "Update workflow definition"),
        ("DELETE", "/api/workflows/definitions/{id}", "Delete workflow definition"),
        ("POST", "/api/workflows/templates", "Create workflow template"),
        ("GET", "/api/workflows/templates", "List workflow templates"),
        ("PUT", "/api/workflows/templates/{id}", "Update workflow template"),
        ("GET", "/api/workflows/definitions/{id}/analytics", "Get workflow analytics"),
        ("POST", "/api/workflows/definitions/{id}/execute", "Execute workflow"),
        ("POST", "/api/workflows/definitions/validate", "Validate workflow"),
        ("GET", "/api/workflows/node-types", "Get supported node types"),
    ]

    for method, endpoint, description in endpoints:
        print(f"  {method:6} {endpoint:45} {description}")

    print(f"\n✅ Total: {len(endpoints)} new API endpoints")


if __name__ == "__main__":
    asyncio.run(demonstrate_workflow_backend_integration())
    print_api_summary()
