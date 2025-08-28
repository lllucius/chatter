from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.tool_server_response import ToolServerResponse
from ...models.tool_server_update import ToolServerUpdate
from ...types import Response


def _get_kwargs(
    server_id: str,
    *,
    body: ToolServerUpdate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/api/v1/toolservers/servers/{server_id}",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, ToolServerResponse]]:
    if response.status_code == 200:
        response_200 = ToolServerResponse.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, ToolServerResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    server_id: str,
    *,
    client: AuthenticatedClient,
    body: ToolServerUpdate,
) -> Response[Union[HTTPValidationError, ToolServerResponse]]:
    """Update Tool Server

     Update a tool server.

    Args:
        server_id: Server ID
        update_data: Update data
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        Updated server response

    Args:
        server_id (str):
        body (ToolServerUpdate): Schema for updating a tool server.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, ToolServerResponse]]
    """

    kwargs = _get_kwargs(
        server_id=server_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    server_id: str,
    *,
    client: AuthenticatedClient,
    body: ToolServerUpdate,
) -> Optional[Union[HTTPValidationError, ToolServerResponse]]:
    """Update Tool Server

     Update a tool server.

    Args:
        server_id: Server ID
        update_data: Update data
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        Updated server response

    Args:
        server_id (str):
        body (ToolServerUpdate): Schema for updating a tool server.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, ToolServerResponse]
    """

    return sync_detailed(
        server_id=server_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    server_id: str,
    *,
    client: AuthenticatedClient,
    body: ToolServerUpdate,
) -> Response[Union[HTTPValidationError, ToolServerResponse]]:
    """Update Tool Server

     Update a tool server.

    Args:
        server_id: Server ID
        update_data: Update data
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        Updated server response

    Args:
        server_id (str):
        body (ToolServerUpdate): Schema for updating a tool server.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, ToolServerResponse]]
    """

    kwargs = _get_kwargs(
        server_id=server_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    server_id: str,
    *,
    client: AuthenticatedClient,
    body: ToolServerUpdate,
) -> Optional[Union[HTTPValidationError, ToolServerResponse]]:
    """Update Tool Server

     Update a tool server.

    Args:
        server_id: Server ID
        update_data: Update data
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        Updated server response

    Args:
        server_id (str):
        body (ToolServerUpdate): Schema for updating a tool server.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, ToolServerResponse]
    """

    return (
        await asyncio_detailed(
            server_id=server_id,
            client=client,
            body=body,
        )
    ).parsed
