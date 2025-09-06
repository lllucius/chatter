"""Model and embedding registry endpoints."""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
    status,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.api.auth import get_current_user
from chatter.core.model_registry import ListParams, ModelRegistryService
from chatter.models.registry import ModelType
from chatter.models.user import User
from chatter.schemas.model_registry import (
    DefaultProvider,
    EmbeddingSpaceCreate,
    EmbeddingSpaceDefaultResponse,
    EmbeddingSpaceDeleteResponse,
    EmbeddingSpaceList,
    EmbeddingSpaceUpdate,
    EmbeddingSpaceWithModel,
    ModelDefaultResponse,
    ModelDefCreate,
    ModelDefList,
    ModelDefUpdate,
    ModelDefWithProvider,
    ModelDeleteResponse,
    Provider,
    ProviderCreate,
    ProviderDefaultResponse,
    ProviderDeleteResponse,
    ProviderList,
    ProviderUpdate,
)
from chatter.utils.database import get_session_generator
from chatter.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


# Provider endpoints
@router.get("/providers", response_model=ProviderList)
async def list_providers(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(
        20, ge=1, le=100, description="Items per page"
    ),
    active_only: bool = Query(
        True, description="Show only active providers"
    ),
    session: AsyncSession = Depends(get_session_generator),
    current_user: User = Depends(get_current_user),
):
    """List all providers."""
    service = ModelRegistryService(session)
    params = ListParams(
        page=page, per_page=per_page, active_only=active_only
    )

    providers, total = await service.list_providers(params)

    return ProviderList(
        providers=providers,  # Can use sequence directly
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/providers/{provider_id}", response_model=Provider)
async def get_provider(
    provider_id: str,
    session: AsyncSession = Depends(get_session_generator),
    current_user: User = Depends(get_current_user),
):
    """Get a specific provider."""
    service = ModelRegistryService(session)
    provider = await service.get_provider(provider_id)

    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider not found",
        )

    return provider


@router.post(
    "/providers",
    response_model=Provider,
    status_code=status.HTTP_201_CREATED,
)
async def create_provider(
    provider_data: ProviderCreate,
    request: Request,
    session: AsyncSession = Depends(get_session_generator),
    current_user: User = Depends(get_current_user),
):
    """Create a new provider."""
    from chatter.utils.audit_logging import (
        AuditEventType,
        AuditResult,
        get_audit_logger,
    )

    service = ModelRegistryService(session)
    audit_logger = get_audit_logger(session)

    try:
        # Check if provider name already exists
        existing = await service.get_provider_by_name(
            provider_data.name
        )
        if existing:
            await audit_logger.log_event(
                event_type=AuditEventType.PROVIDER_CREATE,
                result=AuditResult.FAILURE,
                user_id=current_user.id,
                details={
                    "provider_name": provider_data.name,
                    "error": "name_already_exists",
                },
                request=request,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provider with this name already exists",
            )

        provider = await service.create_provider(provider_data)

        # Log successful creation
        await audit_logger.log_provider_create(
            provider_id=provider.id,
            provider_name=provider.name,
            user_id=current_user.id,
            request=request,
            success=True,
        )

        logger.info(
            "Created provider",
            provider_id=provider.id,
            provider_name=provider.name,
            user_id=current_user.id,
        )

        return provider

    except HTTPException:
        raise
    except Exception as e:
        # Log failed creation
        await audit_logger.log_provider_create(
            provider_id="unknown",
            provider_name=provider_data.name,
            user_id=current_user.id,
            request=request,
            success=False,
            error_message=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create provider",
        ) from e


