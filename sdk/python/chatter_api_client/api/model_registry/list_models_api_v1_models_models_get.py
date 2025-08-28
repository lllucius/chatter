from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.model_def_list import ModelDefList
from ...models.model_type import ModelType
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    provider_id: Union[Unset, str] = UNSET,
    model_type: Union[Unset, ModelType] = UNSET,
    page: Union[Unset, int] = 1,
    per_page: Union[Unset, int] = 20,
    active_only: Union[Unset, bool] = True,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["provider_id"] = provider_id

    json_model_type: Union[Unset, str] = UNSET
    if not isinstance(model_type, Unset):
        json_model_type = model_type.value

    params["model_type"] = json_model_type

    params["page"] = page

    params["per_page"] = per_page

    params["active_only"] = active_only

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/models/models",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, ModelDefList]]:
    if response.status_code == 200:
        response_200 = ModelDefList.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, ModelDefList]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    provider_id: Union[Unset, str] = UNSET,
    model_type: Union[Unset, ModelType] = UNSET,
    page: Union[Unset, int] = 1,
    per_page: Union[Unset, int] = 20,
    active_only: Union[Unset, bool] = True,
) -> Response[Union[HTTPValidationError, ModelDefList]]:
    """List Models

     List all model definitions.

    Args:
        provider_id (Union[Unset, str]): Filter by provider ID
        model_type (Union[Unset, ModelType]): Types of AI models.
        page (Union[Unset, int]): Page number Default: 1.
        per_page (Union[Unset, int]): Items per page Default: 20.
        active_only (Union[Unset, bool]): Show only active models Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, ModelDefList]]
    """

    kwargs = _get_kwargs(
        provider_id=provider_id,
        model_type=model_type,
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
    provider_id: Union[Unset, str] = UNSET,
    model_type: Union[Unset, ModelType] = UNSET,
    page: Union[Unset, int] = 1,
    per_page: Union[Unset, int] = 20,
    active_only: Union[Unset, bool] = True,
) -> Optional[Union[HTTPValidationError, ModelDefList]]:
    """List Models

     List all model definitions.

    Args:
        provider_id (Union[Unset, str]): Filter by provider ID
        model_type (Union[Unset, ModelType]): Types of AI models.
        page (Union[Unset, int]): Page number Default: 1.
        per_page (Union[Unset, int]): Items per page Default: 20.
        active_only (Union[Unset, bool]): Show only active models Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, ModelDefList]
    """

    return sync_detailed(
        client=client,
        provider_id=provider_id,
        model_type=model_type,
        page=page,
        per_page=per_page,
        active_only=active_only,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    provider_id: Union[Unset, str] = UNSET,
    model_type: Union[Unset, ModelType] = UNSET,
    page: Union[Unset, int] = 1,
    per_page: Union[Unset, int] = 20,
    active_only: Union[Unset, bool] = True,
) -> Response[Union[HTTPValidationError, ModelDefList]]:
    """List Models

     List all model definitions.

    Args:
        provider_id (Union[Unset, str]): Filter by provider ID
        model_type (Union[Unset, ModelType]): Types of AI models.
        page (Union[Unset, int]): Page number Default: 1.
        per_page (Union[Unset, int]): Items per page Default: 20.
        active_only (Union[Unset, bool]): Show only active models Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, ModelDefList]]
    """

    kwargs = _get_kwargs(
        provider_id=provider_id,
        model_type=model_type,
        page=page,
        per_page=per_page,
        active_only=active_only,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    provider_id: Union[Unset, str] = UNSET,
    model_type: Union[Unset, ModelType] = UNSET,
    page: Union[Unset, int] = 1,
    per_page: Union[Unset, int] = 20,
    active_only: Union[Unset, bool] = True,
) -> Optional[Union[HTTPValidationError, ModelDefList]]:
    """List Models

     List all model definitions.

    Args:
        provider_id (Union[Unset, str]): Filter by provider ID
        model_type (Union[Unset, ModelType]): Types of AI models.
        page (Union[Unset, int]): Page number Default: 1.
        per_page (Union[Unset, int]): Items per page Default: 20.
        active_only (Union[Unset, bool]): Show only active models Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, ModelDefList]
    """

    return (
        await asyncio_detailed(
            client=client,
            provider_id=provider_id,
            model_type=model_type,
            page=page,
            per_page=per_page,
            active_only=active_only,
        )
    ).parsed
