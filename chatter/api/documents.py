"""Document management endpoints."""


from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.api.auth import get_current_user
from chatter.core.documents import DocumentError, DocumentService
from chatter.models.user import User
from chatter.schemas.common import PaginationRequest, SortingRequest
from chatter.schemas.document import (
    DocumentChunkResponse,
    DocumentCreate,
    DocumentDeleteRequest,
    DocumentGetRequest,
    DocumentListRequest,
    DocumentListResponse,
    DocumentProcessingRequest,
    DocumentProcessingResponse,
    DocumentResponse,
    DocumentSearchRequest,
    DocumentSearchResponse,
    DocumentSearchResult,
    DocumentStatsRequest,
    DocumentStatsResponse,
    DocumentUpdate,
)
from chatter.utils.database import get_session
from chatter.utils.logging import get_logger
from chatter.utils.problem import (
    BadRequestProblem,
    InternalServerProblem,
    NotFoundProblem,
    ProblemException,
    ValidationProblem,
)

logger = get_logger(__name__)
router = APIRouter()


async def get_document_service(session: AsyncSession = Depends(get_session)) -> DocumentService:
    """Get document service instance."""
    return DocumentService(session)


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(None),
    description: str = Form(None),
    tags: str = Form(None),  # JSON string
    chunk_size: int = Form(1000),
    chunk_overlap: int = Form(200),
    is_public: bool = Form(False),
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service)
) -> DocumentResponse:
    """Upload a document.

    Args:
        file: Document file to upload
        title: Document title
        description: Document description
        tags: Document tags (JSON array string)
        chunk_size: Text chunk size for processing
        chunk_overlap: Text chunk overlap
        is_public: Whether document is public
        current_user: Current authenticated user
        document_service: Document service

    Returns:
        Created document information
    """
    try:
        # Parse tags if provided
        parsed_tags = None
        if tags:
            import json
            try:
                parsed_tags = json.loads(tags)
            except json.JSONDecodeError:
                # Fallback: split by comma
                parsed_tags = [tag.strip() for tag in tags.split(",") if tag.strip()]

        # Create document data
        document_data = DocumentCreate(
            title=title,
            description=description,
            tags=parsed_tags,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            is_public=is_public,
        )

        # Create document
        document = await document_service.create_document(
            current_user.id, file, document_data
        )

        return DocumentResponse.model_validate(document)

    except DocumentError as e:
        raise BadRequestProblem(
            detail=str(e)
        )
    except Exception as e:
        logger.error("Document upload failed", error=str(e))
        raise InternalServerProblem(
            detail="Failed to upload document"
        )


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    request: DocumentListRequest = Depends(),
    pagination: PaginationRequest = Depends(),
    sorting: SortingRequest = Depends(),
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service)
) -> DocumentListResponse:
    """List user's documents.

    Args:
        request: List request parameters
        pagination: Pagination parameters
        sorting: Sorting parameters
        current_user: Current authenticated user
        document_service: Document service

    Returns:
        List of documents with pagination info
    """
    try:
        # Get documents
        documents, total_count = await document_service.list_documents(
            current_user.id, request, pagination, sorting
        )

        return DocumentListResponse(
            documents=[DocumentResponse.model_validate(doc) for doc in documents],
            total_count=total_count,
            limit=pagination.limit,
            offset=pagination.offset,
        )

    except Exception as e:
        logger.error("Failed to list documents", error=str(e))
        raise InternalServerProblem(
            detail="Failed to list documents"
        )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    request: DocumentGetRequest = Depends(),
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service)
) -> DocumentResponse:
    """Get document details.

    Args:
        document_id: Document ID
        request: Get request parameters
        current_user: Current authenticated user
        document_service: Document service

    Returns:
        Document information
    """
    try:
        document = await document_service.get_document(document_id, current_user.id)

        if not document:
            raise NotFoundProblem(
                detail="Document not found",
                resource_type="document",
                resource_id=document_id
            )

        return DocumentResponse.model_validate(document)

    except (NotFoundProblem, ValidationProblem):
        raise
    except Exception as e:
        logger.error("Failed to get document", document_id=document_id, error=str(e))
        raise InternalServerProblem(
            detail="Failed to get document",
            error_id=document_id
        )


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    update_data: DocumentUpdate,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service)
) -> DocumentResponse:
    """Update document metadata.

    Args:
        document_id: Document ID
        update_data: Update data
        current_user: Current authenticated user
        document_service: Document service

    Returns:
        Updated document information
    """
    try:
        document = await document_service.update_document(
            document_id, current_user.id, update_data
        )

        if not document:
            raise NotFoundProblem(
                detail="Document not found",
                resource_type="document",
                resource_id=document_id
            )

        return DocumentResponse.model_validate(document)

    except ProblemException:
        raise
    except Exception as e:
        logger.error("Failed to update document", document_id=document_id, error=str(e))
        raise InternalServerProblem(
            detail="Failed to update document"
        )


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    request: DocumentDeleteRequest = Depends(),
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service)
) -> dict:
    """Delete document.

    Args:
        document_id: Document ID
        request: Delete request parameters
        current_user: Current authenticated user
        document_service: Document service

    Returns:
        Success message
    """
    try:
        success = await document_service.delete_document(document_id, current_user.id)

        if not success:
            raise NotFoundProblem(
                detail="Document not found",
                resource_type="document",
                resource_id=document_id
            )

        return {"message": "Document deleted successfully"}

    except ProblemException:
        raise
    except Exception as e:
        logger.error("Failed to delete document", document_id=document_id, error=str(e))
        raise InternalServerProblem(
            detail="Failed to delete document"
        )


