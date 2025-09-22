"""Comprehensive database seeding system."""

import secrets
import string
from enum import Enum
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.models.conversation import (
    Conversation,
    ConversationStatus,
    Message,
    MessageRole,
)
from chatter.models.document import (
    Document,
    DocumentChunk,
    DocumentStatus,
    DocumentType,
)
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
from chatter.models.workflow import TemplateCategory, WorkflowTemplate
from chatter.utils.database import DatabaseManager
from chatter.utils.logging import get_logger
from chatter.utils.security_enhanced import hash_password

logger = get_logger(__name__)


async def _create_default_registry_data(session: AsyncSession) -> None:
    """Create default provider, models, and embedding spaces for the registry."""
    from sqlalchemy import select

    from chatter.models.registry import (
        EmbeddingSpace,
        ModelDef,
        Provider,
        ProviderType,
    )

    # Check if any providers already exist
    result = await session.execute(select(Provider).limit(1))
    existing_provider = result.scalar_one_or_none()

    if existing_provider is not None:
        logger.info(
            "Registry data already exists, skipping default registry initialization"
        )
        return

    logger.info(
        "Creating default registry data (providers, models, embedding spaces)"
    )

    # Create default OpenAI provider
    openai_provider = Provider(
        name="openai",
        provider_type=ProviderType.OPENAI,
        display_name="OpenAI",
        description="OpenAI language models including GPT-4 and embedding models",
        api_key_required=True,
        base_url="https://api.openai.com/v1",
        default_config={
            "max_retries": 3,
            "timeout": 60,
        },
        is_active=True,
        is_default=True,
    )
    session.add(openai_provider)
    await session.commit()
    await session.refresh(openai_provider)

    logger.info(
        "Created default OpenAI provider",
        provider_id=openai_provider.id,
    )

    # Create default LLM model (GPT-4)
    gpt4_model = ModelDef(
        provider_id=openai_provider.id,
        name="gpt-4",
        model_type=ModelType.LLM,
        display_name="GPT-4",
        description="OpenAI's most capable LLM model with excellent reasoning and broad knowledge",
        model_name="gpt-4",
        max_tokens=4096,
        context_length=8192,
        supports_batch=False,
        default_config={
            "temperature": 0.7,
            "top_p": 1.0,
            "presence_penalty": 0.0,
            "frequency_penalty": 0.0,
        },
        is_active=True,
        is_default=True,
    )
    session.add(gpt4_model)

    # Create default embedding model (text-embedding-3-large)
    embedding_model = ModelDef(
        provider_id=openai_provider.id,
        name="text-embedding-3-large",
        model_type=ModelType.EMBEDDING,
        display_name="OpenAI Text Embedding 3 Large",
        description="OpenAI's large embedding model with 3072 dimensions",
        model_name="text-embedding-3-large",
        dimensions=3072,
        chunk_size=8191,  # Max tokens for embedding model
        supports_batch=True,
        max_batch_size=2048,
        default_config={
            "encoding_format": "float",
        },
        is_active=True,
        is_default=True,
    )
    session.add(embedding_model)
    await session.commit()
    await session.refresh(gpt4_model)
    await session.refresh(embedding_model)

    logger.info(
        "Created default models",
        gpt4_id=gpt4_model.id,
        embedding_id=embedding_model.id,
    )

    # Create default embedding space
    default_embedding_space = EmbeddingSpace(
        model_id=embedding_model.id,
        name="openai_3large_default",
        display_name="Default OpenAI Embedding Space",
        description="Default embedding space using OpenAI text-embedding-3-large model",
        base_dimensions=3072,
        effective_dimensions=3072,
        reduction_strategy=ReductionStrategy.NONE,
        normalize_vectors=True,
        distance_metric=DistanceMetric.COSINE,
        table_name="embeddings_default",
        index_type="hnsw",
        index_config={
            "m": 16,
            "ef_construction": 200,
        },
        is_active=True,
        is_default=True,
    )
    session.add(default_embedding_space)
    await session.commit()
    await session.refresh(default_embedding_space)

    logger.info(
        "Created default embedding space",
        space_id=default_embedding_space.id,
        table_name=default_embedding_space.table_name,
    )


