"""Comprehensive database seeding system."""

import json
import secrets
import string
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.models.conversation import Conversation, ConversationStatus, Message, MessageRole
from chatter.models.document import Document, DocumentChunk, DocumentStatus, DocumentType
from chatter.models.profile import Profile, ProfileType
from chatter.models.prompt import Prompt, PromptCategory, PromptType
from chatter.models.registry import (
    DistanceMetric,
    EmbeddingSpace,
    ModelDef,
    ModelType,
    Provider,
    ReductionStrategy,
)
from chatter.models.user import User
from chatter.utils.database import DatabaseManager
from chatter.utils.logging import get_logger
from chatter.utils.security_enhanced import hash_password

logger = get_logger(__name__)


class SeedingMode(str, Enum):
    """Seeding modes for different use cases."""
    
    MINIMAL = "minimal"      # Only essential data (admin user, basic defaults)
    DEVELOPMENT = "development"  # Development-friendly data set
    DEMO = "demo"           # Full demo data with sample content
    TESTING = "testing"     # Data for automated testing
    PRODUCTION = "production"  # Production-ready minimal set


class DatabaseSeeder:
    """Comprehensive database seeding system."""
    
    def __init__(self, session: Optional[AsyncSession] = None):
        """Initialize the database seeder.
        
        Args:
            session: Optional database session to use
        """
        self.session = session
        self._should_close_session = session is None

    async def __aenter__(self):
        """Async context manager entry."""
        if self.session is None:
            self.db_manager = DatabaseManager()
            self.session = await self.db_manager.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._should_close_session and hasattr(self, 'db_manager'):
            await self.db_manager.__aexit__(exc_type, exc_val, exc_tb)

    async def seed_database(
        self,
        mode: SeedingMode = SeedingMode.DEVELOPMENT,
        force: bool = False,
        skip_existing: bool = True
    ) -> Dict[str, Any]:
        """Seed the database with comprehensive data.
        
        Args:
            mode: Seeding mode to determine what data to create
            force: Whether to create data even if database has existing users
            skip_existing: Skip creating data if it already exists
            
        Returns:
            Dictionary with seeding results and created entity counts
        """
        logger.info(f"Starting database seeding in {mode} mode", 
                   force=force, skip_existing=skip_existing)
        
        results = {
            "mode": mode,
            "created": {},
            "skipped": {},
            "errors": []
        }
        
        try:
            # Check if database is virgin (for non-force mode)
            if not force:
                existing_users = await self._count_users()
                if existing_users > 0 and mode != SeedingMode.TESTING:
                    logger.info(f"Database has {existing_users} users, skipping seeding")
                    results["skipped"]["reason"] = "Database not empty"
                    return results
            
            # Seed based on mode
            if mode == SeedingMode.MINIMAL:
                await self._seed_minimal_data(results, skip_existing)
            elif mode == SeedingMode.DEVELOPMENT:
                await self._seed_development_data(results, skip_existing)
            elif mode == SeedingMode.DEMO:
                await self._seed_demo_data(results, skip_existing)
            elif mode == SeedingMode.TESTING:
                await self._seed_testing_data(results, skip_existing)
            elif mode == SeedingMode.PRODUCTION:
                await self._seed_production_data(results, skip_existing)
            
            logger.info("Database seeding completed successfully", results=results)
            return results
            
        except Exception as e:
            logger.error("Database seeding failed", error=str(e))
            results["errors"].append(str(e))
            raise

    async def _count_users(self) -> int:
        """Count existing users in database."""
        result = await self.session.execute(
            select(User).limit(1)
        )
        return 1 if result.scalar_one_or_none() is not None else 0

    async def _seed_minimal_data(self, results: Dict[str, Any], skip_existing: bool):
        """Seed minimal essential data."""
        logger.info("Seeding minimal data")
        
        # Create admin user
        admin_user = await self._create_admin_user(skip_existing)
        results["created"]["users"] = 1 if admin_user else 0
        
        # Create basic provider and models
        provider_count, model_count = await self._create_basic_registry(skip_existing)
        results["created"]["providers"] = provider_count
        results["created"]["models"] = model_count
        
        # Create basic profiles
        profile_count = await self._create_basic_profiles(admin_user, skip_existing)
        results["created"]["profiles"] = profile_count
        
        # Create basic prompts
        prompt_count = await self._create_basic_prompts(admin_user, skip_existing)
        results["created"]["prompts"] = prompt_count

    async def _seed_development_data(self, results: Dict[str, Any], skip_existing: bool):
        """Seed development-friendly data set."""
        logger.info("Seeding development data")
        
        # First seed minimal data
        await self._seed_minimal_data(results, skip_existing)
        
        # Add development users
        dev_users = await self._create_development_users(skip_existing)
        results["created"]["users"] = results["created"].get("users", 0) + len(dev_users)
        
        # Add sample conversations
        conversation_count = await self._create_sample_conversations(dev_users, skip_existing)
        results["created"]["conversations"] = conversation_count
        
        # Add sample documents
        document_count = await self._create_sample_documents(dev_users, skip_existing)
        results["created"]["documents"] = document_count

    async def _seed_demo_data(self, results: Dict[str, Any], skip_existing: bool):
        """Seed full demo data with comprehensive content."""
        logger.info("Seeding demo data")
        
        # First seed development data
        await self._seed_development_data(results, skip_existing)
        
        # Add more comprehensive data for demos
        # Additional profiles
        extra_profiles = await self._create_demo_profiles(skip_existing)
        results["created"]["profiles"] += len(extra_profiles)
        
        # Additional prompts
        extra_prompts = await self._create_demo_prompts(skip_existing)
        results["created"]["prompts"] += len(extra_prompts)
        
        # Sample embedding spaces
        embedding_spaces = await self._create_demo_embedding_spaces(skip_existing)
        results["created"]["embedding_spaces"] = len(embedding_spaces)

    async def _seed_testing_data(self, results: Dict[str, Any], skip_existing: bool):
        """Seed data specifically for automated testing."""
        logger.info("Seeding testing data")
        
        # Create test users with predictable credentials
        test_users = await self._create_test_users(skip_existing)
        results["created"]["users"] = len(test_users)
        
        # Create test data for each model type
        await self._create_test_registry_data(skip_existing)
        await self._create_test_conversations(test_users, skip_existing)
        await self._create_test_documents(test_users, skip_existing)
        
        results["created"]["test_entities"] = "all_models"

    async def _seed_production_data(self, results: Dict[str, Any], skip_existing: bool):
        """Seed production-ready minimal data."""
        logger.info("Seeding production data")
        
        # Only essential data for production
        await self._seed_minimal_data(results, skip_existing)

    async def _create_admin_user(self, skip_existing: bool = True) -> Optional[User]:
        """Create admin user."""
        if skip_existing:
            existing = await self.session.execute(
                select(User).where(User.username == "admin")
            )
            if existing.scalar_one_or_none():
                logger.info("Admin user already exists, skipping")
                return None
        
        # Generate secure random password
        admin_password = ''.join(
            secrets.choice(string.ascii_letters + string.digits + "!@#$%^&*")
            for _ in range(16)
        )
        
        admin_user = User(
            email="admin@admin.net",
            username="admin",
            hashed_password=hash_password(admin_password),
            full_name="System Administrator",
            is_active=True,
            is_verified=True,
            is_superuser=True,
            bio="Default system administrator account",
        )
        
        self.session.add(admin_user)
        await self.session.commit()
        await self.session.refresh(admin_user)
        
        logger.warning(
            f"Admin user created - Email: admin@admin.net, Password: {admin_password}. "
            "Please change this password immediately!"
        )
        
        return admin_user

    async def _create_development_users(self, skip_existing: bool = True) -> List[User]:
        """Create development users with known credentials."""
        users_data = [
            {
                "username": "developer",
                "email": "dev@example.com",
                "full_name": "Development User",
                "password": "dev123!",
                "is_superuser": False,
            },
            {
                "username": "tester",
                "email": "test@example.com", 
                "full_name": "Test User",
                "password": "test123!",
                "is_superuser": False,
            },
            {
                "username": "demo",
                "email": "demo@example.com",
                "full_name": "Demo User", 
                "password": "demo123!",
                "is_superuser": False,
            }
        ]
        
        created_users = []
        for user_data in users_data:
            if skip_existing:
                existing = await self.session.execute(
                    select(User).where(User.username == user_data["username"])
                )
                if existing.scalar_one_or_none():
                    continue
            
            user = User(
                email=user_data["email"],
                username=user_data["username"],
                hashed_password=hash_password(user_data["password"]),
                full_name=user_data["full_name"],
                is_active=True,
                is_verified=True,
                is_superuser=user_data["is_superuser"],
                bio=f"Development user: {user_data['full_name']}",
            )
            
            self.session.add(user)
            created_users.append(user)
        
        if created_users:
            await self.session.commit()
            for user in created_users:
                await self.session.refresh(user)
        
        logger.info(f"Created {len(created_users)} development users")
        return created_users

    async def _create_test_users(self, skip_existing: bool = True) -> List[User]:
        """Create predictable test users."""
        test_users_data = [
            {
                "username": "testuser1",
                "email": "testuser1@test.com",
                "full_name": "Test User One",
                "password": "testpass1",
            },
            {
                "username": "testuser2", 
                "email": "testuser2@test.com",
                "full_name": "Test User Two",
                "password": "testpass2",
            },
        ]
        
        created_users = []
        for user_data in test_users_data:
            if skip_existing:
                existing = await self.session.execute(
                    select(User).where(User.username == user_data["username"])
                )
                if existing.scalar_one_or_none():
                    continue
                    
            user = User(
                email=user_data["email"],
                username=user_data["username"],
                hashed_password=hash_password(user_data["password"]),
                full_name=user_data["full_name"],
                is_active=True,
                is_verified=True,
                is_superuser=False,
                bio="Test user for automated testing",
            )
            
            self.session.add(user)
            created_users.append(user)
        
        if created_users:
            await self.session.commit()
            for user in created_users:
                await self.session.refresh(user)
                
        return created_users

    async def _create_basic_registry(self, skip_existing: bool = True) -> tuple[int, int]:
        """Create basic provider and model registry data."""
        # Import here to avoid circular imports
        from chatter.utils.database import _create_default_registry_data
        
        if skip_existing:
            existing_provider = await self.session.execute(
                select(Provider).where(Provider.name == "openai")
            )
            if existing_provider.scalar_one_or_none():
                logger.info("Default registry data already exists, skipping")
                return 0, 0
        
        await _create_default_registry_data(self.session)
        return 1, 2  # 1 provider, 2 models

    async def _create_basic_profiles(self, admin_user: Optional[User], skip_existing: bool = True) -> int:
        """Create basic chat profiles."""
        if not admin_user:
            # Get admin user if not provided
            result = await self.session.execute(
                select(User).where(User.username == "admin")
            )
            admin_user = result.scalar_one_or_none()
            if not admin_user:
                logger.warning("No admin user found, skipping profile creation")
                return 0
        
        profiles_data = [
            {
                "name": "Deterministic/Factual Mode",
                "description": "Low temperature profile for factual, consistent responses",
                "profile_type": ProfileType.ANALYTICAL,
                "llm_provider": "openai",
                "llm_model": "gpt-4",
                "temperature": 0.1,
                "max_tokens": 2048,
            },
            {
                "name": "Creative Writing Mode", 
                "description": "High temperature profile for creative and diverse responses",
                "profile_type": ProfileType.CREATIVE,
                "llm_provider": "openai",
                "llm_model": "gpt-4",
                "temperature": 0.9,
                "max_tokens": 4096,
            },
            {
                "name": "Balanced Mode",
                "description": "Balanced temperature for general-purpose conversations",
                "profile_type": ProfileType.CONVERSATIONAL,
                "llm_provider": "openai", 
                "llm_model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 2048,
            }
        ]
        
        created_count = 0
        for profile_data in profiles_data:
            if skip_existing:
                existing = await self.session.execute(
                    select(Profile).where(Profile.name == profile_data["name"])
                )
                if existing.scalar_one_or_none():
                    continue
            
            profile = Profile(
                owner_id=admin_user.id,
                name=profile_data["name"],
                description=profile_data["description"],
                profile_type=profile_data["profile_type"],
                llm_provider=profile_data["llm_provider"],
                llm_model=profile_data["llm_model"],
                temperature=profile_data["temperature"],
                max_tokens=profile_data["max_tokens"],
                is_public=True,
            )
            
            self.session.add(profile)
            created_count += 1
        
        if created_count > 0:
            await self.session.commit()
        
        logger.info(f"Created {created_count} basic profiles")
        return created_count

    async def _create_basic_prompts(self, admin_user: Optional[User], skip_existing: bool = True) -> int:
        """Create basic prompt templates."""
        if not admin_user:
            result = await self.session.execute(
                select(User).where(User.username == "admin")
            )
            admin_user = result.scalar_one_or_none()
            if not admin_user:
                logger.warning("No admin user found, skipping prompt creation")
                return 0
        
        prompts_data = [
            {
                "name": "Instruction Task Template",
                "description": "Template for giving clear instructions to AI",
                "category": PromptCategory.GENERAL,
                "content": """Please complete the following task with precision and clarity:

Task: {task}

Requirements:
- {requirements}

Context: {context}

Please provide a detailed response that addresses all aspects of the task.""",
                "variables": ["task", "requirements", "context"],
            },
            {
                "name": "Code Review Template",
                "description": "Template for code review and analysis",
                "category": PromptCategory.DEVELOPMENT,
                "content": """Please review the following code:

Language: {language}
Code:
```{language}
{code}
```

Please analyze:
1. Code quality and readability
2. Potential bugs or issues
3. Performance considerations
4. Best practices and improvements
5. Security considerations

Provide specific, actionable feedback.""",
                "variables": ["language", "code"],
            },
            {
                "name": "Document Summary Template",
                "description": "Template for summarizing documents",
                "category": PromptCategory.ANALYSIS,
                "content": """Please summarize the following document:

Document Title: {title}
Document Type: {type}
Target Audience: {audience}

Content:
{content}

Please provide:
1. Executive summary (2-3 sentences)
2. Key points (3-5 bullet points)
3. Main conclusions or recommendations
4. Action items (if applicable)

Keep the summary {length} and focused on {focus_area}.""",
                "variables": ["title", "type", "audience", "content", "length", "focus_area"],
            }
        ]
        
        created_count = 0
        for prompt_data in prompts_data:
            if skip_existing:
                existing = await self.session.execute(
                    select(Prompt).where(Prompt.name == prompt_data["name"])
                )
                if existing.scalar_one_or_none():
                    continue
            
            prompt = Prompt(
                owner_id=admin_user.id,
                name=prompt_data["name"],
                description=prompt_data["description"],
                prompt_type=PromptType.TEMPLATE,
                category=prompt_data["category"],
                content=prompt_data["content"],
                variables=prompt_data["variables"],
                is_public=True,
            )
            
            self.session.add(prompt)
            created_count += 1
        
        if created_count > 0:
            await self.session.commit()
        
        logger.info(f"Created {created_count} basic prompts")
        return created_count

    async def _create_sample_conversations(self, users: List[User], skip_existing: bool = True) -> int:
        """Create sample conversations."""
        if not users:
            return 0
        
        conversations_data = [
            {
                "title": "Welcome Conversation",
                "description": "Initial welcome chat",
                "messages": [
                    {"role": MessageRole.USER, "content": "Hello! Can you help me understand what this platform does?"},
                    {"role": MessageRole.ASSISTANT, "content": "Welcome to Chatter! I'm an AI assistant built on an advanced platform that supports multiple AI models, document analysis, and intelligent conversations. I can help you with various tasks like answering questions, analyzing documents, creative writing, and more. What would you like to explore?"},
                    {"role": MessageRole.USER, "content": "That sounds great! How do I get started?"},
                    {"role": MessageRole.ASSISTANT, "content": "Getting started is easy! You can:\n\n1. **Start a conversation** - Just ask me anything\n2. **Upload documents** - I can analyze and answer questions about your files\n3. **Use templates** - Try our pre-built prompt templates for specific tasks\n4. **Customize profiles** - Adjust my behavior for different use cases\n\nWhat interests you most?"}
                ]
            }
        ]
        
        created_count = 0
        for conv_data in conversations_data:
            if skip_existing:
                existing = await self.session.execute(
                    select(Conversation).where(Conversation.title == conv_data["title"])
                )
                if existing.scalar_one_or_none():
                    continue
            
            # Use first user for sample conversations
            user = users[0]
            
            conversation = Conversation(
                user_id=user.id,
                title=conv_data["title"],
                description=conv_data["description"],
                status=ConversationStatus.ACTIVE,
            )
            
            self.session.add(conversation)
            await self.session.commit()
            await self.session.refresh(conversation)
            
            # Add messages
            for idx, msg_data in enumerate(conv_data["messages"]):
                message = Message(
                    conversation_id=conversation.id,
                    role=msg_data["role"],
                    content=msg_data["content"],
                    sequence_number=idx,
                )
                self.session.add(message)
            
            await self.session.commit()
            created_count += 1
        
        logger.info(f"Created {created_count} sample conversations")
        return created_count

    async def _create_sample_documents(self, users: List[User], skip_existing: bool = True) -> int:
        """Create sample documents."""
        if not users:
            return 0
        
        documents_data = [
            {
                "filename": "welcome_guide.md",
                "title": "Platform Welcome Guide", 
                "content": """# Welcome to Chatter Platform

## Overview
Chatter is an advanced AI chatbot platform that provides intelligent conversations, document analysis, and customizable AI interactions.

## Key Features
- **Multi-Model Support**: Work with various AI providers (OpenAI, Anthropic, etc.)
- **Document Intelligence**: Upload and chat with your documents
- **Custom Profiles**: Create specialized AI assistants for different tasks
- **Prompt Templates**: Use pre-built templates for common scenarios
- **Vector Search**: Advanced semantic search across your knowledge base

## Getting Started
1. Create an account or log in
2. Start a conversation with the AI
3. Upload documents to your knowledge base
4. Explore different chat profiles
5. Try prompt templates for specific tasks

## Support
Need help? Check our documentation or contact support.
""",
                "doc_type": DocumentType.MARKDOWN,
            },
            {
                "filename": "api_documentation.md",
                "title": "API Documentation Overview",
                "content": """# API Documentation

## Authentication
All API requests require authentication using JWT tokens.

### Endpoints
- `POST /auth/login` - Authenticate user
- `GET /conversations` - List conversations
- `POST /conversations` - Create new conversation
- `POST /documents` - Upload document
- `GET /profiles` - List chat profiles

## Rate Limits
- 100 requests per minute for authenticated users
- 10 requests per minute for unauthenticated users

## Error Codes
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 429: Rate Limited
- 500: Internal Server Error
""",
                "doc_type": DocumentType.MARKDOWN,
            }
        ]
        
        created_count = 0
        for doc_data in documents_data:
            if skip_existing:
                existing = await self.session.execute(
                    select(Document).where(Document.filename == doc_data["filename"])
                )
                if existing.scalar_one_or_none():
                    continue
            
            user = users[0]
            
            document = Document(
                user_id=user.id,
                filename=doc_data["filename"],
                title=doc_data["title"],
                content=doc_data["content"],
                document_type=doc_data["doc_type"],
                file_size=len(doc_data["content"]),
                status=DocumentStatus.PROCESSED,
                chunk_count=1,
            )
            
            self.session.add(document)
            await self.session.commit()
            await self.session.refresh(document)
            
            # Create a document chunk
            chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=0,
                content=doc_data["content"],
                token_count=len(doc_data["content"].split()),
                metadata={"title": doc_data["title"]},
            )
            
            self.session.add(chunk)
            created_count += 1
        
        if created_count > 0:
            await self.session.commit()
        
        logger.info(f"Created {created_count} sample documents")
        return created_count

    # Additional methods for demo and test data would go here...
    async def _create_demo_profiles(self, skip_existing: bool = True) -> List[Profile]:
        """Create additional profiles for demo purposes."""
        # Implementation would create more specialized profiles
        return []

    async def _create_demo_prompts(self, skip_existing: bool = True) -> List[Prompt]:
        """Create additional prompts for demo purposes."""
        # Implementation would create more specialized prompts
        return []

    async def _create_demo_embedding_spaces(self, skip_existing: bool = True) -> List[EmbeddingSpace]:
        """Create demo embedding spaces."""
        # Implementation would create additional embedding spaces
        return []

    async def _create_test_registry_data(self, skip_existing: bool = True):
        """Create test registry data."""
        # Implementation would create test-specific registry data
        pass

    async def _create_test_conversations(self, users: List[User], skip_existing: bool = True):
        """Create test conversations."""
        # Implementation would create test-specific conversations
        pass

    async def _create_test_documents(self, users: List[User], skip_existing: bool = True):
        """Create test documents."""
        # Implementation would create test-specific documents
        pass


