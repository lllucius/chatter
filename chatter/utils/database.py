"""Database utilities and connection management."""

import asyncio
from collections.abc import AsyncGenerator

from sqlalchemy import event, text

# Compatibility layer for SQLAlchemy versions
try:
    from sqlalchemy.ext.asyncio import (
        AsyncEngine,
        AsyncSession,
        async_sessionmaker,
        create_async_engine,
    )
except ImportError:
    # Fallback for older SQLAlchemy versions
    from sqlalchemy.ext.asyncio import (
        AsyncEngine,
        AsyncSession,
        create_async_engine,
    )
    from sqlalchemy.orm import sessionmaker

    async_sessionmaker = sessionmaker

from chatter.config import settings
from chatter.models.base import Base
from chatter.utils.logging import get_logger

logger = get_logger(__name__)

# Import QueryOptimizer from database_optimization for backward compatibility

# Global database engine and session maker
_engine: AsyncEngine | None = None
_session_maker: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Get the database engine, creating it if necessary."""
    global _engine

    if _engine is None:
        database_url = settings.database_url_for_env

        # Engine configuration
        engine_kwargs = {
            "echo": settings.debug_database_queries,
            "future": True,
        }

        # PostgreSQL-specific settings
        engine_kwargs.update(
            {
                "pool_size": settings.db_pool_size,
                "max_overflow": settings.db_max_overflow,
                "pool_pre_ping": settings.db_pool_pre_ping,
                "pool_recycle": settings.db_pool_recycle,
            }
        )

        _engine = create_async_engine(database_url, **engine_kwargs)

        # Add query logging event listener
        if settings.debug_database_queries:

            @event.listens_for(
                _engine.sync_engine, "before_cursor_execute"
            )
            def receive_before_cursor_execute(
                conn,
                cursor,
                statement,
                parameters,
                context,
                executemany,
            ):
                """Log SQL queries when debug mode is enabled."""
                logger.debug(
                    "SQL Query",
                    statement=statement,
                    parameters=parameters,
                )

    return _engine


def get_session_maker() -> async_sessionmaker[AsyncSession]:
    """Get the session maker, creating it if necessary."""
    global _session_maker

    if _session_maker is None:
        engine = get_engine()
        _session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    return _session_maker


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session.

    This is typically used as a dependency in FastAPI endpoints.

    Yields:
        AsyncSession: Database session
    """
    session_maker = get_session_maker()
    session = session_maker()

    try:
        yield session
    except GeneratorExit:
        # Handle generator cleanup gracefully
        # On GeneratorExit, avoid operations that might conflict with ongoing transactions
        logger.debug("Database session generator closed")
        try:
            # Check if session is still usable before attempting cleanup
            if session:
                # Don't commit or rollback on GeneratorExit - just close if safe
                if not session.in_transaction():
                    await session.close()
                else:
                    # If in transaction, let the session cleanup happen naturally
                    session.expunge_all()
        except Exception as e:
            logger.debug(
                "Session cleanup during generator exit", error=str(e)
            )
        raise
    except Exception:
        # On other exceptions, attempt rollback
        try:
            if session:
                await session.rollback()
        except Exception as e:
            logger.warning("Error rolling back session", error=str(e))
        raise
    else:
        # Normal completion - commit the transaction
        try:
            if session:
                await session.commit()
        except Exception as e:
            logger.warning("Error committing session", error=str(e))
            try:
                await session.rollback()
            except Exception:
                pass
            raise
    finally:
        # Final cleanup - close the session if it's still open and safe to do so
        try:
            if session:
                # Only attempt close if not in the middle of a transaction operation
                if not session.in_transaction():
                    await session.close()
        except Exception as e:
            logger.debug("Error in final session cleanup", error=str(e))


