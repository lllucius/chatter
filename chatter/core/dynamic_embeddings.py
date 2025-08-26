"""Dynamic embedding model factory for multiple LLMs with different vector sizes."""

from typing import Any, Dict, Type

from sqlalchemy import Column, Integer, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

try:
    from pgvector.sqlalchemy import Vector
    PGVECTOR_AVAILABLE = True
except ImportError:
    from sqlalchemy import Text as Vector
    PGVECTOR_AVAILABLE = False

from chatter.utils.logging import get_logger

logger = get_logger(__name__)

Base = declarative_base()

# Global registry for embedding models
embedding_models: Dict[str, Type] = {}


def make_embedding_model(model_name: str, dim: int):
    """
    Dynamically creates and registers a SQLAlchemy model for an embedding table.
    Each model gets its own table with the correct vector dimension.
    
    Args:
        model_name: Name of the embedding model (e.g., "openai", "anthropic")
        dim: Vector dimension for this model
        
    Returns:
        SQLAlchemy model class for the embedding table
    """
    table_name = f"{model_name.lower()}_embeddings"
    
    model_class = type(
        f"{model_name.capitalize()}Embedding",
        (Base,),
        {
            "__tablename__": table_name,
            "id": Column(Integer, primary_key=True),
            "document_id": Column(String(12), nullable=False, index=True),
            "chunk_id": Column(String(12), nullable=False, index=True),
            "embedding": Column(Vector(dim) if PGVECTOR_AVAILABLE else String, nullable=False),
            "content": Column(String, nullable=False),
            "metadata": Column(String, nullable=True),
        },
    )
    
    embedding_models[model_name.lower()] = model_class
    return model_class


def ensure_table_and_index(
    engine,
    model_class: Type,
    metric: str = "cosine",
    index_type: str = "ivfflat",
    lists: int = 100,
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
        index_type: Index type ("ivfflat" or "hnsw")
        lists: IVFFlat partitions
        m: HNSW m parameter
        ef_construction: HNSW ef_construction parameter
    """
    if not PGVECTOR_AVAILABLE:
        logger.warning("pgvector not available, skipping index creation")
        # Create table without vector index
        Base.metadata.create_all(engine, tables=[model_class.__table__])
        return
    
    # Create the table if missing
    Base.metadata.create_all(engine, tables=[model_class.__table__])
    
    # Pick operator family
    ops = {
        "cosine": "vector_cosine_ops",
        "l2": "vector_l2_ops",
        "ip": "vector_ip_ops"
    }.get(metric, "vector_cosine_ops")
    
    table_name = model_class.__tablename__
    index_name = f"{table_name}_embedding_idx"
    
    # Pick index SQL
    if index_type == "ivfflat":
        index_sql = f"""
        CREATE INDEX IF NOT EXISTS {index_name}
        ON {table_name} USING ivfflat (embedding {ops})
        WITH (lists = {lists});
        """
    elif index_type == "hnsw":
        index_sql = f"""
        CREATE INDEX IF NOT EXISTS {index_name}
        ON {table_name} USING hnsw (embedding {ops})
        WITH (m = {m}, ef_construction = {ef_construction});
        """
    else:
        raise ValueError(f"Unsupported index_type: {index_type}")
    
    # Run index creation + analyze
    with engine.connect() as conn:
        conn.execute(text(index_sql))
        conn.execute(text(f"ANALYZE {table_name};"))
        conn.commit()
        
    logger.info(
        "Created embedding table and index",
        table=table_name,
        index_type=index_type,
        metric=metric
    )


def get_embedding_model(
    model_name: str,
    dim: int,
    engine=None,
    metric: str = "cosine",
    index_type: str = "ivfflat",
    lists: int = 100,
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
    model_name = model_name.lower()
    
    if model_name in embedding_models:
        return embedding_models[model_name]
    
    # Not registered → create dynamically
    model_class = make_embedding_model(model_name, dim)
    
    if engine is not None:
        ensure_table_and_index(
            engine,
            model_class,
            metric=metric,
            index_type=index_type,
            lists=lists,
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
        "openai": 1536,
        "anthropic": 768,
        "google": 768,
        "cohere": 1024,
        "mistral": 4096,
    }
    
    return dimensions.get(provider_name.lower(), 1536)


def list_embedding_models() -> Dict[str, Type]:
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