class SeedingMode(str, Enum):
    """Seeding modes for different use cases."""

    MINIMAL = (
        "minimal"  # Only essential data (admin user, basic defaults)
    )
    DEVELOPMENT = "development"  # Development-friendly data set
    DEMO = "demo"  # Full demo data with sample content
    TESTING = "testing"  # Data for automated testing
    PRODUCTION = "production"  # Production-ready minimal set


class DatabaseSeeder:
    """Comprehensive database seeding system."""

    def __init__(self, session: AsyncSession | None = None):
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
        if self._should_close_session and hasattr(self, "db_manager"):
            await self.db_manager.__aexit__(exc_type, exc_val, exc_tb)

    async def seed_database(
        self,
        mode: SeedingMode = SeedingMode.DEVELOPMENT,
        force: bool = False,
        skip_existing: bool = True,
    ) -> dict[str, Any]:
        """Seed the database with comprehensive data.

        Args:
            mode: Seeding mode to determine what data to create
            force: Whether to create data even if database has existing users
            skip_existing: Skip creating data if it already exists

        Returns:
            Dictionary with seeding results and created entity counts
        """
        logger.info(
            f"Starting database seeding in {mode} mode",
            force=force,
            skip_existing=skip_existing,
        )

        results = {
            "mode": mode,
            "created": {},
            "skipped": {},
            "errors": [],
        }

        try:
            # Check if database is virgin (for non-force mode)
            if not force:
                try:
                    existing_users = await self._count_users()
                    if existing_users > 0:
                        # Testing mode should still respect existing data unless forced
                        logger.info(
                            f"Database has {existing_users} users, skipping seeding"
                        )
                        results["skipped"][
                            "reason"
                        ] = "Database not empty"
                        return results
                except Exception as e:
                    # If we can't count users, rollback and let seeding continue
                    logger.warning(
                        f"Could not count existing users: {e}"
                    )
                    await self.session.rollback()

            # Begin fresh transaction for consistent seeding
            # Note: Individual methods handle their own commits for efficiency

            # Seed based on mode
            if mode == SeedingMode.MINIMAL:
                await self._seed_minimal_data(results, skip_existing)
            elif mode == SeedingMode.DEVELOPMENT:
                await self._seed_development_data(
                    results, skip_existing
                )
            elif mode == SeedingMode.DEMO:
                await self._seed_demo_data(results, skip_existing)
            elif mode == SeedingMode.TESTING:
                await self._seed_testing_data(results, skip_existing)
            elif mode == SeedingMode.PRODUCTION:
                await self._seed_production_data(results, skip_existing)

            logger.info(
                "Database seeding completed successfully",
                results=results,
            )
            return results

        except Exception as e:
            logger.error("Database seeding failed", error=str(e))
            results["errors"].append(str(e))
            # Ensure transaction is rolled back on failure
            try:
                await self.session.rollback()
            except Exception as rollback_error:
                logger.error(
                    f"Failed to rollback transaction: {rollback_error}"
                )
            raise

    async def _count_users(self) -> int:
        """Count existing users in database."""
        from sqlalchemy import func
        from sqlalchemy.exc import ProgrammingError

        try:
            result = await self.session.execute(
                select(func.count(User.id))
            )
            return result.scalar() or 0
        except ProgrammingError as e:
            # Table doesn't exist yet, return 0
            if "does not exist" in str(e):
                logger.debug(
                    "Users table does not exist, returning 0 count"
                )
                # Rollback transaction to reset failed state for PostgreSQL
                await self.session.rollback()
                return 0
            # For other errors, rollback and re-raise
            await self.session.rollback()
            raise
        except Exception as e:
            # For any other database errors, rollback transaction
            await self.session.rollback()
            logger.error(f"Error counting users: {e}")
            raise

    async def _seed_minimal_data(
        self, results: dict[str, Any], skip_existing: bool
    ):
        """Seed minimal essential data."""
        logger.info("Seeding minimal data")

        # Create admin user
        admin_user = await self._create_admin_user(skip_existing)
        results["created"]["users"] = 1 if admin_user else 0

        # Create basic provider and models
        provider_count, model_count = await self._create_basic_registry(
            skip_existing
        )
        results["created"]["providers"] = provider_count
        results["created"]["models"] = model_count

        # Create basic profiles
        profile_count = await self._create_basic_profiles(
            admin_user, skip_existing
        )
        results["created"]["profiles"] = profile_count

        # Create basic prompts
        prompt_count = await self._create_basic_prompts(
            admin_user, skip_existing
        )
        results["created"]["prompts"] = prompt_count

        # Create basic workflow templates
        workflow_template_count = (
            await self._create_basic_workflow_templates(
                admin_user, skip_existing
            )
        )
        results["created"][
            "workflow_templates"
        ] = workflow_template_count

    async def _seed_development_data(
        self, results: dict[str, Any], skip_existing: bool
    ):
        """Seed development-friendly data set."""
        logger.info("Seeding development data")

        # First seed minimal data
        await self._seed_minimal_data(results, skip_existing)

        # Add development users
        dev_users = await self._create_development_users(skip_existing)
        results["created"]["users"] = results["created"].get(
            "users", 0
        ) + len(dev_users)

        # Add sample conversations
        conversation_count = await self._create_sample_conversations(
            dev_users, skip_existing
        )
        results["created"]["conversations"] = conversation_count

        # Add sample documents
        document_count = await self._create_sample_documents(
            dev_users, skip_existing
        )
        results["created"]["documents"] = document_count

    async def _seed_demo_data(
        self, results: dict[str, Any], skip_existing: bool
    ):
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

        # Additional workflow templates
        extra_workflow_templates = (
            await self._create_demo_workflow_templates(skip_existing)
        )
        results["created"]["workflow_templates"] += len(
            extra_workflow_templates
        )

        # Sample embedding spaces
        embedding_spaces = await self._create_demo_embedding_spaces(
            skip_existing
        )
        results["created"]["embedding_spaces"] = len(embedding_spaces)

    async def _seed_testing_data(
        self, results: dict[str, Any], skip_existing: bool
    ):
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

    async def _seed_production_data(
        self, results: dict[str, Any], skip_existing: bool
    ):
        """Seed production-ready minimal data."""
        logger.info("Seeding production data")

        # Only essential data for production
        await self._seed_minimal_data(results, skip_existing)

    async def _create_admin_user(
        self, skip_existing: bool = True
    ) -> User | None:
        """Create admin user."""
        try:
            if skip_existing:
                try:
                    existing = await self.session.execute(
                        select(User).where(User.username == "admin")
                    )
                    existing_user = existing.scalar_one_or_none()
                    if existing_user:
                        logger.info(
                            "Admin user already exists, skipping"
                        )
                        return existing_user
                except Exception as e:
                    # If query fails (e.g., table doesn't exist), rollback and continue
                    await self.session.rollback()
                    logger.debug(
                        f"Could not check for existing admin user: {e}"
                    )

            # Generate secure random password
            admin_password = "".join(
                secrets.choice(
                    string.ascii_letters + string.digits + "!@#$%^&*"
                )
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
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to create admin user: {e}")
            raise

    async def _create_development_users(
        self, skip_existing: bool = True
    ) -> list[User]:
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
            },
        ]

        created_users = []
        try:
            for user_data in users_data:
                if skip_existing:
                    try:
                        existing = await self.session.execute(
                            select(User).where(
                                User.username == user_data["username"]
                            )
                        )
                        if existing.scalar_one_or_none():
                            continue
                    except Exception as e:
                        # If query fails, rollback and continue
                        await self.session.rollback()
                        logger.debug(
                            f"Could not check for existing user {user_data['username']}: {e}"
                        )

                user = User(
                    email=user_data["email"],
                    username=user_data["username"],
                    hashed_password=hash_password(
                        str(user_data["password"])
                    ),
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

            logger.info(
                f"Created {len(created_users)} development users"
            )
            return created_users
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to create development users: {e}")
            raise

    async def _create_test_users(
        self, skip_existing: bool = True
    ) -> list[User]:
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
                try:
                    existing = await self.session.execute(
                        select(User).where(
                            User.username == user_data["username"]
                        )
                    )
                    if existing.scalar_one_or_none():
                        continue
                except Exception as e:
                    # If query fails, rollback and continue
                    await self.session.rollback()
                    logger.debug(
                        f"Could not check for existing test user {user_data['username']}: {e}"
                    )

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

    async def _create_basic_registry(
        self, skip_existing: bool = True
    ) -> tuple[int, int]:
        """Create basic provider and model registry data."""
        try:
            if skip_existing:
                existing_provider = await self.session.execute(
                    select(Provider).where(Provider.name == "openai")
                )
                if existing_provider.scalar_one_or_none():
                    logger.info(
                        "Default registry data already exists, skipping"
                    )
                    return 0, 0

            await _create_default_registry_data(self.session)
            return 1, 2  # 1 provider, 2 models
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to create basic registry data: {e}")
            raise

    async def _create_basic_profiles(
        self, admin_user: User | None, skip_existing: bool = True
    ) -> int:
        """Create basic chat profiles."""
        try:
            if not admin_user:
                # Get admin user if not provided
                result = await self.session.execute(
                    select(User).where(User.username == "admin")
                )
                admin_user = result.scalar_one_or_none()
                if not admin_user:
                    logger.warning(
                        "No admin user found, skipping profile creation"
                    )
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
                },
            ]

            created_count = 0
            for profile_data in profiles_data:
                if skip_existing:
                    existing = await self.session.execute(
                        select(Profile).where(
                            Profile.name == profile_data["name"]
                        )
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
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to create basic profiles: {e}")
            raise

    async def _create_basic_prompts(
        self, admin_user: User | None, skip_existing: bool = True
    ) -> int:
        """Create basic prompt templates."""
        if not admin_user:
            result = await self.session.execute(
                select(User).where(User.username == "admin")
            )
            admin_user = result.scalar_one_or_none()
            if not admin_user:
                logger.warning(
                    "No admin user found, skipping prompt creation"
                )
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
                "category": PromptCategory.CODING,
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
                "category": PromptCategory.ANALYTICAL,
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
                "variables": [
                    "title",
                    "type",
                    "audience",
                    "content",
                    "length",
                    "focus_area",
                ],
            },
        ]

        created_count = 0
        for prompt_data in prompts_data:
            if skip_existing:
                existing = await self.session.execute(
                    select(Prompt).where(
                        Prompt.name == prompt_data["name"]
                    )
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

    async def _create_basic_workflow_templates(
        self, admin_user: User, skip_existing: bool = True
    ) -> int:
        """Create basic workflow templates."""
        if not admin_user:
            logger.warning(
                "No admin user provided, skipping basic workflow templates"
            )
            return 0

        templates_data = [
            {
                "name": "general_chat",
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
                "name": "code_assistant",

                "category": TemplateCategory.PROGRAMMING,
                "description": "Programming assistant with code tools",
                "default_params": {
                    "enable_memory": True,
                    "memory_window": 100,
                    "max_tool_calls": 10,
                    "system_message": "You are an expert programming assistant. Help users with coding tasks, debugging, code review, and software development best practices. Use available tools to execute code, run tests, and access documentation when needed.",
                },
                "required_tools": [
                    "execute_code",
                    "search_docs",
                    "generate_tests",
                ],
            },
        ]

        created_count = 0
        for template_data in templates_data:
            if skip_existing:
                existing = await self.session.execute(
                    select(WorkflowTemplate).where(
                        WorkflowTemplate.name == template_data["name"],
                        WorkflowTemplate.is_builtin,
                    )
                )
                if existing.scalar_one_or_none():
                    continue

            workflow_template = WorkflowTemplate(
                owner_id=admin_user.id,
                name=template_data["name"],
                description=template_data["description"],
                category=template_data["category"],
                default_params=template_data["default_params"],
                required_tools=template_data.get("required_tools"),
                required_retrievers=template_data.get(
                    "required_retrievers"
                ),
                is_builtin=True,
                is_public=True,  # Built-in templates are public by default
                version=1,
                is_latest=True,
            )

            self.session.add(workflow_template)
            created_count += 1

        if created_count > 0:
            await self.session.commit()

        logger.info(f"Created {created_count} basic workflow templates")
        return created_count

    async def _create_demo_workflow_templates(
        self, skip_existing: bool = True
    ) -> list[WorkflowTemplate]:
        """Create demo workflow templates."""
        # Get admin user
        result = await self.session.execute(
            select(User).where(User.username == "admin")
        )
        admin_user = result.scalar_one_or_none()
        if not admin_user:
            logger.warning(
                "No admin user found for demo workflow templates"
            )
            return []

        extended_templates_data = [
            {
                "name": "customer_support",

                "category": TemplateCategory.CUSTOMER_SUPPORT,
                "description": "Customer support with knowledge base and tools",
                "default_params": {
                    "enable_memory": True,
                    "memory_window": 50,
                    "max_tool_calls": 5,
                    "system_message": "You are a helpful customer support assistant. Use the knowledge base to find relevant information and available tools to help resolve customer issues. Always be polite, professional, and thorough in your responses.",
                },
                "required_tools": [
                    "search_kb",
                    "create_ticket",
                    "escalate",
                ],
                "required_retrievers": ["support_docs"],
            },
            {
                "name": "research_assistant",

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
                "name": "data_analyst",

                "category": TemplateCategory.DATA_ANALYSIS,
                "description": "Data analysis assistant with computation tools",
                "default_params": {
                    "enable_memory": True,
                    "memory_window": 50,
                    "max_tool_calls": 15,
                    "system_message": "You are a data analyst assistant. Help users analyze data, create visualizations, and derive insights. Use computational tools to perform calculations and generate charts.",
                },
                "required_tools": [
                    "execute_python",
                    "create_chart",
                    "analyze_data",
                ],
            },
            {
                "name": "blog_writing_assistant",

                "category": TemplateCategory.CREATIVE,
                "description": "Blog writing assistant with research and editing tools",
                "default_params": {
                    "enable_memory": True,
                    "memory_window": 40,
                    "max_tool_calls": 8,
                    "system_message": "You are a professional blog writing assistant. Help create engaging, well-researched blog posts with proper structure, compelling headlines, and SEO optimization.",
                },
                "required_tools": [
                    "web_search",
                    "grammar_check",
                    "seo_analyzer",
                ],
            },
            {
                "name": "meeting_summarizer",

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

                "category": TemplateCategory.EDUCATIONAL,
                "description": "Personalized learning tutor with assessment tools",
                "default_params": {
                    "enable_memory": True,
                    "memory_window": 100,
                    "max_tool_calls": 12,
                    "system_message": "You are a personalized learning tutor. Adapt your teaching style to the student's needs, provide clear explanations, create practice problems, and track learning progress.",
                },
                "required_tools": [
                    "create_quiz",
                    "check_answers",
                    "progress_tracker",
                ],
                "required_retrievers": ["learning_materials"],
            },
        ]

        created_templates = []
        for template_data in extended_templates_data:
            if skip_existing:
                existing = await self.session.execute(
                    select(WorkflowTemplate).where(
                        WorkflowTemplate.name == template_data["name"],
                        WorkflowTemplate.owner_id == admin_user.id,
                    )
                )
                if existing.scalar_one_or_none():
                    continue

            workflow_template = WorkflowTemplate(
                owner_id=admin_user.id,
                name=template_data["name"],
                description=template_data["description"],
                category=template_data["category"],
                default_params=template_data["default_params"],
                required_tools=template_data.get("required_tools"),
                required_retrievers=template_data.get(
                    "required_retrievers"
                ),
                is_builtin=False,
                is_public=True,  # Demo templates are public
                version=1,
                is_latest=True,
            )

            self.session.add(workflow_template)
            created_templates.append(workflow_template)

        if created_templates:
            await self.session.commit()
            for template in created_templates:
                await self.session.refresh(template)

        logger.info(
            f"Created {len(created_templates)} demo workflow templates"
        )
        return created_templates

    async def _create_sample_conversations(
        self, users: list[User], skip_existing: bool = True
    ) -> int:
        """Create sample conversations."""
        if not users:
            return 0

        conversations_data = [
            {
                "title": "Welcome Conversation",
                "description": "Initial welcome chat",
                "messages": [
                    {
                        "role": MessageRole.USER,
                        "content": "Hello! Can you help me understand what this platform does?",
                    },
                    {
                        "role": MessageRole.ASSISTANT,
                        "content": "Welcome to Chatter! I'm an AI assistant built on an advanced platform that supports multiple AI models, document analysis, and intelligent conversations. I can help you with various tasks like answering questions, analyzing documents, creative writing, and more. What would you like to explore?",
                    },
                    {
                        "role": MessageRole.USER,
                        "content": "That sounds great! How do I get started?",
                    },
                    {
                        "role": MessageRole.ASSISTANT,
                        "content": "Getting started is easy! You can:\n\n1. **Start a conversation** - Just ask me anything\n2. **Upload documents** - I can analyze and answer questions about your files\n3. **Use templates** - Try our pre-built prompt templates for specific tasks\n4. **Customize profiles** - Adjust my behavior for different use cases\n\nWhat interests you most?",
                    },
                ],
            }
        ]

        created_count = 0
        for conv_data in conversations_data:
            if skip_existing:
                existing = await self.session.execute(
                    select(Conversation).where(
                        Conversation.title == conv_data["title"]
                    )
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

    async def _create_sample_documents(
        self, users: list[User], skip_existing: bool = True
    ) -> int:
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
            },
        ]

        created_count = 0
        for doc_data in documents_data:
            if skip_existing:
                existing = await self.session.execute(
                    select(Document).where(
                        Document.filename == doc_data["filename"]
                    )
                )
                if existing.scalar_one_or_none():
                    continue

            user = users[0]

            document = Document(
                owner_id=user.id,
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
    async def _create_demo_profiles(
        self, skip_existing: bool = True
    ) -> list[Profile]:
        """Create additional profiles for demo purposes."""
        # Implementation would create more specialized profiles
        return []

    async def _create_demo_prompts(
        self, skip_existing: bool = True
    ) -> list[Prompt]:
        """Create additional prompts for demo purposes."""
        # Implementation would create more specialized prompts
        return []

    async def _create_demo_embedding_spaces(
        self, skip_existing: bool = True
    ) -> list[EmbeddingSpace]:
        """Create demo embedding spaces."""
        from sqlalchemy import select

        from chatter.models.registry import EmbeddingSpace, ModelDef

        # Get the embedding model
        result = await self.session.execute(
            select(ModelDef).where(
                ModelDef.model_name == "text-embedding-ada-002"
            )
        )
        embedding_model = result.scalar_one_or_none()
        if not embedding_model:
            logger.warning(
                "No embedding model found, skipping embedding space creation"
            )
            return []

        spaces_data = [
            {
                "name": "default_documents",
                "description": "Default embedding space for document processing",
                "distance_metric": DistanceMetric.COSINE,
                "dimensions": 1536,
                "reduction_strategy": ReductionStrategy.NONE,
            },
            {
                "name": "conversations",
                "description": "Embedding space optimized for conversation context",
                "distance_metric": DistanceMetric.COSINE,
                "dimensions": 512,
                "reduction_strategy": ReductionStrategy.PCA,
            },
        ]

        created_spaces = []
        for space_data in spaces_data:
            if skip_existing:
                existing = await self.session.execute(
                    select(EmbeddingSpace).where(
                        EmbeddingSpace.name == space_data["name"]
                    )
                )
                if existing.scalar_one_or_none():
                    continue

            space = EmbeddingSpace(
                model_id=embedding_model.id,
                name=space_data["name"],
                description=space_data["description"],
                distance_metric=space_data["distance_metric"],
                dimensions=space_data["dimensions"],
                reduction_strategy=space_data["reduction_strategy"],
                is_default=space_data["name"] == "default_documents",
            )

            self.session.add(space)
            created_spaces.append(space)

        if created_spaces:
            await self.session.commit()
            for space in created_spaces:
                await self.session.refresh(space)

        logger.info(
            f"Created {len(created_spaces)} demo embedding spaces"
        )
        return created_spaces

    async def _create_test_registry_data(
        self, skip_existing: bool = True
    ):
        """Create test registry data."""
        # For testing, we use the same default registry data for consistency
        await _create_default_registry_data(self.session)
        logger.info("Created test registry data (using defaults)")

        # Could add additional test-specific providers/models here in the future
        pass

    async def _create_test_conversations(
        self, users: list[User], skip_existing: bool = True
    ):
        """Create test conversations."""
        if not users:
            return 0

        test_conversations = [
            {
                "title": "Test Conversation 1",
                "description": "First test conversation for automated testing",
                "messages": [
                    {"role": MessageRole.USER, "content": "Hello test"},
                    {
                        "role": MessageRole.ASSISTANT,
                        "content": "Hello! This is a test response.",
                    },
                ],
            },
            {
                "title": "Test Conversation 2",
                "description": "Second test conversation for automated testing",
                "messages": [
                    {
                        "role": MessageRole.USER,
                        "content": "What is 2+2?",
                    },
                    {
                        "role": MessageRole.ASSISTANT,
                        "content": "2+2 equals 4.",
                    },
                ],
            },
        ]

        created_count = 0
        for conv_data in test_conversations:
            if skip_existing:
                existing = await self.session.execute(
                    select(Conversation).where(
                        Conversation.title == conv_data["title"]
                    )
                )
                if existing.scalar_one_or_none():
                    continue

            # Use first user for test conversations
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

        logger.info(f"Created {created_count} test conversations")
        return created_count

    async def _create_test_documents(
        self, users: list[User], skip_existing: bool = True
    ):
        """Create test documents."""
        if not users:
            return 0

        test_documents = [
            {
                "filename": "test_doc_1.txt",
                "title": "Test Document 1",
                "content": "This is the first test document content for automated testing.",
                "doc_type": DocumentType.TEXT,
            },
            {
                "filename": "test_doc_2.md",
                "title": "Test Document 2",
                "content": "# Test Document\n\nThis is a markdown test document.\n\n## Section 1\nTest content here.",
                "doc_type": DocumentType.MARKDOWN,
            },
        ]

        created_count = 0
        for doc_data in test_documents:
            if skip_existing:
                existing = await self.session.execute(
                    select(Document).where(
                        Document.filename == doc_data["filename"]
                    )
                )
                if existing.scalar_one_or_none():
                    continue

            user = users[0]

            document = Document(
                owner_id=user.id,
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

            # Create document chunk
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

        logger.info(f"Created {created_count} test documents")
        return created_count


# Convenience functions for direct usage
async def seed_database(
    mode: SeedingMode = SeedingMode.DEVELOPMENT,
    force: bool = False,
    skip_existing: bool = True,
) -> dict[str, Any]:
    """Convenience function to seed database."""
    try:
        async with DatabaseSeeder() as seeder:
            return await seeder.seed_database(
                mode, force, skip_existing
            )
    except Exception as e:
        logger.error(f"Database seeding failed: {e}")
        raise


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
        # Delete messages first (depends on conversations)
        await session.execute(delete(Message))

        # Delete conversations (depends on users)
        await session.execute(delete(Conversation))

        # Delete document chunks (depends on documents)
        await session.execute(delete(DocumentChunk))

        # Delete documents (depends on users)
        await session.execute(delete(Document))

        # Delete prompts (depends on users)
        await session.execute(delete(Prompt))

        # Delete profiles (depends on users)
        await session.execute(delete(Profile))

        # Delete embedding spaces (depends on model_defs)
        await session.execute(delete(EmbeddingSpace))

        # Delete model definitions (depends on providers)
        await session.execute(delete(ModelDef))

        # Delete providers
        await session.execute(delete(Provider))

        # Delete users last
        await session.execute(delete(User))

        await session.commit()

    logger.warning("All database data cleared")
    return True
