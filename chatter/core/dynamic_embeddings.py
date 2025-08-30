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
            "document_id": Column(String(26), nullable=False, index=True),
            "chunk_id": Column(String(26), nullable=False, index=True),
            "embedding": Column(Vector(dim) if PGVECTOR_AVAILABLE else String, nullable=False),
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
        logger.warning("pgvector not available, skipping index creation")
        # Create table without vector index
        Base.metadata.create_all(engine, tables=[table_name])
        return

    # Create the table if missing
    Base.metadata.create_all(engine, tables=[table_name])

    # Pick operator family
    ops = {
        "cosine": "vector_cosine_ops",
        "l2": "vector_l2_ops",
        "ip": "vector_ip_ops"
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
        metric=metric
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