@router.post("/search", response_model=DocumentSearchResponse)
async def search_documents(
    search_request: DocumentSearchRequest,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service)
) -> DocumentSearchResponse:
    """Search documents using vector similarity.

    Args:
        search_request: Search request
        current_user: Current authenticated user
        document_service: Document service

    Returns:
        Search results
    """
    try:
        # Perform search
        search_results = await document_service.search_documents(
            current_user.id, search_request
        )

        # Format results
        results = []
        for chunk, score, document in search_results:
            result = DocumentSearchResult(
                document_id=document.id,
                chunk_id=chunk.id,
                score=score,
                content=chunk.content,
                metadata=chunk.extra_metadata,
                document=DocumentResponse.model_validate(document)
            )
            results.append(result)

        return DocumentSearchResponse(
            results=results,
            total_results=len(results),
            query=search_request.query,
            score_threshold=search_request.score_threshold,
        )

    except Exception as e:
        logger.error("Document search failed", error=str(e))
        raise InternalServerProblem(
            detail="Document search failed"
        )


@router.get("/{document_id}/chunks", response_model=list[DocumentChunkResponse])
async def get_document_chunks(
    document_id: str,
    request: DocumentGetRequest = Depends(),
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service)
) -> list[DocumentChunkResponse]:
    """Get document chunks.

    Args:
        document_id: Document ID
        request: Get request parameters
        current_user: Current authenticated user
        document_service: Document service

    Returns:
        List of document chunks
    """
    try:
        chunks = await document_service.get_document_chunks(document_id, current_user.id)

        return [DocumentChunkResponse.model_validate(chunk) for chunk in chunks]

    except Exception as e:
        logger.error("Failed to get document chunks", document_id=document_id, error=str(e))
        raise InternalServerProblem(
            detail="Failed to get document chunks"
        )


@router.post("/{document_id}/process", response_model=DocumentProcessingResponse)
async def process_document(
    document_id: str,
    processing_request: DocumentProcessingRequest,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service)
) -> DocumentProcessingResponse:
    """Trigger document processing.

    Args:
        document_id: Document ID
        processing_request: Processing request
        current_user: Current authenticated user
        document_service: Document service

    Returns:
        Processing status
    """
    try:
        success = await document_service.process_document(
            document_id, current_user.id, processing_request
        )

        if not success:
            raise NotFoundProblem(
                detail="Document not found or processing failed",
                resource_type="document",
                resource_id=document_id
            )

        return DocumentProcessingResponse(
            document_id=document_id,
            status="processing",
            message="Document processing started successfully",
            processing_started_at=None,  # Would be filled by service
        )

    except ProblemException:
        raise
    except Exception as e:
        logger.error("Failed to process document", document_id=document_id, error=str(e))
        raise InternalServerProblem(
            detail="Failed to process document"
        )


@router.get("/stats/overview", response_model=DocumentStatsResponse)
async def get_document_stats(
    request: DocumentStatsRequest = Depends(),
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service)
) -> DocumentStatsResponse:
    """Get document statistics.

    Args:
        request: Stats request parameters
        current_user: Current authenticated user
        document_service: Document service

    Returns:
        Document statistics
    """
    try:
        stats = await document_service.get_document_stats(current_user.id)

        return DocumentStatsResponse(
            total_documents=stats.get("total_documents", 0),
            total_chunks=stats.get("total_chunks", 0),
            total_size_bytes=stats.get("total_storage_bytes", 0),
            documents_by_status=stats.get("status_counts", {}),
            documents_by_type=stats.get("type_counts", {}),
            processing_stats=stats.get("processing_stats", {}),
        )

    except Exception as e:
        logger.error("Failed to get document stats", error=str(e))
        raise InternalServerProblem(
            detail="Failed to get document stats"
        )
