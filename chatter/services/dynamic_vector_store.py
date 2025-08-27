"""Dynamic vector store service using per-model embedding tables.

Parity with legacy VectorStoreService:
- similarity_search returns List[tuple[DocumentChunk, float]]
- JSON fallback similarity implemented
- hybrid_search implemented
"""

import asyncio
import json
import math
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import create_engine, select, func, or_
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
        model_name: str | None = None,
        metadata: Optional[Dict[str, Any]] = None,
        **index_params,
    ) -> bool:
        """Store embedding for a document chunk using dynamic model tables."""
        try:
            # Get the chunk from the main documents table (async, on main loop)
            result = await self.session.execute(
                select(DocumentChunk).where(DocumentChunk.id == chunk_id)
            )
            chunk = result.scalar_one_or_none()

            if not chunk:
                logger.error("Chunk not found", chunk_id=chunk_id)
                return False

            # Use provider name as model name if not specified
            table_model_name = model_name or provider_name
            
            # Validate vector dimension for this provider if known
            dim = len(embedding)
            expected_dim = get_model_dimensions(provider_name)
            if expected_dim and dim != expected_dim:
                logger.warning(
                    "Embedding dimension mismatch",
                    provider=provider_name,
                    expected=expected_dim,
                    actual=dim,
                )

            # Store embedding based on vector store type
            if self.store_type == "pgvector" and PGVECTOR_AVAILABLE:
                ok = await asyncio.to_thread(
                    self._store_dynamic_pgvector_embedding_sync,
                    chunk,
                    embedding,
                    table_model_name,
                    dim,
                    metadata,
                    index_params,
                )
            else:
                # Fallback: update the main chunk table (async)
                ok = await self._store_fallback_embedding(
                    chunk, embedding, provider_name, metadata
                )

            # Update the main chunk with embedding metadata (common) - async on main loop
            if ok:
                chunk.add_embedding_model(table_model_name, set_as_primary=True)
                chunk.embedding_provider = provider_name
                await self.session.commit()
                await self.session.refresh(chunk)

            return ok

        except Exception as e:
            logger.error(
                "Failed to store embedding",
                chunk_id=chunk_id,
                provider=provider_name,
                error=str(e),
            )
            return False

    # Synchronous helper: runs entirely on a worker thread via asyncio.to_thread
    def _store_dynamic_pgvector_embedding_sync(
        self,
        chunk: DocumentChunk,
        embedding: List[float],
        model_name: str,
        dim: int,
        metadata: Optional[Dict[str, Any]] = None,
        index_params: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Store embedding using dynamic PGVector tables (sync path, threaded)."""
        try:
            # Get or create the embedding model for this provider
            embedding_model_class = get_embedding_model(
                model_name, dim, self.sync_engine, **(index_params or {})
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
                        extra_metadata=json.dumps(metadata) if metadata else None,
                    )
                    sync_session.add(embedding_record)

                sync_session.commit()

            logger.debug(
                "Dynamic PGVector embedding stored",
                chunk_id=chunk.id,
                model=model_name,
                dimension=dim,
            )
            return True

        except Exception as e:
            # Note: do not touch AsyncSession here (we're in a worker thread)
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
        """Store embedding as JSON string in main table (fallback)."""
        try:
            # Store embedding as JSON string in the main table
            chunk.embedding = json.dumps(embedding)
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
        model_name: str | None = None,
        limit: int = 10,
        score_threshold: float = 0.5,
        document_ids: Optional[List[str]] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[DocumentChunk, float]]:
        """Perform similarity search using dynamic model tables.

        Returns:
            List of (chunk, similarity_score) tuples
        """
        try:
            table_model_name = model_name or provider_name
            
            if self.store_type == "pgvector" and PGVECTOR_AVAILABLE:
                rows = await asyncio.to_thread(
                    self._pgvector_search_rows_sync,
                    table_model_name,
                    query_embedding,
                    limit,
                    document_ids,
                )
                # Convert to similarity and fetch chunks asynchronously
                id_with_scores: List[Tuple[str, float]] = []
                for chunk_id, distance in rows:
                    similarity_score = 1.0 - float(distance)
                    if similarity_score >= score_threshold:
                        id_with_scores.append((chunk_id, similarity_score))

                if not id_with_scores:
                    return []

                # Fetch chunks in one async query
                chunk_ids = [cid for cid, _ in id_with_scores]
                result = await self.session.execute(
                    select(DocumentChunk).where(DocumentChunk.id.in_(chunk_ids))
                )
                chunks = result.scalars().all()
                chunk_map = {c.id: c for c in chunks}

                # Preserve order and filter out any missing
                ordered: List[Tuple[DocumentChunk, float]] = []
                for cid, score in id_with_scores:
                    chunk = chunk_map.get(cid)
                    if not chunk:
                        continue
                    # Optional metadata filter
                    if metadata_filter:
                        ok = True
                        for k, v in metadata_filter.items():
                            if not chunk.extra_metadata or str(chunk.extra_metadata.get(k)) != str(v):
                                ok = False
                                break
                        if not ok:
                            continue
                    ordered.append((chunk, score))

                logger.debug(
                    "PGVector similarity search completed",
                    results_count=len(ordered),
                    model=table_model_name,
                    limit=limit,
                    threshold=score_threshold,
                )
                return ordered
            else:
                return await self._similarity_search_fallback(
                    query_embedding,
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

    # Sync helper for PGVector similarity, runs in thread
    def _pgvector_search_rows_sync(
        self,
        model_name: str,
        query_embedding: List[float],
        limit: int,
        document_ids: Optional[List[str]],
    ) -> List[Tuple[str, float]]:
        """Perform PGVector query synchronously and return (chunk_id, distance) rows."""
        try:
            # Get the embedding model for this provider (don't create if it doesn't exist)
            embedding_models_dict = list_embedding_models()
            if model_name not in embedding_models_dict:
                logger.warning("No embedding model found for provider", model=model_name)
                return []

            embedding_model_class = embedding_models_dict[model_name]
            
            # Create synchronous session for querying
            sync_session_maker = sessionmaker(bind=self.sync_engine)
            with sync_session_maker() as sync_session:
                # Build query: compute cosine distance then order by it
                query = select(
                    embedding_model_class.chunk_id,
                    embedding_model_class.embedding.cosine_distance(query_embedding).label("distance"),
                ).order_by(
                    embedding_model_class.embedding.cosine_distance(query_embedding)
                ).limit(limit)

                # Apply filters
                if document_ids:
                    query = query.where(embedding_model_class.document_id.in_(document_ids))

                # Execute query synchronously
                rows = sync_session.execute(query).fetchall()

            return rows
        except Exception as e:
            logger.error("PGVector similarity search failed", error=str(e))
            return []

    async def _similarity_search_fallback(
        self,
        query_embedding: List[float],
        limit: int,
        score_threshold: float,
        document_ids: Optional[List[str]],
        metadata_filter: Optional[Dict[str, Any]],
    ) -> List[Tuple[DocumentChunk, float]]:
        """Perform similarity search using JSON embeddings (fallback)."""
        try:
            # Select chunks that have legacy JSON embeddings
            query = select(DocumentChunk).where(DocumentChunk.embedding.is_not(None))

            # Apply filters
            if document_ids:
                query = query.where(DocumentChunk.document_id.in_(document_ids))

            if metadata_filter:
                # Simplified metadata equals filter
                for key, value in metadata_filter.items():
                    query = query.where(
                        DocumentChunk.extra_metadata[key].astext == str(value)
                    )

            result = await self.session.execute(query)
            chunks = result.scalars().all()

            matches: List[Tuple[DocumentChunk, float]] = []
            for chunk in chunks:
                try:
                    # Parse JSON embedding
                    emb = chunk.embedding
                    if isinstance(emb, str):
                        chunk_embedding = json.loads(emb)
                    else:
                        # Some DBs may return list directly
                        chunk_embedding = emb

                    similarity = self._cosine_similarity(query_embedding, chunk_embedding)
                    if similarity >= score_threshold:
                        matches.append((chunk, float(similarity)))
                except Exception:
                    continue

            # Sort and limit
            matches.sort(key=lambda x: x[1], reverse=True)
            return matches[:limit]

        except Exception as e:
            logger.error("Fallback similarity search failed", error=str(e))
            return []

    async def hybrid_search(
        self,
        query_embedding: List[float],
        provider_name: str,
        model_name: str | None = None,
        text_query: str = "",
        limit: int = 10,
        score_threshold: float = 0.5,
        document_ids: Optional[List[str]] = None,
        semantic_weight: float = 0.7,
        text_weight: float = 0.3,
    ) -> List[Tuple[DocumentChunk, float]]:
        """Perform hybrid search combining semantic and text search.

        Returns:
            List of (chunk, combined_score) tuples
        """
        try:
            # Semantic search
            semantic_results = await self.similarity_search(
                query_embedding=query_embedding,
                provider_name=provider_name,
                model_name=model_name,
                limit=limit * 2,
                score_threshold=score_threshold * 0.5,
                document_ids=document_ids,
            )

            # Text search (simple LIKE-based)
            from sqlalchemy import select as sa_select, func as sa_func
            text_query_words = (text_query or "").lower().split()
            text_query_obj = sa_select(DocumentChunk)

            if document_ids:
                text_query_obj = text_query_obj.where(
                    DocumentChunk.document_id.in_(document_ids)
                )

            for word in text_query_words:
                text_query_obj = text_query_obj.where(
                    sa_func.lower(DocumentChunk.content).contains(word)
                )

            text_result = await self.session.execute(text_query_obj.limit(limit * 2))
            text_chunks = text_result.scalars().all()

            # Combine
            combined_scores: dict[str, dict[str, Any]] = {}

            for chunk, score in semantic_results:
                combined_scores[chunk.id] = {
                    "chunk": chunk,
                    "semantic_score": float(score),
                    "text_score": 0.0,
                }

            for chunk in text_chunks:
                text_score = self._calculate_text_score(chunk.content or "", text_query)
                if chunk.id in combined_scores:
                    combined_scores[chunk.id]["text_score"] = text_score
                else:
                    combined_scores[chunk.id] = {
                        "chunk": chunk,
                        "semantic_score": 0.0,
                        "text_score": text_score,
                    }

            results: List[Tuple[DocumentChunk, float]] = []
            for data in combined_scores.values():
                semantic_score = float(data["semantic_score"])
                text_score = float(data["text_score"])
                chunk_obj: DocumentChunk = data["chunk"]
                combined = semantic_weight * semantic_score + text_weight * text_score
                if combined >= score_threshold:
                    results.append((chunk_obj, combined))

            results.sort(key=lambda x: x[1], reverse=True)
            return results[:limit]

        except Exception as e:
            logger.error("Hybrid search failed", error=str(e))
            return []

    async def get_embedding_stats(self) -> Dict[str, Any]:
        """Get statistics about stored embeddings across all models."""
        try:
            stats: Dict[str, Any] = {
                "total_chunks": 0,
                "embedded_chunks": 0,
                "models_used": {},
                "vector_store_type": self.store_type,
                "pgvector_available": PGVECTOR_AVAILABLE,
            }

            # Total chunks
            total_result = await self.session.execute(
                select(func.count(DocumentChunk.id))
            )
            stats["total_chunks"] = int(total_result.scalar() or 0)

            # Chunks with any embeddings (legacy or dynamic metadata)
            embedded_result = await self.session.execute(
                select(func.count(DocumentChunk.id)).where(
                    or_(
                        DocumentChunk.embedding.is_not(None),
                        DocumentChunk.embedding_models.is_not(None),
                    )
                )
            )
            stats["embedded_chunks"] = int(embedded_result.scalar() or 0)

            # Dynamic tables counts (PGVector only)
            embedding_models_dict = list_embedding_models()
            if embedding_models_dict and PGVECTOR_AVAILABLE:
                sync_session_maker = sessionmaker(bind=self.sync_engine)
                rows: Dict[str, Dict[str, Any]] = {}
                # Offload the synchronous count queries
                def _count_sync() -> Dict[str, Dict[str, Any]]:
                    with sync_session_maker() as sync_session:
                        out: Dict[str, Dict[str, Any]] = {}
                        for model_name, model_class in embedding_models_dict.items():
                            try:
                                count_result = sync_session.execute(
                                    select(func.count(model_class.id))
                                ).scalar()
                                out[model_name] = {
                                    "embeddings_count": int(count_result or 0),
                                    "table_name": model_class.__tablename__,
                                }
                            except Exception as e:
                                logger.warning("Failed to get stats for model", model=model_name, error=str(e))
                        return out
                rows = await asyncio.to_thread(_count_sync)
                stats["models_used"] = rows

            stats["embedding_coverage"] = (
                (stats["embedded_chunks"] / stats["total_chunks"]) * 100.0
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

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        try:
            if not vec1 or not vec2 or len(vec1) != len(vec2):
                return 0.0
            dot = sum(a * b for a, b in zip(vec1, vec2, strict=False))
            mag1 = math.sqrt(sum(a * a for a in vec1))
            mag2 = math.sqrt(sum(b * b for b in vec2))
            if mag1 == 0.0 or mag2 == 0.0:
                return 0.0
            return float(dot) / float(mag1 * mag2)
        except Exception:
            return 0.0

    def _calculate_text_score(self, content: str, query: str) -> float:
        """Simple text similarity based on word matches."""
        try:
            content_lower = (content or "").lower()
            query_lower = (query or "").lower()
            words = [w for w in query_lower.split() if w]
            if not words:
                return 0.0
            matches = sum(1 for w in words if w in content_lower)
            return matches / len(words)
        except Exception:
            return 0.0
