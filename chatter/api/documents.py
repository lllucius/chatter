"""Document management endpoints."""

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.api.auth import get_current_user
from chatter.core.documents import DocumentError, DocumentService
from chatter.models.document import DocumentStatus, DocumentType
from chatter.models.user import User
from chatter.schemas.common import PaginationRequest, SortingRequest
from chatter.schemas.document import (
    DocumentChunkResponse,
    DocumentChunksResponse,
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


async def get_document_service(
    session: AsyncSession = Depends(get_session)
) -> DocumentService:
    """Get document service instance."""
    return DocumentService(session)


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(None),
    description: str = Form(None),
    tags: str = Form(None),  # JSON string
    chunk_size: int = Form(1000),
    chunk_overlap: int = Form(200),
    is_public: bool = Form(False),
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
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
                parsed_tags = [
                    tag.strip()
                    for tag in tags.split(",")
                    if tag.strip()
                ]

        # Create document data
        document_data = DocumentCreate(
            title=title,
            description=description,
            tags=parsed_tags,
            extra_metadata=None,  # Add missing parameter
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
        raise BadRequestProblem(detail=str(e)) from None
    except Exception as e:
        logger.error("Document upload failed", error=str(e))
        raise InternalServerProblem(
            detail="Failed to upload document"
        ) from None


@router.get("", response_model=DocumentListResponse, responses={
    401: {"description": "Unauthorized - Invalid or missing authentication token"},
    403: {"description": "Forbidden - User lacks permission to access documents"},
    422: {"description": "Validation Error"},
})
async def list_documents(
    status: DocumentStatus | None = Query(None, description="Filter by status"),
    document_type: DocumentType | None = Query(None, description="Filter by document type"),
    tags: list[str] | None = Query(None, description="Filter by tags"),
    owner_id: str | None = Query(None, description="Filter by owner (admin only)"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
) -> DocumentListResponse:
    """List user's documents.

    Args:
        status: Filter by document status
        document_type: Filter by document type
        tags: Filter by tags
        owner_id: Filter by owner (admin only)
        limit: Maximum number of results
        offset: Number of results to skip
        sort_by: Sort field
        sort_order: Sort order (asc/desc)
        current_user: Current authenticated user
        document_service: Document service

    Returns:
        List of documents with pagination info
    """
    try:
        # Create request object from query parameters
        from chatter.schemas.document import DocumentListRequest
        merged_request = DocumentListRequest(
            status=status,
            document_type=document_type,
            tags=tags,
            owner_id=owner_id,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        # Get documents
        documents, total_count = await document_service.list_documents(
            current_user.id, merged_request
        )

        return DocumentListResponse(
            documents=[
                DocumentResponse.model_validate(doc)
                for doc in documents
            ],
            total_count=total_count,
            limit=limit,
            offset=offset,
        )

    except Exception as e:
        logger.error("Failed to list documents", error=str(e))
        raise InternalServerProblem(
            detail="Failed to list documents"
        ) from None


@router.get("/{document_id}", response_model=DocumentResponse, responses={
    401: {"description": "Unauthorized - Invalid or missing authentication token"},
    403: {"description": "Forbidden - User lacks permission to access this document"},
    404: {"description": "Not Found - Document does not exist"},
    422: {"description": "Validation Error"},
})
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    """Get document details.

    Args:
        document_id: Document ID
        current_user: Current authenticated user
        document_service: Document service

    Returns:
        Document information
    """
    try:
        document = await document_service.get_document(
            document_id, current_user.id
        )

        if not document:
            raise NotFoundProblem(
                detail="Document not found",
                resource_type="document",
                resource_id=document_id,
            ) from None

        response = DocumentResponse.model_validate(document)

        return response

    except (NotFoundProblem, ValidationProblem):
        import traceback
        print(traceback.format_stack())
        raise
    except Exception as e:
        logger.error(
            "Failed to get document",
            document_id=document_id,
            error=str(e),
        )
        raise InternalServerProblem(
            detail="Failed to get document", error_id=document_id
        ) from None


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    update_data: DocumentUpdate,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
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
                resource_id=document_id,
            ) from None

        return DocumentResponse.model_validate(document)

    except ProblemException:
        raise
    except Exception as e:
        logger.error(
            "Failed to update document",
            document_id=document_id,
            error=str(e),
        )
        raise InternalServerProblem(
            detail="Failed to update document"
        ) from None


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    request: DocumentDeleteRequest = Depends(),
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
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
        success = await document_service.delete_document(
            document_id, current_user.id
        )

        if not success:
            raise NotFoundProblem(
                detail="Document not found",
                resource_type="document",
                resource_id=document_id,
            ) from None

        return {"message": "Document deleted successfully"}

    except ProblemException:
        raise
    except Exception as e:
        logger.error(
            "Failed to delete document",
            document_id=document_id,
            error=str(e),
        )
        raise InternalServerProblem(
            detail="Failed to delete document"
        ) from None


@router.post("/search", response_model=DocumentSearchResponse)
async def search_documents(
    search_request: DocumentSearchRequest,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
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
                document=DocumentResponse.model_validate(document),
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
        ) from None


@router.get(
    "/{document_id}/chunks", response_model=DocumentChunksResponse
)
async def get_document_chunks(
    document_id: str,
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
) -> DocumentChunksResponse:
    """Get document chunks.

    Args:
        document_id: Document ID
        limit: Maximum number of results
        offset: Number of results to skip
        current_user: Current authenticated user
        document_service: Document service

    Returns:
        List of document chunks with pagination
    """
    try:
        chunks = await document_service.get_document_chunks(
            document_id, current_user.id
        )

        # Apply pagination manually for now
        total_count = len(chunks)
        start_index = offset
        end_index = start_index + limit
        paginated_chunks = chunks[start_index:end_index]

        return DocumentChunksResponse(
            chunks=[
                DocumentChunkResponse.model_validate(chunk)
                for chunk in paginated_chunks
            ],
            total_count=total_count,
            limit=limit,
            offset=offset,
        )

    except Exception as e:
        logger.error(
            "Failed to get document chunks",
            document_id=document_id,
            error=str(e),
        )
        raise InternalServerProblem(
            detail="Failed to get document chunks"
        ) from None


@router.post(
    "/{document_id}/process", response_model=DocumentProcessingResponse
)
async def process_document(
    document_id: str,
    processing_request: DocumentProcessingRequest,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
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
                resource_id=document_id,
            ) from None

        return DocumentProcessingResponse(
            document_id=document_id,
            status=DocumentStatus.PROCESSING,
            message="Document processing started successfully",
            processing_started_at=None,  # Would be filled by service
        )

    except ProblemException:
        raise
    except Exception as e:
        logger.error(
            "Failed to process document",
            document_id=document_id,
            error=str(e),
        )
        raise InternalServerProblem(
            detail="Failed to process document"
        ) from None


@router.get("/stats/overview", response_model=DocumentStatsResponse)
async def get_document_stats(
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
) -> DocumentStatsResponse:
    """Get document statistics.

    Args:
        current_user: Current authenticated user
        document_service: Document service

    Returns:
        Document statistics
    """
    try:
        stats = await document_service.get_document_stats(
            current_user.id
        )

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
        ) from None


@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
):
    """Download original document file.

    Args:
        document_id: Document ID
        current_user: Current authenticated user
        document_service: Document service

    Returns:
        File download response
    """
    try:
        from fastapi.responses import FileResponse
        file_path = await document_service.get_document_file_path(
            document_id, current_user.id
        )
        
        if not file_path:
            raise NotFoundProblem(
                detail="Document file not found",
                resource_type="document",
                resource_id=document_id,
            ) from None
            
        return FileResponse(
            path=file_path,
            filename=f"document_{document_id}",
            media_type='application/octet-stream'
        )
        
    except ProblemException:
        raise
    except Exception as e:
        logger.error(
            "Failed to download document",
            document_id=document_id,
            error=str(e),
        )
        raise InternalServerProblem(
            detail="Failed to download document"
        ) from None


@router.post("/{document_id}/reprocess", response_model=DocumentProcessingResponse)
async def reprocess_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
) -> DocumentProcessingResponse:
    """Reprocess an existing document.

    Args:
        document_id: Document ID
        current_user: Current authenticated user
        document_service: Document service

    Returns:
        Processing status
    """
    try:
        success = await document_service.reprocess_document(
            document_id, current_user.id
        )

        if not success:
            raise NotFoundProblem(
                detail="Document not found or reprocessing failed",
                resource_type="document",
                resource_id=document_id,
            ) from None

        return DocumentProcessingResponse(
            document_id=document_id,
            status=DocumentStatus.PROCESSING,
            message="Document reprocessing started successfully",
            processing_started_at=None,  # Would be filled by service
        )

    except ProblemException:
        raise
    except Exception as e:
        logger.error(
            "Failed to reprocess document",
            document_id=document_id,
            error=str(e),
        )
        raise InternalServerProblem(
            detail="Failed to reprocess document"
        ) from None
