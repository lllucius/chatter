"""New simplified document API endpoints using the clean embedding pipeline.

This replaces the complex document API with a clean, simple implementation.
NO backwards compatibility - completely new design.
"""

from typing import Any

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.api.auth import get_current_user
from chatter.models.user import User
from chatter.schemas.document import (
    DocumentCreate,
    DocumentListRequest,
    DocumentResponse,
    DocumentSearchRequest,
    DocumentStatsResponse,
    SearchResultResponse,
)
from chatter.services.new_document_service import (
    DocumentServiceError,
    NewDocumentService,
)
from chatter.utils.database import get_session_generator
from chatter.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: str | None = Form(None),
    description: str | None = Form(None),
    tags: str | None = Form(None),  # JSON string of tags list
    chunk_size: int = Form(1000),
    chunk_overlap: int = Form(200),
    is_public: bool = Form(False),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_generator),
) -> DocumentResponse:
    """Upload and process a new document.

    This endpoint uploads a file, creates a document record, and starts
    the embedding processing pipeline asynchronously.
    """
    try:
        # Parse tags if provided
        parsed_tags = None
        if tags:
            try:
                import json

                parsed_tags = json.loads(tags)
            except json.JSONDecodeError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, from e
                    detail="Invalid tags format. Must be valid JSON array.",
                ) from e

        # Create document request
        document_data = DocumentCreate(
            title=title,
            description=description,
            tags=parsed_tags,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            is_public=is_public,
        )

        # Create document using new service
        service = NewDocumentService(session)
        document = await service.create_document(
            user_id=current_user.id,
            upload_file=file,
            document_data=document_data,
        )

        logger.info(
            "Document uploaded successfully",
            document_id=document.id,
            filename=file.filename,
            user_id=current_user.id,
        )

        return DocumentResponse.model_validate(document)

    except DocumentServiceError as e:
        logger.error("Document upload failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e) from e
        ) from e
    except Exception as e:
        logger.error(
            "Unexpected error in document upload", error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, from e
            detail="Internal server error",
        ) from e


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_generator),
) -> DocumentResponse:
    """Get a document by ID."""
    try:
        service = NewDocumentService(session)
        document = await service.get_document(
            document_id, current_user.id
        )

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, from e
                detail="Document not found",
            )

        return DocumentResponse.model_validate(document)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error getting document",
            document_id=document_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error", from e
        ) from e


@router.get("", response_model=dict)
async def list_documents_get(
    limit: int = 10,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_generator),
) -> dict[str, Any]:
    """List documents with pagination (GET endpoint for frontend compatibility)."""
    try:
        from chatter.schemas.document import DocumentListRequest

        # Create request object from query parameters
        list_request = DocumentListRequest(limit=limit, offset=offset)

        service = NewDocumentService(session)
        documents, total_count = await service.list_documents(
            current_user.id, list_request
        )

        return {
            "documents": [
                DocumentResponse.model_validate(doc)
                for doc in documents
            ],
            "total_count": total_count,
            "offset": offset,
            "limit": limit,
        }

    except Exception as e:
        logger.error("Error listing documents", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, from e
            detail="Internal server error",
        )


@router.post("/list")
async def list_documents_post(
    list_request: DocumentListRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_generator),
) -> dict[str, Any]:
    """List documents with filtering and pagination (POST endpoint for advanced filtering)."""
    try:
        service = NewDocumentService(session)
        documents, total_count = await service.list_documents(
            current_user.id, list_request
        )

        return {
            "documents": [
                DocumentResponse.model_validate(doc)
                for doc in documents
            ],
            "total_count": total_count,
            "offset": list_request.offset,
            "limit": list_request.limit,
        }

    except Exception as e:
        logger.error("Error listing documents", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error", from e
        )


@router.post("/search", response_model=list[SearchResultResponse])
async def search_documents(
    search_request: DocumentSearchRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_generator),
) -> list[SearchResultResponse]:
    """Search documents using semantic similarity."""
    try:
        service = NewDocumentService(session)
        results = await service.search_documents(
            current_user.id, search_request
        )

        return [
            SearchResultResponse(
                chunk_id=chunk.id,
                document_id=document.id,
                content=chunk.content,
                similarity_score=similarity_score,
                document_title=document.title,
                document_filename=document.original_filename,
                chunk_index=chunk.chunk_index,
            )
            for chunk, similarity_score, document in results
        ]

    except Exception as e:
        logger.error("Error searching documents", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, from e
            detail="Internal server error",
        )


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_generator),
) -> dict[str, str]:
    """Delete a document."""
    try:
        service = NewDocumentService(session)
        success = await service.delete_document(
            document_id, current_user.id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, from e
                detail="Document not found",
            )

        return {"message": "Document deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error deleting document",
            document_id=document_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error", from e
        )


@router.post("/{document_id}/reprocess")
async def reprocess_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_generator),
) -> dict[str, str]:
    """Reprocess a document through the embedding pipeline."""
    try:
        service = NewDocumentService(session)
        success = await service.reprocess_document(
            document_id, current_user.id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, from e
                detail="Document not found or cannot be reprocessed",
            )

        return {"message": "Document reprocessing started"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error reprocessing document",
            document_id=document_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error", from e
        )


@router.get("/stats/user", response_model=DocumentStatsResponse)
async def get_user_document_stats(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_generator),
) -> DocumentStatsResponse:
    """Get document statistics for the current user."""
    try:
        service = NewDocumentService(session)
        stats = await service.get_document_stats(current_user.id)

        return DocumentStatsResponse(**stats)

    except Exception as e:
        logger.error("Error getting document stats", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error", from e
        )
