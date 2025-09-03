"""Dynamic embedding model factory for multiple LLMs with different vector sizes."""

import re

from sqlalchemy import Column, Integer, String, text
from sqlalchemy.orm import declarative_base

try:
    from pgvector.sqlalchemy import Vector

    PGVECTOR_AVAILABLE = True
except ImportError:
    from sqlalchemy import Text as Vector

    PGVECTOR_AVAILABLE = False

from chatter.config import settings
from chatter.utils.logging import get_logger

logger = get_logger(__name__)

Base = declarative_base()

# Global registry for embedding models
embedding_models: dict[str, type] = {}


def _to_name(name: str, dim: int) -> str:
    # Should contain the dimension and suffiix
    ending = f"_{str(dim)}_embed"

    # Make it all lowercase
    name = name.lower()

    # Replace invalid chars with underscore
    name = re.sub(r'[^a-z0-9_]', '_', name)

    # Ensure it starts with a letter or underscore
    if not re.match(r'^[a-z_]', name):
        name = "_" + name

    # Combine and truncate to max Postgres identifier length
    name = f"{name[:63 - len(ending)]}{ending}"

    return name


def make_embedding_model(name: str, dim: int):
    """
    Dynamically creates and registers a SQLAlchemy model for an embedding table.
    Each model gets its own table with the correct vector dimension.

    Args:
        name: Name of the embedding model (from _to_name())
        dim: Vector dimension for this model

    Returns:
        SQLAlchemy model class for the embedding table
    """
    model_class = type(
        name,
        (Base,),
        {
            "__tablename__": name,
            "id": Column(Integer, primary_key=True),
            "document_id": Column(
                String(26), nullable=False, index=True
            ),
            "chunk_id": Column(String(26), nullable=False, index=True),
            "embedding": Column(
                Vector(dim) if PGVECTOR_AVAILABLE else String,
                nullable=False,
            ),
            "content": Column(String, nullable=False),
            "extra_metadata": Column(String, nullable=True),
        },
    )

    embedding_models[name] = model_class
    return model_class


def ensure_table_and_index(
    engine,
    model_class: type,
    metric: str = "cosine",
    m: int = 16,
    ef_construction: int = 64,
):
    """
    Create the table and ANN index if they don't exist.
    Also runs ANALYZE after creating the index.

    Args:
        engine: SQLAlchemy engine
        model_class: The SQLAlchemy model class
        metric: Distance metric ("cosine", "l2", or "ip")
        m: HNSW m parameter
        ef_construction: HNSW ef_construction parameter
    """
    table_name = model_class.__table__

    if not PGVECTOR_AVAILABLE:
        logger.warning(
            "pgvector not available, skipping index creation"
        )
        # Create table without vector index
        Base.metadata.create_all(engine, tables=[table_name])
        return

    # Create the table if missing
    Base.metadata.create_all(engine, tables=[table_name])

    # Pick operator family
    ops = {
        "cosine": "vector_cosine_ops",
        "l2": "vector_l2_ops",
        "ip": "vector_ip_ops",
    }.get(metric, "vector_cosine_ops")

    index_name = f"{table_name}_idx"
    index_sql = f"""
    CREATE INDEX IF NOT EXISTS {index_name}
    ON {table_name} USING hnsw (embedding {ops})
    WITH (m = {m}, ef_construction = {ef_construction});
    """

    # Run index creation + analyze
    with engine.connect() as conn:
        conn.execute(text(index_sql))
        conn.execute(text(f"ANALYZE {table_name};"))
        conn.commit()

    logger.info(
        "Created embedding table and index",
        table=table_name,
        index_type="hnsw",
        metric=metric,
    )


