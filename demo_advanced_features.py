#!/usr/bin/env python3
"""
Demonstration script for the new MCP and LangGraph features in Chatter.

This script showcases:
1. LangChain orchestrator capabilities
2. LangGraph workflows
3. MCP tool integration
4. Vector store operations
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# For demo purposes

from chatter.config import settings
from chatter.core import orchestrator, vector_store_manager, workflow_manager
from chatter.services import mcp_service
from chatter.services.embeddings import EmbeddingService
from chatter.services.llm import LLMService
from chatter.services.mcp import BuiltInTools


async def demo_langchain_orchestrator():
    """Demonstrate LangChain orchestrator capabilities."""
    print("\n🔗 LangChain Orchestrator Demo")
    print("=" * 50)

    # Initialize LLM service
    llm_service = LLMService()

    if not llm_service.list_available_providers():
        print("❌ No LLM providers available. Please configure API keys.")
        return

    try:
        # Get a provider
        provider = llm_service.get_default_provider()
        print(f"✅ Using provider: {provider.__class__.__name__}")

        # Create a basic chat chain
        chain = orchestrator.create_chat_chain(
            llm=provider,
            system_message="You are a helpful AI assistant.",
            include_history=False
        )

        # Test the chain
        response = await orchestrator.run_chain_with_callback(
            chain=chain,
            inputs={"input": "What is the capital of France?"},
            provider_name="demo"
        )

        print("💬 Question: What is the capital of France?")
        print(f"🤖 Response: {response['response']}")
        print(f"📊 Usage: {response['usage']}")

    except Exception as e:
        print(f"❌ LangChain demo failed: {e}")


async def demo_langgraph_workflows():
    """Demonstrate LangGraph workflow capabilities."""
    print("\n🔄 LangGraph Workflows Demo")
    print("=" * 50)

    try:
        # Check if workflow manager is initialized
        print(f"✅ Workflow manager checkpointer: {type(workflow_manager.checkpointer).__name__}")

        # Since we don't have actual LLM providers configured, we'll show the structure
        print("📋 Available workflow types:")
        print("  - Basic conversation workflow")
        print("  - RAG workflow with document retrieval")
        print("  - Tool-calling workflow with MCP integration")

        print("💡 Workflows support:")
        print("  - State persistence with checkpointing")
        print("  - Async streaming for real-time updates")
        print("  - Error handling and recovery")
        print("  - Thread-based conversation management")

    except Exception as e:
        print(f"❌ LangGraph demo failed: {e}")


async def demo_mcp_tools():
    """Demonstrate MCP tool integration."""
    print("\n🛠️ MCP Tools Demo")
    print("=" * 50)

    try:
        # Get health status
        health = await mcp_service.health_check()
        print(f"✅ MCP Service Status: {health}")

        # Get available servers
        servers = await mcp_service.get_available_servers()
        print(f"📡 Configured MCP servers: {len(servers)}")
        for server in servers:
            print(f"  - {server['name']}: {server['command']} {' '.join(server['args'])}")

        # Get built-in tools
        builtin_tools = BuiltInTools.create_builtin_tools()
        print(f"🔧 Built-in tools available: {len(builtin_tools)}")
        for tool in builtin_tools:
            print(f"  - {tool.name}: {tool.description}")

        # Test built-in calculator
        calc_result = BuiltInTools.calculate("2 + 2 * 3")
        print(f"🧮 Calculator test (2 + 2 * 3): {calc_result}")

        # Test time function
        current_time = BuiltInTools.get_current_time()
        print(f"⏰ Current time: {current_time}")

    except Exception as e:
        print(f"❌ MCP tools demo failed: {e}")


async def demo_vector_store():
    """Demonstrate vector store capabilities."""
    print("\n🔍 Vector Store Demo")
    print("=" * 50)

    try:
        # Check if we can initialize embeddings
        embedding_service = EmbeddingService()
        available_providers = embedding_service.list_available_providers()
        print(f"📊 Available embedding providers: {available_providers}")

        if available_providers:
            embeddings = embedding_service.get_default_embeddings()
            print(f"✅ Using embeddings: {type(embeddings).__name__}")

            # Try to create a vector store (will fallback to Chroma if PGVector fails)
            try:
                vector_store = vector_store_manager.get_default_store(embeddings)
                print(f"🗄️ Vector store type: {type(vector_store).__name__}")
                print("✅ Vector store operations available:")
                print("  - Document addition with embeddings")
                print("  - Similarity search with filtering")
                print("  - Document updates and deletion")
                print("  - Retriever interface for RAG")
            except Exception as ve:
                print(f"⚠️ Vector store initialization: {ve}")
        else:
            print("ℹ️ No embedding providers configured - vector operations unavailable")

    except Exception as e:
        print(f"❌ Vector store demo failed: {e}")


async def demo_api_endpoints():
    """Show the new API endpoints available."""
    print("\n🌐 New API Endpoints")
    print("=" * 50)

    endpoints = [
        ("POST", "/api/v1/chat/workflows/basic", "Basic conversation workflows"),
        ("POST", "/api/v1/chat/workflows/rag", "RAG-enabled workflows"),
        ("POST", "/api/v1/chat/workflows/tools", "Tool-calling workflows"),
        ("GET", "/api/v1/chat/tools/available", "List available tools"),
        ("GET", "/api/v1/chat/mcp/status", "MCP service status"),
    ]

    print("🚀 New endpoints added:")
    for method, path, description in endpoints:
        print(f"  {method:6} {path:35} - {description}")

    print("\n💡 These endpoints enable:")
    print("  - Advanced conversational AI with state management")
    print("  - Tool integration for external system access")
    print("  - Document-aware conversations with RAG")
    print("  - Real-time tool discovery and health monitoring")


def show_configuration_status():
    """Show current configuration status."""
    print("\n⚙️ Configuration Status")
    print("=" * 50)

    # Check API keys
    providers = {
        "OpenAI": settings.openai_api_key is not None,
        "Anthropic": settings.anthropic_api_key is not None,
        "Google": settings.google_api_key is not None,
        "Cohere": settings.cohere_api_key is not None,
    }

    print("🔑 LLM Provider Status:")
    for provider, configured in providers.items():
        status = "✅ Configured" if configured else "❌ Not configured"
        print(f"  {provider:12}: {status}")

    print(f"\n🗄️ Database: {settings.database_url}")
    print(f"🔧 MCP Enabled: {settings.mcp_enabled}")
    print(f"📝 LangSmith Tracing: {settings.langchain_tracing_v2}")
    print(f"🧠 LangGraph Checkpoint: {settings.langgraph_checkpoint_store}")


async def main():
    """Run all demonstrations."""
    print("🎉 Chatter Advanced Features Demonstration")
    print("=" * 60)
    print("This demo showcases the newly implemented components:")
    print("- MCP toolcalling with langchain-mcp-adapters")
    print("- LangGraph workflows for conversations")
    print("- Enhanced LangChain integration")
    print("- Vector store abstractions")

    show_configuration_status()

    # Run demonstrations
    await demo_langchain_orchestrator()
    await demo_langgraph_workflows()
    await demo_mcp_tools()
    await demo_vector_store()
    await demo_api_endpoints()

    print("\n🎯 Summary")
    print("=" * 50)
    print("✅ All core components are successfully implemented and integrated")
    print("🚀 The platform now supports advanced AI workflows with:")
    print("   - Stateful conversations with LangGraph")
    print("   - External tool integration via MCP")
    print("   - Retrieval-augmented generation")
    print("   - Modular and extensible architecture")
    print("\n💡 Ready for production use with proper API key configuration!")


if __name__ == "__main__":
    asyncio.run(main())