@router.put("/providers/{provider_id}", response_model=Provider)
async def update_provider(
    provider_id: str,
    provider_data: ProviderUpdate,
    session: AsyncSession = Depends(get_session_generator),
    current_user: User = Depends(get_current_user),
):
    """Update a provider."""
    from chatter.core.exceptions import ValidationError

    service = ModelRegistryService(session)

    try:
        provider = await service.update_provider(
            provider_id, provider_data
        )

        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Provider not found",
            )

        logger.info(
            "Updated provider",
            provider_id=provider.id,
            provider_name=provider.name,
            user_id=current_user.id,
        )

        return provider

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.delete(
    "/providers/{provider_id}", response_model=ProviderDeleteResponse
)
async def delete_provider(
    provider_id: str,
    session: AsyncSession = Depends(get_session_generator),
    current_user: User = Depends(get_current_user),
) -> ProviderDeleteResponse:
    """Delete a provider and all its dependent models and embedding spaces."""
    service = ModelRegistryService(session)
    try:
        deleted = await service.delete_provider(provider_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Provider not found",
            )

        logger.info(
            "Deleted provider and its dependencies",
            provider_id=provider_id,
            user_id=current_user.id,
        )

        return ProviderDeleteResponse(
            message="Provider and its dependent models/embedding spaces deleted successfully"
        )
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete provider due to existing dependencies",
        ) from e


@router.post(
    "/providers/{provider_id}/set-default",
    response_model=ProviderDefaultResponse,
)
async def set_default_provider(
    provider_id: str,
    default_data: DefaultProvider,
    session: AsyncSession = Depends(get_session_generator),
    current_user: User = Depends(get_current_user),
) -> ProviderDefaultResponse:
    """Set a provider as default for a model type."""

    service = ModelRegistryService(session)

    try:
        success = await service.set_default_provider(
            provider_id, default_data.model_type
        )

        if not success:
            # Check if provider exists
            provider = await service.get_provider(provider_id)
            if not provider:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Provider not found",
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Provider {provider.name} has no active models of type {default_data.model_type}",
                )

        logger.info(
            "Set default provider",
            provider_id=provider_id,
            model_type=default_data.model_type,
            user_id=current_user.id,
        )

        return ProviderDefaultResponse(
            message="Default provider set successfully"
        )

    except Exception as e:
        logger.error(
            "Failed to set default provider",
            provider_id=provider_id,
            model_type=default_data.model_type,
            error=str(e),
            user_id=current_user.id,
        )
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to set default provider",
        ) from e


# Model endpoints
@router.get("/models", response_model=ModelDefList)
async def list_models(
    provider_id: str = Query(None, description="Filter by provider ID"),
    model_type: ModelType = Query(
        None, description="Filter by model type"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(
        20, ge=1, le=100, description="Items per page"
    ),
    active_only: bool = Query(
        True, description="Show only active models"
    ),
    session: AsyncSession = Depends(get_session_generator),
    current_user: User = Depends(get_current_user),
):
    """List all model definitions."""
    service = ModelRegistryService(session)
    params = ListParams(
        page=page, per_page=per_page, active_only=active_only
    )

    models, total = await service.list_models(
        provider_id, model_type, params
    )

    return ModelDefList(
        models=models, total=total, page=page, per_page=per_page
    )


@router.get("/models/{model_id}", response_model=ModelDefWithProvider)
async def get_model(
    model_id: str,
    session: AsyncSession = Depends(get_session_generator),
    current_user: User = Depends(get_current_user),
):
    """Get a specific model definition."""
    service = ModelRegistryService(session)
    model = await service.get_model(model_id)

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found",
        )

    return model


@router.post(
    "/models",
    response_model=ModelDefWithProvider,
    status_code=status.HTTP_201_CREATED,
)
async def create_model(
    model_data: ModelDefCreate,
    session: AsyncSession = Depends(get_session_generator),
    current_user: User = Depends(get_current_user),
):
    """Create a new model definition."""
    from chatter.core.exceptions import ValidationError

    service = ModelRegistryService(session)

    try:
        # Check if model name already exists for this provider
        existing = await service.get_model_by_name(
            model_data.provider_id, model_data.name
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Model with this name already exists for this provider",
            )

        model = await service.create_model(model_data)

        # Refresh to get provider relationship
        model = await service.get_model(model.id)

        if not model:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve created model",
            )

        logger.info(
            "Created model",
            model_id=model.id,
            model_name=model.name,
            provider_id=model.provider_id,
            user_id=current_user.id,
        )

        return model

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        await session.rollback()
        logger.error(
            "Failed to create model",
            model_name=model_data.name,
            provider_id=model_data.provider_id,
            error=str(e),
            user_id=current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create model",
        ) from e


