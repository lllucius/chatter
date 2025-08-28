from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.tool_server_metrics import ToolServerMetrics
from ...types import Response


def _get_kwargs(
    server_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v1/toolservers/servers/{server_id}/metrics",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, ToolServerMetrics]]:
    if response.status_code == 200:
        response_200 = ToolServerMetrics.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, ToolServerMetrics]]:
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
) -> Response[Union[HTTPValidationError, ToolServerMetrics]]:
    """Get Server Metrics

     Get analytics for a specific server.

    Args:
        server_id: Server ID
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        Server metrics

    Args:
        server_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, ToolServerMetrics]]
    """

    kwargs = _get_kwargs(
        server_id=server_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    server_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[HTTPValidationError, ToolServerMetrics]]:
    """Get Server Metrics

     Get analytics for a specific server.

    Args:
        server_id: Server ID
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        Server metrics

    Args:
        server_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, ToolServerMetrics]
    """

    return sync_detailed(
        server_id=server_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    server_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[HTTPValidationError, ToolServerMetrics]]:
    """Get Server Metrics

     Get analytics for a specific server.

    Args:
        server_id: Server ID
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        Server metrics

    Args:
        server_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, ToolServerMetrics]]
    """

    kwargs = _get_kwargs(
        server_id=server_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    server_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[HTTPValidationError, ToolServerMetrics]]:
    """Get Server Metrics

     Get analytics for a specific server.

    Args:
        server_id: Server ID
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        Server metrics

    Args:
        server_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, ToolServerMetrics]
    """

    return (
        await asyncio_detailed(
            server_id=server_id,
            client=client,
        )
    ).parsed
