from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.password_change import PasswordChange
from ...models.password_change_response import PasswordChangeResponse
from ...types import Response


def _get_kwargs(
    *,
    body: PasswordChange,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/auth/change-password",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, PasswordChangeResponse]]:
    if response.status_code == 200:
        response_200 = PasswordChangeResponse.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, PasswordChangeResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: PasswordChange,
) -> Response[Union[HTTPValidationError, PasswordChangeResponse]]:
    """Change Password

     Change user password.

    Args:
        password_data: Password change data
        current_user: Current authenticated user
        auth_service: Authentication service

    Returns:
        Success message

    Args:
        body (PasswordChange): Schema for password change.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, PasswordChangeResponse]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: PasswordChange,
) -> Optional[Union[HTTPValidationError, PasswordChangeResponse]]:
    """Change Password

     Change user password.

    Args:
        password_data: Password change data
        current_user: Current authenticated user
        auth_service: Authentication service

    Returns:
        Success message

    Args:
        body (PasswordChange): Schema for password change.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, PasswordChangeResponse]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: PasswordChange,
) -> Response[Union[HTTPValidationError, PasswordChangeResponse]]:
    """Change Password

     Change user password.

    Args:
        password_data: Password change data
        current_user: Current authenticated user
        auth_service: Authentication service

    Returns:
        Success message

    Args:
        body (PasswordChange): Schema for password change.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, PasswordChangeResponse]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: PasswordChange,
) -> Optional[Union[HTTPValidationError, PasswordChangeResponse]]:
    """Change Password

     Change user password.

    Args:
        password_data: Password change data
        current_user: Current authenticated user
        auth_service: Authentication service

    Returns:
        Success message

    Args:
        body (PasswordChange): Schema for password change.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, PasswordChangeResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
