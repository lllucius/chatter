"""Document management service."""

import hashlib
import mimetypes
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastapi import UploadFile
from sqlalchemy import and_, asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.config import settings
from chatter.models.document import (
    Document,
    DocumentChunk,
    DocumentStatus,
    DocumentType,
)
from chatter.schemas.document import (
    DocumentCreate,
    DocumentListRequest,
    DocumentProcessingRequest,
    DocumentSearchRequest,
    DocumentUpdate,
)
from chatter.services.document_processing import (
    DocumentProcessingService,
)
from chatter.services.dynamic_vector_store import (
    DynamicVectorStoreService,
)
from chatter.services.embeddings import EmbeddingService
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class DocumentService:
    """Service for document management operations."""

    def __init__(self, session: AsyncSession):
        """Initialize document service.

        Args:
            session: Database session
        """
        self.session = session
        self.processing_service = DocumentProcessingService(session)
        self.vector_store_service = DynamicVectorStoreService(session)
        self.embedding_service = EmbeddingService()
        self.storage_path = Path(settings.document_storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    async def create_document(
        self,
        user_id: str,
        upload_file: UploadFile,
        document_data: DocumentCreate,
    ) -> Document:
        """Create a new document from uploaded file.

        Args:
            user_id: Owner user ID
            upload_file: Uploaded file
            document_data: Document creation data

        Returns:
            Created document

        Raises:
            DocumentError: If document creation fails
        """
        try:
            # Read file content
            file_content = await upload_file.read()
            file_size = len(file_content)

            # Validate file size
            if file_size > settings.max_file_size:
                raise DocumentError(
                    f"File size exceeds maximum allowed size of {settings.max_file_size} bytes"
                ) from None

            # Calculate file hash
            file_hash = hashlib.sha256(file_content).hexdigest()

            # Check for duplicate files
            existing_doc_result = await self.session.execute(
                select(Document).where(
                    and_(
                        Document.owner_id == user_id,
                        Document.file_hash == file_hash,
                    )
                )
            )
            existing_doc = existing_doc_result.scalar_one_or_none()

            if existing_doc:
                raise DocumentError(
                    "Document with identical content already exists"
                ) from None

            # Detect MIME type and document type
            mime_type = (
                upload_file.content_type
                or mimetypes.guess_type(upload_file.filename)[0]
                or "application/octet-stream"
            )
            document_type = (
                self.processing_service.detect_document_type(
                    upload_file.filename, mime_type
                )
            )

            # Validate file type
            file_ext = (
                Path(upload_file.filename).suffix.lower().lstrip(".")
            )
            if file_ext not in settings.allowed_file_types:
                raise DocumentError(
                    f"File type '{file_ext}' is not allowed"
                ) from None

            # Generate unique filename
            unique_filename = f"{uuid.uuid4()}.{file_ext}"

            # Save file to storage
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
                tags=document_data.tags,
                extra_metadata=document_data.extra_metadata,
                chunk_size=document_data.chunk_size,
                chunk_overlap=document_data.chunk_overlap,
                is_public=document_data.is_public,
                status=DocumentStatus.PENDING,
            )

            self.session.add(document)
            await self.session.commit()
            await self.session.refresh(document)

            # Trigger document uploaded event
            try:
                from chatter.services.sse_events import (
                    trigger_document_uploaded,
                )
                await trigger_document_uploaded(
                    str(document.id),
                    upload_file.filename,
                    user_id
                )
            except Exception as e:
                logger.warning("Failed to trigger document uploaded event", error=str(e))

            # Start background processing
            await self._process_document_async(
                document.id, file_content
            )

            logger.info(
                "Document created",
                document_id=document.id,
                filename=upload_file.filename,
                file_size=file_size,
                user_id=user_id,
            )

            return document

        except DocumentError:
            raise
        except Exception as e:
            logger.error("Document creation failed", error=str(e))
            raise DocumentError(
                f"Failed to create document: {str(e)}"
            ) from e

    async def get_document(
        self, document_id: str, user_id: str
    ) -> Document | None:
        """Get document by ID with access control.

        Args:
            document_id: Document ID
            user_id: Requesting user ID

        Returns:
            Document if found and accessible, None otherwise
        """
        try:
            result = await self.session.execute(
                select(Document).where(
                    and_(
                        Document.id == document_id,
                        or_(
                            Document.owner_id == user_id,
                            Document.is_public is True,
                        ),
                    )
                )
            )
            document = result.scalar_one_or_none()

            if document:
                # Update view count and last accessed time
                document.view_count += 1
                document.last_accessed_at = datetime.now(UTC)
                await self.session.commit()
                await self.session.refresh(document)

            return document

        except Exception as e:
            logger.error(
                "Failed to get document",
                document_id=document_id,
                error=str(e),
            )
            return None

    async def list_documents(
        self, user_id: str, list_request: DocumentListRequest
    ) -> tuple[list[Document], int]:
        """List documents with filtering and pagination.

        Args:
            user_id: Requesting user ID
            list_request: List request parameters

        Returns:
            Tuple of (documents list, total count)
        """
        try:
            # Build base query with access control
            query = select(Document).where(
                or_(
                    Document.owner_id == user_id,
                    Document.is_public is True,
                )
            )

            # Add filters
            if list_request.status:
                query = query.where(
                    Document.status == list_request.status
                )

            if list_request.document_type:
                query = query.where(
                    Document.document_type == list_request.document_type
                )

            if list_request.tags:
                for tag in list_request.tags:
                    query = query.where(Document.tags.contains([tag]))

            if list_request.owner_id:
                # Only allow filtering by owner_id if user is admin (simplified check)
                query = query.where(
                    Document.owner_id == list_request.owner_id
                )

            # Get total count
            count_query = select(func.count()).select_from(
                query.subquery()
            )
            count_result = await self.session.execute(count_query)
            total_count = count_result.scalar()

            # Add sorting
            sort_column = getattr(
                Document, list_request.sort_by, Document.created_at
            )
            if list_request.sort_order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))

            # Add pagination
            query = query.offset(list_request.offset).limit(
                list_request.limit
            )

            # Execute query
            result = await self.session.execute(query)
            documents = result.scalars().all()

            return list(documents), total_count

        except Exception as e:
            logger.error("Failed to list documents", error=str(e))
            return [], 0

    async def update_document(
        self,
        document_id: str,
        user_id: str,
        update_data: DocumentUpdate,
    ) -> Document | None:
        """Update document metadata.

        Args:
            document_id: Document ID
            user_id: Requesting user ID
            update_data: Update data

        Returns:
            Updated document if successful, None otherwise
        """
        try:
            # Get document with ownership check
            result = await self.session.execute(
                select(Document).where(
                    and_(
                        Document.id == document_id,
                        Document.owner_id == user_id,
                    )
                )
            )
            document = result.scalar_one_or_none()

            if not document:
                return None

            # Update fields
            update_dict = update_data.model_dump(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(document, field, value)

            await self.session.commit()
            await self.session.refresh(document)

            logger.info(
                "Document updated",
                document_id=document_id,
                user_id=user_id,
            )
            return document

        except Exception as e:
            logger.error(
                "Failed to update document",
                document_id=document_id,
                error=str(e),
            )
            return None

    async def delete_document(
        self, document_id: str, user_id: str
    ) -> bool:
        """Delete document and its chunks.

        Args:
            document_id: Document ID
            user_id: Requesting user ID

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            # Get document with ownership check
            result = await self.session.execute(
                select(Document).where(
                    and_(
                        Document.id == document_id,
                        Document.owner_id == user_id,
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
                    logger.warning(
                        "Failed to delete file",
                        file_path=document.file_path,
                        error=str(e),
                    )

            # Delete document (cascades to chunks)
            await self.session.delete(document)
            await self.session.commit()

            logger.info(
                "Document deleted",
                document_id=document_id,
                user_id=user_id,
            )
            return True

        except Exception as e:
            logger.error(
                "Failed to delete document",
                document_id=document_id,
                error=str(e),
            )
            return False

    async def search_documents(
        self, user_id: str, search_request: DocumentSearchRequest
    ) -> list[tuple[DocumentChunk, float, Document]]:
        """Search documents using vector similarity.

        Args:
            user_id: Requesting user ID
            search_request: Search request parameters

        Returns:
            List of (chunk, similarity_score, document) tuples
        """
        try:
            # Generate query embedding
            (
                query_embedding,
                usage,
            ) = await self.embedding_service.generate_embedding(
                search_request.query
            )

            provider = usage.get("provider") if isinstance(usage, dict) else None
            model = usage.get("model") if isinstance(usage, dict) else None

            print("USAGES$%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
            # Get accessible document IDs
            accessible_docs_result = await self.session.execute(
                select(Document.id).where(
                    or_(
                        Document.owner_id == user_id,
                        Document.is_public is True,
                    )
                )
            )
            accessible_doc_ids = [
                doc_id for (doc_id,) in accessible_docs_result.all()
            ]

            if not accessible_doc_ids:
                return []

            print("USAGES$%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
            # Apply document type filter
            if search_request.document_types:
                filtered_docs_result = await self.session.execute(
                    select(Document.id).where(
                        and_(
                            Document.id.in_(accessible_doc_ids),
                            Document.document_type.in_(
                                search_request.document_types
                            ),
                        )
                    )
                )
                accessible_doc_ids = [
                    doc_id for (doc_id,) in filtered_docs_result.all()
                ]

            # Apply tags filter
            if search_request.tags:
                for tag in search_request.tags:
                    filtered_docs_result = await self.session.execute(
                        select(Document.id).where(
                            and_(
                                Document.id.in_(accessible_doc_ids),
                                Document.tags.contains([tag]),
                            )
                        )
                    )
                    accessible_doc_ids = [
                        doc_id
                        for (doc_id,) in filtered_docs_result.all()
                    ]

            if not accessible_doc_ids:
                return []

            # Perform vector search with dynamic store (parity: returns tuples)
            similar_chunks = await self.vector_store_service.similarity_search(
                query_embedding=query_embedding,
                provider_name=provider or "provider",
                model_name=model,
                limit=search_request.limit,
                score_threshold=search_request.score_threshold,
                document_ids=accessible_doc_ids,
            )

            # Get document information for each chunk
            results: list[tuple[DocumentChunk, float, Document]] = []
            for chunk, score in similar_chunks:
                # Increment search count
                if chunk.document:
                    chunk.document.search_count += 1
                    results.append((chunk, score, chunk.document))

            await self.session.commit()
            for _, _, document in results:
                await self.session.refresh(document)

            logger.info(
                "Document search completed",
                query=search_request.query,
                results_count=len(results),
                user_id=user_id,
            )

            return results

        except Exception as e:
            logger.error("Document search failed", error=str(e))
            return []

    async def process_document(
        self,
        document_id: str,
        user_id: str,
        processing_request: DocumentProcessingRequest,
    ) -> bool:
        """Manually trigger document processing.

        Args:
            document_id: Document ID
            user_id: Requesting user ID
            processing_request: Processing request parameters

        Returns:
            True if processing started successfully, False otherwise
        """
        try:
            # Get document with ownership check
            result = await self.session.execute(
                select(Document).where(
                    and_(
                        Document.id == document_id,
                        Document.owner_id == user_id,
                    )
                )
            )
            document = result.scalar_one_or_none()

            if not document:
                return False

            # Update chunk settings if provided
            if processing_request.chunk_size:
                document.chunk_size = processing_request.chunk_size
            if processing_request.chunk_overlap:
                document.chunk_overlap = (
                    processing_request.chunk_overlap
                )

            await self.session.commit()
            await self.session.refresh(document)

            # Load file content
            if (
                not document.file_path
                or not Path(document.file_path).exists()
            ):
                logger.error(
                    "Document file not found", document_id=document_id
                )
                return False

            with open(document.file_path, "rb") as f:
                file_content = f.read()

            # Start processing
            success = await self.processing_service.process_document(
                document_id, file_content, processing_request.reprocess
            )

            logger.info(
                "Document processing triggered",
                document_id=document_id,
                success=success,
            )
            return success

        except Exception as e:
            logger.error(
                "Failed to trigger document processing",
                document_id=document_id,
                error=str(e),
            )
            return False

    async def get_document_chunks(
        self, document_id: str, user_id: str
    ) -> list[DocumentChunk]:
        """Get chunks for a document.

        Args:
            document_id: Document ID
            user_id: Requesting user ID

        Returns:
            List of document chunks
        """
        try:
            # Check document access
            document = await self.get_document(document_id, user_id)
            if not document:
                return []

            # Get chunks
            result = await self.session.execute(
                select(DocumentChunk)
                .where(DocumentChunk.document_id == document_id)
                .order_by(DocumentChunk.chunk_index)
            )
            chunks = result.scalars().all()

            return list(chunks)

        except Exception as e:
            logger.error(
                "Failed to get document chunks",
                document_id=document_id,
                error=str(e),
            )
            return []

    async def get_document_stats(self, user_id: str) -> dict[str, Any]:
        """Get document statistics for user.

        Args:
            user_id: User ID

        Returns:
            Dictionary with document statistics
        """
        try:
            # Count documents by status
            status_counts = {}
            for status in DocumentStatus:
                result = await self.session.execute(
                    select(func.count(Document.id)).where(
                        and_(
                            Document.owner_id == user_id,
                            Document.status == status,
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
                            Document.document_type == doc_type,
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

            # Vector store embedding stats (from dynamic service)
            embedding_stats = await self.vector_store_service.get_embedding_stats()

            return {
                "total_documents": sum(status_counts.values()),
                "status_counts": status_counts,
                "type_counts": type_counts,
                "total_storage_bytes": total_storage,
                "total_chunks": total_chunks,
                "processing_stats": await self.processing_service.get_processing_stats(),
                "embedding_stats": embedding_stats,
            }

        except Exception as e:
            logger.error("Failed to get document stats", error=str(e))
            return {}

    async def _process_document_async(
        self, document_id: str, file_content: bytes
    ) -> None:
        """Process document asynchronously using job queue.

        Args:
            document_id: Document ID
            file_content: File content bytes
        """
        try:
            from chatter.services.job_queue import (
                JobPriority,
                job_queue,
            )

            # Add document processing job to the queue
            job_id = await job_queue.add_job(
                name=f"Document Processing: {document_id}",
                function_name="document_processing",
                args=[document_id, file_content],
                priority=JobPriority.NORMAL,
                tags=["document", "processing"],
                metadata={"document_id": document_id}
            )

            logger.info(
                "Document processing job queued",
                document_id=document_id,
                job_id=job_id,
            )

        except Exception as e:
            logger.error(
                "Failed to queue document processing job",
                document_id=document_id,
                error=str(e),
            )

    async def reprocess_document(self, document_id: str, user_id: str) -> bool:
        """Reprocess a document."""
        try:
            # Get the document first
            document = await self.get_document(document_id, user_id)
            if not document:
                return False

            # Trigger reprocessing (similar to process_document but for existing docs)
            processing_request = DocumentProcessingRequest(reprocess=True)
            await self.process_document(document_id, user_id, processing_request)
            return True
        except Exception as e:
            logger.error(
                "Failed to reprocess document",
                document_id=document_id,
                user_id=user_id,
                error=str(e),
            )
            return False


class DocumentError(Exception):
    """Document operation error."""

    pass


class ChunkingStrategy:
    """Strategy for chunking documents into smaller pieces."""

    def __init__(self, chunk_size: int = 1000, overlap: int = 100):
        """Initialize the chunking strategy.
        
        Args:
            chunk_size: Size of each chunk in characters
            overlap: Overlap between chunks in characters
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str) -> list[str]:
        """Chunk text into smaller pieces.
        
        Args:
            text: Text to chunk
            
        Returns:
            List of text chunks
        """
        if len(text) <= self.chunk_size:
            return [text]

        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - self.overlap
            
        return chunks

    def chunk_document(self, document: dict[str, Any]) -> list[dict[str, Any]]:
        """Chunk a document into smaller pieces.
        
        Args:
            document: Document to chunk
            
        Returns:
            List of document chunks
        """
        content = document.get("content", "")
        chunks = self.chunk_text(content)
        
        chunked_docs = []
        for i, chunk in enumerate(chunks):
            chunked_doc = {
                **document,
                "content": chunk,
                "chunk_id": i,
                "total_chunks": len(chunks)
            }
            chunked_docs.append(chunked_doc)
            
        return chunked_docs


