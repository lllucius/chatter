from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.document_response import DocumentResponse
from ...models.document_update import DocumentUpdate
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    document_id: str,
    *,
    body: DocumentUpdate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/api/v1/documents/{document_id}",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DocumentResponse, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = DocumentResponse.from_dict(response.json())

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
) -> Response[Union[DocumentResponse, HTTPValidationError]]:
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
    body: DocumentUpdate,
) -> Response[Union[DocumentResponse, HTTPValidationError]]:
    """Update Document

     Update document metadata.

    Args:
        document_id: Document ID
        update_data: Update data
        current_user: Current authenticated user
        document_service: Document service

    Returns:
        Updated document information

    Args:
        document_id (str):
        body (DocumentUpdate): Schema for updating a document.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DocumentResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        document_id=document_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    document_id: str,
    *,
    client: AuthenticatedClient,
    body: DocumentUpdate,
) -> Optional[Union[DocumentResponse, HTTPValidationError]]:
    """Update Document

     Update document metadata.

    Args:
        document_id: Document ID
        update_data: Update data
        current_user: Current authenticated user
        document_service: Document service

    Returns:
        Updated document information

    Args:
        document_id (str):
        body (DocumentUpdate): Schema for updating a document.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DocumentResponse, HTTPValidationError]
    """

    return sync_detailed(
        document_id=document_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    document_id: str,
    *,
    client: AuthenticatedClient,
    body: DocumentUpdate,
) -> Response[Union[DocumentResponse, HTTPValidationError]]:
    """Update Document

     Update document metadata.

    Args:
        document_id: Document ID
        update_data: Update data
        current_user: Current authenticated user
        document_service: Document service

    Returns:
        Updated document information

    Args:
        document_id (str):
        body (DocumentUpdate): Schema for updating a document.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DocumentResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        document_id=document_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    document_id: str,
    *,
    client: AuthenticatedClient,
    body: DocumentUpdate,
) -> Optional[Union[DocumentResponse, HTTPValidationError]]:
    """Update Document

     Update document metadata.

    Args:
        document_id: Document ID
        update_data: Update data
        current_user: Current authenticated user
        document_service: Document service

    Returns:
        Updated document information

    Args:
        document_id (str):
        body (DocumentUpdate): Schema for updating a document.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DocumentResponse, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            document_id=document_id,
            client=client,
            body=body,
        )
    ).parsed