@router.put("/models/{model_id}", response_model=ModelDefWithProvider)
async def update_model(
    model_id: str,
    model_data: ModelDefUpdate,
    session: AsyncSession = Depends(get_session_generator),
    current_user: User = Depends(get_current_user),
):
    """Update a model definition."""
    from chatter.core.exceptions import ValidationError

    service = ModelRegistryService(session)

    try:
        model = await service.update_model(model_id, model_data)

        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Model not found",
            )

        # Refresh to get provider relationship
        model = await service.get_model(model.id)

        if not model:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve updated model",
            )

        logger.info(
            "Updated model",
            model_id=model.id,
            model_name=model.name,
            user_id=current_user.id,
        )

        return model

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.delete("/models/{model_id}", response_model=ModelDeleteResponse)
async def delete_model(
    model_id: str,
    session: AsyncSession = Depends(get_session_generator),
    current_user: User = Depends(get_current_user),
) -> ModelDeleteResponse:
    """Delete a model definition and its dependent embedding spaces."""
    service = ModelRegistryService(session)
    try:
        deleted = await service.delete_model(model_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Model not found",
            )

        logger.info(
            "Deleted model and its dependencies",
            model_id=model_id,
            user_id=current_user.id,
        )

        return ModelDeleteResponse(
            message="Model and its dependent embedding spaces deleted successfully"
        )
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete model due to existing dependencies",
        ) from e


@router.post(
    "/models/{model_id}/set-default",
    response_model=ModelDefaultResponse,
)
async def set_default_model(
    model_id: str,
    session: AsyncSession = Depends(get_session_generator),
    current_user: User = Depends(get_current_user),
) -> ModelDefaultResponse:
    """Set a model as default for its type."""
    service = ModelRegistryService(session)
    success = await service.set_default_model(model_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found",
        )

    logger.info(
        "Set default model", model_id=model_id, user_id=current_user.id
    )

    return ModelDefaultResponse(
        message="Default model set successfully"
    )


# Embedding space endpoints
@router.get("/embedding-spaces", response_model=EmbeddingSpaceList)
async def list_embedding_spaces(
    model_id: str = Query(None, description="Filter by model ID"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(
        20, ge=1, le=100, description="Items per page"
    ),
    active_only: bool = Query(
        True, description="Show only active spaces"
    ),
    session: AsyncSession = Depends(get_session_generator),
    current_user: User = Depends(get_current_user),
):
    """List all embedding spaces."""
    service = ModelRegistryService(session)
    params = ListParams(
        page=page, per_page=per_page, active_only=active_only
    )

    spaces, total = await service.list_embedding_spaces(
        model_id, params
    )

    return EmbeddingSpaceList(
        spaces=spaces, total=total, page=page, per_page=per_page
    )


@router.get(
    "/embedding-spaces/{space_id}",
    response_model=EmbeddingSpaceWithModel,
)
async def get_embedding_space(
    space_id: str,
    session: AsyncSession = Depends(get_session_generator),
    current_user: User = Depends(get_current_user),
):
    """Get a specific embedding space."""
    service = ModelRegistryService(session)
    space = await service.get_embedding_space(space_id)

    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Embedding space not found",
        )

    return space


@router.post(
    "/embedding-spaces",
    response_model=EmbeddingSpaceWithModel,
    status_code=status.HTTP_201_CREATED,
)
async def create_embedding_space(
    space_data: EmbeddingSpaceCreate,
    session: AsyncSession = Depends(get_session_generator),
    current_user: User = Depends(get_current_user),
):
    """Create a new embedding space with backing table and index."""
    from chatter.core.exceptions import ValidationError

    service = ModelRegistryService(session)

    try:
        # Check if space name already exists
        existing = await service.get_embedding_space_by_name(
            space_data.name
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Embedding space with this name already exists",
            )

        # Check if table name already exists
        existing_table = (
            await service.get_embedding_space_by_table_name(
                space_data.table_name
            )
        )
        if existing_table:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Embedding space with this table name already exists",
            )

        # Get user ID before any potential rollback
        user_id = current_user.id

        space = await service.create_embedding_space(space_data)

        # Refresh to get full relationships
        space = await service.get_embedding_space(space.id)

        if not space:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve created embedding space",
            )

        logger.info(
            "Created embedding space",
            space_id=space.id,
            space_name=space.name,
            table_name=space.table_name,
            model_id=space.model_id,
            user_id=user_id,
        )

        return space

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(
            "Failed to create embedding space",
            space_name=space_data.name,
            error=str(e),
            user_id=current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create embedding space: {str(e)}",
        ) from e


