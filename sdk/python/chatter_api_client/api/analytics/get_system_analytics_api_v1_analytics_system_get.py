from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.system_analytics_response import SystemAnalyticsResponse
from ...types import Response


def _get_kwargs() -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/analytics/system",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[SystemAnalyticsResponse]:
    if response.status_code == 200:
        response_200 = SystemAnalyticsResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[SystemAnalyticsResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[SystemAnalyticsResponse]:
    """Get System Analytics

     Get system analytics.

    Args:
        request: System analytics request parameters
        current_user: Current authenticated user
        analytics_service: Analytics service

    Returns:
        System analytics

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SystemAnalyticsResponse]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
) -> Optional[SystemAnalyticsResponse]:
    """Get System Analytics

     Get system analytics.

    Args:
        request: System analytics request parameters
        current_user: Current authenticated user
        analytics_service: Analytics service

    Returns:
        System analytics

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SystemAnalyticsResponse
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[SystemAnalyticsResponse]:
    """Get System Analytics

     Get system analytics.

    Args:
        request: System analytics request parameters
        current_user: Current authenticated user
        analytics_service: Analytics service

    Returns:
        System analytics

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SystemAnalyticsResponse]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
) -> Optional[SystemAnalyticsResponse]:
    """Get System Analytics

     Get system analytics.

    Args:
        request: System analytics request parameters
        current_user: Current authenticated user
        analytics_service: Analytics service

    Returns:
        System analytics

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SystemAnalyticsResponse
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
