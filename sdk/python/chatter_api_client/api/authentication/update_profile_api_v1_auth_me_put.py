from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.user_response import UserResponse
from ...models.user_update import UserUpdate
from ...types import Response


def _get_kwargs(
    *,
    body: UserUpdate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/api/v1/auth/me",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, UserResponse]]:
    if response.status_code == 200:
        response_200 = UserResponse.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, UserResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: UserUpdate,
) -> Response[Union[HTTPValidationError, UserResponse]]:
    """Update Profile

     Update current user profile.

    Args:
        user_data: Profile update data
        current_user: Current authenticated user
        auth_service: Authentication service

    Returns:
        Updated user data

    Args:
        body (UserUpdate): Schema for user profile updates.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, UserResponse]]
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
    body: UserUpdate,
) -> Optional[Union[HTTPValidationError, UserResponse]]:
    """Update Profile

     Update current user profile.

    Args:
        user_data: Profile update data
        current_user: Current authenticated user
        auth_service: Authentication service

    Returns:
        Updated user data

    Args:
        body (UserUpdate): Schema for user profile updates.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, UserResponse]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: UserUpdate,
) -> Response[Union[HTTPValidationError, UserResponse]]:
    """Update Profile

     Update current user profile.

    Args:
        user_data: Profile update data
        current_user: Current authenticated user
        auth_service: Authentication service

    Returns:
        Updated user data

    Args:
        body (UserUpdate): Schema for user profile updates.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, UserResponse]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: UserUpdate,
) -> Optional[Union[HTTPValidationError, UserResponse]]:
    """Update Profile

     Update current user profile.

    Args:
        user_data: Profile update data
        current_user: Current authenticated user
        auth_service: Authentication service

    Returns:
        Updated user data

    Args:
        body (UserUpdate): Schema for user profile updates.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, UserResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