class DocumentProcessor:
    """Processor for handling document operations."""

    def __init__(self):
        """Initialize the document processor."""
        self.processors: dict[str, callable] = {}

    def register_processor(self, file_type: str, processor: callable) -> None:
        """Register a processor for a file type.
        
        Args:
            file_type: File type extension
            processor: Processor function
        """
        self.processors[file_type] = processor

    async def process_document(self, document: dict[str, Any]) -> dict[str, Any]:
        """Process a document.
        
        Args:
            document: Document to process
            
        Returns:
            Processed document
        """
        file_type = document.get("file_type", "").lower()
        
        if file_type in self.processors:
            return await self.processors[file_type](document)
        
        # Default processing
        return {
            **document,
            "processed": True,
            "processed_at": datetime.now(UTC).isoformat()
        }

    def get_supported_types(self) -> list[str]:
        """Get list of supported file types.
        
        Returns:
            List of supported file types
        """
        return list(self.processors.keys())


class DocumentSearchEngine:
    """Search engine for finding documents."""

    def __init__(self):
        """Initialize the document search engine."""
        self.indexed_documents: dict[str, dict[str, Any]] = {}
        self.search_index: dict[str, set[str]] = {}

    def index_document(self, document_id: str, document: dict[str, Any]) -> None:
        """Index a document for searching.
        
        Args:
            document_id: ID of the document
            document: Document data
        """
        self.indexed_documents[document_id] = document
        
        # Simple keyword indexing
        content = document.get("content", "").lower()
        words = content.split()
        
        for word in words:
            if word not in self.search_index:
                self.search_index[word] = set()
            self.search_index[word].add(document_id)

    async def search(
        self, 
        query: str, 
        limit: int = 10
    ) -> list[dict[str, Any]]:
        """Search for documents.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching documents
        """
        query_words = query.lower().split()
        document_scores: dict[str, int] = {}
        
        for word in query_words:
            if word in self.search_index:
                for doc_id in self.search_index[word]:
                    document_scores[doc_id] = document_scores.get(doc_id, 0) + 1
        
        # Sort by score and return top results
        sorted_docs = sorted(
            document_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        results = []
        for doc_id, score in sorted_docs[:limit]:
            doc = self.indexed_documents[doc_id].copy()
            doc["search_score"] = score
            results.append(doc)
            
        return results

    def get_document_count(self) -> int:
        """Get total number of indexed documents.
        
        Returns:
            Number of indexed documents
        """
        return len(self.indexed_documents)


class DocumentValidator:
    """Validator for document content and metadata."""

    def __init__(self):
        """Initialize the document validator."""
        self.validation_rules: dict[str, callable] = {}

    def register_validation_rule(self, name: str, rule: callable) -> None:
        """Register a validation rule.
        
        Args:
            name: Name of the rule
            rule: Validation function that returns bool
        """
        self.validation_rules[name] = rule

    def validate_document(self, document: dict[str, Any]) -> dict[str, Any]:
        """Validate a document.
        
        Args:
            document: Document to validate
            
        Returns:
            Validation result
        """
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }

        # Basic validation
        if not document.get("content"):
            validation_result["is_valid"] = False
            validation_result["errors"].append("Document content is empty")

        if not document.get("title"):
            validation_result["warnings"].append("Document title is missing")

        # Run custom validation rules
        for rule_name, rule_func in self.validation_rules.items():
            try:
                if not rule_func(document):
                    validation_result["is_valid"] = False
                    validation_result["errors"].append(f"Validation rule failed: {rule_name}")
            except Exception as e:
                validation_result["warnings"].append(f"Validation rule error: {rule_name} - {e}")

        return validation_result

    def is_valid_document(self, document: dict[str, Any]) -> bool:
        """Check if a document is valid.
        
        Args:
            document: Document to check
            
        Returns:
            True if document is valid
        """
        result = self.validate_document(document)
        return result["is_valid"]
