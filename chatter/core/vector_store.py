"""Vector store operations and abstractions."""

import asyncio
from abc import ABC, abstractmethod
from typing import Any

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_postgres import PGVector

from chatter.config import settings
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


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
        **kwargs
    ) -> list[str]:
        """Add documents to the vector store."""
        pass

    @abstractmethod
    async def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: dict[str, Any] | None = None,
        **kwargs
    ) -> list[Document]:
        """Perform similarity search."""
        pass

    @abstractmethod
    async def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        filter: dict[str, Any] | None = None,
        **kwargs
    ) -> list[tuple[Document, float]]:
        """Perform similarity search with scores."""
        pass

    @abstractmethod
    async def delete(self, ids: list[str]) -> bool:
        """Delete documents by IDs."""
        pass

    @abstractmethod
    async def update_documents(
        self,
        ids: list[str],
        documents: list[Document]
    ) -> bool:
        """Update documents by IDs."""
        pass


class PGVectorStore(AbstractVectorStore):
    """PostgreSQL + pgvector implementation."""

    def __init__(
        self,
        embeddings: Embeddings,
        collection_name: str = "documents",
        connection_string: str | None = None,
        **kwargs
    ):
        """Initialize PGVector store."""
        self.embeddings = embeddings
        self.collection_name = collection_name
        self.connection_string = connection_string or settings.database_url

        # Remove async driver from connection string for pgvector
        if "+asyncpg" in self.connection_string:
            self.connection_string = self.connection_string.replace("+asyncpg", "")

        self._store = None
        self._initialize_store()

    def _initialize_store(self) -> None:
        """Initialize the PGVector store."""
        try:
            self._store = PGVector(
                embeddings=self.embeddings,
                collection_name=self.collection_name,
                connection_string=self.connection_string,
                use_jsonb=True,
            )
            logger.info("PGVector store initialized", collection=self.collection_name)
        except Exception as e:
            logger.error("Failed to initialize PGVector store", error=str(e))
            raise VectorStoreError(f"PGVector initialization failed: {str(e)}")

    async def add_documents(
        self,
        documents: list[Document],
        embeddings: list[list[float]] | None = None,
        ids: list[str] | None = None,
        **kwargs
    ) -> list[str]:
        """Add documents to PGVector."""
        try:
            if embeddings:
                return await asyncio.to_thread(
                    self._store.add_embeddings,
                    list(zip([doc.page_content for doc in documents], embeddings, strict=False)),
                    [doc.metadata for doc in documents],
                    ids
                )
            else:
                return await asyncio.to_thread(
                    self._store.add_documents,
                    documents,
                    ids
                )
        except Exception as e:
            logger.error("Failed to add documents to PGVector", error=str(e))
            raise VectorStoreError(f"Add documents failed: {str(e)}")

    async def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: dict[str, Any] | None = None,
        **kwargs
    ) -> list[Document]:
        """Perform similarity search in PGVector."""
        try:
            return await asyncio.to_thread(
                self._store.similarity_search,
                query,
                k=k,
                filter=filter,
                **kwargs
            )
        except Exception as e:
            logger.error("Similarity search failed", error=str(e))
            raise VectorStoreError(f"Similarity search failed: {str(e)}")

    async def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        filter: dict[str, Any] | None = None,
        **kwargs
    ) -> list[tuple[Document, float]]:
        """Perform similarity search with scores in PGVector."""
        try:
            return await asyncio.to_thread(
                self._store.similarity_search_with_score,
                query,
                k=k,
                filter=filter,
                **kwargs
            )
        except Exception as e:
            logger.error("Similarity search with score failed", error=str(e))
            raise VectorStoreError(f"Similarity search with score failed: {str(e)}")

    async def delete(self, ids: list[str]) -> bool:
        """Delete documents by IDs."""
        try:
            return await asyncio.to_thread(self._store.delete, ids)
        except Exception as e:
            logger.error("Delete documents failed", error=str(e))
            raise VectorStoreError(f"Delete failed: {str(e)}")

    async def update_documents(
        self,
        ids: list[str],
        documents: list[Document]
    ) -> bool:
        """Update documents by IDs."""
        try:
            # PGVector doesn't have direct update, so delete and re-add
            await self.delete(ids)
            await self.add_documents(documents, ids=ids)
            return True
        except Exception as e:
            logger.error("Update documents failed", error=str(e))
            raise VectorStoreError(f"Update failed: {str(e)}")

    def as_retriever(self, **kwargs) -> Any:
        """Get retriever interface."""
        return self._store.as_retriever(**kwargs)


