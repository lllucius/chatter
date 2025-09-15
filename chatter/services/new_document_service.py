"""New simplified document service using the clean embedding pipeline.

This replaces the complex DocumentService with a clean, simple implementation.
NO backwards compatibility - completely new design.
"""

import hashlib
import mimetypes
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastapi import UploadFile
from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.config import settings
from chatter.core.embedding_pipeline import EmbeddingPipeline
from chatter.models.base import generate_ulid
from chatter.models.document import Document, DocumentChunk, DocumentStatus, DocumentType
from chatter.schemas.document import DocumentCreate, DocumentListRequest, DocumentSearchRequest
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class DocumentServiceError(Exception):
    """Document service error."""
    pass


class NewDocumentService:
    """Simplified document service using the new embedding pipeline."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.pipeline = EmbeddingPipeline(session)
        self.storage_path = Path(settings.document_storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    async def create_document(
        self,
        user_id: str,
        upload_file: UploadFile,
        document_data: DocumentCreate
    ) -> Document:
        """Create and process a new document.

        Args:
            user_id: Document owner ID
            upload_file: Uploaded file
            document_data: Document metadata

        Returns:
            Created document

        Raises:
            DocumentServiceError: If creation fails
        """
        try:
            # Read file content first
            file_content = await upload_file.read()
            file_size = len(file_content)

            # Validate file size
            if file_size > settings.max_file_size:
                raise DocumentServiceError(f"File too large: {file_size} bytes")

            # Reset file pointer for any subsequent operations
            await upload_file.seek(0)

            # Calculate hash
            file_hash = hashlib.sha256(file_content).hexdigest()

            # Detect document type
            mime_type = (
                upload_file.content_type
                or mimetypes.guess_type(upload_file.filename)[0]
                or "application/octet-stream"
            )
            document_type = self._detect_document_type(upload_file.filename, mime_type)

            # Validate file extension
            file_ext = Path(upload_file.filename).suffix.lower().lstrip(".")
            if file_ext not in settings.allowed_file_types:
                raise DocumentServiceError(f"File type not allowed: {file_ext}")

            # Generate unique filename and save file
            unique_filename = f"{generate_ulid()}.{file_ext}"
            file_path = self.storage_path / unique_filename

            with open(file_path, "wb") as f:
                f.write(file_content)

            # Create document record
            document = Document(
                owner_id=user_id,
                filename=unique_filename,
                original_filename=upload_file.filename,
                file_path=str(file_path),
                file_size=file_size,
                file_hash=file_hash,
                mime_type=mime_type,
                document_type=document_type,
                title=document_data.title or upload_file.filename,
                description=document_data.description,
                tags=document_data.tags or [],
                extra_metadata=document_data.extra_metadata or {},
                chunk_size=document_data.chunk_size or settings.default_chunk_size,
                chunk_overlap=document_data.chunk_overlap or settings.default_chunk_overlap,
                is_public=document_data.is_public or False,
                status=DocumentStatus.PENDING
            )

            self.session.add(document)
            await self.session.commit()
            await self.session.refresh(document)

            logger.info(
                "Document created",
                document_id=document.id,
                filename=upload_file.filename,
                user_id=user_id
            )

            # Start processing asynchronously
            import asyncio
            asyncio.create_task(self._process_document_async(document.id, file_content))

            return document

        except DocumentServiceError:
            raise
        except Exception as e:
            logger.error("Document creation failed", error=str(e))
            raise DocumentServiceError(f"Failed to create document: {e}") from e

    async def get_document(self, document_id: str, user_id: str) -> Document | None:
        """Get a document by ID with access control.

        Args:
            document_id: Document ID
            user_id: Requesting user ID

        Returns:
            Document if found and accessible
        """
        try:
            result = await self.session.execute(
                select(Document).where(
                    and_(
                        Document.id == document_id,
                        or_(
                            Document.owner_id == user_id,
                            Document.is_public
                        )
                    )
                )
            )
            document = result.scalar_one_or_none()

            if document:
                # Update view statistics
                document.view_count += 1
                document.last_accessed_at = datetime.now(UTC)
                await self.session.commit()
                await self.session.refresh(document)

            return document

        except Exception as e:
            logger.error("Failed to get document", document_id=document_id, error=str(e))
            return None

    async def list_documents(
        self,
        user_id: str,
        list_request: DocumentListRequest
    ) -> tuple[list[Document], int]:
        """List documents with filtering and pagination.

        Args:
            user_id: Requesting user ID
            list_request: List parameters

        Returns:
            Tuple of (documents, total_count)
        """
        try:
            # Base query with access control
            query = select(Document).where(
                or_(
                    Document.owner_id == user_id,
                    Document.is_public
                )
            )

            # Apply filters
            if list_request.status:
                query = query.where(Document.status == list_request.status)

            if list_request.document_type:
                query = query.where(Document.document_type == list_request.document_type)

            if list_request.tags:
                for tag in list_request.tags:
                    query = query.where(Document.tags.contains([tag]))

            # Get total count
            count_query = select(func.count()).select_from(query.subquery())
            count_result = await self.session.execute(count_query)
            total_count = count_result.scalar()

            # Apply sorting and pagination
            sort_column = getattr(Document, list_request.sort_by, Document.created_at)
            if list_request.sort_order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(sort_column)

            query = query.offset(list_request.offset).limit(list_request.limit)

            # Execute query
            result = await self.session.execute(query)
            documents = list(result.scalars().all())

            return documents, total_count

        except Exception as e:
            logger.error("Failed to list documents", error=str(e))
            return [], 0

    async def search_documents(
        self,
        user_id: str,
        search_request: DocumentSearchRequest
    ) -> list[tuple[DocumentChunk, float, Document]]:
        """Search documents using semantic similarity.

        Args:
            user_id: Requesting user ID
            search_request: Search parameters

        Returns:
            List of (chunk, similarity_score, document) tuples
        """
        try:
            # Get accessible document IDs
            accessible_docs_result = await self.session.execute(
                select(Document.id).where(
                    or_(
                        Document.owner_id == user_id,
                        Document.is_public
                    )
                )
            )
            accessible_doc_ids = [doc_id for (doc_id,) in accessible_docs_result.all()]

            if not accessible_doc_ids:
                return []

            # Apply document type filter
            if search_request.document_types:
                filtered_docs_result = await self.session.execute(
                    select(Document.id).where(
                        and_(
                            Document.id.in_(accessible_doc_ids),
                            Document.document_type.in_(search_request.document_types)
                        )
                    )
                )
                accessible_doc_ids = [doc_id for (doc_id,) in filtered_docs_result.all()]

            # Apply tags filter
            if search_request.tags:
                for tag in search_request.tags:
                    filtered_docs_result = await self.session.execute(
                        select(Document.id).where(
                            and_(
                                Document.id.in_(accessible_doc_ids),
                                Document.tags.contains([tag])
                            )
                        )
                    )
                    accessible_doc_ids = [doc_id for (doc_id,) in filtered_docs_result.all()]

            if not accessible_doc_ids:
                return []

            # Perform semantic search
            chunk_results = await self.pipeline.search_documents(
                query=search_request.query,
                limit=search_request.limit,
                document_ids=accessible_doc_ids
            )

            # Filter by score threshold and get document info
            results = []
            for chunk, similarity_score in chunk_results:
                if similarity_score >= search_request.score_threshold:
                    # Get document (should be cached or fast lookup)
                    doc_result = await self.session.execute(
                        select(Document).where(Document.id == chunk.document_id)
                    )
                    document = doc_result.scalar_one_or_none()
                    if document:
                        results.append((chunk, similarity_score, document))
                        # Update search statistics
                        document.search_count += 1

            await self.session.commit()

            logger.info(
                "Document search completed",
                query=search_request.query,
                results=len(results),
                user_id=user_id
            )

            return results

        except Exception as e:
            logger.error("Document search failed", error=str(e))
            return []

    async def delete_document(self, document_id: str, user_id: str) -> bool:
        """Delete a document and its data.

        Args:
            document_id: Document ID
            user_id: Requesting user ID

        Returns:
            True if deleted successfully
        """
        try:
            # Get document with ownership check
            result = await self.session.execute(
                select(Document).where(
                    and_(
                        Document.id == document_id,
                        Document.owner_id == user_id
                    )
                )
            )
            document = result.scalar_one_or_none()

            if not document:
                return False

            # Delete file from storage
            if document.file_path and Path(document.file_path).exists():
                try:
                    Path(document.file_path).unlink()
                except OSError as e:
                    logger.warning("Failed to delete file", file_path=document.file_path, error=str(e))

            # Delete document (cascades to chunks)
            await self.session.delete(document)
            await self.session.commit()

            logger.info("Document deleted", document_id=document_id, user_id=user_id)
            return True

        except Exception as e:
            await self.session.rollback()
            logger.error("Failed to delete document", document_id=document_id, error=str(e))
            return False

    async def reprocess_document(self, document_id: str, user_id: str) -> bool:
        """Reprocess a document through the embedding pipeline.

        Args:
            document_id: Document ID
            user_id: Requesting user ID

        Returns:
            True if reprocessing started successfully
        """
        try:
            # Get document with ownership check
            result = await self.session.execute(
                select(Document).where(
                    and_(
                        Document.id == document_id,
                        Document.owner_id == user_id
                    )
                )
            )
            document = result.scalar_one_or_none()

            if not document:
                return False

            # Check if file exists
            if not document.file_path or not Path(document.file_path).exists():
                logger.error("Document file not found", document_id=document_id)
                return False

            # Delete existing chunks
            await self.session.execute(
                select(DocumentChunk).where(DocumentChunk.document_id == document_id)
            )
            await self.session.commit()

            # Read file and start processing with dedicated session
            with open(document.file_path, "rb") as f:
                file_content = f.read()

            import asyncio
            asyncio.create_task(self._process_document_async(document.id, file_content))

            logger.info("Document reprocessing started", document_id=document_id)
            return True

        except Exception as e:
            logger.error("Failed to start document reprocessing", document_id=document_id, error=str(e))
            return False

    async def get_document_stats(self, user_id: str) -> dict[str, Any]:
        """Get document statistics for user.

        Args:
            user_id: User ID

        Returns:
            Document statistics
        """
        try:
            # Count documents by status
            status_counts = {}
            for status in DocumentStatus:
                result = await self.session.execute(
                    select(func.count(Document.id)).where(
                        and_(
                            Document.owner_id == user_id,
                            Document.status == status
                        )
                    )
                )
                status_counts[status.value] = result.scalar()

            # Count documents by type
            type_counts = {}
            for doc_type in DocumentType:
                result = await self.session.execute(
                    select(func.count(Document.id)).where(
                        and_(
                            Document.owner_id == user_id,
                            Document.document_type == doc_type
                        )
                    )
                )
                type_counts[doc_type.value] = result.scalar()

            # Get total storage used
            storage_result = await self.session.execute(
                select(func.sum(Document.file_size)).where(
                    Document.owner_id == user_id
                )
            )
            total_storage = storage_result.scalar() or 0

            # Get total chunks
            chunks_result = await self.session.execute(
                select(func.count(DocumentChunk.id))
                .select_from(DocumentChunk)
                .join(Document)
                .where(Document.owner_id == user_id)
            )
            total_chunks = chunks_result.scalar()

            return {
                "total_documents": sum(status_counts.values()),
                "status_counts": status_counts,
                "type_counts": type_counts,
                "total_storage_bytes": total_storage,
                "total_chunks": total_chunks
            }

        except Exception as e:
            logger.error("Failed to get document stats", error=str(e))
            return {}

    def _detect_document_type(self, filename: str, mime_type: str) -> DocumentType:
        """Detect document type from filename and MIME type."""
        file_ext = Path(filename).suffix.lower()

        extension_map = {
            ".txt": DocumentType.TEXT,
            ".pdf": DocumentType.PDF,
            ".doc": DocumentType.DOC,
            ".docx": DocumentType.DOCX,
            ".html": DocumentType.HTML,
            ".htm": DocumentType.HTML,
            ".md": DocumentType.MARKDOWN,
            ".markdown": DocumentType.MARKDOWN,
            ".json": DocumentType.JSON,
            ".xml": DocumentType.XML,
        }

        if file_ext in extension_map:
            return extension_map[file_ext]

        # Check MIME type as fallback
        if mime_type:
            if "pdf" in mime_type:
                return DocumentType.PDF
            elif "html" in mime_type:
                return DocumentType.HTML
            elif "json" in mime_type:
                return DocumentType.JSON
            elif "xml" in mime_type:
                return DocumentType.XML
            elif "word" in mime_type or "msword" in mime_type:
                return DocumentType.DOCX if "openxml" in mime_type else DocumentType.DOC

        return DocumentType.OTHER

    async def _process_document_async(self, document_id: str, file_content: bytes) -> None:
        """Process document asynchronously with dedicated session."""
        from chatter.utils.database import get_session_maker
        
        # Create a fresh session for background processing to avoid session state issues
        session_maker = get_session_maker()
        async with session_maker() as processing_session:
            try:
                # Create a new pipeline with the dedicated session
                processing_pipeline = EmbeddingPipeline(processing_session)
                success = await processing_pipeline.process_document(document_id, file_content)
                
                if success:
                    logger.info("Document processing completed successfully", document_id=document_id)
                else:
                    logger.error("Document processing failed", document_id=document_id)
            except Exception as e:
                logger.error("Document processing exception", document_id=document_id, error=str(e))
