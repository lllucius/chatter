from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.server_status import ServerStatus
from ...models.tool_server_response import ToolServerResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    status: Union[None, ServerStatus, Unset] = UNSET,
    include_builtin: Union[Unset, bool] = True,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_status: Union[None, Unset, str]
    if isinstance(status, Unset):
        json_status = UNSET
    elif isinstance(status, ServerStatus):
        json_status = status.value
    else:
        json_status = status
    params["status"] = json_status

    params["include_builtin"] = include_builtin

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/toolservers/servers",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, list["ToolServerResponse"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ToolServerResponse.from_dict(response_200_item_data)

            response_200.append(response_200_item)

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
) -> Response[Union[HTTPValidationError, list["ToolServerResponse"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    status: Union[None, ServerStatus, Unset] = UNSET,
    include_builtin: Union[Unset, bool] = True,
) -> Response[Union[HTTPValidationError, list["ToolServerResponse"]]]:
    """List Tool Servers

     List tool servers with optional filtering.

    Args:
        request: List request with filter parameters
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        List of server responses

    Args:
        status (Union[None, ServerStatus, Unset]):
        include_builtin (Union[Unset, bool]):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, list['ToolServerResponse']]]
    """

    kwargs = _get_kwargs(
        status=status,
        include_builtin=include_builtin,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    status: Union[None, ServerStatus, Unset] = UNSET,
    include_builtin: Union[Unset, bool] = True,
) -> Optional[Union[HTTPValidationError, list["ToolServerResponse"]]]:
    """List Tool Servers

     List tool servers with optional filtering.

    Args:
        request: List request with filter parameters
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        List of server responses

    Args:
        status (Union[None, ServerStatus, Unset]):
        include_builtin (Union[Unset, bool]):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, list['ToolServerResponse']]
    """

    return sync_detailed(
        client=client,
        status=status,
        include_builtin=include_builtin,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    status: Union[None, ServerStatus, Unset] = UNSET,
    include_builtin: Union[Unset, bool] = True,
) -> Response[Union[HTTPValidationError, list["ToolServerResponse"]]]:
    """List Tool Servers

     List tool servers with optional filtering.

    Args:
        request: List request with filter parameters
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        List of server responses

    Args:
        status (Union[None, ServerStatus, Unset]):
        include_builtin (Union[Unset, bool]):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, list['ToolServerResponse']]]
    """

    kwargs = _get_kwargs(
        status=status,
        include_builtin=include_builtin,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    status: Union[None, ServerStatus, Unset] = UNSET,
    include_builtin: Union[Unset, bool] = True,
) -> Optional[Union[HTTPValidationError, list["ToolServerResponse"]]]:
    """List Tool Servers

     List tool servers with optional filtering.

    Args:
        request: List request with filter parameters
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        List of server responses

    Args:
        status (Union[None, ServerStatus, Unset]):
        include_builtin (Union[Unset, bool]):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, list['ToolServerResponse']]
    """

    return (
        await asyncio_detailed(
            client=client,
            status=status,
            include_builtin=include_builtin,
        )
    ).parsed
