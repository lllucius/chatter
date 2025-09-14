"""Clean, simplified document embedding pipeline.

This module provides a single, clean interface for the entire document embedding process:
1. Document text extraction
2. Text chunking  
3. Embedding generation
4. Vector storage

NO backwards compatibility - completely new implementation.
"""

import asyncio
import hashlib
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, AsyncContextManager

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.config import settings
from chatter.core.model_registry import ModelRegistryService
from chatter.models.document import Document, DocumentChunk, DocumentStatus, DocumentType, HybridVectorSearchHelper
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class EmbeddingPipelineError(Exception):
    """Error in the embedding pipeline."""
    pass


class DocumentTextExtractor:
    """Handles text extraction from various document formats."""
    
    async def extract_text(self, document: Document, file_content: bytes) -> str:
        """Extract text from document content.
        
        Args:
            document: Document model instance
            file_content: Raw file bytes
            
        Returns:
            Extracted text content
            
        Raises:
            EmbeddingPipelineError: If text extraction fails
        """
        try:
            if document.document_type == DocumentType.TEXT:
                return await self._extract_text_plain(file_content)
            elif document.document_type == DocumentType.PDF:
                return await self._extract_text_pdf(file_content)
            elif document.document_type in [DocumentType.DOC, DocumentType.DOCX]:
                return await self._extract_text_docx(file_content)
            elif document.document_type == DocumentType.HTML:
                return await self._extract_text_html(file_content)
            elif document.document_type == DocumentType.MARKDOWN:
                return await self._extract_text_markdown(file_content)
            elif document.document_type == DocumentType.JSON:
                return await self._extract_text_json(file_content)
            else:
                # Try unstructured as fallback
                return await self._extract_text_unstructured(file_content)
                
        except Exception as e:
            logger.error("Text extraction failed", document_id=document.id, error=str(e))
            raise EmbeddingPipelineError(f"Failed to extract text: {e}") from e
    
    async def _extract_text_plain(self, content: bytes) -> str:
        """Extract from plain text files."""
        for encoding in ["utf-8", "latin-1", "cp1252"]:
            try:
                return content.decode(encoding)
            except UnicodeDecodeError:
                continue
        raise EmbeddingPipelineError("Could not decode text file with any encoding")
    
    async def _extract_text_pdf(self, content: bytes) -> str:
        """Extract from PDF files."""
        # Offload to thread pool
        return await asyncio.to_thread(self._extract_pdf_sync, content)
        
    def _extract_pdf_sync(self, content: bytes) -> str:
        """Sync PDF extraction in thread."""
        try:
            from pypdf import PdfReader
            import io
            
            reader = PdfReader(io.BytesIO(content))
            text_parts = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            return "\n".join(text_parts)
        except ImportError:
            raise EmbeddingPipelineError("pypdf not available for PDF extraction")
        except Exception as e:
            raise EmbeddingPipelineError(f"PDF extraction failed: {e}")
    
    async def _extract_text_docx(self, content: bytes) -> str:
        """Extract from DOCX files."""
        return await asyncio.to_thread(self._extract_docx_sync, content)
        
    def _extract_docx_sync(self, content: bytes) -> str:
        """Sync DOCX extraction in thread."""
        try:
            from unstructured.partition.docx import partition_docx
            import io
            
            with tempfile.NamedTemporaryFile() as tmp:
                tmp.write(content)
                tmp.flush()
                elements = partition_docx(filename=tmp.name)
                return "\n".join([e.text for e in elements if hasattr(e, 'text')])
        except ImportError:
            raise EmbeddingPipelineError("unstructured not available for DOCX extraction")
        except Exception as e:
            raise EmbeddingPipelineError(f"DOCX extraction failed: {e}")
    
    async def _extract_text_html(self, content: bytes) -> str:
        """Extract from HTML files."""
        try:
            from unstructured.partition.html import partition_html
            
            html_text = content.decode("utf-8", errors="ignore")
            elements = partition_html(text=html_text)
            return "\n".join([e.text for e in elements if hasattr(e, 'text')])
        except ImportError:
            raise EmbeddingPipelineError("unstructured not available for HTML extraction")
        except Exception as e:
            raise EmbeddingPipelineError(f"HTML extraction failed: {e}")
    
    async def _extract_text_markdown(self, content: bytes) -> str:
        """Extract from Markdown files."""
        return content.decode("utf-8", errors="ignore")
    
    async def _extract_text_json(self, content: bytes) -> str:
        """Extract from JSON files."""
        return await asyncio.to_thread(self._extract_json_sync, content)
        
    def _extract_json_sync(self, content: bytes) -> str:
        """Sync JSON extraction in thread."""
        try:
            import json
            
            data = json.loads(content.decode("utf-8"))
            
            def extract_text_recursive(obj):
                if isinstance(obj, str):
                    return obj
                elif isinstance(obj, dict):
                    return " ".join(extract_text_recursive(v) for v in obj.values())
                elif isinstance(obj, list):
                    return " ".join(extract_text_recursive(item) for item in obj)
                else:
                    return str(obj)
            
            return extract_text_recursive(data)
        except Exception as e:
            raise EmbeddingPipelineError(f"JSON extraction failed: {e}")
    
    async def _extract_text_unstructured(self, content: bytes) -> str:
        """Extract using unstructured library as fallback."""
        return await asyncio.to_thread(self._extract_unstructured_sync, content)
        
    def _extract_unstructured_sync(self, content: bytes) -> str:
        """Sync unstructured extraction in thread."""
        try:
            from unstructured.partition.auto import partition
            
            with tempfile.NamedTemporaryFile() as tmp:
                tmp.write(content)
                tmp.flush()
                elements = partition(filename=tmp.name)
                return "\n".join([e.text for e in elements if hasattr(e, 'text')])
        except ImportError:
            raise EmbeddingPipelineError("unstructured not available")
        except Exception as e:
            raise EmbeddingPipelineError(f"Unstructured extraction failed: {e}")


