from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.tool_access_result import ToolAccessResult
from ...models.user_tool_access_check import UserToolAccessCheck
from ...types import Response


def _get_kwargs(
    *,
    body: UserToolAccessCheck,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/toolservers/access-check",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, ToolAccessResult]]:
    if response.status_code == 200:
        response_200 = ToolAccessResult.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, ToolAccessResult]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: UserToolAccessCheck,
) -> Response[Union[HTTPValidationError, ToolAccessResult]]:
    """Check Tool Access

     Check if user has access to a tool.

    Args:
        check_data: Access check data
        current_user: Current authenticated user
        access_service: Tool access service

    Returns:
        Access check result

    Args:
        body (UserToolAccessCheck): Schema for checking user tool access.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, ToolAccessResult]]
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
    body: UserToolAccessCheck,
) -> Optional[Union[HTTPValidationError, ToolAccessResult]]:
    """Check Tool Access

     Check if user has access to a tool.

    Args:
        check_data: Access check data
        current_user: Current authenticated user
        access_service: Tool access service

    Returns:
        Access check result

    Args:
        body (UserToolAccessCheck): Schema for checking user tool access.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, ToolAccessResult]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: UserToolAccessCheck,
) -> Response[Union[HTTPValidationError, ToolAccessResult]]:
    """Check Tool Access

     Check if user has access to a tool.

    Args:
        check_data: Access check data
        current_user: Current authenticated user
        access_service: Tool access service

    Returns:
        Access check result

    Args:
        body (UserToolAccessCheck): Schema for checking user tool access.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, ToolAccessResult]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: UserToolAccessCheck,
) -> Optional[Union[HTTPValidationError, ToolAccessResult]]:
    """Check Tool Access

     Check if user has access to a tool.

    Args:
        check_data: Access check data
        current_user: Current authenticated user
        access_service: Tool access service

    Returns:
        Access check result

    Args:
        body (UserToolAccessCheck): Schema for checking user tool access.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, ToolAccessResult]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
