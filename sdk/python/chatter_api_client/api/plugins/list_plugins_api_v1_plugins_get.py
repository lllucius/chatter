from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.plugin_list_response import PluginListResponse
from ...models.plugin_status import PluginStatus
from ...models.plugin_type import PluginType
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    plugin_type: Union[None, PluginType, Unset] = UNSET,
    status: Union[None, PluginStatus, Unset] = UNSET,
    enabled: Union[None, Unset, bool] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_plugin_type: Union[None, Unset, str]
    if isinstance(plugin_type, Unset):
        json_plugin_type = UNSET
    elif isinstance(plugin_type, PluginType):
        json_plugin_type = plugin_type.value
    else:
        json_plugin_type = plugin_type
    params["plugin_type"] = json_plugin_type

    json_status: Union[None, Unset, str]
    if isinstance(status, Unset):
        json_status = UNSET
    elif isinstance(status, PluginStatus):
        json_status = status.value
    else:
        json_status = status
    params["status"] = json_status

    json_enabled: Union[None, Unset, bool]
    if isinstance(enabled, Unset):
        json_enabled = UNSET
    else:
        json_enabled = enabled
    params["enabled"] = json_enabled

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/plugins/",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, PluginListResponse]]:
    if response.status_code == 200:
        response_200 = PluginListResponse.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, PluginListResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    plugin_type: Union[None, PluginType, Unset] = UNSET,
    status: Union[None, PluginStatus, Unset] = UNSET,
    enabled: Union[None, Unset, bool] = UNSET,
) -> Response[Union[HTTPValidationError, PluginListResponse]]:
    """List Plugins

     List installed plugins with optional filtering.

    Args:
        request: List request parameters
        current_user: Current authenticated user
        plugin_manager: Plugin manager instance

    Returns:
        List of installed plugins

    Args:
        plugin_type (Union[None, PluginType, Unset]):
        status (Union[None, PluginStatus, Unset]):
        enabled (Union[None, Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, PluginListResponse]]
    """

    kwargs = _get_kwargs(
        plugin_type=plugin_type,
        status=status,
        enabled=enabled,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    plugin_type: Union[None, PluginType, Unset] = UNSET,
    status: Union[None, PluginStatus, Unset] = UNSET,
    enabled: Union[None, Unset, bool] = UNSET,
) -> Optional[Union[HTTPValidationError, PluginListResponse]]:
    """List Plugins

     List installed plugins with optional filtering.

    Args:
        request: List request parameters
        current_user: Current authenticated user
        plugin_manager: Plugin manager instance

    Returns:
        List of installed plugins

    Args:
        plugin_type (Union[None, PluginType, Unset]):
        status (Union[None, PluginStatus, Unset]):
        enabled (Union[None, Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, PluginListResponse]
    """

    return sync_detailed(
        client=client,
        plugin_type=plugin_type,
        status=status,
        enabled=enabled,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    plugin_type: Union[None, PluginType, Unset] = UNSET,
    status: Union[None, PluginStatus, Unset] = UNSET,
    enabled: Union[None, Unset, bool] = UNSET,
) -> Response[Union[HTTPValidationError, PluginListResponse]]:
    """List Plugins

     List installed plugins with optional filtering.

    Args:
        request: List request parameters
        current_user: Current authenticated user
        plugin_manager: Plugin manager instance

    Returns:
        List of installed plugins

    Args:
        plugin_type (Union[None, PluginType, Unset]):
        status (Union[None, PluginStatus, Unset]):
        enabled (Union[None, Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, PluginListResponse]]
    """

    kwargs = _get_kwargs(
        plugin_type=plugin_type,
        status=status,
        enabled=enabled,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    plugin_type: Union[None, PluginType, Unset] = UNSET,
    status: Union[None, PluginStatus, Unset] = UNSET,
    enabled: Union[None, Unset, bool] = UNSET,
) -> Optional[Union[HTTPValidationError, PluginListResponse]]:
    """List Plugins

     List installed plugins with optional filtering.

    Args:
        request: List request parameters
        current_user: Current authenticated user
        plugin_manager: Plugin manager instance

    Returns:
        List of installed plugins

    Args:
        plugin_type (Union[None, PluginType, Unset]):
        status (Union[None, PluginStatus, Unset]):
        enabled (Union[None, Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, PluginListResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            plugin_type=plugin_type,
            status=status,
            enabled=enabled,
        )
    ).parsed
