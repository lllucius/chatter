from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.profile_clone_request import ProfileCloneRequest
from ...models.profile_response import ProfileResponse
from ...types import Response


def _get_kwargs(
    profile_id: str,
    *,
    body: ProfileCloneRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/api/v1/profiles/{profile_id}/clone",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, ProfileResponse]]:
    if response.status_code == 200:
        response_200 = ProfileResponse.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, ProfileResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    profile_id: str,
    *,
    client: AuthenticatedClient,
    body: ProfileCloneRequest,
) -> Response[Union[HTTPValidationError, ProfileResponse]]:
    """Clone Profile

     Clone an existing profile.

    Args:
        profile_id: Source profile ID
        clone_request: Clone request
        current_user: Current authenticated user
        profile_service: Profile service

    Returns:
        Cloned profile information

    Args:
        profile_id (str):
        body (ProfileCloneRequest): Schema for profile clone request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, ProfileResponse]]
    """

    kwargs = _get_kwargs(
        profile_id=profile_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    profile_id: str,
    *,
    client: AuthenticatedClient,
    body: ProfileCloneRequest,
) -> Optional[Union[HTTPValidationError, ProfileResponse]]:
    """Clone Profile

     Clone an existing profile.

    Args:
        profile_id: Source profile ID
        clone_request: Clone request
        current_user: Current authenticated user
        profile_service: Profile service

    Returns:
        Cloned profile information

    Args:
        profile_id (str):
        body (ProfileCloneRequest): Schema for profile clone request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, ProfileResponse]
    """

    return sync_detailed(
        profile_id=profile_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    profile_id: str,
    *,
    client: AuthenticatedClient,
    body: ProfileCloneRequest,
) -> Response[Union[HTTPValidationError, ProfileResponse]]:
    """Clone Profile

     Clone an existing profile.

    Args:
        profile_id: Source profile ID
        clone_request: Clone request
        current_user: Current authenticated user
        profile_service: Profile service

    Returns:
        Cloned profile information

    Args:
        profile_id (str):
        body (ProfileCloneRequest): Schema for profile clone request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, ProfileResponse]]
    """

    kwargs = _get_kwargs(
        profile_id=profile_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    profile_id: str,
    *,
    client: AuthenticatedClient,
    body: ProfileCloneRequest,
) -> Optional[Union[HTTPValidationError, ProfileResponse]]:
    """Clone Profile

     Clone an existing profile.

    Args:
        profile_id: Source profile ID
        clone_request: Clone request
        current_user: Current authenticated user
        profile_service: Profile service

    Returns:
        Cloned profile information

    Args:
        profile_id (str):
        body (ProfileCloneRequest): Schema for profile clone request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, ProfileResponse]
    """

    return (
        await asyncio_detailed(
            profile_id=profile_id,
            client=client,
            body=body,
        )
    ).parsed
