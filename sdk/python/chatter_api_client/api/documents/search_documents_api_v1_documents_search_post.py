from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.document_search_request import DocumentSearchRequest
from ...models.document_search_response import DocumentSearchResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    *,
    body: DocumentSearchRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/documents/search",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DocumentSearchResponse, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = DocumentSearchResponse.from_dict(response.json())

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
) -> Response[Union[DocumentSearchResponse, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: DocumentSearchRequest,
) -> Response[Union[DocumentSearchResponse, HTTPValidationError]]:
    """Search Documents

     Search documents using vector similarity.

    Args:
        search_request: Search request
        current_user: Current authenticated user
        document_service: Document service

    Returns:
        Search results

    Args:
        body (DocumentSearchRequest): Schema for document search request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DocumentSearchResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: DocumentSearchRequest,
) -> Optional[Union[DocumentSearchResponse, HTTPValidationError]]:
    """Search Documents

     Search documents using vector similarity.

    Args:
        search_request: Search request
        current_user: Current authenticated user
        document_service: Document service

    Returns:
        Search results

    Args:
        body (DocumentSearchRequest): Schema for document search request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DocumentSearchResponse, HTTPValidationError]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: DocumentSearchRequest,
) -> Response[Union[DocumentSearchResponse, HTTPValidationError]]:
    """Search Documents

     Search documents using vector similarity.

    Args:
        search_request: Search request
        current_user: Current authenticated user
        document_service: Document service

    Returns:
        Search results

    Args:
        body (DocumentSearchRequest): Schema for document search request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DocumentSearchResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: DocumentSearchRequest,
) -> Optional[Union[DocumentSearchResponse, HTTPValidationError]]:
    """Search Documents

     Search documents using vector similarity.

    Args:
        search_request: Search request
        current_user: Current authenticated user
        document_service: Document service

    Returns:
        Search results

    Args:
        body (DocumentSearchRequest): Schema for document search request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DocumentSearchResponse, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
