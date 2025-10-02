"""Custom retriever that works with document_chunks table."""

from typing import Any

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from chatter.utils.database import get_session_generator
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class DocumentChunkRetriever:
    """Custom retriever that queries document_chunks table directly."""
    
    def __init__(
        self,
        embeddings: Embeddings,
        user_id: str | None = None,
        document_ids: list[str] | None = None,
        k: int = 5,
    ):
        """Initialize the retriever.
        
        Args:
            embeddings: Embeddings provider to encode queries
            user_id: Optional user ID filter
            document_ids: Optional document IDs filter
            k: Number of documents to retrieve
        """
        self.embeddings = embeddings
        self.user_id = user_id
        self.document_ids = document_ids
        self.k = k
        
    async def ainvoke(self, query: str, **kwargs: Any) -> list[Document]:
        """Retrieve documents for the query.
        
        Args:
            query: Query string
            **kwargs: Additional arguments
            
        Returns:
            List of relevant documents
        """
        try:
            logger.info(
                f"DocumentChunkRetriever retrieving for query",
                query=query[:100],
                user_id=self.user_id,
                document_ids=self.document_ids,
                k=self.k,
            )
            
            # Generate query embedding
            query_embedding = await self.embeddings.aembed_query(query)
            
            logger.info(
                f"Generated query embedding",
                embedding_dim=len(query_embedding),
            )
            
            # Get database session
            async for session in get_session_generator():
                # Use SimpleVectorStore to search
                from chatter.core.embedding_pipeline import SimpleVectorStore
                
                vector_store = SimpleVectorStore(session)
                results = await vector_store.search_similar(
                    query_embedding=query_embedding,
                    limit=self.k,
                    document_ids=self.document_ids,
                    prefer_exact_match=True,
                )
                
                logger.info(
                    f"SimpleVectorStore returned results",
                    result_count=len(results),
                )
                
                # Convert to langchain Document format
                documents = []
                for chunk, score in results:
                    doc = Document(
                        page_content=chunk.content,
                        metadata={
                            "document_id": chunk.document_id,
                            "chunk_index": chunk.chunk_index,
                            "score": float(score),
                            "user_id": self.user_id,
                        }
                    )
                    documents.append(doc)
                
                logger.info(
                    f"DocumentChunkRetriever returning documents",
                    doc_count=len(documents),
                )
                
                return documents
                
        except Exception as e:
            logger.error(f"DocumentChunkRetriever failed: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []
