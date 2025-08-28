from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.backup_list_response import BackupListResponse
from ...models.backup_type import BackupType
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    backup_type: Union[BackupType, None, Unset] = UNSET,
    status: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_backup_type: Union[None, Unset, str]
    if isinstance(backup_type, Unset):
        json_backup_type = UNSET
    elif isinstance(backup_type, BackupType):
        json_backup_type = backup_type.value
    else:
        json_backup_type = backup_type
    params["backup_type"] = json_backup_type

    json_status: Union[None, Unset, str]
    if isinstance(status, Unset):
        json_status = UNSET
    else:
        json_status = status
    params["status"] = json_status

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/data/backups",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[BackupListResponse, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = BackupListResponse.from_dict(response.json())

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
) -> Response[Union[BackupListResponse, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    backup_type: Union[BackupType, None, Unset] = UNSET,
    status: Union[None, Unset, str] = UNSET,
) -> Response[Union[BackupListResponse, HTTPValidationError]]:
    """List Backups

     List available backups.

    Args:
        backup_type (Union[BackupType, None, Unset]):
        status (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BackupListResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        backup_type=backup_type,
        status=status,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    backup_type: Union[BackupType, None, Unset] = UNSET,
    status: Union[None, Unset, str] = UNSET,
) -> Optional[Union[BackupListResponse, HTTPValidationError]]:
    """List Backups

     List available backups.

    Args:
        backup_type (Union[BackupType, None, Unset]):
        status (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BackupListResponse, HTTPValidationError]
    """

    return sync_detailed(
        client=client,
        backup_type=backup_type,
        status=status,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    backup_type: Union[BackupType, None, Unset] = UNSET,
    status: Union[None, Unset, str] = UNSET,
) -> Response[Union[BackupListResponse, HTTPValidationError]]:
    """List Backups

     List available backups.

    Args:
        backup_type (Union[BackupType, None, Unset]):
        status (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BackupListResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        backup_type=backup_type,
        status=status,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    backup_type: Union[BackupType, None, Unset] = UNSET,
    status: Union[None, Unset, str] = UNSET,
) -> Optional[Union[BackupListResponse, HTTPValidationError]]:
    """List Backups

     List available backups.

    Args:
        backup_type (Union[BackupType, None, Unset]):
        status (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BackupListResponse, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            client=client,
            backup_type=backup_type,
            status=status,
        )
    ).parsed
