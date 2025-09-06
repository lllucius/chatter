import os
import asyncio

# Set minimal environment variables for testing
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///test.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"

# Test basic agent functionality without database
async def test_agents():
    try:
        from chatter.core.agents import BaseAgent, ConversationalAgent, AgentProfile, AgentType, AgentStatus
        
        # Create a simple fake chat model
        class FakeChatModel:
            def __init__(self, responses):
                self.responses = responses
                self.call_count = 0
                
            async def ainvoke(self, messages):
                class Response:
                    def __init__(self, content):
                        self.content = content
                        
                response = self.responses[self.call_count % len(self.responses)]
                self.call_count += 1
                return Response(response)
        
        # Create a test agent profile
        profile = AgentProfile(
            name="Test Agent",
            description="A test conversational agent", 
            type=AgentType.CONVERSATIONAL,
            system_message="You are a helpful assistant.",
            status=AgentStatus.ACTIVE
        )
        
        # Create a fake LLM for testing
        fake_llm = FakeChatModel(responses=["Hello! I'm a test response."])
        
        # Create an agent instance
        agent = ConversationalAgent(profile=profile, llm=fake_llm)
        
        print(f"✓ Created agent: {agent.profile.name}")
        print(f"✓ Agent type: {agent.profile.type}")
        print(f"✓ Agent status: {agent.profile.status}")
        
        # Test agent capabilities
        capabilities = await agent.get_capabilities()
        print(f"✓ Agent capabilities: {capabilities}")
        
        # Test message processing
        response = await agent.process_message(
            message="Hello, how are you?",
            conversation_id="test-conversation"
        )
        print(f"✓ Agent response: {response}")
        
        # Test agent manager
        from chatter.core.agents import AgentManager
        manager = AgentManager()
        
        print(f"✓ Created agent manager with {len(manager.agent_classes)} agent types")
        
        print("\n🎉 Basic agent functionality works!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing agents: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_agents())
    exit(0 if result else 1)
