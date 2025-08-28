from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.model_def_update import ModelDefUpdate
from ...models.model_def_with_provider import ModelDefWithProvider
from ...types import Response


def _get_kwargs(
    model_id: str,
    *,
    body: ModelDefUpdate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/api/v1/models/models/{model_id}",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, ModelDefWithProvider]]:
    if response.status_code == 200:
        response_200 = ModelDefWithProvider.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, ModelDefWithProvider]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    model_id: str,
    *,
    client: AuthenticatedClient,
    body: ModelDefUpdate,
) -> Response[Union[HTTPValidationError, ModelDefWithProvider]]:
    """Update Model

     Update a model definition.

    Args:
        model_id (str):
        body (ModelDefUpdate): Schema for updating a model definition.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, ModelDefWithProvider]]
    """

    kwargs = _get_kwargs(
        model_id=model_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    model_id: str,
    *,
    client: AuthenticatedClient,
    body: ModelDefUpdate,
) -> Optional[Union[HTTPValidationError, ModelDefWithProvider]]:
    """Update Model

     Update a model definition.

    Args:
        model_id (str):
        body (ModelDefUpdate): Schema for updating a model definition.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, ModelDefWithProvider]
    """

    return sync_detailed(
        model_id=model_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    model_id: str,
    *,
    client: AuthenticatedClient,
    body: ModelDefUpdate,
) -> Response[Union[HTTPValidationError, ModelDefWithProvider]]:
    """Update Model

     Update a model definition.

    Args:
        model_id (str):
        body (ModelDefUpdate): Schema for updating a model definition.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, ModelDefWithProvider]]
    """

    kwargs = _get_kwargs(
        model_id=model_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    model_id: str,
    *,
    client: AuthenticatedClient,
    body: ModelDefUpdate,
) -> Optional[Union[HTTPValidationError, ModelDefWithProvider]]:
    """Update Model

     Update a model definition.

    Args:
        model_id (str):
        body (ModelDefUpdate): Schema for updating a model definition.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, ModelDefWithProvider]
    """

    return (
        await asyncio_detailed(
            model_id=model_id,
            client=client,
            body=body,
        )
    ).parsed
