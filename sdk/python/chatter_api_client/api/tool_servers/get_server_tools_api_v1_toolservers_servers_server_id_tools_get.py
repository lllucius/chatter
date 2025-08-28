from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.server_tools_response import ServerToolsResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    server_id: str,
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
        "url": f"/api/v1/toolservers/servers/{server_id}/tools",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, ServerToolsResponse]]:
    if response.status_code == 200:
        response_200 = ServerToolsResponse.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, ServerToolsResponse]]:
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
    limit: Union[Unset, int] = 50,
    offset: Union[Unset, int] = 0,
) -> Response[Union[HTTPValidationError, ServerToolsResponse]]:
    """Get Server Tools

     Get tools for a specific server.

    Args:
        server_id: Server ID
        request: Server tools request with pagination
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        List of server tools with pagination

    Args:
        server_id (str):
        limit (Union[Unset, int]):  Default: 50.
        offset (Union[Unset, int]):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, ServerToolsResponse]]
    """

    kwargs = _get_kwargs(
        server_id=server_id,
        limit=limit,
        offset=offset,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    server_id: str,
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = 50,
    offset: Union[Unset, int] = 0,
) -> Optional[Union[HTTPValidationError, ServerToolsResponse]]:
    """Get Server Tools

     Get tools for a specific server.

    Args:
        server_id: Server ID
        request: Server tools request with pagination
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        List of server tools with pagination

    Args:
        server_id (str):
        limit (Union[Unset, int]):  Default: 50.
        offset (Union[Unset, int]):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, ServerToolsResponse]
    """

    return sync_detailed(
        server_id=server_id,
        client=client,
        limit=limit,
        offset=offset,
    ).parsed


async def asyncio_detailed(
    server_id: str,
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = 50,
    offset: Union[Unset, int] = 0,
) -> Response[Union[HTTPValidationError, ServerToolsResponse]]:
    """Get Server Tools

     Get tools for a specific server.

    Args:
        server_id: Server ID
        request: Server tools request with pagination
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        List of server tools with pagination

    Args:
        server_id (str):
        limit (Union[Unset, int]):  Default: 50.
        offset (Union[Unset, int]):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, ServerToolsResponse]]
    """

    kwargs = _get_kwargs(
        server_id=server_id,
        limit=limit,
        offset=offset,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    server_id: str,
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = 50,
    offset: Union[Unset, int] = 0,
) -> Optional[Union[HTTPValidationError, ServerToolsResponse]]:
    """Get Server Tools

     Get tools for a specific server.

    Args:
        server_id: Server ID
        request: Server tools request with pagination
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        List of server tools with pagination

    Args:
        server_id (str):
        limit (Union[Unset, int]):  Default: 50.
        offset (Union[Unset, int]):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, ServerToolsResponse]
    """

    return (
        await asyncio_detailed(
            server_id=server_id,
            client=client,
            limit=limit,
            offset=offset,
        )
    ).parsed
