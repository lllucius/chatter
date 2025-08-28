from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.provider_list import ProviderList
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    page: Union[Unset, int] = 1,
    per_page: Union[Unset, int] = 20,
    active_only: Union[Unset, bool] = True,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["per_page"] = per_page

    params["active_only"] = active_only

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/models/providers",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, ProviderList]]:
    if response.status_code == 200:
        response_200 = ProviderList.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, ProviderList]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, int] = 1,
    per_page: Union[Unset, int] = 20,
    active_only: Union[Unset, bool] = True,
) -> Response[Union[HTTPValidationError, ProviderList]]:
    """List Providers

     List all providers.

    Args:
        page (Union[Unset, int]): Page number Default: 1.
        per_page (Union[Unset, int]): Items per page Default: 20.
        active_only (Union[Unset, bool]): Show only active providers Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, ProviderList]]
    """

    kwargs = _get_kwargs(
        page=page,
        per_page=per_page,
        active_only=active_only,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, int] = 1,
    per_page: Union[Unset, int] = 20,
    active_only: Union[Unset, bool] = True,
) -> Optional[Union[HTTPValidationError, ProviderList]]:
    """List Providers

     List all providers.

    Args:
        page (Union[Unset, int]): Page number Default: 1.
        per_page (Union[Unset, int]): Items per page Default: 20.
        active_only (Union[Unset, bool]): Show only active providers Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, ProviderList]
    """

    return sync_detailed(
        client=client,
        page=page,
        per_page=per_page,
        active_only=active_only,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, int] = 1,
    per_page: Union[Unset, int] = 20,
    active_only: Union[Unset, bool] = True,
) -> Response[Union[HTTPValidationError, ProviderList]]:
    """List Providers

     List all providers.

    Args:
        page (Union[Unset, int]): Page number Default: 1.
        per_page (Union[Unset, int]): Items per page Default: 20.
        active_only (Union[Unset, bool]): Show only active providers Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, ProviderList]]
    """

    kwargs = _get_kwargs(
        page=page,
        per_page=per_page,
        active_only=active_only,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, int] = 1,
    per_page: Union[Unset, int] = 20,
    active_only: Union[Unset, bool] = True,
) -> Optional[Union[HTTPValidationError, ProviderList]]:
    """List Providers

     List all providers.

    Args:
        page (Union[Unset, int]): Page number Default: 1.
        per_page (Union[Unset, int]): Items per page Default: 20.
        active_only (Union[Unset, bool]): Show only active providers Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, ProviderList]
    """

    return (
        await asyncio_detailed(
            client=client,
            page=page,
            per_page=per_page,
            active_only=active_only,
        )
    ).parsed
