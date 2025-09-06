"""Database seeding for workflow templates.

This script demonstrates how to seed the database with built-in workflow templates
if needed for consistency or to provide default templates for all users.
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from chatter.models.workflow import (
    WorkflowTemplate as DBWorkflowTemplate,
    TemplateCategory,
    WorkflowType,
)
from chatter.models.user import User


class WorkflowTemplateSeeder:
    """Seeder for workflow templates."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def seed_builtin_templates(self, admin_user_id: str) -> int:
        """Seed built-in workflow templates into the database.
        
        Args:
            admin_user_id: ID of the admin user to own the built-in templates
            
        Returns:
            Number of templates created
        """
        builtin_templates = [
            {
                "name": "customer_support",
                "workflow_type": WorkflowType.FULL,
                "category": TemplateCategory.CUSTOMER_SUPPORT,
                "description": "Customer support with knowledge base and tools",
                "default_params": {
                    "enable_memory": True,
                    "memory_window": 50,
                    "max_tool_calls": 5,
                    "system_message": "You are a helpful customer support assistant. Use the knowledge base to find relevant information and available tools to help resolve customer issues. Always be polite, professional, and thorough in your responses.",
                },
                "required_tools": ["search_kb", "create_ticket", "escalate"],
                "required_retrievers": ["support_docs"],
            },
            {
                "name": "code_assistant",
                "workflow_type": WorkflowType.TOOLS,
                "category": TemplateCategory.PROGRAMMING,
                "description": "Programming assistant with code tools",
                "default_params": {
                    "enable_memory": True,
                    "memory_window": 100,
                    "max_tool_calls": 10,
                    "system_message": "You are an expert programming assistant. Help users with coding tasks, debugging, code review, and software development best practices. Use available tools to execute code, run tests, and access documentation when needed.",
                },
                "required_tools": ["execute_code", "search_docs", "generate_tests"],
            },
            {
                "name": "research_assistant",
                "workflow_type": WorkflowType.RAG,
                "category": TemplateCategory.RESEARCH,
                "description": "Research assistant with document retrieval",
                "default_params": {
                    "enable_memory": True,
                    "memory_window": 30,
                    "max_documents": 10,
                    "system_message": "You are a research assistant. Use the provided documents to answer questions accurately and thoroughly. Always cite your sources and explain your reasoning. If information is not available in the documents, clearly state this limitation.",
                },
                "required_retrievers": ["research_docs"],
            },
            {
                "name": "general_chat",
                "workflow_type": WorkflowType.PLAIN,
                "category": TemplateCategory.GENERAL,
                "description": "General conversation assistant",
                "default_params": {
                    "enable_memory": True,
                    "memory_window": 20,
                    "system_message": "You are a helpful, harmless, and honest AI assistant. Engage in natural conversation while being informative and supportive.",
                },
            },
            {
                "name": "document_qa",
                "workflow_type": WorkflowType.RAG,
                "category": TemplateCategory.RESEARCH,
                "description": "Document question answering with retrieval",
                "default_params": {
                    "enable_memory": False,  # Each question should be independent
                    "max_documents": 15,
                    "similarity_threshold": 0.7,
                    "system_message": "You are a document analysis assistant. Answer questions based solely on the provided documents. Be precise and cite specific sections when possible.",
                },
                "required_retrievers": ["document_store"],
            },
            {
                "name": "data_analyst",
                "workflow_type": WorkflowType.TOOLS,
                "category": TemplateCategory.DATA_ANALYSIS,
                "description": "Data analysis assistant with computation tools",
                "default_params": {
                    "enable_memory": True,
                    "memory_window": 50,
                    "max_tool_calls": 15,
                    "system_message": "You are a data analyst assistant. Help users analyze data, create visualizations, and derive insights. Use computational tools to perform calculations and generate charts.",
                },
                "required_tools": ["execute_python", "create_chart", "analyze_data"],
            },
        ]
        
        created_count = 0
        
        for template_data in builtin_templates:
            # Check if template already exists
            existing_query = select(DBWorkflowTemplate).where(
                DBWorkflowTemplate.name == template_data["name"],
                DBWorkflowTemplate.is_builtin == True
            )
            result = await self.session.execute(existing_query)
            existing = result.scalar_one_or_none()
            
            if existing:
                continue
                
            # Create new built-in template
            db_template = DBWorkflowTemplate(
                owner_id=admin_user_id,
                name=template_data["name"],
                description=template_data["description"],
                workflow_type=template_data["workflow_type"],
                category=template_data["category"],
                default_params=template_data["default_params"],
                required_tools=template_data.get("required_tools"),
                required_retrievers=template_data.get("required_retrievers"),
                is_builtin=True,
                is_public=True,  # Built-in templates are public by default
                version=1,
                is_latest=True,
            )
            
            self.session.add(db_template)
            created_count += 1
        
        await self.session.commit()
        return created_count

    async def create_example_custom_templates(self, user_id: str) -> int:
        """Create example custom templates for a user.
        
        Args:
            user_id: ID of the user to create templates for
            
        Returns:
            Number of templates created
        """
        custom_templates = [
            {
                "name": "blog_writing_assistant",
                "workflow_type": WorkflowType.TOOLS,
                "category": TemplateCategory.CREATIVE,
                "description": "Blog writing assistant with research and editing tools",
                "default_params": {
                    "enable_memory": True,
                    "memory_window": 40,
                    "max_tool_calls": 8,
                    "system_message": "You are a professional blog writing assistant. Help create engaging, well-researched blog posts with proper structure, compelling headlines, and SEO optimization.",
                },
                "required_tools": ["web_search", "grammar_check", "seo_analyzer"],
            },
            {
                "name": "meeting_summarizer",
                "workflow_type": WorkflowType.RAG,
                "category": TemplateCategory.BUSINESS,
                "description": "Meeting transcript summarizer and action item extractor",
                "default_params": {
                    "enable_memory": False,
                    "max_documents": 5,
                    "system_message": "You are a meeting summarizer. Analyze meeting transcripts to create concise summaries, identify key decisions, extract action items, and highlight important discussion points.",
                },
                "required_retrievers": ["meeting_transcripts"],
            },
            {
                "name": "learning_tutor",
                "workflow_type": WorkflowType.FULL,
                "category": TemplateCategory.EDUCATIONAL,
                "description": "Personalized learning tutor with assessment tools",
                "default_params": {
                    "enable_memory": True,
                    "memory_window": 100,
                    "max_tool_calls": 12,
                    "system_message": "You are a personalized learning tutor. Adapt your teaching style to the student's needs, provide clear explanations, create practice problems, and track learning progress.",
                },
                "required_tools": ["create_quiz", "check_answers", "progress_tracker"],
                "required_retrievers": ["learning_materials"],
            },
        ]
        
        created_count = 0
        
        for template_data in custom_templates:
            # Check if template already exists for this user
            existing_query = select(DBWorkflowTemplate).where(
                DBWorkflowTemplate.name == template_data["name"],
                DBWorkflowTemplate.owner_id == user_id
            )
            result = await self.session.execute(existing_query)
            existing = result.scalar_one_or_none()
            
            if existing:
                continue
                
            # Create new custom template
            db_template = DBWorkflowTemplate(
                owner_id=user_id,
                name=template_data["name"],
                description=template_data["description"],
                workflow_type=template_data["workflow_type"],
                category=template_data["category"],
                default_params=template_data["default_params"],
                required_tools=template_data.get("required_tools"),
                required_retrievers=template_data.get("required_retrievers"),
                is_builtin=False,
                is_public=False,  # Custom templates are private by default
                version=1,
                is_latest=True,
            )
            
            self.session.add(db_template)
            created_count += 1
        
        await self.session.commit()
        return created_count


async def seed_workflow_templates(session: AsyncSession, admin_user_id: str = None, example_user_id: str = None):
    """Main function to seed workflow templates.
    
    Args:
        session: Database session
        admin_user_id: Optional admin user ID for built-in templates
        example_user_id: Optional user ID for example custom templates
    """
    seeder = WorkflowTemplateSeeder(session)
    
    # Seed built-in templates if admin user provided
    if admin_user_id:
        try:
            builtin_count = await seeder.seed_builtin_templates(admin_user_id)
            print(f"Created {builtin_count} built-in workflow templates")
        except Exception as e:
            print(f"Error creating built-in templates: {e}")
            await session.rollback()
    
    # Seed example custom templates if user provided
    if example_user_id:
        try:
            custom_count = await seeder.create_example_custom_templates(example_user_id)
            print(f"Created {custom_count} example custom templates for user {example_user_id}")
        except Exception as e:
            print(f"Error creating custom templates: {e}")
            await session.rollback()


if __name__ == "__main__":
    # This would be used in a real seeding script with actual database connection
    print("Workflow template seeder ready. Use seed_workflow_templates() with a database session.")