from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.tool_permission_response import ToolPermissionResponse
from ...models.tool_permission_update import ToolPermissionUpdate
from ...types import Response


def _get_kwargs(
    permission_id: str,
    *,
    body: ToolPermissionUpdate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/api/v1/toolservers/permissions/{permission_id}",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, ToolPermissionResponse]]:
    if response.status_code == 200:
        response_200 = ToolPermissionResponse.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, ToolPermissionResponse]]:
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
    body: ToolPermissionUpdate,
) -> Response[Union[HTTPValidationError, ToolPermissionResponse]]:
    """Update Tool Permission

     Update tool permission.

    Args:
        permission_id: Permission ID
        update_data: Update data
        current_user: Current authenticated user
        access_service: Tool access service

    Returns:
        Updated permission

    Args:
        permission_id (str):
        body (ToolPermissionUpdate): Schema for updating tool permissions.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, ToolPermissionResponse]]
    """

    kwargs = _get_kwargs(
        permission_id=permission_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    permission_id: str,
    *,
    client: AuthenticatedClient,
    body: ToolPermissionUpdate,
) -> Optional[Union[HTTPValidationError, ToolPermissionResponse]]:
    """Update Tool Permission

     Update tool permission.

    Args:
        permission_id: Permission ID
        update_data: Update data
        current_user: Current authenticated user
        access_service: Tool access service

    Returns:
        Updated permission

    Args:
        permission_id (str):
        body (ToolPermissionUpdate): Schema for updating tool permissions.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, ToolPermissionResponse]
    """

    return sync_detailed(
        permission_id=permission_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    permission_id: str,
    *,
    client: AuthenticatedClient,
    body: ToolPermissionUpdate,
) -> Response[Union[HTTPValidationError, ToolPermissionResponse]]:
    """Update Tool Permission

     Update tool permission.

    Args:
        permission_id: Permission ID
        update_data: Update data
        current_user: Current authenticated user
        access_service: Tool access service

    Returns:
        Updated permission

    Args:
        permission_id (str):
        body (ToolPermissionUpdate): Schema for updating tool permissions.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, ToolPermissionResponse]]
    """

    kwargs = _get_kwargs(
        permission_id=permission_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    permission_id: str,
    *,
    client: AuthenticatedClient,
    body: ToolPermissionUpdate,
) -> Optional[Union[HTTPValidationError, ToolPermissionResponse]]:
    """Update Tool Permission

     Update tool permission.

    Args:
        permission_id: Permission ID
        update_data: Update data
        current_user: Current authenticated user
        access_service: Tool access service

    Returns:
        Updated permission

    Args:
        permission_id (str):
        body (ToolPermissionUpdate): Schema for updating tool permissions.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, ToolPermissionResponse]
    """

    return (
        await asyncio_detailed(
            permission_id=permission_id,
            client=client,
            body=body,
        )
    ).parsed
