import os
import asyncio

# Set minimal environment variables for testing  
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///test.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"

async def test_improved_agents():
    try:
        from chatter.core.agents import AgentManager, AgentType
        
        print("🧪 Testing improved agent functionality...")
        
        # Create agent manager
        manager = AgentManager()
        
        # Test agent templates
        templates = await manager.get_agent_templates()
        print(f"✓ Retrieved {len(templates)} agent templates")
        for template in templates:
            print(f"  - {template['name']}: {template['description']}")
        
        # Create a simple fake LLM for testing
        class FakeChatModel:
            def __init__(self):
                pass
                
            async def ainvoke(self, messages):
                class Response:
                    def __init__(self, content):
                        self.content = content
                return Response("I'm a fake response from the agent!")
        
        # Test creating agent from template with fake LLM
        template = templates[0]  # Use first template
        fake_llm = FakeChatModel()
        
        agent_id = await manager.create_agent(
            name="Test Agent from Template",
            agent_type=template['agent_type'],
            description=template['description'],
            system_message=template['system_message'],
            llm=fake_llm,  # Provide fake LLM to avoid API key issues
            personality_traits=template['personality_traits'],
            response_style=template['response_style'],
            temperature=template['temperature'],
            max_tokens=template['max_tokens'],
            created_by="test-user"
        )
        print(f"✓ Created agent from template: {agent_id}")
        
        # Test retrieving the agent
        agent = await manager.get_agent(agent_id)
        if agent:
            print(f"✓ Retrieved agent: {agent.profile.name}")
            
            # Test agent interaction
            response = await agent.process_message(
                "Hello!", 
                "test-conversation",
                {"user_id": "test-user"}
            )
            print(f"✓ Agent response: {response}")
        else:
            print("❌ Failed to retrieve created agent")
            return False
        
        # Test listing agents 
        agents, total = await manager.list_agents()
        print(f"✓ Listed {len(agents)} agents (total: {total})")
        
        # Test filtering agents by user
        user_agents, user_total = await manager.list_agents(user_id="test-user")
        print(f"✓ Listed {len(user_agents)} agents for test-user (total: {user_total})")
        
        print("\n🎉 Improved agent functionality works!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing improved agents: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_improved_agents())
    exit(0 if result else 1)
