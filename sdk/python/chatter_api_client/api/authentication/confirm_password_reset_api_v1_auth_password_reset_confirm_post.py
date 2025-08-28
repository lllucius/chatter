from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.password_reset_confirm_response import PasswordResetConfirmResponse
from ...types import UNSET, Response


def _get_kwargs(
    *,
    token: str,
    new_password: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["token"] = token

    params["new_password"] = new_password

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/auth/password-reset/confirm",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, PasswordResetConfirmResponse]]:
    if response.status_code == 200:
        response_200 = PasswordResetConfirmResponse.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, PasswordResetConfirmResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    token: str,
    new_password: str,
) -> Response[Union[HTTPValidationError, PasswordResetConfirmResponse]]:
    """Confirm Password Reset

     Confirm password reset.

    Args:
        token: Reset token
        new_password: New password
        auth_service: Authentication service

    Returns:
        Success message

    Args:
        token (str):
        new_password (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, PasswordResetConfirmResponse]]
    """

    kwargs = _get_kwargs(
        token=token,
        new_password=new_password,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    token: str,
    new_password: str,
) -> Optional[Union[HTTPValidationError, PasswordResetConfirmResponse]]:
    """Confirm Password Reset

     Confirm password reset.

    Args:
        token: Reset token
        new_password: New password
        auth_service: Authentication service

    Returns:
        Success message

    Args:
        token (str):
        new_password (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, PasswordResetConfirmResponse]
    """

    return sync_detailed(
        client=client,
        token=token,
        new_password=new_password,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    token: str,
    new_password: str,
) -> Response[Union[HTTPValidationError, PasswordResetConfirmResponse]]:
    """Confirm Password Reset

     Confirm password reset.

    Args:
        token: Reset token
        new_password: New password
        auth_service: Authentication service

    Returns:
        Success message

    Args:
        token (str):
        new_password (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, PasswordResetConfirmResponse]]
    """

    kwargs = _get_kwargs(
        token=token,
        new_password=new_password,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    token: str,
    new_password: str,
) -> Optional[Union[HTTPValidationError, PasswordResetConfirmResponse]]:
    """Confirm Password Reset

     Confirm password reset.

    Args:
        token: Reset token
        new_password: New password
        auth_service: Authentication service

    Returns:
        Success message

    Args:
        token (str):
        new_password (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, PasswordResetConfirmResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            token=token,
            new_password=new_password,
        )
    ).parsed
