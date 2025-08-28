from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.plugin_delete_response import PluginDeleteResponse
from ...types import Response


def _get_kwargs(
    plugin_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": f"/api/v1/plugins/{plugin_id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, PluginDeleteResponse]]:
    if response.status_code == 200:
        response_200 = PluginDeleteResponse.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, PluginDeleteResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    plugin_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[HTTPValidationError, PluginDeleteResponse]]:
    """Uninstall Plugin

     Uninstall a plugin.

    Args:
        plugin_id: Plugin ID
        current_user: Current authenticated user
        plugin_manager: Plugin manager instance

    Returns:
        Uninstall result

    Args:
        plugin_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, PluginDeleteResponse]]
    """

    kwargs = _get_kwargs(
        plugin_id=plugin_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    plugin_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[HTTPValidationError, PluginDeleteResponse]]:
    """Uninstall Plugin

     Uninstall a plugin.

    Args:
        plugin_id: Plugin ID
        current_user: Current authenticated user
        plugin_manager: Plugin manager instance

    Returns:
        Uninstall result

    Args:
        plugin_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, PluginDeleteResponse]
    """

    return sync_detailed(
        plugin_id=plugin_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    plugin_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[HTTPValidationError, PluginDeleteResponse]]:
    """Uninstall Plugin

     Uninstall a plugin.

    Args:
        plugin_id: Plugin ID
        current_user: Current authenticated user
        plugin_manager: Plugin manager instance

    Returns:
        Uninstall result

    Args:
        plugin_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, PluginDeleteResponse]]
    """

    kwargs = _get_kwargs(
        plugin_id=plugin_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    plugin_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[HTTPValidationError, PluginDeleteResponse]]:
    """Uninstall Plugin

     Uninstall a plugin.

    Args:
        plugin_id: Plugin ID
        current_user: Current authenticated user
        plugin_manager: Plugin manager instance

    Returns:
        Uninstall result

    Args:
        plugin_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, PluginDeleteResponse]
    """

    return (
        await asyncio_detailed(
            plugin_id=plugin_id,
            client=client,
        )
    ).parsed