@router.put(
    "/embedding-spaces/{space_id}",
    response_model=EmbeddingSpaceWithModel,
)
async def update_embedding_space(
    space_id: str,
    space_data: EmbeddingSpaceUpdate,
    session: AsyncSession = Depends(get_session_generator),
    current_user: User = Depends(get_current_user),
):
    """Update an embedding space."""
    service = ModelRegistryService(session)
    space = await service.update_embedding_space(space_id, space_data)

    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Embedding space not found",
        )

    # Refresh to get full relationships
    space = await service.get_embedding_space(space.id)

    if not space:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve updated embedding space",
        )

    logger.info(
        "Updated embedding space",
        space_id=space.id,
        space_name=space.name,
        user_id=current_user.id,
    )

    return space


@router.delete(
    "/embedding-spaces/{space_id}",
    response_model=EmbeddingSpaceDeleteResponse,
)
async def delete_embedding_space(
    space_id: str,
    session: AsyncSession = Depends(get_session_generator),
    current_user: User = Depends(get_current_user),
) -> EmbeddingSpaceDeleteResponse:
    """Delete an embedding space (does not drop the table)."""
    service = ModelRegistryService(session)
    deleted = await service.delete_embedding_space(space_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Embedding space not found",
        )

    logger.info(
        "Deleted embedding space",
        space_id=space_id,
        user_id=current_user.id,
    )

    return EmbeddingSpaceDeleteResponse(
        message="Embedding space deleted successfully"
    )


@router.post(
    "/embedding-spaces/{space_id}/set-default",
    response_model=EmbeddingSpaceDefaultResponse,
)
async def set_default_embedding_space(
    space_id: str,
    session: AsyncSession = Depends(get_session_generator),
    current_user: User = Depends(get_current_user),
) -> EmbeddingSpaceDefaultResponse:
    """Set an embedding space as default."""
    service = ModelRegistryService(session)
    success = await service.set_default_embedding_space(space_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Embedding space not found",
        )

    logger.info(
        "Set default embedding space",
        space_id=space_id,
        user_id=current_user.id,
    )

    return EmbeddingSpaceDefaultResponse(
        message="Default embedding space set successfully"
    )


# Default lookup endpoints
@router.get("/defaults/provider/{model_type}", response_model=Provider)
async def get_default_provider(
    model_type: ModelType,
    session: AsyncSession = Depends(get_session_generator),
    current_user: User = Depends(get_current_user),
):
    """Get the default provider for a model type."""
    service = ModelRegistryService(session)
    provider = await service.get_default_provider(model_type)

    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No default provider found for {model_type}",
        )

    return provider


@router.get(
    "/defaults/model/{model_type}", response_model=ModelDefWithProvider
)
async def get_default_model(
    model_type: ModelType,
    session: AsyncSession = Depends(get_session_generator),
    current_user: User = Depends(get_current_user),
):
    """Get the default model for a type."""
    service = ModelRegistryService(session)
    model = await service.get_default_model(model_type)

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No default model found for {model_type}",
        )

    return model


@router.get(
    "/defaults/embedding-space", response_model=EmbeddingSpaceWithModel
)
async def get_default_embedding_space(
    session: AsyncSession = Depends(get_session_generator),
    current_user: User = Depends(get_current_user),
):
    """Get the default embedding space."""
    service = ModelRegistryService(session)
    space = await service.get_default_embedding_space()

    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No default embedding space found",
        )

    return space
