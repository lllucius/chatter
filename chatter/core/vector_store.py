"""Vector store operations and abstractions."""

import asyncio
from abc import ABC, abstractmethod
from typing import Any

try:
    from langchain_core.documents import Document
    from langchain_core.embeddings import Embeddings
    from langchain_postgres import PGVector
except ImportError:
    # Fallback classes when langchain is not available
    class Document:
        def __init__(
            self, page_content: str = "", metadata: dict = None
        ):
            self.page_content = page_content
            self.metadata = metadata or {}

    class Embeddings:
        pass

    class PGVector:
        pass


from chatter.config import settings
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class VectorSearchResult:
    """Result from vector search operation."""

    def __init__(
        self, id: str, score: float, document=None, vector=None
    ):
        """Initialize search result."""
        self.id = id
        self.score = score
        self.document = document
        self.vector = vector


class VectorStoreError(Exception):
    """Vector store operation error."""

    pass


class AbstractVectorStore(ABC):
    """Abstract base class for vector store operations."""

    @abstractmethod
    async def add_documents(
        self,
        documents: list[Document],
        embeddings: list[list[float]] | None = None,
        ids: list[str] | None = None,
        **kwargs: Any,
    ) -> list[str]:
        """Add documents to the vector store."""
        pass

    @abstractmethod
    async def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> list[Document]:
        """Perform similarity search."""
        pass

    @abstractmethod
    async def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        filter: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> list[tuple[Document, float]]:
        """Perform similarity search with scores."""
        pass

    @abstractmethod
    async def delete(self, ids: list[str]) -> bool:
        """Delete documents by IDs."""
        pass

    @abstractmethod
    async def update_documents(
        self, ids: list[str], documents: list[Document]
    ) -> bool:
        """Update documents by IDs."""
        pass

    @abstractmethod
    async def advanced_search(
        self,
        query: str | None = None,
        k: int = 4,
        metadata_filter: dict[str, Any] | None = None,
        semantic_filter: str | None = None,
        date_range: tuple[str, str] | None = None,
        content_type: str | None = None,
        similarity_threshold: float = 0.0,
        **kwargs: Any,
    ) -> list[tuple[Document, float]]:
        """Perform advanced search with multiple filter types."""
        pass

    @abstractmethod
    async def get_document_metadata(
        self, doc_id: str
    ) -> dict[str, Any] | None:
        """Get metadata for a specific document."""
        pass

    @abstractmethod
    async def query_metadata(
        self,
        metadata_query: dict[str, Any],
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Query documents by metadata only."""
        pass

    @abstractmethod
    async def get_similar_documents_by_metadata(
        self,
        reference_metadata: dict[str, Any],
        k: int = 4,
        exclude_ids: list[str] | None = None,
    ) -> list[Document]:
        """Find documents with similar metadata patterns."""
        pass


class PGVectorStore(AbstractVectorStore):
    """PostgreSQL + pgvector implementation."""

    def __init__(
        self,
        embeddings: Embeddings,
        collection_name: str = "documents",
        connection_string: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize PGVector store."""
        self.embeddings = embeddings
        self.collection_name = collection_name
        self.connection_string = (
            connection_string or settings.database_url
        )

        # Keep async driver for async mode, remove it only for sync mode
        # Since we're now using async_mode=True, we need the async driver
        if "+asyncpg" not in self.connection_string:
            # Ensure we have the async driver for async mode
            self.connection_string = self.connection_string.replace(
                "postgresql://", "postgresql+asyncpg://"
            )

        # Set query-time accuracy/speed. Higher = more accurate, slower.
        # (This should be made configurable per workflow.)
        # Note: asyncpg doesn't support options in connection string, so skip for async mode
        if "+asyncpg" not in self.connection_string:
            self.connection_string += (
                "?options=-c%20hnsw.ef_search%3D60"
            )

        self._store: PGVector | None = None
        self._initialize_store()

    def _initialize_store(self) -> None:
        """Initialize the PGVector store."""
        try:
            # Set create_extension=False to prevent langchain-postgres from
            # concatenating advisory lock and CREATE EXTENSION statements,
            # which causes PostgreSQL syntax errors. The extension should be
            # created separately during database initialization.
            self._store = PGVector(
                embeddings=self.embeddings,
                collection_name=self.collection_name,
                connection=self.connection_string,
                use_jsonb=True,
                async_mode=True,
                create_extension=False,  # Prevent SQL concatenation issues
            )
            logger.info(
                "PGVector store initialized",
                collection=self.collection_name,
            )
        except Exception as e:
            logger.error(
                "Failed to initialize PGVector store", error=str(e)
            )
            raise VectorStoreError(
                f"PGVector initialization failed: {str(e)}"
            ) from e

    async def add_documents(
        self,
        documents: list[Document],
        embeddings: list[list[float]] | None = None,
        ids: list[str] | None = None,
        **kwargs: Any,
    ) -> list[str]:
        """Add documents to PGVector."""
        try:
            assert (
                self._store is not None
            ), "PGVector store not initialized"
            if embeddings:
                return await asyncio.to_thread(
                    self._store.add_embeddings,
                    list(
                        zip(  # type: ignore # Complex langchain integration
                            [doc.page_content for doc in documents],
                            embeddings,
                            strict=False,
                        )
                    ),
                    [doc.metadata for doc in documents],
                    ids,  # type: ignore # Complex langchain parameter handling
                )
            else:
                assert (
                    self._store is not None
                ), "PGVector store not initialized"
                return await asyncio.to_thread(
                    self._store.add_documents, documents, ids  # type: ignore # Complex langchain parameter handling
                )
        except Exception as e:
            logger.error(
                "Failed to add documents to PGVector", error=str(e)
            )
            raise VectorStoreError(
                f"Add documents failed: {str(e)}"
            ) from e

    async def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: dict[str, Any] | None = None,
        **kwargs,
    ) -> list[Document]:
        """Perform similarity search in PGVector."""
        try:
            return await asyncio.to_thread(
                self._store.similarity_search,
                query,
                k=k,
                filter=filter,
                **kwargs,
            )
        except Exception as e:
            logger.error("Similarity search failed", error=str(e))
            raise VectorStoreError(
                f"Similarity search failed: {str(e)}"
            ) from e

    async def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        filter: dict[str, Any] | None = None,
        **kwargs,
    ) -> list[tuple[Document, float]]:
        """Perform similarity search with scores in PGVector."""
        try:
            return await asyncio.to_thread(
                self._store.similarity_search_with_score,
                query,
                k=k,
                filter=filter,
                **kwargs,
            )
        except Exception as e:
            logger.error(
                "Similarity search with score failed", error=str(e)
            )
            raise VectorStoreError(
                f"Similarity search with score failed: {str(e)}"
            ) from e

    async def delete(self, ids: list[str]) -> bool:
        """Delete documents by IDs."""
        try:
            return await asyncio.to_thread(self._store.delete, ids)
        except Exception as e:
            logger.error("Delete documents failed", error=str(e))
            raise VectorStoreError(f"Delete failed: {str(e)}") from e

    async def update_documents(
        self, ids: list[str], documents: list[Document]
    ) -> bool:
        """Update documents by IDs."""
        try:
            # PGVector doesn't have direct update, so delete and re-add
            await self.delete(ids)
            await self.add_documents(documents, ids=ids)
            return True
        except Exception as e:
            logger.error("Update documents failed", error=str(e))
            raise VectorStoreError(f"Update failed: {str(e)}") from e

    async def advanced_search(
        self,
        query: str | None = None,
        k: int = 4,
        metadata_filter: dict[str, Any] | None = None,
        semantic_filter: str | None = None,
        date_range: tuple[str, str] | None = None,
        content_type: str | None = None,
        similarity_threshold: float = 0.0,
        **kwargs: Any,
    ) -> list[tuple[Document, float]]:
        """Perform advanced search with multiple filter types."""
        try:
            # Build complex filter
            combined_filter = {}

            if metadata_filter:
                combined_filter.update(metadata_filter)

            if date_range:
                start_date, end_date = date_range
                combined_filter["created_at"] = {
                    "$gte": start_date,
                    "$lte": end_date,
                }

            if content_type:
                combined_filter["content_type"] = content_type

            if semantic_filter:
                combined_filter["semantic_tags"] = {
                    "$contains": semantic_filter
                }

            # If no query provided, use metadata-only search
            if not query:
                # For metadata-only search, we need to get all documents and filter
                docs_with_scores = await asyncio.to_thread(
                    self._store.similarity_search_with_score,
                    "retrieving documents",  # dummy query
                    k=k * 10,  # Get more to filter properly
                    filter=combined_filter,
                    **kwargs,
                )
                # Filter by similarity threshold and limit results
                filtered_docs = [
                    (doc, score)
                    for doc, score in docs_with_scores
                    if score >= similarity_threshold
                ]
                return filtered_docs[:k]
            else:
                # Standard similarity search with filters
                docs_with_scores = await asyncio.to_thread(
                    self._store.similarity_search_with_score,
                    query,
                    k=k,
                    filter=combined_filter,
                    **kwargs,
                )
                # Filter by similarity threshold
                return [
                    (doc, score)
                    for doc, score in docs_with_scores
                    if score >= similarity_threshold
                ]

        except Exception as e:
            logger.error("Advanced search failed", error=str(e))
            raise VectorStoreError(
                f"Advanced search failed: {str(e)}"
            ) from e

    async def get_document_metadata(
        self, doc_id: str
    ) -> dict[str, Any] | None:
        """Get metadata for a specific document."""
        try:
            # Search for document by ID in metadata
            results = await asyncio.to_thread(
                self._store.similarity_search,
                "",  # Empty query, rely on filter
                k=1,
                filter={"id": doc_id},
            )

            if results:
                return results[0].metadata
            return None

        except Exception as e:
            logger.error("Get document metadata failed", error=str(e))
            return None

    async def query_metadata(
        self,
        metadata_query: dict[str, Any],
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Query documents by metadata only."""
        try:
            results = await asyncio.to_thread(
                self._store.similarity_search,
                "",  # Empty query, rely on filter
                k=limit,
                filter=metadata_query,
            )

            return [doc.metadata for doc in results]

        except Exception as e:
            logger.error("Query metadata failed", error=str(e))
            raise VectorStoreError(
                f"Query metadata failed: {str(e)}"
            ) from e

    async def get_similar_documents_by_metadata(
        self,
        reference_metadata: dict[str, Any],
        k: int = 4,
        exclude_ids: list[str] | None = None,
    ) -> list[Document]:
        """Find documents with similar metadata patterns."""
        try:
            # Build filter to find similar metadata
            # This is a simplified implementation - in a real system you might want
            # more sophisticated metadata similarity matching
            metadata_filter = {}

            # Match on specific important metadata fields
            for key, value in reference_metadata.items():
                if key in [
                    "content_type",
                    "source",
                    "category",
                    "tags",
                ]:
                    metadata_filter[key] = value

            if exclude_ids:
                metadata_filter["id"] = {"$nin": exclude_ids}

            results = await asyncio.to_thread(
                self._store.similarity_search,
                "",  # Empty query, rely on filter
                k=k,
                filter=metadata_filter,
            )

            return results

        except Exception as e:
            logger.error(
                "Get similar documents by metadata failed", error=str(e)
            )
            raise VectorStoreError(
                f"Similar metadata search failed: {str(e)}"
            ) from e

    def as_retriever(self, **kwargs) -> Any:
        """Get retriever interface."""
        return self._store.as_retriever(**kwargs)


class VectorStoreManager:
    """Manager for vector store operations."""

    def __init__(self):
        """Initialize the vector store manager."""
        self._stores: dict[str, AbstractVectorStore] = {}

    def create_store(
        self,
        store_type: str,
        embeddings: Embeddings,
        collection_name: str = "documents",
        **kwargs,
    ) -> AbstractVectorStore:
        """Create a vector store instance."""
        store_key = f"{store_type}_{collection_name}"

        if store_key in self._stores:
            return self._stores[store_key]

        if store_type.lower() == "pgvector":
            store = PGVectorStore(
                embeddings=embeddings,
                collection_name=collection_name,
                **kwargs,
            )
        else:
            raise VectorStoreError(
                f"Unsupported vector store type: {store_type}. Only 'pgvector' is supported."
            ) from None

        self._stores[store_key] = store
        return store

    def get_store(
        self, store_type: str, collection_name: str = "documents"
    ) -> AbstractVectorStore | None:
        """Get an existing vector store instance."""
        store_key = f"{store_type}_{collection_name}"
        return self._stores.get(store_key)

    def get_default_store(
        self, embeddings: Embeddings, **kwargs
    ) -> AbstractVectorStore:
        """Get the default vector store based on configuration."""
        # Use PGVector as the only supported vector store
        return self.create_store("pgvector", embeddings, **kwargs)


# Global vector store manager instance
vector_store_manager = VectorStoreManager()


async def get_vector_store_retriever(
    user_id: str = None, collection_name: str = "documents"
):
    """Get a retriever for vector search operations.

    Args:
        user_id: User ID for personalized retrieval (optional)
        collection_name: Collection name for the vector store

    Returns:
        Retriever instance that can be used with LangChain workflows
    """
    try:
        from chatter.services.embeddings import get_embedding_service

        # Get embedding service
        embedding_service = get_embedding_service()
        embeddings = await embedding_service.get_default_provider()
        
        if not embeddings:
            logger.warning("No default embedding provider available")
            return None

        # Create or get vector store
        store = vector_store_manager.create_store(
            "pgvector", embeddings, collection_name=collection_name
        )

        # Return retriever interface
        if hasattr(store._store, 'as_retriever'):
            return store._store.as_retriever(
                search_kwargs={
                    "k": 5,
                    "filter": {"user_id": user_id} if user_id else None,
                }
            )
        else:
            # Fallback implementation
            logger.warning(
                "Vector store does not support as_retriever, returning None"
            )
            return None

    except Exception as e:
        logger.error(f"Could not create vector store retriever: {e}")
        return None