class DocumentChunker:
    """Handles intelligent text chunking."""
    
    def create_chunks(self, document: Document, text: str) -> list[str]:
        """Create text chunks from extracted text.
        
        Args:
            document: Document model instance
            text: Extracted text content
            
        Returns:
            List of text chunks
        """
        try:
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            
            # Choose separators based on document type
            if document.document_type == DocumentType.MARKDOWN:
                separators = ["\n# ", "\n## ", "\n### ", "\n\n", "\n", ".", " "]
            elif document.document_type == DocumentType.HTML:
                separators = ["\n\n", "\n", "<p>", "<div>", "<br>", ".", " "]
            else:
                separators = ["\n\n", "\n", ".", "!", "?", " "]
            
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=document.chunk_size,
                chunk_overlap=document.chunk_overlap,
                separators=separators
            )
            
            chunks = splitter.split_text(text)
            
            # Filter out very short chunks
            min_length = max(50, document.chunk_size // 10)
            filtered_chunks = [
                chunk.strip() for chunk in chunks 
                if len(chunk.strip()) >= min_length
            ]
            
            logger.debug(
                "Created text chunks",
                document_id=document.id,
                total_chunks=len(filtered_chunks),
                chunk_size=document.chunk_size
            )
            
            return filtered_chunks
            
        except Exception as e:
            logger.error("Chunk creation failed", document_id=document.id, error=str(e))
            raise EmbeddingPipelineError(f"Failed to create chunks: {e}") from e


class SimpleEmbeddingService:
    """Simple embedding service using model registry."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.registry = ModelRegistryService(session)
        
    async def generate_embeddings(self, texts: list[str]) -> tuple[list[list[float]], dict[str, Any]]:
        """Generate embeddings for texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            Tuple of (embeddings, metadata)
            
        Raises:
            EmbeddingPipelineError: If embedding generation fails
        """
        try:
            # Get default embedding provider
            provider = await self.registry.get_default_provider(model_type="embedding")
            if not provider:
                raise EmbeddingPipelineError("No default embedding provider configured")
            
            # Get default embedding model
            models, _ = await self.registry.list_models(provider.id, model_type="embedding")
            model = next((m for m in models if m.is_default and m.is_active), None)
            if not model:
                model = next((m for m in models if m.is_active), None)
            if not model:
                raise EmbeddingPipelineError(f"No active embedding model for provider {provider.name}")
            
            # Create embedding instance
            embedding_instance = await self._create_embedding_instance(provider, model)
            if not embedding_instance:
                raise EmbeddingPipelineError(f"Failed to create embedding instance for {provider.name}")
            
            # Generate embeddings
            embeddings = await embedding_instance.aembed_documents(texts)
            
            metadata = {
                "provider": provider.name,
                "model": model.model_name,
                "dimensions": len(embeddings[0]) if embeddings else 0,
                "text_count": len(texts)
            }
            
            logger.info(
                "Generated embeddings",
                provider=provider.name,
                model=model.model_name,
                text_count=len(texts),
                dimensions=metadata["dimensions"]
            )
            
            return embeddings, metadata
            
        except Exception as e:
            logger.error("Embedding generation failed", error=str(e))
            raise EmbeddingPipelineError(f"Failed to generate embeddings: {e}") from e
    
    async def _create_embedding_instance(self, provider, model):
        """Create embedding provider instance."""
        import os
        from chatter.models.registry import ProviderType
        
        try:
            if provider.provider_type == ProviderType.OPENAI:
                from langchain_openai import OpenAIEmbeddings
                
                api_key = (
                    provider.default_config.get("api_key") 
                    or os.getenv("OPENAI_API_KEY")
                )
                if not api_key:
                    return None
                
                return OpenAIEmbeddings(
                    api_key=api_key,
                    base_url=provider.base_url,
                    model=model.model_name,
                    chunk_size=model.chunk_size or 1000
                )
            
            # Add other providers as needed
            return None
            
        except Exception as e:
            logger.error("Failed to create embedding instance", error=str(e))
            return None


class SimpleVectorStore:
    """Simple vector store using direct PGVector."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def store_embeddings(
        self, 
        chunks: list[DocumentChunk], 
        embeddings: list[list[float]], 
        metadata: dict[str, Any]
    ) -> bool:
        """Store embeddings for chunks using hybrid vector storage.
        
        Args:
            chunks: Document chunks
            embeddings: Corresponding embeddings
            metadata: Embedding metadata
            
        Returns:
            True if successful
        """
        try:
            # Update chunks with embeddings using the new hybrid system
            for chunk, embedding in zip(chunks, embeddings, strict=True):
                # Use the new set_embedding_vector method which triggers event listeners
                chunk.set_embedding_vector(
                    vector=embedding,
                    provider=metadata.get("provider"),
                    model=metadata.get("model")
                )
                
            await self.session.commit()
            
            # Refresh chunks to get updated data
            for chunk in chunks:
                await self.session.refresh(chunk)
                
            logger.info(
                "Stored embeddings using hybrid vector system",
                chunk_count=len(chunks),
                provider=metadata.get("provider"),
                dimensions=metadata.get("dimensions"),
                hybrid_columns=["embedding", "raw_embedding", "computed_embedding"]
            )
            
            return True
            
        except Exception as e:
            await self.session.rollback()
            logger.error("Failed to store embeddings", error=str(e))
            return False
    
    async def search_similar(
        self, 
        query_embedding: list[float], 
        limit: int = 10,
        document_ids: list[str] | None = None,
        prefer_exact_match: bool = True
    ) -> list[tuple[DocumentChunk, float]]:
        """Search for similar chunks using hybrid vector search.
        
        Args:
            query_embedding: Query embedding vector
            limit: Maximum results
            document_ids: Optional document ID filter
            prefer_exact_match: Whether to prefer exact dimension matches
            
        Returns:
            List of (chunk, similarity_score) tuples
        """
        try:
            # Use hybrid search helper to choose optimal column
            search_helper = HybridVectorSearchHelper()
            search_column = search_helper.choose_search_column(
                query_embedding, prefer_exact_match
            )
            prepared_query = search_helper.prepare_query_vector(
                query_embedding, search_column
            )
            
            logger.debug(
                "Hybrid vector search initiated",
                query_dim=len(query_embedding),
                search_column=search_column,
                prepared_dim=len(prepared_query)
            )
            
            # Build base query
            query = select(DocumentChunk)
            
            # Apply document filter if provided
            if document_ids:
                query = query.where(DocumentChunk.document_id.in_(document_ids))
            
            # Apply dimension filter for exact matches
            if prefer_exact_match and search_column == 'raw_embedding':
                query = query.where(DocumentChunk.raw_dim == len(query_embedding))
            
            # Filter out chunks without the required embedding column
            if search_column == 'embedding':
                query = query.where(DocumentChunk.embedding.is_not(None))
            elif search_column == 'computed_embedding':
                query = query.where(DocumentChunk.computed_embedding.is_not(None))
            elif search_column == 'raw_embedding':
                query = query.where(DocumentChunk.raw_embedding.is_not(None))
            
            # Add vector similarity ordering using the appropriate column
            if search_column == 'embedding':
                query = query.order_by(
                    DocumentChunk.embedding.cosine_distance(prepared_query)
                ).limit(limit)
            elif search_column == 'computed_embedding':
                query = query.order_by(
                    DocumentChunk.computed_embedding.cosine_distance(prepared_query)
                ).limit(limit)
            else:
                # For raw_embedding, we need to use a different approach since it's JSON
                # Fall back to computed_embedding for consistent indexing
                logger.debug("Falling back to computed_embedding for raw_embedding search")
                query = query.where(DocumentChunk.computed_embedding.is_not(None))
                query = query.order_by(
                    DocumentChunk.computed_embedding.cosine_distance(prepared_query)
                ).limit(limit)
            
            result = await self.session.execute(query)
            chunks = result.scalars().all()
            
            # Calculate similarity scores using the appropriate embedding
            results = []
            for chunk in chunks:
                embedding_vector = None
                
                if search_column == 'embedding' and chunk.embedding:
                    embedding_vector = chunk.embedding
                elif search_column == 'computed_embedding' and chunk.computed_embedding:
                    embedding_vector = chunk.computed_embedding
                elif search_column == 'raw_embedding' and chunk.raw_embedding:
                    embedding_vector = chunk.raw_embedding
                elif chunk.computed_embedding:
                    # Fallback to computed_embedding
                    embedding_vector = chunk.computed_embedding
                
                if embedding_vector:
                    # Calculate cosine similarity
                    import numpy as np
                    
                    chunk_vec = np.array(embedding_vector)
                    query_vec = np.array(prepared_query)
                    
                    # Ensure vectors have the same dimension for similarity calculation
                    if len(chunk_vec) != len(query_vec):
                        if search_column == 'raw_embedding':
                            # Use original query for raw embedding comparison
                            query_vec = np.array(query_embedding)
                            if len(chunk_vec) != len(query_vec):
                                continue  # Skip mismatched dimensions
                        else:
                            continue  # Skip mismatched dimensions
                    
                    # Cosine similarity
                    similarity = np.dot(chunk_vec, query_vec) / (
                        np.linalg.norm(chunk_vec) * np.linalg.norm(query_vec)
                    )
                    
                    results.append((chunk, float(similarity)))
            
            logger.debug(
                "Hybrid vector search completed",
                results_count=len(results),
                search_column=search_column
            )
            return results
            
        except Exception as e:
            logger.error("Hybrid vector search failed", error=str(e))
            return []


