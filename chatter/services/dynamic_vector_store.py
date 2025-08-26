"""Dynamic vector store service using per-model embedding tables."""

import json
from typing import Any, Dict, List, Optional

from sqlalchemy import create_engine, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from chatter.config import get_settings
from chatter.core.dynamic_embeddings import (
    get_embedding_model,
    get_model_dimensions,
    list_embedding_models,
    PGVECTOR_AVAILABLE,
)
from chatter.models.document import DocumentChunk
from chatter.utils.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class DynamicVectorStoreService:
    """Service for vector storage using dynamic per-model tables."""

    def __init__(self, session: AsyncSession):
        """Initialize dynamic vector store service.

        Args:
            session: Database session
        """
        self.session = session
        self.store_type = settings.vector_store_type
        
        # Create synchronous engine for dynamic table operations
        # Remove async driver from connection string
        sync_db_url = settings.database_url
        if "+asyncpg" in sync_db_url:
            sync_db_url = sync_db_url.replace("+asyncpg", "")
        
        self.sync_engine = create_engine(sync_db_url)

    async def store_embedding(
        self,
        chunk_id: str,
        embedding: List[float],
        provider_name: str,
        model_name: str = None,
        metadata: Optional[Dict[str, Any]] = None,
        **index_params,
    ) -> bool:
        """Store embedding for a document chunk using dynamic model tables.

        Args:
            chunk_id: Document chunk ID
            embedding: Embedding vector
            provider_name: Name of the embedding provider (e.g., "openai")
            model_name: Optional specific model name for the table
            metadata: Additional metadata
            **index_params: Index configuration parameters

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the chunk from the main documents table
            result = await self.session.execute(
                select(DocumentChunk).where(DocumentChunk.id == chunk_id)
            )
            chunk = result.scalar_one_or_none()

            if not chunk:
                logger.error("Chunk not found", chunk_id=chunk_id)
                return False

            # Use provider name as model name if not specified
            table_model_name = model_name or provider_name
            
            # Get vector dimension for this provider
            dim = len(embedding)
            expected_dim = get_model_dimensions(provider_name)
            
            if dim != expected_dim:
                logger.warning(
                    "Embedding dimension mismatch",
                    provider=provider_name,
                    expected=expected_dim,
                    actual=dim,
                )

            # Store embedding based on vector store type
            if self.store_type == "pgvector" and PGVECTOR_AVAILABLE:
                return await self._store_dynamic_pgvector_embedding(
                    chunk, embedding, table_model_name, dim, metadata, **index_params
                )
            else:
                # Fallback: update the main chunk table
                return await self._store_fallback_embedding(
                    chunk, embedding, provider_name, metadata
                )

        except Exception as e:
            logger.error(
                "Failed to store embedding",
                chunk_id=chunk_id,
                provider=provider_name,
                error=str(e),
            )
            return False

    async def _store_dynamic_pgvector_embedding(
        self,
        chunk: DocumentChunk,
        embedding: List[float],
        model_name: str,
        dim: int,
        metadata: Optional[Dict[str, Any]] = None,
        **index_params,
    ) -> bool:
        """Store embedding using dynamic PGVector tables.

        Args:
            chunk: Document chunk
            embedding: Embedding vector
            model_name: Name for the embedding table
            dim: Vector dimension
            metadata: Additional metadata
            **index_params: Index configuration parameters

        Returns:
            True if successful
        """
        try:
            # Get or create the embedding model for this provider
            embedding_model_class = get_embedding_model(
                model_name, dim, self.sync_engine, **index_params
            )

            # Create synchronous session for the embedding table
            sync_session_maker = sessionmaker(bind=self.sync_engine)
            
            with sync_session_maker() as sync_session:
                # Check if embedding already exists
                existing = sync_session.execute(
                    select(embedding_model_class).where(
                        embedding_model_class.chunk_id == chunk.id
                    )
                ).scalar_one_or_none()

                if existing:
                    # Update existing embedding
                    existing.embedding = embedding
                    existing.content = chunk.content
                    existing.metadata = json.dumps(metadata) if metadata else None
                else:
                    # Create new embedding record
                    embedding_record = embedding_model_class(
                        document_id=chunk.document_id,
                        chunk_id=chunk.id,
                        embedding=embedding,
                        content=chunk.content,
                        metadata=json.dumps(metadata) if metadata else None,
                    )
                    sync_session.add(embedding_record)

                sync_session.commit()

            # Update the main chunk with embedding metadata
            chunk.embedding_model = model_name
            chunk.embedding_provider = model_name.split("_")[0]  # Extract provider from model name
            
            await self.session.commit()
            await self.session.refresh(chunk)

            logger.debug(
                "Dynamic PGVector embedding stored",
                chunk_id=chunk.id,
                model=model_name,
                dimension=dim,
            )
            return True

        except Exception as e:
            await self.session.rollback()
            logger.error(
                "Failed to store dynamic PGVector embedding",
                chunk_id=chunk.id,
                model=model_name,
                error=str(e),
            )
            return False

    async def _store_fallback_embedding(
        self,
        chunk: DocumentChunk,
        embedding: List[float],
        provider_name: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Store embedding as JSON string in main table (fallback).

        Args:
            chunk: Document chunk
            embedding: Embedding vector
            provider_name: Name of the embedding provider
            metadata: Additional metadata

        Returns:
            True if successful
        """
        try:
            # Store embedding as JSON string in the main table
            chunk.embedding = json.dumps(embedding)
            chunk.embedding_provider = provider_name
            
            if metadata:
                chunk.extra_metadata = {
                    **(chunk.extra_metadata or {}),
                    **metadata,
                }

            await self.session.commit()
            await self.session.refresh(chunk)

            logger.debug("Fallback JSON embedding stored", chunk_id=chunk.id)
            return True

        except Exception as e:
            await self.session.rollback()
            logger.error(
                "Failed to store fallback embedding",
                chunk_id=chunk.id,
                error=str(e),
            )
            return False

    async def similarity_search(
        self,
        query_embedding: List[float],
        provider_name: str,
        model_name: str = None,
        limit: int = 10,
        score_threshold: float = 0.5,
        document_ids: Optional[List[str]] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Perform similarity search using dynamic model tables.

        Args:
            query_embedding: Query vector
            provider_name: Name of the embedding provider
            model_name: Optional specific model name
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            document_ids: Optional list of document IDs to filter by
            metadata_filter: Optional metadata filter

        Returns:
            List of similar chunks with scores
        """
        try:
            table_model_name = model_name or provider_name
            
            if self.store_type == "pgvector" and PGVECTOR_AVAILABLE:
                return await self._similarity_search_pgvector(
                    query_embedding,
                    table_model_name,
                    limit,
                    score_threshold,
                    document_ids,
                    metadata_filter,
                )
            else:
                return await self._similarity_search_fallback(
                    query_embedding,
                    provider_name,
                    limit,
                    score_threshold,
                    document_ids,
                    metadata_filter,
                )

        except Exception as e:
            logger.error(
                "Failed to perform similarity search",
                provider=provider_name,
                error=str(e),
            )
            return []

    async def _similarity_search_pgvector(
        self,
        query_embedding: List[float],
        model_name: str,
        limit: int,
        score_threshold: float,
        document_ids: Optional[List[str]],
        metadata_filter: Optional[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Perform similarity search using PGVector on dynamic tables."""
        
        # Get the embedding model for this provider (don't create if it doesn't exist)
        embedding_models_dict = list_embedding_models()
        if model_name not in embedding_models_dict:
            logger.warning(
                "No embedding model found for provider",
                model=model_name,
            )
            return []

        embedding_model_class = embedding_models_dict[model_name]
        
        # Create synchronous session for querying
        sync_session_maker = sessionmaker(bind=self.sync_engine)
        
        with sync_session_maker() as sync_session:
            # Build query
            query = select(
                embedding_model_class.chunk_id,
                embedding_model_class.document_id,
                embedding_model_class.content,
                embedding_model_class.metadata,
                embedding_model_class.embedding.cosine_distance(query_embedding).label("distance"),
            ).order_by(
                embedding_model_class.embedding.cosine_distance(query_embedding)
            ).limit(limit)

            # Apply filters
            if document_ids:
                query = query.where(embedding_model_class.document_id.in_(document_ids))

            # Execute query
            results = sync_session.execute(query).fetchall()

            # Convert to list of dictionaries
            similar_chunks = []
            for result in results:
                similarity_score = 1 - result.distance  # Convert distance to similarity
                
                if similarity_score >= score_threshold:
                    similar_chunks.append({
                        "chunk_id": result.chunk_id,
                        "document_id": result.document_id,
                        "content": result.content,
                        "metadata": json.loads(result.metadata) if result.metadata else {},
                        "similarity_score": similarity_score,
                    })

            logger.debug(
                "PGVector similarity search completed",
                model=model_name,
                results_count=len(similar_chunks),
            )
            return similar_chunks

    async def _similarity_search_fallback(
        self,
        query_embedding: List[float],
        provider_name: str,
        limit: int,
        score_threshold: float,
        document_ids: Optional[List[str]],
        metadata_filter: Optional[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Perform similarity search using JSON embeddings (fallback)."""
        # This would implement cosine similarity in Python
        # For brevity, returning empty list - would need full implementation
        logger.warning("Fallback similarity search not fully implemented")
        return []

    async def get_embedding_stats(self) -> Dict[str, Any]:
        """Get statistics about stored embeddings across all models."""
        try:
            stats = {
                "total_chunks": 0,
                "embedded_chunks": 0,
                "models_used": {},
                "vector_store_type": self.store_type,
                "pgvector_available": PGVECTOR_AVAILABLE,
            }

            # Get stats from main chunks table
            main_result = await self.session.execute(
                select(
                    func.count(DocumentChunk.id).label("total"),
                    func.count(DocumentChunk.embedding_model).label("embedded"),
                )
            )
            main_stats = main_result.first()
            
            stats["total_chunks"] = main_stats.total
            stats["embedded_chunks"] = main_stats.embedded

            # Get stats from dynamic embedding tables
            embedding_models_dict = list_embedding_models()
            
            if embedding_models_dict and PGVECTOR_AVAILABLE:
                sync_session_maker = sessionmaker(bind=self.sync_engine)
                
                with sync_session_maker() as sync_session:
                    for model_name, model_class in embedding_models_dict.items():
                        try:
                            count_result = sync_session.execute(
                                select(func.count(model_class.id))
                            ).scalar()
                            
                            stats["models_used"][model_name] = {
                                "embeddings_count": count_result,
                                "table_name": model_class.__tablename__,
                            }
                        except Exception as e:
                            logger.warning(
                                "Failed to get stats for model",
                                model=model_name,
                                error=str(e),
                            )

            stats["embedding_coverage"] = (
                (stats["embedded_chunks"] / stats["total_chunks"]) * 100
                if stats["total_chunks"] > 0
                else 0.0
            )

            return stats

        except Exception as e:
            logger.error("Failed to get embedding stats", error=str(e))
            return {
                "total_chunks": 0,
                "embedded_chunks": 0,
                "embedding_coverage": 0.0,
                "models_used": {},
                "vector_store_type": self.store_type,
                "pgvector_available": PGVECTOR_AVAILABLE,
            }