def get_embedding_model(
    model_name: str,
    dim: int,
    engine=None,
    metric: str = "cosine",
    m: int = 16,
    ef_construction: int = 64,
):
    """
    Get or create the embedding model for the given LLM.
    Ensures ANN index exists if engine is provided.

    Args:
        model_name: Name of the embedding model
        dim: Vector dimension
        engine: SQLAlchemy engine (optional)
        metric: Distance metric
        index_type: Index type
        lists: IVFFlat lists parameter
        m: HNSW m parameter
        ef_construction: HNSW ef_construction parameter

    Returns:
        SQLAlchemy model class for the embedding table
    """
    name = _to_name(model_name, dim)

    if name in embedding_models:
        return embedding_models[name]

    # Not registered → create dynamically
    model_class = make_embedding_model(name, dim)

    if engine is not None:
        ensure_table_and_index(
            engine,
            model_class,
            metric=metric,
            m=m,
            ef_construction=ef_construction,
        )

    return model_class


def get_model_dimensions(provider_name: str) -> int:
    """
    Get the default vector dimension for a given provider.

    Args:
        provider_name: Name of the embedding provider

    Returns:
        Vector dimension for the provider
    """
    # Default dimensions for known providers
    dimensions = {
        "openai": settings.openai_embedding_dimensions or 1536,
        "anthropic": 768,
        "google": settings.google_embedding_dimensions or 768,
        "cohere": settings.cohere_embedding_dimensions or 1024,
        "mistral": 4096,
    }

    return dimensions.get(provider_name.lower(), 1536)


def list_embedding_models() -> dict[str, type]:
    """
    List all registered embedding models.

    Returns:
        Dictionary mapping model names to SQLAlchemy classes
    """
    return embedding_models.copy()


def clear_embedding_models():
    """Clear all registered embedding models (useful for testing)."""
    global embedding_models
    embedding_models.clear()


class DynamicEmbeddingService:
    """Service for dynamic embedding operations."""

    def __init__(self, session=None):
        """Initialize the service with an optional database session."""
        self.session = session

    async def store_embeddings(
        self,
        model_name: str,
        dimension: int,
        embeddings_data: list[dict],
    ) -> bool:
        """Store embeddings in dynamic table."""
        try:
            # Get or create the embedding model for this dimension
            embedding_model = get_embedding_model(model_name, dimension)

            # Create instances and add to session
            for data in embeddings_data:
                instance = embedding_model(
                    document_id=data["document_id"],
                    chunk_id=data.get("chunk_id", data["document_id"]),
                    embedding=data["embedding"],
                    content=data["text"],
                    extra_metadata=data.get("metadata"),
                )
                self.session.add(instance)

            await self.session.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to store embeddings: {e}")
            return False

    async def retrieve_embeddings(
        self, model_name: str, dimension: int, document_id: str
    ) -> list:
        """Retrieve embeddings from dynamic table."""
        try:
            embedding_model = get_embedding_model(model_name, dimension)
            from sqlalchemy import select

            query = select(embedding_model).where(
                embedding_model.document_id == document_id
            )
            result = await self.session.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to retrieve embeddings: {e}")
            return []

    async def search_similar_embeddings(
        self,
        model_name: str,
        dimension: int,
        query_embedding: list[float],
        limit: int = 5,
    ) -> list:
        """Search for similar embeddings."""
        try:
            embedding_model = get_embedding_model(model_name, dimension)
            # This would need proper vector similarity search implementation
            # For now, return empty list as placeholder
            return []
        except Exception as e:
            logger.error(f"Failed to search similar embeddings: {e}")
            return []


