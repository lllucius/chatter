"""Vector store service for document search and retrieval."""

import json
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from pgvector.sqlalchemy import Vector
    from sqlalchemy import text
    PGVECTOR_AVAILABLE = True
except ImportError:
    PGVECTOR_AVAILABLE = False

from chatter.config import get_settings
from chatter.models.document import DocumentChunk
from chatter.utils.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class VectorStoreService:
    """Service for vector storage and similarity search."""

    def __init__(self, session: AsyncSession):
        """Initialize vector store service.

        Args:
            session: Database session
        """
        self.session = session
        self.store_type = settings.vector_store_type
        self.collection_name = settings.pgvector_collection_name
        self.embedding_dimension = settings.pgvector_embedding_dimension

    async def store_embedding(
        self,
        chunk_id: str,
        embedding: list[float],
        metadata: dict[str, Any] | None = None
    ) -> bool:
        """Store embedding for a document chunk.

        Args:
            chunk_id: Document chunk ID
            embedding: Embedding vector
            metadata: Additional metadata

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the chunk
            result = await self.session.execute(
                select(DocumentChunk).where(DocumentChunk.id == chunk_id)
            )
            chunk = result.scalar_one_or_none()

            if not chunk:
                logger.error("Chunk not found", chunk_id=chunk_id)
                return False

            # Store embedding based on vector store type
            if self.store_type == "pgvector" and PGVECTOR_AVAILABLE:
                return await self._store_pgvector_embedding(chunk, embedding, metadata)
            else:
                # Fallback: store as JSON string
                return await self._store_json_embedding(chunk, embedding, metadata)

        except Exception as e:
            logger.error("Failed to store embedding", chunk_id=chunk_id, error=str(e))
            return False

    async def _store_pgvector_embedding(
        self,
        chunk: DocumentChunk,
        embedding: list[float],
        metadata: dict[str, Any] | None = None
    ) -> bool:
        """Store embedding using PGVector.

        Args:
            chunk: Document chunk
            embedding: Embedding vector
            metadata: Additional metadata

        Returns:
            True if successful
        """
        try:
            # Validate embedding dimension
            if len(embedding) != self.embedding_dimension:
                logger.warning(
                    "Embedding dimension mismatch",
                    expected=self.embedding_dimension,
                    actual=len(embedding)
                )

            # Update chunk with embedding
            chunk.embedding = embedding
            if metadata:
                chunk.extra_metadata = {**(chunk.extra_metadata or {}), **metadata}

            await self.session.commit()

            logger.debug("PGVector embedding stored", chunk_id=chunk.id)
            return True

        except Exception as e:
            await self.session.rollback()
            logger.error("Failed to store PGVector embedding", chunk_id=chunk.id, error=str(e))
            return False

    async def _store_json_embedding(
        self,
        chunk: DocumentChunk,
        embedding: list[float],
        metadata: dict[str, Any] | None = None
    ) -> bool:
        """Store embedding as JSON string (fallback).

        Args:
            chunk: Document chunk
            embedding: Embedding vector
            metadata: Additional metadata

        Returns:
            True if successful
        """
        try:
            # Store embedding as JSON string
            chunk.embedding = json.dumps(embedding)
            if metadata:
                chunk.extra_metadata = {**(chunk.extra_metadata or {}), **metadata}

            await self.session.commit()

            logger.debug("JSON embedding stored", chunk_id=chunk.id)
            return True

        except Exception as e:
            await self.session.rollback()
            logger.error("Failed to store JSON embedding", chunk_id=chunk.id, error=str(e))
            return False

    async def similarity_search(
        self,
        query_embedding: list[float],
        limit: int = 10,
        score_threshold: float = 0.5,
        document_ids: list[str] | None = None,
        metadata_filter: dict[str, Any] | None = None
    ) -> list[tuple[DocumentChunk, float]]:
        """Perform similarity search.

        Args:
            query_embedding: Query embedding vector
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            document_ids: Filter by document IDs
            metadata_filter: Filter by metadata

        Returns:
            List of (chunk, similarity_score) tuples
        """
        try:
            if self.store_type == "pgvector" and PGVECTOR_AVAILABLE:
                return await self._pgvector_similarity_search(
                    query_embedding, limit, score_threshold, document_ids, metadata_filter
                )
            else:
                return await self._json_similarity_search(
                    query_embedding, limit, score_threshold, document_ids, metadata_filter
                )

        except Exception as e:
            logger.error("Similarity search failed", error=str(e))
            return []

    async def _pgvector_similarity_search(
        self,
        query_embedding: list[float],
        limit: int,
        score_threshold: float,
        document_ids: list[str] | None = None,
        metadata_filter: dict[str, Any] | None = None
    ) -> list[tuple[DocumentChunk, float]]:
        """Perform similarity search using PGVector.

        Args:
            query_embedding: Query embedding vector
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            document_ids: Filter by document IDs
            metadata_filter: Filter by metadata

        Returns:
            List of (chunk, similarity_score) tuples
        """
        try:
            # Build query with similarity calculation
            query = select(
                DocumentChunk,
                (1 - DocumentChunk.embedding.cosine_distance(query_embedding)).label("similarity")
            ).where(
                DocumentChunk.embedding.is_not(None)
            )

            # Add filters
            if document_ids:
                query = query.where(DocumentChunk.document_id.in_(document_ids))

            if metadata_filter:
                # Add metadata filters (this is a simplified version)
                for key, value in metadata_filter.items():
                    query = query.where(
                        DocumentChunk.extra_metadata[key].astext == str(value)
                    )

            # Add similarity threshold and ordering
            query = query.where(
                (1 - DocumentChunk.embedding.cosine_distance(query_embedding)) >= score_threshold
            ).order_by(
                (1 - DocumentChunk.embedding.cosine_distance(query_embedding)).desc()
            ).limit(limit)

            # Execute query
            result = await self.session.execute(query)
            results = result.all()

            logger.debug(
                "PGVector similarity search completed",
                results_count=len(results),
                limit=limit,
                threshold=score_threshold
            )

            return [(chunk, float(similarity)) for chunk, similarity in results]

        except Exception as e:
            logger.error("PGVector similarity search failed", error=str(e))
            return []

    async def _json_similarity_search(
        self,
        query_embedding: list[float],
        limit: int,
        score_threshold: float,
        document_ids: list[str] | None = None,
        metadata_filter: dict[str, Any] | None = None
    ) -> list[tuple[DocumentChunk, float]]:
        """Perform similarity search using JSON embeddings (fallback).

        Args:
            query_embedding: Query embedding vector
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            document_ids: Filter by document IDs
            metadata_filter: Filter by metadata

        Returns:
            List of (chunk, similarity_score) tuples
        """
        try:
            # Get chunks with embeddings
            query = select(DocumentChunk).where(
                DocumentChunk.embedding.is_not(None)
            )

            # Add filters
            if document_ids:
                query = query.where(DocumentChunk.document_id.in_(document_ids))

            if metadata_filter:
                for key, value in metadata_filter.items():
                    query = query.where(
                        DocumentChunk.extra_metadata[key].astext == str(value)
                    )

            result = await self.session.execute(query)
            chunks = result.scalars().all()

            # Calculate similarities in Python
            results = []
            for chunk in chunks:
                try:
                    # Parse JSON embedding
                    chunk_embedding = json.loads(chunk.embedding)

                    # Calculate cosine similarity
                    similarity = self._cosine_similarity(query_embedding, chunk_embedding)

                    if similarity >= score_threshold:
                        results.append((chunk, similarity))

                except (json.JSONDecodeError, TypeError):
                    logger.warning("Invalid embedding format", chunk_id=chunk.id)
                    continue

            # Sort by similarity and limit
            results.sort(key=lambda x: x[1], reverse=True)
            results = results[:limit]

            logger.debug(
                "JSON similarity search completed",
                results_count=len(results),
                limit=limit,
                threshold=score_threshold
            )

            return results

        except Exception as e:
            logger.error("JSON similarity search failed", error=str(e))
            return []

    def _cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """Calculate cosine similarity between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Cosine similarity score
        """
        try:
            import math

            if len(vec1) != len(vec2):
                return 0.0

            # Calculate dot product
            dot_product = sum(a * b for a, b in zip(vec1, vec2, strict=False))

            # Calculate magnitudes
            magnitude1 = math.sqrt(sum(a * a for a in vec1))
            magnitude2 = math.sqrt(sum(b * b for b in vec2))

            if magnitude1 == 0.0 or magnitude2 == 0.0:
                return 0.0

            return dot_product / (magnitude1 * magnitude2)

        except Exception:
            return 0.0

    async def hybrid_search(
        self,
        query_embedding: list[float],
        text_query: str,
        limit: int = 10,
        score_threshold: float = 0.5,
        document_ids: list[str] | None = None,
        semantic_weight: float = 0.7,
        text_weight: float = 0.3
    ) -> list[tuple[DocumentChunk, float]]:
        """Perform hybrid search combining semantic and text search.

        Args:
            query_embedding: Query embedding vector
            text_query: Text query for keyword search
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            document_ids: Filter by document IDs
            semantic_weight: Weight for semantic similarity
            text_weight: Weight for text similarity

        Returns:
            List of (chunk, combined_score) tuples
        """
        try:
            # Perform semantic search
            semantic_results = await self.similarity_search(
                query_embedding, limit * 2, score_threshold * 0.5, document_ids
            )

            # Perform text search (using LIKE for simplicity)
            text_query_words = text_query.lower().split()
            text_query_obj = select(DocumentChunk)

            if document_ids:
                text_query_obj = text_query_obj.where(DocumentChunk.document_id.in_(document_ids))

            # Simple text matching (can be enhanced with full-text search)
            for word in text_query_words:
                text_query_obj = text_query_obj.where(
                    func.lower(DocumentChunk.content).contains(word)
                )

            text_result = await self.session.execute(text_query_obj.limit(limit * 2))
            text_chunks = text_result.scalars().all()

            # Combine results
            combined_scores = {}

            # Add semantic scores
            for chunk, score in semantic_results:
                combined_scores[chunk.id] = {
                    'chunk': chunk,
                    'semantic_score': score,
                    'text_score': 0.0
                }

            # Add text scores
            for chunk in text_chunks:
                text_score = self._calculate_text_score(chunk.content, text_query)

                if chunk.id in combined_scores:
                    combined_scores[chunk.id]['text_score'] = text_score
                else:
                    combined_scores[chunk.id] = {
                        'chunk': chunk,
                        'semantic_score': 0.0,
                        'text_score': text_score
                    }

            # Calculate combined scores
            results = []
            for chunk_data in combined_scores.values():
                combined_score = (
                    semantic_weight * chunk_data['semantic_score'] +
                    text_weight * chunk_data['text_score']
                )

                if combined_score >= score_threshold:
                    results.append((chunk_data['chunk'], combined_score))

            # Sort by combined score and limit
            results.sort(key=lambda x: x[1], reverse=True)
            results = results[:limit]

            logger.debug(
                "Hybrid search completed",
                results_count=len(results),
                semantic_results=len(semantic_results),
                text_results=len(text_chunks),
                limit=limit
            )

            return results

        except Exception as e:
            logger.error("Hybrid search failed", error=str(e))
            return []

    def _calculate_text_score(self, content: str, query: str) -> float:
        """Calculate text similarity score.

        Args:
            content: Text content
            query: Search query

        Returns:
            Text similarity score (0.0 to 1.0)
        """
        try:
            content_lower = content.lower()
            query_lower = query.lower()
            query_words = query_lower.split()

            if not query_words:
                return 0.0

            # Simple scoring based on word matches
            matches = 0
            for word in query_words:
                if word in content_lower:
                    matches += 1

            return matches / len(query_words)

        except Exception:
            return 0.0

    async def get_embedding_stats(self) -> dict[str, Any]:
        """Get embedding statistics.

        Returns:
            Dictionary with embedding statistics
        """
        try:
            # Count total chunks
            total_result = await self.session.execute(
                select(func.count(DocumentChunk.id))
            )
            total_chunks = total_result.scalar()

            # Count chunks with embeddings
            embedded_result = await self.session.execute(
                select(func.count(DocumentChunk.id)).where(
                    DocumentChunk.embedding.is_not(None)
                )
            )
            embedded_chunks = embedded_result.scalar()

            # Get embedding models used
            models_result = await self.session.execute(
                select(
                    DocumentChunk.embedding_model,
                    func.count(DocumentChunk.id)
                ).where(
                    DocumentChunk.embedding_model.is_not(None)
                ).group_by(DocumentChunk.embedding_model)
            )
            models_stats = dict(models_result.all())

            return {
                "total_chunks": total_chunks,
                "embedded_chunks": embedded_chunks,
                "embedding_coverage": embedded_chunks / total_chunks if total_chunks > 0 else 0.0,
                "models_used": models_stats,
                "vector_store_type": self.store_type,
                "pgvector_available": PGVECTOR_AVAILABLE,
            }

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


class VectorStoreError(Exception):
    """Vector store operation error."""
    pass