async def _create_default_registry_data(session: AsyncSession) -> None:
    """Create default provider, models, and embedding spaces for the registry."""
    from sqlalchemy import select

    from chatter.models.registry import (
        DistanceMetric,
        EmbeddingSpace,
        ModelDef,
        ModelType,
        Provider,
        ProviderType,
        ReductionStrategy,
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


async def initialize_default_data() -> None:
    """Initialize default prompts, profiles, and admin user when database is virgin."""
    from sqlalchemy import select

    from chatter.models.profile import Profile, ProfileType
    from chatter.models.prompt import Prompt, PromptCategory, PromptType
    from chatter.models.user import User
    from chatter.utils.security import hash_password

    async with DatabaseManager() as session:
        # Check if this is a virgin database (no users exist)
        result = await session.execute(select(User).limit(1))
        existing_user = result.scalar_one_or_none()

        if existing_user is not None:
            logger.info(
                "Database already has users, skipping default data initialization"
            )
            return

        logger.info(
            "Virgin database detected, initializing default data"
        )

        # Create admin user with secure random password
        import secrets
        import string

        # Generate a secure random password
        admin_password = ''.join(
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
        session.add(admin_user)
        await session.commit()
        await session.refresh(admin_user)

        logger.info("Created admin user", user_id=admin_user.id)
        logger.warning(
            "IMPORTANT: Admin user created with random password. "
            f"Email: admin@admin.net, Password: {admin_password}. "
            "Please change this password immediately after first login!"
        )

        # Create default prompts
        default_prompts = [
            {
                "name": "Instruction Task Template",
                "description": "A template for giving clear instructions and tasks to the AI",
                "category": PromptCategory.GENERAL,
                "content": """Please complete the following task with precision and clarity:

Task: {task}

Requirements:
- {requirements}

Context: {context}

Please provide a detailed response that addresses all aspects of the task.""",
                "variables": ["task", "requirements", "context"],
                "examples": [
                    {
                        "input": {
                            "task": "Summarize the quarterly report",
                            "requirements": "Keep it under 200 words, highlight key metrics",
                            "context": "Q3 2024 financial data",
                        },
                        "output": "A concise summary focusing on revenue growth, expenses, "
                        "and key performance indicators from Q3 2024.",
                    }
                ],
                "suggested_temperature": 0.3,
                "suggested_max_tokens": 1000,
            },
            {
                "name": "Few-Shot Learning Template",
                "description": "Template for providing examples to guide AI responses",
                "category": PromptCategory.EDUCATIONAL,
                "content": """Here are some examples of the desired format:

Example 1:
Input: {example1_input}
Output: {example1_output}

Example 2:
Input: {example2_input}
Output: {example2_output}

Example 3:
Input: {example3_input}
Output: {example3_output}

Now, please follow the same pattern for:
Input: {new_input}
Output:""",
                "variables": [
                    "example1_input",
                    "example1_output",
                    "example2_input",
                    "example2_output",
                    "example3_input",
                    "example3_output",
                    "new_input",
                ],
                "suggested_temperature": 0.2,
                "suggested_max_tokens": 800,
            },
            {
                "name": "Chain-of-Thought Reasoning",
                "description": "Template to encourage step-by-step logical reasoning",
                "category": PromptCategory.ANALYTICAL,
                "content": """Let's solve this step by step.

Problem: {problem}

Step 1: First, let me understand what is being asked.
{understanding}

Step 2: Let me identify the key information.
{key_info}

Step 3: Let me work through the logic.
{reasoning_steps}

Step 4: Let me verify my reasoning.
{verification}

Final Answer: {conclusion}""",
                "variables": [
                    "problem",
                    "understanding",
                    "key_info",
                    "reasoning_steps",
                    "verification",
                    "conclusion",
                ],
                "suggested_temperature": 0.4,
                "suggested_max_tokens": 1500,
            },
            {
                "name": "Role and Persona Template",
                "description": "Template for defining specific roles and personas for the AI",
                "category": PromptCategory.CREATIVE,
                "content": """You are a {role} with {experience} years of experience in {field}.

Your personality traits:
- {trait1}
- {trait2}
- {trait3}

Your expertise includes:
- {expertise1}
- {expertise2}
- {expertise3}

Speaking style: {speaking_style}

Now, please respond to the following as this character:
{prompt}""",
                "variables": [
                    "role",
                    "experience",
                    "field",
                    "trait1",
                    "trait2",
                    "trait3",
                    "expertise1",
                    "expertise2",
                    "expertise3",
                    "speaking_style",
                    "prompt",
                ],
                "suggested_temperature": 0.8,
                "suggested_max_tokens": 1200,
            },
            {
                "name": "Context and Question Template",
                "description": "Template for providing context before asking questions",
                "category": PromptCategory.GENERAL,
                "content": """Context Information:
{context_background}

Relevant Details:
- {detail1}
- {detail2}
- {detail3}

Current Situation:
{current_situation}

Question: {question}

Please provide a comprehensive answer that takes into account all the context provided above.""",
                "variables": [
                    "context_background",
                    "detail1",
                    "detail2",
                    "detail3",
                    "current_situation",
                    "question",
                ],
                "suggested_temperature": 0.5,
                "suggested_max_tokens": 1000,
            },
            {
                "name": "Format-Constrained Response",
                "description": "Template for responses requiring specific formatting",
                "category": PromptCategory.TECHNICAL,
                "content": """Please respond to the following in the exact format specified:

Request: {request}

Format Requirements:
{format_requirements}

Output Format:
{output_format}

Constraints:
- {constraint1}
- {constraint2}
- {constraint3}

Please ensure your response strictly follows the specified format.""",
                "variables": [
                    "request",
                    "format_requirements",
                    "output_format",
                    "constraint1",
                    "constraint2",
                    "constraint3",
                ],
                "suggested_temperature": 0.1,
                "suggested_max_tokens": 800,
            },
            {
                "name": "Delimited Input Template",
                "description": "Template using clear delimiters to separate different input sections",
                "category": PromptCategory.TECHNICAL,
                "content": """Please analyze the following information separated by delimiters:

===== MAIN CONTENT =====
{main_content}

===== ADDITIONAL CONTEXT =====
{additional_context}

===== SPECIFIC REQUIREMENTS =====
{requirements}

===== CONSTRAINTS =====
{constraints}

===== END OF INPUT =====

Based on the delimited sections above, please provide your analysis.""",
                "variables": [
                    "main_content",
                    "additional_context",
                    "requirements",
                    "constraints",
                ],
                "suggested_temperature": 0.3,
                "suggested_max_tokens": 1200,
            },
            {
                "name": "Meta Prompt Engineering Pattern",
                "description": "Template for prompt engineering and optimization",
                "category": PromptCategory.CUSTOM,
                "content": """Meta-Prompt Engineering Task:

Objective: {objective}
Target Audience: {audience}
Desired Outcome: {outcome}

Current Prompt Analysis:
Original Prompt: {original_prompt}

Improvement Areas:
1. Clarity: {clarity_issues}
2. Specificity: {specificity_issues}
3. Context: {context_issues}

Enhancement Strategy:
- {strategy1}
- {strategy2}
- {strategy3}

Please create an improved prompt that addresses these meta-considerations.""",
                "variables": [
                    "objective",
                    "audience",
                    "outcome",
                    "original_prompt",
                    "clarity_issues",
                    "specificity_issues",
                    "context_issues",
                    "strategy1",
                    "strategy2",
                    "strategy3",
                ],
                "suggested_temperature": 0.6,
                "suggested_max_tokens": 1500,
            },
        ]

        for prompt_data in default_prompts:
            prompt = Prompt(
                owner_id=admin_user.id,
                name=prompt_data["name"],
                description=prompt_data["description"],
                prompt_type=PromptType.TEMPLATE,
                category=prompt_data["category"],
                content=prompt_data["content"],
                variables=prompt_data["variables"],
                examples=prompt_data.get("examples"),
                suggested_temperature=prompt_data.get(
                    "suggested_temperature"
                ),
                suggested_max_tokens=prompt_data.get(
                    "suggested_max_tokens"
                ),
                is_public=True,
            )
            session.add(prompt)

        # Create default profiles
        default_profiles = [
            {
                "name": "Deterministic/Factual Mode",
                "description": "Low temperature profile for factual, consistent responses",
                "profile_type": ProfileType.ANALYTICAL,
                "llm_provider": "openai",
                "llm_model": "gpt-4",
                "temperature": 0.1,
                "max_tokens": 2048,
                "top_p": 0.9,
                "system_prompt": "You are a factual assistant that provides accurate, consistent, and well-researched information. Focus on objectivity and precision in your responses.",
                "enable_tools": False,
                "tags": ["factual", "deterministic", "analytical"],
            },
            {
                "name": "Balanced/Default Mode",
                "description": "Balanced settings suitable for general conversation",
                "profile_type": ProfileType.CONVERSATIONAL,
                "llm_provider": "openai",
                "llm_model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 4096,
                "top_p": 1.0,
                "system_prompt": "You are a helpful, informative, and balanced assistant. Provide thoughtful responses that are both accurate and engaging.",
                "enable_tools": True,
                "tags": ["balanced", "default", "conversational"],
            },
            {
                "name": "Creative/Brainstorming Mode",
                "description": "High temperature profile for creative and diverse outputs",
                "profile_type": ProfileType.CREATIVE,
                "llm_provider": "openai",
                "llm_model": "gpt-4",
                "temperature": 0.9,
                "max_tokens": 4096,
                "top_p": 1.0,
                "system_prompt": "You are a creative assistant focused on generating innovative ideas, exploring possibilities, and thinking outside the box. Embrace creativity and diverse perspectives.",
                "enable_tools": True,
                "tags": ["creative", "brainstorming", "innovative"],
            },
            {
                "name": "Concise/Short-Form Mode",
                "description": "Profile optimized for brief, direct responses",
                "profile_type": ProfileType.CONVERSATIONAL,
                "llm_provider": "openai",
                "llm_model": "gpt-4",
                "temperature": 0.5,
                "max_tokens": 512,
                "top_p": 0.95,
                "system_prompt": "You are a concise assistant that provides direct, brief, and to-the-point responses. Avoid unnecessary elaboration while maintaining accuracy and helpfulness.",
                "enable_tools": False,
                "tags": ["concise", "brief", "direct"],
            },
            {
                "name": "Exploration/Diverse Mode",
                "description": "Profile that encourages diverse perspectives and exploration",
                "profile_type": ProfileType.ANALYTICAL,
                "llm_provider": "openai",
                "llm_model": "gpt-4",
                "temperature": 0.8,
                "max_tokens": 3072,
                "top_p": 0.95,
                "top_k": 50,
                "system_prompt": "You are an exploratory assistant that considers multiple perspectives, examines different angles, and encourages deep thinking about complex topics.",
                "enable_tools": True,
                "tags": ["exploration", "diverse", "multi-perspective"],
            },
            {
                "name": "Step-by-Step Reasoning Mode",
                "description": "Profile focused on methodical, logical problem-solving",
                "profile_type": ProfileType.ANALYTICAL,
                "llm_provider": "openai",
                "llm_model": "gpt-4",
                "temperature": 0.3,
                "max_tokens": 2048,
                "top_p": 0.9,
                "system_prompt": "You are a methodical assistant that breaks down complex problems into clear steps, shows your reasoning process, and provides structured solutions.",
                "enable_tools": True,
                "tags": ["reasoning", "methodical", "step-by-step"],
            },
        ]

        for profile_data in default_profiles:
            profile = Profile(
                owner_id=admin_user.id,
                name=profile_data["name"],
                description=profile_data["description"],
                profile_type=profile_data["profile_type"],
                llm_provider=profile_data["llm_provider"],
                llm_model=profile_data["llm_model"],
                temperature=profile_data["temperature"],
                max_tokens=profile_data["max_tokens"],
                top_p=profile_data.get("top_p"),
                top_k=profile_data.get("top_k"),
                system_prompt=profile_data.get("system_prompt"),
                enable_tools=profile_data.get("enable_tools", False),
                is_public=True,
                tags=profile_data.get("tags", []),
            )
            session.add(profile)

        await session.commit()

        # Create default provider, models, and embedding spaces
        await _create_default_registry_data(session)

        logger.info(
            "Default data initialization completed successfully"
        )


async def init_database() -> None:
    """Initialize the database and create tables."""
    engine = get_engine()

    # Import all models to ensure they're registered

    logger.info("Creating database tables")

    # For PostgreSQL, ensure pgvector extension is installed
    async with engine.begin() as conn:
        try:
            await conn.execute(
                text("CREATE EXTENSION IF NOT EXISTS vector;")
            )
            logger.info("Ensured pgvector extension is installed")
        except Exception as e:
            logger.warning(
                "Could not install pgvector extension", error=str(e)
            )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database tables created")

    # Initialize default data for virgin database
    try:
        await initialize_default_data()
    except Exception as e:
        logger.error("Failed to initialize default data", error=str(e))
        # Don't fail the entire initialization if default data fails

    logger.info("Database initialization completed")


async def check_database_connection() -> bool:
    """Check if database connection is working.

    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        engine = get_engine()
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error("Database connection check failed", error=str(e))
        return False


async def close_database() -> None:
    """Close database connections."""
    global _engine, _session_maker

    if _engine:
        await _engine.dispose()
        _engine = None

    _session_maker = None
    logger.info("Database connections closed")


class DatabaseManager:
    """Context manager for database operations."""

    def __init__(self) -> None:
        """Initialize database session context."""
        self.session: AsyncSession | None = None

    async def __aenter__(self) -> AsyncSession:
        """Enter async context and create session."""
        session_maker = get_session_maker()
        self.session = session_maker()
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit async context and close session."""
        if self.session:
            if exc_type:
                await self.session.rollback()
            else:
                await self.session.commit()
            await self.session.close()


# Alias for backward compatibility
DatabaseConnectionManager = DatabaseManager


async def execute_query(query: str, **params) -> any:
    """Execute a raw SQL query.

    Args:
        query: SQL query string
        **params: Query parameters

    Returns:
        Query result
    """
    async with DatabaseManager() as session:
        result = await session.execute(text(query), params)
        return result


async def health_check() -> dict:
    """Perform database health check.

    Returns:
        dict: Health check results
    """
    try:
        start_time = asyncio.get_event_loop().time()

        # Test basic connection
        is_connected = await check_database_connection()

        # Test query performance
        async with DatabaseManager() as session:
            await session.execute(text("SELECT version()"))

        end_time = asyncio.get_event_loop().time()
        response_time = round((end_time - start_time) * 1000, 2)  # ms

        return {
            "status": "healthy" if is_connected else "unhealthy",
            "connected": is_connected,
            "response_time_ms": response_time,
            "database_url": settings.database_url_for_env.split("@")[
                -1
            ],  # Hide credentials
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "connected": False,
            "error": str(e),
        }


async def create_tables() -> bool:
    """Create database tables.

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        engine = get_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        return True
    except Exception as e:
        logger.error("Failed to create tables", error=str(e))
        return False


async def drop_tables() -> bool:
    """Drop database tables.

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        engine = get_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        return True
    except Exception as e:
        logger.error("Failed to drop tables", error=str(e))
        return False