class EmbeddingModelManager:
    """Manager for dynamic embedding models and database operations."""

    def __init__(self, session=None):
        """Initialize embedding model manager with database session."""
        self.session = session

    async def register_model(
        self, model_name: str, dimension: int
    ) -> type:
        """Register a new embedding model and create its database table."""
        try:
            # Create the model class
            model_class = get_embedding_model(model_name, dimension)

            # Create the table if it doesn't exist
            await self.create_embedding_table(model_name, dimension)

            logger.info(
                f"Registered embedding model: {model_name} (dim={dimension})"
            )
            return model_class
        except Exception as e:
            logger.error(f"Failed to register model {model_name}: {e}")
            raise

    async def unregister_model(
        self, model_name: str, dimension: int
    ) -> bool:
        """Unregister an embedding model and optionally drop its table."""
        try:
            table_name = _to_name(model_name, dimension)

            # Remove from registry
            if table_name in embedding_models:
                del embedding_models[table_name]

            # Optionally drop the table
            await self.drop_embedding_table(model_name, dimension)

            logger.info(
                f"Unregistered embedding model: {model_name} (dim={dimension})"
            )
            return True
        except Exception as e:
            logger.error(
                f"Failed to unregister model {model_name}: {e}"
            )
            return False

    async def create_embedding_table(
        self, model_name: str, dimension: int
    ) -> bool:
        """Create embedding table for the specified model."""
        try:
            table_name = _to_name(model_name, dimension)

            # Create indexes separately
            index_sql_1 = f"CREATE INDEX IF NOT EXISTS idx_{table_name}_document_id ON {table_name}(document_id);"
            index_sql_2 = f"CREATE INDEX IF NOT EXISTS idx_{table_name}_chunk_id ON {table_name}(chunk_id);"

            if self.session:
                # Try to create pgvector extension if needed, but handle failure gracefully
                vector_available = False
                if PGVECTOR_AVAILABLE:
                    try:
                        await self.session.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                        await self.session.commit()
                        vector_available = True
                    except Exception as e:
                        logger.warning(f"Could not create vector extension: {e}")
                        # Rollback the failed transaction
                        await self.session.rollback()
                        vector_available = False

                # Update the SQL to use TEXT if vector is not available
                embedding_type = f"VECTOR({dimension})" if vector_available else "TEXT"
                create_sql = f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id SERIAL PRIMARY KEY,
                    document_id VARCHAR(26) NOT NULL,
                    chunk_id VARCHAR(26) NOT NULL,
                    embedding {embedding_type} NOT NULL,
                    content TEXT NOT NULL,
                    extra_metadata TEXT
                );
                """

                await self.session.execute(text(create_sql))
                await self.session.execute(text(index_sql_1))
                await self.session.execute(text(index_sql_2))
                await self.session.commit()

            return True
        except Exception as e:
            logger.error(
                f"Failed to create table for {model_name}: {e}"
            )
            return False

    async def drop_embedding_table(
        self, model_name: str, dimension: int
    ) -> bool:
        """Drop embedding table for the specified model."""
        try:
            table_name = _to_name(model_name, dimension)

            if self.session:
                await self.session.execute(
                    text(f"DROP TABLE IF EXISTS {table_name}")
                )
                await self.session.commit()

            return True
        except Exception as e:
            logger.error(f"Failed to drop table for {model_name}: {e}")
            return False

    async def table_exists(
        self, model_name: str, dimension: int
    ) -> bool:
        """Check if embedding table exists."""
        try:
            table_name = _to_name(model_name, dimension)

            if self.session:
                result = await self.session.execute(
                    text(
                        "SELECT 1 FROM information_schema.tables WHERE table_name = :table_name"
                    ),
                    {"table_name": table_name},
                )
                return bool(result.scalar())

            return False
        except Exception as e:
            logger.error(
                f"Failed to check table existence for {model_name}: {e}"
            )
            return False

    async def get_table_info(
        self, model_name: str, dimension: int
    ) -> list:
        """Get information about the embedding table."""
        try:
            table_name = _to_name(model_name, dimension)

            if self.session:
                result = await self.session.execute(
                    text(
                        "SELECT column_name, data_type, column_default FROM information_schema.columns WHERE table_name = :table_name"
                    ),
                    {"table_name": table_name},
                )
                return result.fetchall()

            return []
        except Exception as e:
            logger.error(
                f"Failed to get table info for {model_name}: {e}"
            )
            return []
