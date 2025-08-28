import datetime
from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    format_: Union[Unset, str] = "json",
    metrics: list[str],
    start_date: Union[None, Unset, datetime.datetime] = UNSET,
    end_date: Union[None, Unset, datetime.datetime] = UNSET,
    period: Union[Unset, str] = "7d",
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["format"] = format_

    json_metrics = metrics

    params["metrics"] = json_metrics

    json_start_date: Union[None, Unset, str]
    if isinstance(start_date, Unset):
        json_start_date = UNSET
    elif isinstance(start_date, datetime.datetime):
        json_start_date = start_date.isoformat()
    else:
        json_start_date = start_date
    params["start_date"] = json_start_date

    json_end_date: Union[None, Unset, str]
    if isinstance(end_date, Unset):
        json_end_date = UNSET
    elif isinstance(end_date, datetime.datetime):
        json_end_date = end_date.isoformat()
    else:
        json_end_date = end_date
    params["end_date"] = json_end_date

    params["period"] = period

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/analytics/export",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = response.json()
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
) -> Response[Union[Any, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    format_: Union[Unset, str] = "json",
    metrics: list[str],
    start_date: Union[None, Unset, datetime.datetime] = UNSET,
    end_date: Union[None, Unset, datetime.datetime] = UNSET,
    period: Union[Unset, str] = "7d",
) -> Response[Union[Any, HTTPValidationError]]:
    """Export Analytics

     Export analytics reports.

    Args:
        format: Export format
        metrics: List of metrics to export
        start_date: Start date for analytics
        end_date: End date for analytics
        period: Predefined period
        current_user: Current authenticated user
        analytics_service: Analytics service

    Returns:
        Exported analytics report

    Args:
        format_ (Union[Unset, str]): Export format (json, csv, xlsx) Default: 'json'.
        metrics (list[str]): List of metrics to export
        start_date (Union[None, Unset, datetime.datetime]): Start date for analytics
        end_date (Union[None, Unset, datetime.datetime]): End date for analytics
        period (Union[Unset, str]): Predefined period (1h, 24h, 7d, 30d, 90d) Default: '7d'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        format_=format_,
        metrics=metrics,
        start_date=start_date,
        end_date=end_date,
        period=period,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    format_: Union[Unset, str] = "json",
    metrics: list[str],
    start_date: Union[None, Unset, datetime.datetime] = UNSET,
    end_date: Union[None, Unset, datetime.datetime] = UNSET,
    period: Union[Unset, str] = "7d",
) -> Optional[Union[Any, HTTPValidationError]]:
    """Export Analytics

     Export analytics reports.

    Args:
        format: Export format
        metrics: List of metrics to export
        start_date: Start date for analytics
        end_date: End date for analytics
        period: Predefined period
        current_user: Current authenticated user
        analytics_service: Analytics service

    Returns:
        Exported analytics report

    Args:
        format_ (Union[Unset, str]): Export format (json, csv, xlsx) Default: 'json'.
        metrics (list[str]): List of metrics to export
        start_date (Union[None, Unset, datetime.datetime]): Start date for analytics
        end_date (Union[None, Unset, datetime.datetime]): End date for analytics
        period (Union[Unset, str]): Predefined period (1h, 24h, 7d, 30d, 90d) Default: '7d'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, HTTPValidationError]
    """

    return sync_detailed(
        client=client,
        format_=format_,
        metrics=metrics,
        start_date=start_date,
        end_date=end_date,
        period=period,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    format_: Union[Unset, str] = "json",
    metrics: list[str],
    start_date: Union[None, Unset, datetime.datetime] = UNSET,
    end_date: Union[None, Unset, datetime.datetime] = UNSET,
    period: Union[Unset, str] = "7d",
) -> Response[Union[Any, HTTPValidationError]]:
    """Export Analytics

     Export analytics reports.

    Args:
        format: Export format
        metrics: List of metrics to export
        start_date: Start date for analytics
        end_date: End date for analytics
        period: Predefined period
        current_user: Current authenticated user
        analytics_service: Analytics service

    Returns:
        Exported analytics report

    Args:
        format_ (Union[Unset, str]): Export format (json, csv, xlsx) Default: 'json'.
        metrics (list[str]): List of metrics to export
        start_date (Union[None, Unset, datetime.datetime]): Start date for analytics
        end_date (Union[None, Unset, datetime.datetime]): End date for analytics
        period (Union[Unset, str]): Predefined period (1h, 24h, 7d, 30d, 90d) Default: '7d'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        format_=format_,
        metrics=metrics,
        start_date=start_date,
        end_date=end_date,
        period=period,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    format_: Union[Unset, str] = "json",
    metrics: list[str],
    start_date: Union[None, Unset, datetime.datetime] = UNSET,
    end_date: Union[None, Unset, datetime.datetime] = UNSET,
    period: Union[Unset, str] = "7d",
) -> Optional[Union[Any, HTTPValidationError]]:
    """Export Analytics

     Export analytics reports.

    Args:
        format: Export format
        metrics: List of metrics to export
        start_date: Start date for analytics
        end_date: End date for analytics
        period: Predefined period
        current_user: Current authenticated user
        analytics_service: Analytics service

    Returns:
        Exported analytics report

    Args:
        format_ (Union[Unset, str]): Export format (json, csv, xlsx) Default: 'json'.
        metrics (list[str]): List of metrics to export
        start_date (Union[None, Unset, datetime.datetime]): Start date for analytics
        end_date (Union[None, Unset, datetime.datetime]): End date for analytics
        period (Union[Unset, str]): Predefined period (1h, 24h, 7d, 30d, 90d) Default: '7d'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            client=client,
            format_=format_,
            metrics=metrics,
            start_date=start_date,
            end_date=end_date,
            period=period,
        )
    ).parsed
