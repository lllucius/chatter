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
from chatter.models.document import Document, DocumentChunk, DocumentStatus, DocumentType
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
        """Store embeddings for chunks.
        
        Args:
            chunks: Document chunks
            embeddings: Corresponding embeddings
            metadata: Embedding metadata
            
        Returns:
            True if successful
        """
        try:
            # Update chunks with embeddings
            for chunk, embedding in zip(chunks, embeddings, strict=True):
                chunk.embedding = embedding
                chunk.embedding_provider = metadata.get("provider")
                chunk.embedding_model = metadata.get("model")
                chunk.embedding_dimensions = len(embedding)
                
            await self.session.commit()
            
            # Refresh chunks to get updated data
            for chunk in chunks:
                await self.session.refresh(chunk)
                
            logger.info(
                "Stored embeddings",
                chunk_count=len(chunks),
                provider=metadata.get("provider"),
                dimensions=metadata.get("dimensions")
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
        document_ids: list[str] | None = None
    ) -> list[tuple[DocumentChunk, float]]:
        """Search for similar chunks.
        
        Args:
            query_embedding: Query embedding vector
            limit: Maximum results
            document_ids: Optional document ID filter
            
        Returns:
            List of (chunk, similarity_score) tuples
        """
        try:
            # Build query
            query = select(DocumentChunk).where(DocumentChunk.embedding.is_not(None))
            
            if document_ids:
                query = query.where(DocumentChunk.document_id.in_(document_ids))
            
            # Add vector similarity ordering (requires pgvector extension)
            # Using cosine similarity: 1 - cosine_distance
            query = query.order_by(
                DocumentChunk.embedding.cosine_distance(query_embedding)
            ).limit(limit)
            
            result = await self.session.execute(query)
            chunks = result.scalars().all()
            
            # Calculate similarity scores
            results = []
            for chunk in chunks:
                if chunk.embedding:
                    # Calculate cosine similarity
                    import numpy as np
                    
                    chunk_vec = np.array(chunk.embedding)
                    query_vec = np.array(query_embedding)
                    
                    # Cosine similarity
                    similarity = np.dot(chunk_vec, query_vec) / (
                        np.linalg.norm(chunk_vec) * np.linalg.norm(query_vec)
                    )
                    
                    results.append((chunk, float(similarity)))
            
            logger.debug("Vector search completed", results_count=len(results))
            return results
            
        except Exception as e:
            logger.error("Vector search failed", error=str(e))
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
        document_ids: list[str] | None = None
    ) -> list[tuple[DocumentChunk, float]]:
        """Search documents using semantic similarity.
        
        Args:
            query: Search query text
            limit: Maximum results
            document_ids: Optional document filter
            
        Returns:
            List of (chunk, similarity_score) tuples
        """
        try:
            # Generate query embedding
            embeddings, _ = await self.embedding_service.generate_embeddings([query])
            query_embedding = embeddings[0]
            
            # Search vector store
            results = await self.vector_store.search_similar(
                query_embedding, limit, document_ids
            )
            
            logger.info("Document search completed", query=query, results=len(results))
            return results
            
        except Exception as e:
            logger.error("Document search failed", query=query, error=str(e))
            return []