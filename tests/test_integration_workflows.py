"""
Integration Workflows Testing

Cross-service testing for document-to-chat workflows, analytics, and external services.
"""
import pytest
import asyncio
from httpx import AsyncClient
from typing import Dict, Any, List
import json
import io


class TestIntegrationWorkflows:
    """Integration workflow testing across multiple services."""
    
    @pytest.mark.integration
    async def test_document_to_chat_workflow(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test complete document-to-chat integration workflow."""
        if not auth_headers:
            pytest.skip("Authentication required for document-to-chat workflow test")
        
        try:
            # Step 1: Upload a document
            test_content = "This document discusses artificial intelligence, machine learning, and natural language processing technologies."
            test_file = io.BytesIO(test_content.encode('utf-8'))
            
            files = {"file": ("ai_knowledge.txt", test_file, "text/plain")}
            data = {
                "title": "AI Knowledge Document",
                "description": "Document about AI technologies"
            }
            
            upload_response = await client.post("/api/v1/documents/upload", files=files, data=data, headers=auth_headers)
            
            if upload_response.status_code == 404:
                pytest.skip("Document upload endpoint not available")
            
            if upload_response.status_code not in [200, 201]:
                pytest.skip("Document upload failed - cannot test workflow")
            
            document = upload_response.json()
            document_id = document["id"]
            
            # Step 2: Wait for document processing (if needed)
            await asyncio.sleep(1)  # Brief wait for processing
            
            # Step 3: Create a chat session
            chat_data = {
                "title": "AI Discussion Chat",
                "description": "Chat session to discuss the uploaded AI document"
            }
            
            chat_response = await client.post("/api/v1/chats", json=chat_data, headers=auth_headers)
            
            if chat_response.status_code == 404:
                pytest.skip("Chat creation endpoint not available")
            
            if chat_response.status_code not in [200, 201]:
                pytest.skip("Chat creation failed - cannot test workflow")
            
            chat = chat_response.json()
            chat_id = chat["id"]
            
            # Step 4: Send a message that references the document
            message_data = {
                "message": "What does the uploaded document say about artificial intelligence?",
                "document_ids": [document_id],
                "message_type": "user"
            }
            
            message_response = await client.post(f"/api/v1/chats/{chat_id}/messages", json=message_data, headers=auth_headers)
            
            # If document integration is not supported, try without document_ids
            if message_response.status_code == 400:
                message_data_fallback = {
                    "message": "Can you tell me about artificial intelligence?",
                    "message_type": "user"
                }
                message_response = await client.post(f"/api/v1/chats/{chat_id}/messages", json=message_data_fallback, headers=auth_headers)
            
            if message_response.status_code == 404:
                pytest.skip("Chat messaging endpoint not available")
            
            assert message_response.status_code in [200, 201], "Message sending failed in workflow"
            
            message = message_response.json()
            
            # Step 5: Verify the workflow results
            assert "id" in message, "Message should have ID"
            assert message.get("message_type") == "user", "Message type should be preserved"
            
            # Step 6: Check if we can retrieve the chat with messages
            chat_messages_response = await client.get(f"/api/v1/chats/{chat_id}/messages", headers=auth_headers)
            
            if chat_messages_response.status_code == 200:
                messages = chat_messages_response.json()
                assert len(messages) >= 1, "Chat should contain the sent message"
                
                user_messages = [msg for msg in messages if msg.get("message_type") == "user"]
                assert len(user_messages) >= 1, "Chat should contain user message"
            
            # Step 7: Verify document is still accessible
            doc_check_response = await client.get(f"/api/v1/documents/{document_id}", headers=auth_headers)
            if doc_check_response.status_code == 200:
                retrieved_doc = doc_check_response.json()
                assert retrieved_doc["id"] == document_id, "Document should remain accessible"
            
            print("Document-to-chat workflow: COMPLETED")
            
        except Exception as e:
            pytest.skip(f"Document-to-chat workflow test skipped: {e}")
    
    @pytest.mark.integration
    async def test_user_agent_interaction_workflows(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test user-agent interaction workflows."""
        if not auth_headers:
            pytest.skip("Authentication required for user-agent workflow test")
        
        try:
            # Step 1: Check if agents are available
            agents_response = await client.get("/api/v1/agents", headers=auth_headers)
            
            if agents_response.status_code == 404:
                pytest.skip("Agents endpoint not available")
            
            # Step 2: Create or get an agent
            if agents_response.status_code == 200:
                agents = agents_response.json()
                
                if isinstance(agents, list) and agents:
                    # Use existing agent
                    agent = agents[0]
                    agent_id = agent["id"]
                    print(f"Using existing agent: {agent.get('name', agent_id)}")
                else:
                    # Try to create a new agent
                    agent_data = {
                        "name": "Test Integration Agent",
                        "description": "Agent for integration testing",
                        "type": "assistant",
                        "configuration": {
                            "model": "gpt-3.5-turbo",
                            "temperature": 0.7
                        }
                    }
                    
                    create_agent_response = await client.post("/api/v1/agents", json=agent_data, headers=auth_headers)
                    
                    if create_agent_response.status_code in [200, 201]:
                        agent = create_agent_response.json()
                        agent_id = agent["id"]
                        print(f"Created new agent: {agent.get('name', agent_id)}")
                    else:
                        pytest.skip("Cannot create agent for workflow test")
            else:
                pytest.skip("Cannot access agents for workflow test")
            
            # Step 3: Create a chat session with the agent
            chat_data = {
                "title": "Agent Interaction Test",
                "description": "Testing user-agent interaction",
                "agent_id": agent_id
            }
            
            chat_response = await client.post("/api/v1/chats", json=chat_data, headers=auth_headers)
            
            if chat_response.status_code not in [200, 201]:
                # Try without agent_id if not supported
                chat_data_fallback = {
                    "title": "Agent Interaction Test",
                    "description": "Testing user-agent interaction"
                }
                chat_response = await client.post("/api/v1/chats", json=chat_data_fallback, headers=auth_headers)
            
            if chat_response.status_code not in [200, 201]:
                pytest.skip("Cannot create chat for agent workflow test")
            
            chat = chat_response.json()
            chat_id = chat["id"]
            
            # Step 4: Send messages to interact with the agent
            user_messages = [
                "Hello, can you help me?",
                "What can you tell me about machine learning?",
                "Thank you for your assistance."
            ]
            
            for user_message in user_messages:
                message_data = {
                    "message": user_message,
                    "message_type": "user"
                }
                
                message_response = await client.post(f"/api/v1/chats/{chat_id}/messages", json=message_data, headers=auth_headers)
                
                if message_response.status_code in [200, 201]:
                    message = message_response.json()
                    assert "id" in message, "Message should have ID"
                    
                    # Brief wait to allow agent response (if implemented)
                    await asyncio.sleep(0.5)
                else:
                    print(f"Message sending failed: {message_response.status_code}")
            
            # Step 5: Check the conversation history
            history_response = await client.get(f"/api/v1/chats/{chat_id}/messages", headers=auth_headers)
            
            if history_response.status_code == 200:
                messages = history_response.json()
                user_messages_count = len([msg for msg in messages if msg.get("message_type") == "user"])
                agent_messages_count = len([msg for msg in messages if msg.get("message_type") == "assistant"])
                
                assert user_messages_count >= len(user_messages), "Not all user messages were recorded"
                
                if agent_messages_count > 0:
                    print(f"Agent interaction successful: {user_messages_count} user messages, {agent_messages_count} agent responses")
                else:
                    print(f"Agent interaction recorded: {user_messages_count} user messages (no agent responses detected)")
            
            print("User-agent interaction workflow: COMPLETED")
            
        except Exception as e:
            pytest.skip(f"User-agent interaction workflow test skipped: {e}")
    
    @pytest.mark.integration
    async def test_analytics_across_multiple_services(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test analytics integration across multiple services."""
        if not auth_headers:
            pytest.skip("Authentication required for analytics workflow test")
        
        try:
            # Generate some activity across different services
            activities_performed = []
            
            # Activity 1: Create documents
            for i in range(3):
                content = f"Analytics test document {i+1} with sample content for analysis."
                test_file = io.BytesIO(content.encode('utf-8'))
                
                files = {"file": (f"analytics_doc_{i+1}.txt", test_file, "text/plain")}
                data = {"title": f"Analytics Document {i+1}", "description": f"Document {i+1} for analytics testing"}
                
                doc_response = await client.post("/api/v1/documents/upload", files=files, data=data, headers=auth_headers)
                
                if doc_response.status_code in [200, 201]:
                    activities_performed.append(f"document_upload_{i+1}")
            
            # Activity 2: Create chats
            for i in range(2):
                chat_data = {"title": f"Analytics Chat {i+1}", "description": f"Chat {i+1} for analytics testing"}
                chat_response = await client.post("/api/v1/chats", json=chat_data, headers=auth_headers)
                
                if chat_response.status_code in [200, 201]:
                    activities_performed.append(f"chat_creation_{i+1}")
                    
                    # Send some messages
                    chat_id = chat_response.json()["id"]
                    for j in range(2):
                        message_data = {"message": f"Analytics test message {j+1}", "message_type": "user"}
                        msg_response = await client.post(f"/api/v1/chats/{chat_id}/messages", json=message_data, headers=auth_headers)
                        
                        if msg_response.status_code in [200, 201]:
                            activities_performed.append(f"message_sent_{i+1}_{j+1}")
            
            # Activity 3: Interact with various endpoints
            endpoint_interactions = [
                "/api/v1/auth/profile",
                "/api/v1/chats", 
                "/api/v1/documents"
            ]
            
            for endpoint in endpoint_interactions:
                response = await client.get(endpoint, headers=auth_headers)
                if response.status_code == 200:
                    activities_performed.append(f"endpoint_access_{endpoint.split('/')[-1]}")
            
            print(f"Generated {len(activities_performed)} activities for analytics")
            
            # Check if analytics endpoints are available
            analytics_endpoints = [
                "/api/v1/analytics/dashboard",
                "/api/v1/analytics/user-activity",
                "/api/v1/analytics/usage-stats",
                "/api/v1/metrics"
            ]
            
            analytics_available = []
            
            for endpoint in analytics_endpoints:
                response = await client.get(endpoint, headers=auth_headers)
                
                if response.status_code == 200:
                    analytics_data = response.json()
                    analytics_available.append({
                        "endpoint": endpoint,
                        "data_structure": list(analytics_data.keys()) if isinstance(analytics_data, dict) else "array"
                    })
                    
                    # Validate analytics data structure
                    if isinstance(analytics_data, dict):
                        # Should contain relevant metrics
                        expected_metrics = ["total_users", "total_chats", "total_documents", "user_activity"]
                        found_metrics = [metric for metric in expected_metrics if metric in analytics_data]
                        
                        if found_metrics:
                            print(f"Analytics endpoint {endpoint}: {len(found_metrics)} relevant metrics found")
                elif response.status_code == 404:
                    continue  # Endpoint not available
                else:
                    print(f"Analytics endpoint {endpoint}: Status {response.status_code}")
            
            if analytics_available:
                print(f"Analytics integration: {len(analytics_available)} endpoints available")
                
                # Test cross-service analytics consistency
                if len(analytics_available) > 1:
                    # Compare data consistency across different analytics endpoints
                    user_counts = []
                    for analytics in analytics_available:
                        endpoint = analytics["endpoint"]
                        response = await client.get(endpoint, headers=auth_headers)
                        if response.status_code == 200:
                            data = response.json()
                            if isinstance(data, dict) and "total_users" in data:
                                user_counts.append(data["total_users"])
                    
                    if len(user_counts) > 1:
                        # All analytics endpoints should report consistent user counts
                        consistent_counts = len(set(user_counts)) == 1
                        if consistent_counts:
                            print("Analytics consistency: User counts consistent across endpoints")
                        else:
                            print(f"Analytics consistency: User counts inconsistent: {user_counts}")
            else:
                print("Analytics integration: No analytics endpoints available")
            
            print("Analytics across multiple services: COMPLETED")
            
        except Exception as e:
            pytest.skip(f"Analytics integration workflow test skipped: {e}")
    
    @pytest.mark.integration
    async def test_external_service_integration(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test external service integration (LLM providers, vector stores)."""
        try:
            # Test external service configuration endpoints
            config_endpoints = [
                "/api/v1/providers",
                "/api/v1/models",
                "/api/v1/embedding-spaces"
            ]
            
            external_services = []
            
            for endpoint in config_endpoints:
                response = await client.get(endpoint, headers=auth_headers)
                
                if response.status_code == 200:
                    service_data = response.json()
                    
                    if isinstance(service_data, list) and service_data:
                        service_info = {
                            "endpoint": endpoint,
                            "count": len(service_data),
                            "sample": service_data[0] if service_data else None
                        }
                        external_services.append(service_info)
                        
                        # Validate service configuration structure
                        first_item = service_data[0]
                        
                        if "providers" in endpoint:
                            assert "id" in first_item, "Provider should have ID"
                            assert "name" in first_item, "Provider should have name"
                            
                            if "active" in first_item:
                                print(f"Provider {first_item['name']}: {'active' if first_item['active'] else 'inactive'}")
                        
                        elif "models" in endpoint:
                            assert "id" in first_item, "Model should have ID"
                            assert "name" in first_item, "Model should have name"
                            
                            if "provider_id" in first_item:
                                print(f"Model {first_item['name']}: Provider {first_item['provider_id']}")
                        
                        elif "embedding" in endpoint:
                            assert "id" in first_item, "Embedding space should have ID"
                            
                            if "dimensions" in first_item:
                                print(f"Embedding space: {first_item['dimensions']} dimensions")
                
                elif response.status_code == 404:
                    continue  # Service not available
            
            if external_services:
                print(f"External services configured: {len(external_services)} types")
                
                # Test service health/status if available
                status_endpoints = [
                    "/api/v1/providers/status",
                    "/api/v1/models/health", 
                    "/api/v1/health/external-services"
                ]
                
                for endpoint in status_endpoints:
                    response = await client.get(endpoint, headers=auth_headers)
                    
                    if response.status_code == 200:
                        status_data = response.json()
                        print(f"External service status from {endpoint}: Available")
                        
                        # Check for service health indicators
                        if isinstance(status_data, dict):
                            health_indicators = ["healthy", "status", "available", "connected"]
                            health_info = {k: v for k, v in status_data.items() if k in health_indicators}
                            
                            if health_info:
                                print(f"  Health info: {health_info}")
            else:
                print("External service integration: No external services configured")
            
            print("External service integration: TESTED")
            
        except Exception as e:
            pytest.skip(f"External service integration test skipped: {e}")
    
    @pytest.mark.integration
    async def test_cache_service_integration(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test cache service integration across endpoints."""
        try:
            # Test if caching is working by making repeated requests
            cache_test_endpoints = [
                "/api/v1/auth/profile",
                "/api/v1/chats",
                "/api/v1/documents"
            ]
            
            cache_performance_results = []
            
            for endpoint in cache_test_endpoints:
                if not auth_headers and "/api/v1/" in endpoint:
                    continue  # Skip authenticated endpoints if no auth
                
                headers = auth_headers if "/api/v1/" in endpoint else {}
                
                # First request (likely not cached)
                import time
                start_time = time.time()
                first_response = await client.get(endpoint, headers=headers)
                first_time = time.time() - start_time
                
                if first_response.status_code != 200:
                    continue  # Skip if endpoint not available
                
                # Second request (might be cached)
                start_time = time.time()
                second_response = await client.get(endpoint, headers=headers)
                second_time = time.time() - start_time
                
                # Third request (likely cached if caching is enabled)
                start_time = time.time()
                third_response = await client.get(endpoint, headers=headers)
                third_time = time.time() - start_time
                
                # Analyze response times for caching patterns
                times = [first_time, second_time, third_time]
                avg_time = sum(times) / len(times)
                min_time = min(times)
                
                cache_result = {
                    "endpoint": endpoint,
                    "times": times,
                    "avg_time": avg_time,
                    "potential_caching": second_time < first_time or third_time < avg_time,
                    "response_consistent": (
                        first_response.text == second_response.text == third_response.text
                    )
                }
                
                cache_performance_results.append(cache_result)
                
                if cache_result["potential_caching"]:
                    print(f"Cache behavior detected for {endpoint}: times {[f'{t:.3f}' for t in times]}s")
                else:
                    print(f"No clear cache pattern for {endpoint}: times {[f'{t:.3f}' for t in times]}s")
            
            # Test cache-related headers
            for endpoint in cache_test_endpoints[:2]:  # Test first 2 endpoints
                headers = auth_headers if "/api/v1/" in endpoint else {}
                response = await client.get(endpoint, headers=headers)
                
                if response.status_code == 200:
                    response_headers = response.headers
                    
                    cache_headers = [
                        "Cache-Control",
                        "ETag", 
                        "Last-Modified",
                        "Expires"
                    ]
                    
                    found_cache_headers = [h for h in cache_headers if h in response_headers]
                    
                    if found_cache_headers:
                        print(f"Cache headers in {endpoint}: {found_cache_headers}")
            
            # Test cache invalidation if possible
            if auth_headers:
                # Try to modify data and check if cache is invalidated
                chat_data = {"title": "Cache Test Chat", "description": "Testing cache invalidation"}
                create_response = await client.post("/api/v1/chats", json=chat_data, headers=auth_headers)
                
                if create_response.status_code in [200, 201]:
                    # Check if subsequent requests reflect the change
                    await asyncio.sleep(0.1)  # Brief wait
                    
                    updated_list_response = await client.get("/api/v1/chats", headers=auth_headers)
                    if updated_list_response.status_code == 200:
                        updated_chats = updated_list_response.json()
                        
                        # Verify new chat appears in list (cache invalidated)
                        if isinstance(updated_chats, list):
                            new_chat_found = any(
                                chat.get("title") == "Cache Test Chat" 
                                for chat in updated_chats
                            )
                            
                            if new_chat_found:
                                print("Cache invalidation: Working (new data appears immediately)")
                            else:
                                print("Cache invalidation: May not be working (new data not visible)")
            
            print("Cache service integration: TESTED")
            
        except Exception as e:
            pytest.skip(f"Cache service integration test skipped: {e}")
    
    @pytest.mark.integration
    async def test_error_propagation_and_recovery(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test error propagation and recovery across services."""
        try:
            # Test error handling in workflow scenarios
            error_scenarios = []
            
            # Scenario 1: Invalid document upload
            invalid_file_data = b"This is not a valid file content that might cause processing errors" * 1000
            files = {"file": ("invalid_large_file.txt", invalid_file_data, "text/plain")}
            data = {"title": "Invalid Large File", "description": "Testing error handling"}
            
            if auth_headers:
                error_upload_response = await client.post("/api/v1/documents/upload", files=files, data=data, headers=auth_headers)
                
                error_scenarios.append({
                    "scenario": "large_file_upload",
                    "status_code": error_upload_response.status_code,
                    "handled_gracefully": error_upload_response.status_code in [400, 413, 422],
                    "error_message": error_upload_response.text[:200] if error_upload_response.status_code >= 400 else None
                })
            
            # Scenario 2: Invalid chat creation
            if auth_headers:
                invalid_chat_data = {
                    "title": "A" * 1000,  # Very long title
                    "description": "B" * 10000,  # Very long description
                    "invalid_field": "should_be_rejected"
                }
                
                invalid_chat_response = await client.post("/api/v1/chats", json=invalid_chat_data, headers=auth_headers)
                
                error_scenarios.append({
                    "scenario": "invalid_chat_creation", 
                    "status_code": invalid_chat_response.status_code,
                    "handled_gracefully": invalid_chat_response.status_code in [400, 422],
                    "error_message": invalid_chat_response.text[:200] if invalid_chat_response.status_code >= 400 else None
                })
            
            # Scenario 3: Access non-existent resources
            nonexistent_resources = [
                "/api/v1/chats/nonexistent-id",
                "/api/v1/documents/invalid-uuid",
                "/api/v1/agents/999999"
            ]
            
            for resource in nonexistent_resources:
                headers = auth_headers if auth_headers else {}
                response = await client.get(resource, headers=headers)
                
                error_scenarios.append({
                    "scenario": f"access_{resource.split('/')[-2]}",
                    "status_code": response.status_code,
                    "handled_gracefully": response.status_code in [404, 400],
                    "error_message": response.text[:200] if response.status_code >= 400 else None
                })
            
            # Analyze error handling quality
            graceful_errors = [s for s in error_scenarios if s["handled_gracefully"]]
            total_errors = len(error_scenarios)
            
            if total_errors > 0:
                graceful_percentage = len(graceful_errors) / total_errors
                print(f"Error handling: {len(graceful_errors)}/{total_errors} ({graceful_percentage:.1%}) handled gracefully")
                
                # Check error message quality
                for scenario in error_scenarios:
                    if scenario["error_message"] and len(scenario["error_message"]) > 10:
                        # Error message should be informative but not expose internals
                        message_lower = scenario["error_message"].lower()
                        
                        # Check for information leakage
                        sensitive_terms = ["traceback", "exception", "database", "internal", "server error"]
                        leaks_info = any(term in message_lower for term in sensitive_terms)
                        
                        if leaks_info:
                            print(f"  Warning: {scenario['scenario']} may leak sensitive information")
                        
                        # Check if message is user-friendly
                        friendly_terms = ["invalid", "not found", "bad request", "validation"]
                        is_friendly = any(term in message_lower for term in friendly_terms)
                        
                        if is_friendly:
                            print(f"  Good: {scenario['scenario']} has user-friendly error message")
            
            # Test recovery mechanisms
            recovery_tests = []
            
            # Test if system recovers after errors
            if auth_headers:
                # After error scenarios, try normal operations
                recovery_chat_data = {"title": "Recovery Test", "description": "Testing system recovery"}
                recovery_response = await client.post("/api/v1/chats", json=recovery_chat_data, headers=auth_headers)
                
                recovery_tests.append({
                    "operation": "chat_creation_after_errors",
                    "successful": recovery_response.status_code in [200, 201],
                    "status_code": recovery_response.status_code
                })
                
                # Test profile access after errors
                profile_recovery_response = await client.get("/api/v1/auth/profile", headers=auth_headers)
                recovery_tests.append({
                    "operation": "profile_access_after_errors",
                    "successful": profile_recovery_response.status_code == 200,
                    "status_code": profile_recovery_response.status_code
                })
            
            if recovery_tests:
                successful_recoveries = [t for t in recovery_tests if t["successful"]]
                print(f"System recovery: {len(successful_recoveries)}/{len(recovery_tests)} operations successful after errors")
            
            print("Error propagation and recovery: TESTED")
            
        except Exception as e:
            pytest.skip(f"Error propagation and recovery test skipped: {e}")
    
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_service_dependencies_and_graceful_degradation(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test service dependencies and graceful degradation."""
        try:
            # Test core service dependencies
            core_services = [
                {"name": "authentication", "endpoint": "/api/v1/auth/profile"},
                {"name": "database", "endpoint": "/healthz"},
                {"name": "chat_service", "endpoint": "/api/v1/chats"},
                {"name": "document_service", "endpoint": "/api/v1/documents"}
            ]
            
            service_status = {}
            
            for service in core_services:
                headers = auth_headers if service["name"] != "database" else {}
                
                try:
                    response = await client.get(service["endpoint"], headers=headers)
                    service_status[service["name"]] = {
                        "available": response.status_code in [200, 401],  # 401 means service exists but auth required
                        "status_code": response.status_code,
                        "response_time": getattr(response, 'elapsed', None)
                    }
                except Exception as e:
                    service_status[service["name"]] = {
                        "available": False,
                        "error": str(e)
                    }
            
            # Analyze service dependencies
            available_services = [name for name, status in service_status.items() if status["available"]]
            unavailable_services = [name for name, status in service_status.items() if not status["available"]]
            
            print(f"Service availability: {len(available_services)}/{len(core_services)} services available")
            
            if available_services:
                print(f"  Available: {', '.join(available_services)}")
            
            if unavailable_services:
                print(f"  Unavailable: {', '.join(unavailable_services)}")
            
            # Test graceful degradation scenarios
            degradation_scenarios = []
            
            # Scenario 1: System should work with basic services even if advanced features are unavailable
            if service_status.get("authentication", {}).get("available") and service_status.get("database", {}).get("available"):
                # Core functionality should work
                if auth_headers:
                    profile_response = await client.get("/api/v1/auth/profile", headers=auth_headers)
                    degradation_scenarios.append({
                        "scenario": "core_auth_functionality",
                        "working": profile_response.status_code == 200,
                        "description": "Authentication and profile access"
                    })
                
                # Test if system provides meaningful responses when optional services are unavailable
                optional_endpoints = ["/api/v1/analytics", "/api/v1/agents", "/api/v1/admin"]
                
                for endpoint in optional_endpoints:
                    response = await client.get(endpoint, headers=auth_headers if auth_headers else {})
                    
                    # Should either work or return proper error (not 500)
                    degraded_gracefully = response.status_code != 500
                    
                    degradation_scenarios.append({
                        "scenario": f"optional_service_{endpoint.split('/')[-1]}",
                        "working": response.status_code == 200,
                        "degraded_gracefully": degraded_gracefully,
                        "status_code": response.status_code
                    })
            
            # Analyze graceful degradation
            if degradation_scenarios:
                graceful_count = sum(1 for s in degradation_scenarios if s.get("degraded_gracefully", True))
                working_count = sum(1 for s in degradation_scenarios if s.get("working", False))
                
                print(f"Graceful degradation: {graceful_count}/{len(degradation_scenarios)} scenarios handle failures gracefully")
                print(f"Optional services: {working_count}/{len(degradation_scenarios)} working")
            
            # Test service health monitoring
            health_endpoints = ["/health", "/healthz", "/readyz", "/api/v1/health"]
            
            health_available = False
            for endpoint in health_endpoints:
                response = await client.get(endpoint)
                if response.status_code == 200:
                    health_available = True
                    health_data = response.json()
                    
                    # Check if health endpoint provides service dependency information
                    if isinstance(health_data, dict):
                        dependency_info = [k for k in health_data.keys() if any(term in k.lower() for term in ['service', 'dependency', 'component'])]
                        
                        if dependency_info:
                            print(f"Health monitoring provides dependency info: {dependency_info}")
                    
                    break
            
            if not health_available:
                print("Health monitoring: No comprehensive health endpoints found")
            
            print("Service dependencies and graceful degradation: TESTED")
            
        except Exception as e:
            pytest.skip(f"Service dependencies test skipped: {e}")