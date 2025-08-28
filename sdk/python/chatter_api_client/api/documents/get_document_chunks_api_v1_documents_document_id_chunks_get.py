from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.document_chunks_response import DocumentChunksResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    document_id: str,
    *,
    limit: Union[Unset, int] = 50,
    offset: Union[Unset, int] = 0,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["limit"] = limit

    params["offset"] = offset

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v1/documents/{document_id}/chunks",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DocumentChunksResponse, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = DocumentChunksResponse.from_dict(response.json())

        return response_200

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[DocumentChunksResponse, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    document_id: str,
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = 50,
    offset: Union[Unset, int] = 0,
) -> Response[Union[DocumentChunksResponse, HTTPValidationError]]:
    """Get Document Chunks

     Get document chunks.

    Args:
        document_id: Document ID
        limit: Maximum number of results
        offset: Number of results to skip
        current_user: Current authenticated user
        document_service: Document service

    Returns:
        List of document chunks with pagination

    Args:
        document_id (str):
        limit (Union[Unset, int]): Maximum number of results Default: 50.
        offset (Union[Unset, int]): Number of results to skip Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DocumentChunksResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        document_id=document_id,
        limit=limit,
        offset=offset,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    document_id: str,
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = 50,
    offset: Union[Unset, int] = 0,
) -> Optional[Union[DocumentChunksResponse, HTTPValidationError]]:
    """Get Document Chunks

     Get document chunks.

    Args:
        document_id: Document ID
        limit: Maximum number of results
        offset: Number of results to skip
        current_user: Current authenticated user
        document_service: Document service

    Returns:
        List of document chunks with pagination

    Args:
        document_id (str):
        limit (Union[Unset, int]): Maximum number of results Default: 50.
        offset (Union[Unset, int]): Number of results to skip Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DocumentChunksResponse, HTTPValidationError]
    """

    return sync_detailed(
        document_id=document_id,
        client=client,
        limit=limit,
        offset=offset,
    ).parsed


async def asyncio_detailed(
    document_id: str,
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = 50,
    offset: Union[Unset, int] = 0,
) -> Response[Union[DocumentChunksResponse, HTTPValidationError]]:
    """Get Document Chunks

     Get document chunks.

    Args:
        document_id: Document ID
        limit: Maximum number of results
        offset: Number of results to skip
        current_user: Current authenticated user
        document_service: Document service

    Returns:
        List of document chunks with pagination

    Args:
        document_id (str):
        limit (Union[Unset, int]): Maximum number of results Default: 50.
        offset (Union[Unset, int]): Number of results to skip Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DocumentChunksResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        document_id=document_id,
        limit=limit,
        offset=offset,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    document_id: str,
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = 50,
    offset: Union[Unset, int] = 0,
) -> Optional[Union[DocumentChunksResponse, HTTPValidationError]]:
    """Get Document Chunks

     Get document chunks.

    Args:
        document_id: Document ID
        limit: Maximum number of results
        offset: Number of results to skip
        current_user: Current authenticated user
        document_service: Document service

    Returns:
        List of document chunks with pagination

    Args:
        document_id (str):
        limit (Union[Unset, int]): Maximum number of results Default: 50.
        offset (Union[Unset, int]): Number of results to skip Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DocumentChunksResponse, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            document_id=document_id,
            client=client,
            limit=limit,
            offset=offset,
        )
    ).parsed