class ChromaVectorStore(AbstractVectorStore):
    """ChromaDB implementation for development/testing."""

    def __init__(
        self,
        embeddings: Embeddings,
        collection_name: str = "documents",
        persist_directory: str | None = None,
        **kwargs
    ):
        """Initialize Chroma store."""
        self.embeddings = embeddings
        self.collection_name = collection_name
        self.persist_directory = persist_directory

        self._store = None
        self._initialize_store()

    def _initialize_store(self) -> None:
        """Initialize the Chroma store."""
        try:
            self._store = Chroma(
                embedding_function=self.embeddings,
                collection_name=self.collection_name,
                persist_directory=self.persist_directory,
            )
            logger.info("Chroma store initialized", collection=self.collection_name)
        except Exception as e:
            logger.error("Failed to initialize Chroma store", error=str(e))
            raise VectorStoreError(f"Chroma initialization failed: {str(e)}")

    async def add_documents(
        self,
        documents: list[Document],
        embeddings: list[list[float]] | None = None,
        ids: list[str] | None = None,
        **kwargs
    ) -> list[str]:
        """Add documents to Chroma."""
        try:
            return await asyncio.to_thread(
                self._store.add_documents,
                documents,
                ids=ids
            )
        except Exception as e:
            logger.error("Failed to add documents to Chroma", error=str(e))
            raise VectorStoreError(f"Add documents failed: {str(e)}")

    async def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: dict[str, Any] | None = None,
        **kwargs
    ) -> list[Document]:
        """Perform similarity search in Chroma."""
        try:
            return await asyncio.to_thread(
                self._store.similarity_search,
                query,
                k=k,
                filter=filter,
                **kwargs
            )
        except Exception as e:
            logger.error("Similarity search failed", error=str(e))
            raise VectorStoreError(f"Similarity search failed: {str(e)}")

    async def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        filter: dict[str, Any] | None = None,
        **kwargs
    ) -> list[tuple[Document, float]]:
        """Perform similarity search with scores in Chroma."""
        try:
            return await asyncio.to_thread(
                self._store.similarity_search_with_score,
                query,
                k=k,
                filter=filter,
                **kwargs
            )
        except Exception as e:
            logger.error("Similarity search with score failed", error=str(e))
            raise VectorStoreError(f"Similarity search with score failed: {str(e)}")

    async def delete(self, ids: list[str]) -> bool:
        """Delete documents by IDs."""
        try:
            self._store.delete(ids)
            return True
        except Exception as e:
            logger.error("Delete documents failed", error=str(e))
            raise VectorStoreError(f"Delete failed: {str(e)}")

    async def update_documents(
        self,
        ids: list[str],
        documents: list[Document]
    ) -> bool:
        """Update documents by IDs."""
        try:
            # Chroma doesn't have direct update, so delete and re-add
            await self.delete(ids)
            await self.add_documents(documents, ids=ids)
            return True
        except Exception as e:
            logger.error("Update documents failed", error=str(e))
            raise VectorStoreError(f"Update failed: {str(e)}")

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
        **kwargs
    ) -> AbstractVectorStore:
        """Create a vector store instance."""
        store_key = f"{store_type}_{collection_name}"

        if store_key in self._stores:
            return self._stores[store_key]

        if store_type.lower() == "pgvector":
            store = PGVectorStore(
                embeddings=embeddings,
                collection_name=collection_name,
                **kwargs
            )
        elif store_type.lower() == "chroma":
            store = ChromaVectorStore(
                embeddings=embeddings,
                collection_name=collection_name,
                **kwargs
            )
        else:
            raise VectorStoreError(f"Unsupported vector store type: {store_type}") from None

        self._stores[store_key] = store
        return store

    def get_store(self, store_type: str, collection_name: str = "documents") -> AbstractVectorStore | None:
        """Get an existing vector store instance."""
        store_key = f"{store_type}_{collection_name}"
        return self._stores.get(store_key)

    def get_default_store(self, embeddings: Embeddings, **kwargs) -> AbstractVectorStore:
        """Get the default vector store based on configuration."""
        # Prefer PGVector for production, fallback to Chroma for development
        try:
            return self.create_store("pgvector", embeddings, **kwargs)
        except Exception as e:
            logger.warning("Failed to create PGVector store, falling back to Chroma", error=str(e))
            return self.create_store("chroma", embeddings, **kwargs)


# Global vector store manager instance
vector_store_manager = VectorStoreManager()
