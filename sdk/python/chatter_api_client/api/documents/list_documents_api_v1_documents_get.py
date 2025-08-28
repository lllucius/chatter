from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.document_list_response import DocumentListResponse
from ...models.document_status import DocumentStatus
from ...models.document_type import DocumentType
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    status: Union[DocumentStatus, None, Unset] = UNSET,
    document_type: Union[DocumentType, None, Unset] = UNSET,
    tags: Union[None, Unset, list[str]] = UNSET,
    owner_id: Union[None, Unset, str] = UNSET,
    limit: Union[Unset, int] = 50,
    offset: Union[Unset, int] = 0,
    sort_by: Union[Unset, str] = "created_at",
    sort_order: Union[Unset, str] = "desc",
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_status: Union[None, Unset, str]
    if isinstance(status, Unset):
        json_status = UNSET
    elif isinstance(status, DocumentStatus):
        json_status = status.value
    else:
        json_status = status
    params["status"] = json_status

    json_document_type: Union[None, Unset, str]
    if isinstance(document_type, Unset):
        json_document_type = UNSET
    elif isinstance(document_type, DocumentType):
        json_document_type = document_type.value
    else:
        json_document_type = document_type
    params["document_type"] = json_document_type

    json_tags: Union[None, Unset, list[str]]
    if isinstance(tags, Unset):
        json_tags = UNSET
    elif isinstance(tags, list):
        json_tags = tags

    else:
        json_tags = tags
    params["tags"] = json_tags

    json_owner_id: Union[None, Unset, str]
    if isinstance(owner_id, Unset):
        json_owner_id = UNSET
    else:
        json_owner_id = owner_id
    params["owner_id"] = json_owner_id

    params["limit"] = limit

    params["offset"] = offset

    params["sort_by"] = sort_by

    params["sort_order"] = sort_order

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/documents",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, DocumentListResponse]]:
    if response.status_code == 200:
        response_200 = DocumentListResponse.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = cast(Any, None)
        return response_401

    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403

    if response.status_code == 422:
        response_422 = cast(Any, None)
        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, DocumentListResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    status: Union[DocumentStatus, None, Unset] = UNSET,
    document_type: Union[DocumentType, None, Unset] = UNSET,
    tags: Union[None, Unset, list[str]] = UNSET,
    owner_id: Union[None, Unset, str] = UNSET,
    limit: Union[Unset, int] = 50,
    offset: Union[Unset, int] = 0,
    sort_by: Union[Unset, str] = "created_at",
    sort_order: Union[Unset, str] = "desc",
) -> Response[Union[Any, DocumentListResponse]]:
    """List Documents

     List user's documents.

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

    Args:
        status (Union[DocumentStatus, None, Unset]): Filter by status
        document_type (Union[DocumentType, None, Unset]): Filter by document type
        tags (Union[None, Unset, list[str]]): Filter by tags
        owner_id (Union[None, Unset, str]): Filter by owner (admin only)
        limit (Union[Unset, int]): Maximum number of results Default: 50.
        offset (Union[Unset, int]): Number of results to skip Default: 0.
        sort_by (Union[Unset, str]): Sort field Default: 'created_at'.
        sort_order (Union[Unset, str]): Sort order Default: 'desc'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, DocumentListResponse]]
    """

    kwargs = _get_kwargs(
        status=status,
        document_type=document_type,
        tags=tags,
        owner_id=owner_id,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    status: Union[DocumentStatus, None, Unset] = UNSET,
    document_type: Union[DocumentType, None, Unset] = UNSET,
    tags: Union[None, Unset, list[str]] = UNSET,
    owner_id: Union[None, Unset, str] = UNSET,
    limit: Union[Unset, int] = 50,
    offset: Union[Unset, int] = 0,
    sort_by: Union[Unset, str] = "created_at",
    sort_order: Union[Unset, str] = "desc",
) -> Optional[Union[Any, DocumentListResponse]]:
    """List Documents

     List user's documents.

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

    Args:
        status (Union[DocumentStatus, None, Unset]): Filter by status
        document_type (Union[DocumentType, None, Unset]): Filter by document type
        tags (Union[None, Unset, list[str]]): Filter by tags
        owner_id (Union[None, Unset, str]): Filter by owner (admin only)
        limit (Union[Unset, int]): Maximum number of results Default: 50.
        offset (Union[Unset, int]): Number of results to skip Default: 0.
        sort_by (Union[Unset, str]): Sort field Default: 'created_at'.
        sort_order (Union[Unset, str]): Sort order Default: 'desc'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, DocumentListResponse]
    """

    return sync_detailed(
        client=client,
        status=status,
        document_type=document_type,
        tags=tags,
        owner_id=owner_id,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    status: Union[DocumentStatus, None, Unset] = UNSET,
    document_type: Union[DocumentType, None, Unset] = UNSET,
    tags: Union[None, Unset, list[str]] = UNSET,
    owner_id: Union[None, Unset, str] = UNSET,
    limit: Union[Unset, int] = 50,
    offset: Union[Unset, int] = 0,
    sort_by: Union[Unset, str] = "created_at",
    sort_order: Union[Unset, str] = "desc",
) -> Response[Union[Any, DocumentListResponse]]:
    """List Documents

     List user's documents.

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

    Args:
        status (Union[DocumentStatus, None, Unset]): Filter by status
        document_type (Union[DocumentType, None, Unset]): Filter by document type
        tags (Union[None, Unset, list[str]]): Filter by tags
        owner_id (Union[None, Unset, str]): Filter by owner (admin only)
        limit (Union[Unset, int]): Maximum number of results Default: 50.
        offset (Union[Unset, int]): Number of results to skip Default: 0.
        sort_by (Union[Unset, str]): Sort field Default: 'created_at'.
        sort_order (Union[Unset, str]): Sort order Default: 'desc'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, DocumentListResponse]]
    """

    kwargs = _get_kwargs(
        status=status,
        document_type=document_type,
        tags=tags,
        owner_id=owner_id,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    status: Union[DocumentStatus, None, Unset] = UNSET,
    document_type: Union[DocumentType, None, Unset] = UNSET,
    tags: Union[None, Unset, list[str]] = UNSET,
    owner_id: Union[None, Unset, str] = UNSET,
    limit: Union[Unset, int] = 50,
    offset: Union[Unset, int] = 0,
    sort_by: Union[Unset, str] = "created_at",
    sort_order: Union[Unset, str] = "desc",
) -> Optional[Union[Any, DocumentListResponse]]:
    """List Documents

     List user's documents.

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

    Args:
        status (Union[DocumentStatus, None, Unset]): Filter by status
        document_type (Union[DocumentType, None, Unset]): Filter by document type
        tags (Union[None, Unset, list[str]]): Filter by tags
        owner_id (Union[None, Unset, str]): Filter by owner (admin only)
        limit (Union[Unset, int]): Maximum number of results Default: 50.
        offset (Union[Unset, int]): Number of results to skip Default: 0.
        sort_by (Union[Unset, str]): Sort field Default: 'created_at'.
        sort_order (Union[Unset, str]): Sort order Default: 'desc'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, DocumentListResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            status=status,
            document_type=document_type,
            tags=tags,
            owner_id=owner_id,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    ).parsed