# Convenience functions for direct usage
async def seed_database(
    mode: SeedingMode = SeedingMode.DEVELOPMENT,
    force: bool = False,
    skip_existing: bool = True
) -> Dict[str, Any]:
    """Convenience function to seed database."""
    async with DatabaseSeeder() as seeder:
        return await seeder.seed_database(mode, force, skip_existing)


async def clear_all_data(confirm: bool = False) -> bool:
    """Clear all data from database (DANGEROUS).
    
    Args:
        confirm: Must be True to actually clear data
        
    Returns:
        True if data was cleared, False otherwise
    """
    if not confirm:
        logger.warning("clear_all_data called without confirmation")
        return False
    
    logger.warning("CLEARING ALL DATABASE DATA")
    
    async with DatabaseManager() as session:
        # Delete in reverse dependency order to avoid foreign key issues
        await session.execute(text("DELETE FROM messages"))
        await session.execute(text("DELETE FROM conversations"))
        await session.execute(text("DELETE FROM document_chunks")) 
        await session.execute(text("DELETE FROM documents"))
        await session.execute(text("DELETE FROM prompts"))
        await session.execute(text("DELETE FROM profiles"))
        await session.execute(text("DELETE FROM embedding_spaces"))
        await session.execute(text("DELETE FROM model_defs"))
        await session.execute(text("DELETE FROM providers"))
        await session.execute(text("DELETE FROM users"))
        await session.commit()
    
    logger.warning("All database data cleared")
    return True
