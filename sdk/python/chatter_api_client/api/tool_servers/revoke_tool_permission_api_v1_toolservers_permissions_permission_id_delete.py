from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.revoke_tool_permission_api_v1_toolservers_permissions_permission_id_delete_response_revoke_tool_permission_api_v1_toolservers_permissions_permission_id_delete import (
    RevokeToolPermissionApiV1ToolserversPermissionsPermissionIdDeleteResponseRevokeToolPermissionApiV1ToolserversPermissionsPermissionIdDelete,
)
from ...types import Response


def _get_kwargs(
    permission_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": f"/api/v1/toolservers/permissions/{permission_id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        HTTPValidationError,
        RevokeToolPermissionApiV1ToolserversPermissionsPermissionIdDeleteResponseRevokeToolPermissionApiV1ToolserversPermissionsPermissionIdDelete,
    ]
]:
    if response.status_code == 200:
        response_200 = RevokeToolPermissionApiV1ToolserversPermissionsPermissionIdDeleteResponseRevokeToolPermissionApiV1ToolserversPermissionsPermissionIdDelete.from_dict(
            response.json()
        )

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
) -> Response[
    Union[
        HTTPValidationError,
        RevokeToolPermissionApiV1ToolserversPermissionsPermissionIdDeleteResponseRevokeToolPermissionApiV1ToolserversPermissionsPermissionIdDelete,
    ]
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    permission_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[
    Union[
        HTTPValidationError,
        RevokeToolPermissionApiV1ToolserversPermissionsPermissionIdDeleteResponseRevokeToolPermissionApiV1ToolserversPermissionsPermissionIdDelete,
    ]
]:
    """Revoke Tool Permission

     Revoke tool permission.

    Args:
        permission_id: Permission ID
        current_user: Current authenticated user
        access_service: Tool access service

    Returns:
        Success message

    Args:
        permission_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, RevokeToolPermissionApiV1ToolserversPermissionsPermissionIdDeleteResponseRevokeToolPermissionApiV1ToolserversPermissionsPermissionIdDelete]]
    """

    kwargs = _get_kwargs(
        permission_id=permission_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    permission_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[
    Union[
        HTTPValidationError,
        RevokeToolPermissionApiV1ToolserversPermissionsPermissionIdDeleteResponseRevokeToolPermissionApiV1ToolserversPermissionsPermissionIdDelete,
    ]
]:
    """Revoke Tool Permission

     Revoke tool permission.

    Args:
        permission_id: Permission ID
        current_user: Current authenticated user
        access_service: Tool access service

    Returns:
        Success message

    Args:
        permission_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, RevokeToolPermissionApiV1ToolserversPermissionsPermissionIdDeleteResponseRevokeToolPermissionApiV1ToolserversPermissionsPermissionIdDelete]
    """

    return sync_detailed(
        permission_id=permission_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    permission_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[
    Union[
        HTTPValidationError,
        RevokeToolPermissionApiV1ToolserversPermissionsPermissionIdDeleteResponseRevokeToolPermissionApiV1ToolserversPermissionsPermissionIdDelete,
    ]
]:
    """Revoke Tool Permission

     Revoke tool permission.

    Args:
        permission_id: Permission ID
        current_user: Current authenticated user
        access_service: Tool access service

    Returns:
        Success message

    Args:
        permission_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, RevokeToolPermissionApiV1ToolserversPermissionsPermissionIdDeleteResponseRevokeToolPermissionApiV1ToolserversPermissionsPermissionIdDelete]]
    """

    kwargs = _get_kwargs(
        permission_id=permission_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    permission_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[
    Union[
        HTTPValidationError,
        RevokeToolPermissionApiV1ToolserversPermissionsPermissionIdDeleteResponseRevokeToolPermissionApiV1ToolserversPermissionsPermissionIdDelete,
    ]
]:
    """Revoke Tool Permission

     Revoke tool permission.

    Args:
        permission_id: Permission ID
        current_user: Current authenticated user
        access_service: Tool access service

    Returns:
        Success message

    Args:
        permission_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, RevokeToolPermissionApiV1ToolserversPermissionsPermissionIdDeleteResponseRevokeToolPermissionApiV1ToolserversPermissionsPermissionIdDelete]
    """

    return (
        await asyncio_detailed(
            permission_id=permission_id,
            client=client,
        )
    ).parsed