class EmbeddingPipeline:
    """Main embedding pipeline coordinator."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.text_extractor = DocumentTextExtractor()
        self.chunker = DocumentChunker()
        self.embedding_service = SimpleEmbeddingService(session)
        self.vector_store = SimpleVectorStore(session)
        
    async def process_document(self, document_id: str, file_content: bytes) -> bool:
        """Process a document through the complete embedding pipeline.
        
        Args:
            document_id: Document ID to process
            file_content: Raw file content
            
        Returns:
            True if successful
        """
        try:
            # Get document
            result = await self.session.execute(
                select(Document).where(Document.id == document_id)
            )
            document = result.scalar_one_or_none()
            if not document:
                raise EmbeddingPipelineError(f"Document {document_id} not found")
            
            # Update status
            document.status = DocumentStatus.PROCESSING
            document.processing_started_at = datetime.now(UTC)
            document.processing_error = None
            await self.session.commit()
            
            logger.info("Starting document processing", document_id=document_id)
            
            # Step 1: Extract text
            text = await self.text_extractor.extract_text(document, file_content)
            if not text.strip():
                raise EmbeddingPipelineError("No text extracted from document")
            
            document.extracted_text = text
            await self.session.commit()
            
            # Step 2: Create chunks
            chunk_texts = self.chunker.create_chunks(document, text)
            if not chunk_texts:
                raise EmbeddingPipelineError("No chunks created from text")
            
            # Step 3: Store chunks in database
            chunks = []
            for i, chunk_text in enumerate(chunk_texts):
                chunk = DocumentChunk(
                    document_id=document.id,
                    content=chunk_text,
                    chunk_index=i,
                    content_hash=hashlib.sha256(chunk_text.encode()).hexdigest(),
                    token_count=len(chunk_text.split())  # Simple approximation
                )
                chunks.append(chunk)
                self.session.add(chunk)
            
            await self.session.commit()
            
            # Refresh chunks to get IDs
            for chunk in chunks:
                await self.session.refresh(chunk)
            
            # Step 4: Generate embeddings
            embeddings, metadata = await self.embedding_service.generate_embeddings(chunk_texts)
            
            # Step 5: Store embeddings
            success = await self.vector_store.store_embeddings(chunks, embeddings, metadata)
            if not success:
                raise EmbeddingPipelineError("Failed to store embeddings")
            
            # Update document status
            document.status = DocumentStatus.PROCESSED
            document.processing_completed_at = datetime.now(UTC)
            document.chunk_count = len(chunks)
            await self.session.commit()
            
            logger.info(
                "Document processing completed",
                document_id=document_id,
                chunks=len(chunks),
                text_length=len(text)
            )
            
            return True
            
        except Exception as e:
            # Mark as failed
            try:
                document.status = DocumentStatus.FAILED
                document.processing_completed_at = datetime.now(UTC)
                document.processing_error = str(e)
                await self.session.commit()
            except Exception:
                pass  # Don't fail if we can't update status
            
            logger.error("Document processing failed", document_id=document_id, error=str(e))
            return False
    
    async def search_documents(
        self, 
        query: str, 
        limit: int = 10,
        document_ids: list[str] | None = None,
        prefer_exact_match: bool = True
    ) -> list[tuple[DocumentChunk, float]]:
        """Search documents using hybrid semantic similarity.
        
        Args:
            query: Search query text
            limit: Maximum results
            document_ids: Optional document filter
            prefer_exact_match: Whether to prefer exact dimension matches
            
        Returns:
            List of (chunk, similarity_score) tuples
        """
        try:
            # Generate query embedding
            embeddings, metadata = await self.embedding_service.generate_embeddings([query])
            query_embedding = embeddings[0]
            
            # Search vector store using hybrid search
            results = await self.vector_store.search_similar(
                query_embedding, limit, document_ids, prefer_exact_match
            )
            
            logger.info(
                "Hybrid document search completed", 
                query=query, 
                results=len(results),
                query_dim=len(query_embedding),
                provider=metadata.get("provider")
            )
            return results
            
        except Exception as e:
            logger.error("Hybrid document search failed", query=query, error=str(e))
            return []