from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.bulk_operation_result import BulkOperationResult
from ...models.bulk_tool_server_operation import BulkToolServerOperation
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    *,
    body: BulkToolServerOperation,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/toolservers/servers/bulk",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[BulkOperationResult, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = BulkOperationResult.from_dict(response.json())

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
) -> Response[Union[BulkOperationResult, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: BulkToolServerOperation,
) -> Response[Union[BulkOperationResult, HTTPValidationError]]:
    """Bulk Server Operation

     Perform bulk operations on multiple servers.

    Args:
        operation_data: Bulk operation data
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        Bulk operation result

    Args:
        body (BulkToolServerOperation): Schema for bulk operations on tool servers.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BulkOperationResult, HTTPValidationError]]
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
    body: BulkToolServerOperation,
) -> Optional[Union[BulkOperationResult, HTTPValidationError]]:
    """Bulk Server Operation

     Perform bulk operations on multiple servers.

    Args:
        operation_data: Bulk operation data
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        Bulk operation result

    Args:
        body (BulkToolServerOperation): Schema for bulk operations on tool servers.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BulkOperationResult, HTTPValidationError]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: BulkToolServerOperation,
) -> Response[Union[BulkOperationResult, HTTPValidationError]]:
    """Bulk Server Operation

     Perform bulk operations on multiple servers.

    Args:
        operation_data: Bulk operation data
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        Bulk operation result

    Args:
        body (BulkToolServerOperation): Schema for bulk operations on tool servers.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BulkOperationResult, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: BulkToolServerOperation,
) -> Optional[Union[BulkOperationResult, HTTPValidationError]]:
    """Bulk Server Operation

     Perform bulk operations on multiple servers.

    Args:
        operation_data: Bulk operation data
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        Bulk operation result

    Args:
        body (BulkToolServerOperation): Schema for bulk operations on tool servers.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BulkOperationResult, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
