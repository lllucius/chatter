"""Document processing service for text extraction, chunking, and indexing."""

import asyncio
import hashlib
import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

try:
    import unstructured  # noqa: F401
    from unstructured.partition.auto import partition
    from unstructured.partition.docx import partition_docx
    from unstructured.partition.html import partition_html
    from unstructured.partition.pdf import partition_pdf
    from unstructured.partition.text import partition_text  # noqa: F401

    UNSTRUCTURED_AVAILABLE = True
except ImportError:
    UNSTRUCTURED_AVAILABLE = False

try:
    from pypdf import PdfReader

    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

from chatter.config import settings
from chatter.models.document import (
    Document,
    DocumentChunk,
    DocumentStatus,
    DocumentType,
)
from chatter.services.dynamic_vector_store import (
    DynamicVectorStoreService,
)
from chatter.services.embeddings import EmbeddingError, EmbeddingService
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class DocumentProcessingService:
    """Service for processing documents and generating chunks with embeddings."""

    def __init__(self, session: AsyncSession):
        """Initialize document processing service.

        Args:
            session: Database session
        """
        self.session = session
        self.embedding_service = EmbeddingService()
        a = 1
        self.vector_store_service = DynamicVectorStoreService(session)
        self.storage_path = Path(settings.document_storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    async def process_document(
        self,
        document_id: str,
        file_content: bytes,
        force_reprocess: bool = False,
    ) -> bool:
        """Process a document: extract text, create chunks, and generate embeddings."""
        document: Document | None = None
        try:
            # Get document
            result = await self.session.execute(
                select(Document).where(Document.id == document_id)
            )
            document = result.scalar_one_or_none()

            if not document:
                logger.error("Document not found", document_id=document_id)
                return False

            # Already processed?
            if document.status == DocumentStatus.PROCESSED and not force_reprocess:
                logger.info("Document already processed", document_id=document_id)
                return True

            # Update status to processing
            document.status = DocumentStatus.PROCESSING
            document.processing_started_at = datetime.now(UTC)
            document.processing_error = None
            await self.session.commit()
            await self.session.refresh(document)

            logger.info("Starting document processing", document_id=document_id, filename=document.filename)

            # Trigger started event
            try:
                from chatter.services.sse_events import (
                    EventType,
                    sse_service,
                )
                await sse_service.trigger_event(
                    EventType.DOCUMENT_PROCESSING_STARTED,
                    {
                        "document_id": document_id,
                        "filename": document.filename,
                        "started_at": document.processing_started_at.isoformat(),
                    },
                    user_id=document.owner_id
                )
            except Exception as e:
                logger.warning("Failed to trigger document processing started event", error=str(e))

            # Extract text (offloads heavy work)
            extracted_text = await self._extract_text(document, file_content)
            if not extracted_text:
                await self._mark_processing_failed(document, "Failed to extract text from document")
                return False

            # Persist extracted text
            document.extracted_text = extracted_text
            await self.session.commit()
            await self.session.refresh(document)

            # Create chunks (offloaded splitter)
            chunks = await self._create_chunks(document, extracted_text)
            if not chunks:
                await self._mark_processing_failed(document, "Failed to create chunks from text")
                return False

            # Store chunks (async DB)
            chunk_objects = await self._store_chunks(document, chunks)
            if not chunk_objects:
                await self._mark_processing_failed(document, "Failed to store chunks")
                return False

            # Generate embeddings for chunks (async HTTP + async DB; PGVector sync parts are offloaded internally)
            embedding_success = await self._generate_embeddings(document, chunk_objects)
            if not embedding_success:
                logger.warning("Failed to generate embeddings for some chunks", document_id=document_id)

            # Update document status
            document.status = DocumentStatus.PROCESSED
            document.processing_completed_at = datetime.now(UTC)
            document.chunk_count = len(chunk_objects)
            await self.session.commit()
            await self.session.refresh(document)

            logger.info(
                "Document processing completed",
                document_id=document_id,
                chunks_created=len(chunk_objects),
                text_length=len(extracted_text),
            )

            # Trigger completed event
            try:
                from chatter.services.sse_events import (
                    trigger_document_processing_completed,
                )
                await trigger_document_processing_completed(
                    document_id,
                    {
                        "chunks_created": len(chunk_objects),
                        "text_length": len(extracted_text),
                        "processing_time": (document.processing_completed_at - document.processing_started_at).total_seconds(),
                    },
                    document.owner_id
                )
            except Exception as e:
                logger.warning("Failed to trigger document processing completed event", error=str(e))

            return True

        except Exception as e:
            logger.error("Document processing failed", document_id=document_id, error=str(e))
            if document:
                await self._mark_processing_failed(document, f"Processing error: {str(e)}")
            return False

    async def _extract_text(self, document: Document, file_content: bytes) -> str | None:
        """Extract text from document based on its type."""
        try:
            # Save file temporarily for processing in a thread (avoid blocking loop)
            suffix = f".{document.document_type.value}"
            temp_file_path = await asyncio.to_thread(self._write_temp_file, suffix, file_content)

            try:
                if document.document_type == DocumentType.TEXT:
                    return await self._extract_text_plain(file_content)
                elif document.document_type == DocumentType.PDF:
                    return await self._extract_text_pdf(temp_file_path, file_content)
                elif document.document_type in [DocumentType.DOC, DocumentType.DOCX]:
                    return await self._extract_text_docx(temp_file_path)
                elif document.document_type == DocumentType.HTML:
                    return await self._extract_text_html(file_content)
                elif document.document_type == DocumentType.MARKDOWN:
                    return await self._extract_text_markdown(file_content)
                elif document.document_type == DocumentType.JSON:
                    return await self._extract_text_json(file_content)
                else:
                    # Try using unstructured for unknown formats
                    if UNSTRUCTURED_AVAILABLE:
                        return await self._extract_text_unstructured(temp_file_path)
                    return None
            finally:
                # Clean up temporary file (in a thread)
                try:
                    await asyncio.to_thread(self._unlink_file, temp_file_path)
                except Exception:
                    pass

        except Exception as e:
            logger.error("Text extraction failed", document_id=document.id, error=str(e))
            return None

    # -------- blocking helpers offloaded to threads --------

    def _write_temp_file(self, suffix: str, data: bytes) -> str:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(data)
            return temp_file.name

    def _unlink_file(self, path: str) -> None:
        try:
            os.unlink(path)
        except OSError:
            pass

    def _extract_text_pdf_sync(self, file_path: str) -> str | None:
        # Try PyPDF first
        if PYPDF_AVAILABLE:
            try:
                reader = PdfReader(file_path)
                text_parts: list[str] = []
                for page in reader.pages:
                    try:
                        text = page.extract_text()  # may return None
                    except Exception:
                        text = None
                    if text:
                        text_parts.append(text)
                joined = "\n".join(text_parts)
                if joined.strip():
                    return joined
            except Exception as e:
                # fall back to unstructured
                logger.warning("PyPDF extraction failed, trying unstructured", error=str(e))
        # Fallback to unstructured
        if UNSTRUCTURED_AVAILABLE:
            elements = partition_pdf(filename=file_path)
            return "\n".join([element.text for element in elements if hasattr(element, "text")])
        return None

    def _extract_text_docx_sync(self, file_path: str) -> str | None:
        if UNSTRUCTURED_AVAILABLE:
            elements = partition_docx(filename=file_path)
            return "\n".join([element.text for element in elements if hasattr(element, "text")])
        return None

    def _extract_text_html_sync(self, html_text: str) -> str | None:
        if UNSTRUCTURED_AVAILABLE:
            elements = partition_html(text=html_text)
            return "\n".join([element.text for element in elements if hasattr(element, "text")])
        return None

    def _extract_text_unstructured_sync(self, file_path: str) -> str | None:
        if UNSTRUCTURED_AVAILABLE:
            elements = partition(filename=file_path)
            return "\n".join([element.text for element in elements if hasattr(element, "text")])
        return None

    def _create_chunks_sync(self, document: Document, text: str) -> list[str]:
        # Choose splitter based on document type and content
        if document.document_type == DocumentType.MARKDOWN:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=document.chunk_size,
                chunk_overlap=document.chunk_overlap,
                separators=["\n# ", "\n## ", "\n### ", "\n\n", "\n", ".", "!", "?", ";", " "],
            )
        elif document.document_type in [DocumentType.HTML, DocumentType.XML]:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=document.chunk_size,
                chunk_overlap=document.chunk_overlap,
                separators=["\n\n", "\n", "<p>", "<div>", "<br>", ".", "!", "?", ";", " "],
            )
        else:
            # Default recursive character splitter
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=document.chunk_size,
                chunk_overlap=document.chunk_overlap,
                separators=["\n\n", "\n", ".", "!", "?", ";", " "],
            )

        chunks = splitter.split_text(text)

        # Filter out very short chunks
        min_chunk_length = max(50, document.chunk_size // 10)
        chunks = [chunk.strip() for chunk in chunks if len(chunk.strip()) >= min_chunk_length]
        return chunks

    # -------- async wrappers that offload to threads --------

    async def _extract_text_plain(self, file_content: bytes) -> str | None:
        """Extract text from plain text file."""
        try:
            # Try different encodings (cheap enough to do on loop)
            for encoding in ["utf-8", "latin-1", "cp1252"]:
                try:
                    return file_content.decode(encoding)
                except UnicodeDecodeError:
                    continue
            return None
        except Exception as e:
            logger.error("Plain text extraction failed", error=str(e))
            return None

    async def _extract_text_pdf(self, file_path: str, file_content: bytes) -> str | None:
        """Extract text from PDF file (offloaded)."""
        try:
            return await asyncio.to_thread(self._extract_text_pdf_sync, file_path)
        except Exception as e:
            logger.error("PDF text extraction failed", error=str(e))
            return None

    async def _extract_text_docx(self, file_path: str) -> str | None:
        """Extract text from DOCX file (offloaded)."""
        try:
            return await asyncio.to_thread(self._extract_text_docx_sync, file_path)
        except Exception as e:
            logger.error("DOCX text extraction failed", error=str(e))
            return None

    async def _extract_text_html(self, file_content: bytes) -> str | None:
        """Extract text from HTML file (offloaded)."""
        try:
            html_text = file_content.decode("utf-8", errors="ignore")
            return await asyncio.to_thread(self._extract_text_html_sync, html_text)
        except Exception as e:
            logger.error("HTML text extraction failed", error=str(e))
            return None

    async def _extract_text_markdown(self, file_content: bytes) -> str | None:
        """Extract text from Markdown file."""
        try:
            # For markdown, we can just return the text as-is
            return file_content.decode("utf-8", errors="ignore")
        except Exception as e:
            logger.error("Markdown text extraction failed", error=str(e))
            return None

    async def _extract_text_json(self, file_content: bytes) -> str | None:
        """Extract text from JSON file (offloaded)."""
        try:
            import json

            def _parse_json_to_text(data_bytes: bytes) -> str | None:
                try:
                    data = json.loads(data_bytes.decode("utf-8"))

                    def extract_text_from_json(obj: Any) -> str:
                        if isinstance(obj, str):
                            return obj
                        elif isinstance(obj, dict):
                            return " ".join(extract_text_from_json(v) for v in obj.values())
                        elif isinstance(obj, list):
                            return " ".join(extract_text_from_json(item) for item in obj)
                        else:
                            return str(obj)

                    return extract_text_from_json(data)
                except Exception:
                    return None

            return await asyncio.to_thread(_parse_json_to_text, file_content)

        except Exception as e:
            logger.error("JSON text extraction failed", error=str(e))
            return None

    async def _extract_text_unstructured(self, file_path: str) -> str | None:
        """Extract text using unstructured library (offloaded)."""
        try:
            return await asyncio.to_thread(self._extract_text_unstructured_sync, file_path)
        except Exception as e:
            logger.error("Unstructured text extraction failed", error=str(e))
            return None

    async def _create_chunks(self, document: Document, text: str) -> list[str]:
        """Create text chunks from extracted text (offloaded splitter)."""
        try:
            chunks = await asyncio.to_thread(self._create_chunks_sync, document, text)
            logger.debug(
                "Text chunks created",
                document_id=document.id,
                total_chunks=len(chunks),
                chunk_size=document.chunk_size,
                chunk_overlap=document.chunk_overlap,
            )
            return chunks
        except Exception as e:
            logger.error("Chunk creation failed", document_id=document.id, error=str(e))
            return []

    async def _store_chunks(self, document: Document, chunks: list[str]) -> list[DocumentChunk]:
        """Store text chunks in the database."""
        logger.info("Storing chunks")
        try:
            chunk_objects = []

            for i, chunk_text in enumerate(chunks):
                # Calculate content hash (cheap; keep on loop)
                content_hash = hashlib.sha256(chunk_text.encode("utf-8")).hexdigest()

                # Create chunk object
                chunk = DocumentChunk(
                    document_id=document.id,
                    content=chunk_text,
                    chunk_index=i,
                    content_hash=content_hash,
                    token_count=len(chunk_text.split()),  # Simple token count approximation
                )
                chunk_objects.append(chunk)
                self.session.add(chunk)

            await self.session.commit()
            await self.session.refresh(document)

            # Refresh objects to get IDs
            for chunk in chunk_objects:
                await self.session.refresh(chunk)

            logger.debug("Chunks stored in database", document_id=document.id, chunk_count=len(chunk_objects))
            return chunk_objects

        except Exception as e:
            await self.session.rollback()
            logger.error("Chunk storage failed", document_id=document.id, error=str(e))
            return []

    async def _generate_embeddings(self, document: Document, chunks: list[DocumentChunk]) -> bool:
        """Generate embeddings for document chunks."""
        try:
            # Check if embedding service is available
            if not self.embedding_service.list_available_providers():
                logger.warning("No embedding providers available, skipping embedding generation")
                return False

            # Process chunks in batches
            batch_size = settings.embedding_batch_size
            success_count = 0

            for i in range(0, len(chunks), batch_size):
                batch = chunks[i : i + batch_size]
                batch_texts = [chunk.content for chunk in batch]

                try:
                    # Generate embeddings for batch (async HTTP, non-blocking)
                    (embeddings, usage_info) = await self.embedding_service.generate_embeddings(batch_texts)

                    # Store embeddings
                    for chunk, embedding in zip(batch, embeddings, strict=False):
                        provider = usage_info.get("provider")
                        model = usage_info.get("model")
                        embedding_metadata = {
                            "model": model,
                            "provider": provider,
                            "dimensions": len(embedding),
                        }

                        # Update chunk with embedding metadata in vector store (offloads sync parts internally)
                        success = await self.vector_store_service.store_embedding(
                            chunk_id=chunk.id,
                            embedding=embedding,
                            provider_name=provider or "provider",
                            model_name=model,
                            metadata=embedding_metadata,
                        )

                        if not success:
                            logger.warning("Failed to store embedding", chunk_id=chunk.id)
                            raise EmbeddingError

                    success_count += len(batch)
                    await self.session.commit()

                except EmbeddingError as e:
                    logger.error("Embedding generation failed for batch", error=str(e))
                    await self.session.rollback()
                    await self.session.refresh(document, ["chunks"])
                    continue

            success_rate = success_count / len(chunks) if chunks else 0
            logger.info(
                "Embedding generation completed",
                total_chunks=len(chunks),
                successful_embeddings=success_count,
                success_rate=success_rate,
            )

            return success_rate > 0.5  # Consider successful if >50% of embeddings generated

        except Exception as e:
            logger.error("Embedding generation failed", error=str(e))
            return False

    async def _mark_processing_failed(self, document: Document, error_message: str) -> None:
        """Mark document processing as failed."""
        try:
            document.status = DocumentStatus.FAILED
            document.processing_completed_at = datetime.now(UTC)
            document.processing_error = error_message
            await self.session.commit()
            await self.session.refresh(document)

            logger.error("Document processing marked as failed", document_id=document.id, error=error_message)

            # Trigger document processing failed event
            try:
                from chatter.services.sse_events import (
                    trigger_document_processing_failed,
                )
                await trigger_document_processing_failed(str(document.id), error_message, document.owner_id)
            except Exception as e:
                logger.warning("Failed to trigger document processing failed event", error=str(e))

        except Exception as e:
            logger.error("Failed to mark processing as failed", document_id=document.id, error=str(e))

    def detect_document_type(self, filename: str, mime_type: str) -> DocumentType:
        """Detect document type from filename and MIME type."""
        # Get file extension
        file_ext = Path(filename).suffix.lower()

        # Map extensions to document types
        extension_map = {
            ".txt": DocumentType.TEXT,
            ".text": DocumentType.TEXT,
            ".pdf": DocumentType.PDF,
            ".doc": DocumentType.DOC,
            ".docx": DocumentType.DOCX,
            ".rtf": DocumentType.RTF,
            ".odt": DocumentType.ODT,
            ".html": DocumentType.HTML,
            ".htm": DocumentType.HTML,
            ".md": DocumentType.MARKDOWN,
            ".markdown": DocumentType.MARKDOWN,
            ".csv": DocumentType.CSV,
            ".json": DocumentType.JSON,
            ".xml": DocumentType.XML,
        }

        # Check extension first
        if file_ext in extension_map:
            return extension_map[file_ext]

        # Check MIME type
        if mime_type:
            if mime_type.startswith("text/"):
                if "html" in mime_type:
                    return DocumentType.HTML
                elif "markdown" in mime_type:
                    return DocumentType.MARKDOWN
                else:
                    return DocumentType.TEXT
            elif mime_type == "application/pdf":
                return DocumentType.PDF
            elif "word" in mime_type or "msword" in mime_type:
                return DocumentType.DOCX if "openxml" in mime_type else DocumentType.DOC
            elif mime_type == "application/json":
                return DocumentType.JSON
            elif "xml" in mime_type:
                return DocumentType.XML

        return DocumentType.OTHER

    async def get_processing_stats(self) -> dict[str, Any]:
        """Get document processing statistics."""
        try:
            # Count documents by status
            status_counts = {}
            for status in DocumentStatus:
                result = await self.session.execute(
                    select(func.count(Document.id)).where(Document.status == status)
                )
                status_counts[status.value] = result.scalar()

            # Get processing times
            processing_times_result = await self.session.execute(
                select(
                    Document.processing_started_at,
                    Document.processing_completed_at,
                ).where(
                    and_(
                        Document.processing_started_at.is_not(None),
                        Document.processing_completed_at.is_not(None),
                    )
                )
            )

            processing_times = []
            for start_time, end_time in processing_times_result.all():
                if start_time and end_time:
                    duration = (end_time - start_time).total_seconds()
                    processing_times.append(duration)

            avg_processing_time = (sum(processing_times) / len(processing_times)) if processing_times else 0

            return {
                "status_counts": status_counts,
                "total_documents": sum(status_counts.values()),
                "processing_success_rate": (
                    status_counts.get("processed", 0) / sum(status_counts.values())
                    if sum(status_counts.values()) > 0
                    else 0
                ),
                "average_processing_time_seconds": avg_processing_time,
                "unstructured_available": UNSTRUCTURED_AVAILABLE,
                "pypdf_available": PYPDF_AVAILABLE,
            }

        except Exception as e:
            logger.error("Failed to get processing stats", error=str(e))
            return {
                "status_counts": {},
                "total_documents": 0,
                "processing_success_rate": 0.0,
                "average_processing_time_seconds": 0.0,
                "unstructured_available": UNSTRUCTURED_AVAILABLE,
                "pypdf_available": PYPDF_AVAILABLE,
            }


class DocumentProcessingError(Exception):
    """Document processing error."""

    pass
