from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.embedding_space_update import EmbeddingSpaceUpdate
from ...models.embedding_space_with_model import EmbeddingSpaceWithModel
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    space_id: str,
    *,
    body: EmbeddingSpaceUpdate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/api/v1/models/embedding-spaces/{space_id}",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[EmbeddingSpaceWithModel, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = EmbeddingSpaceWithModel.from_dict(response.json())

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
) -> Response[Union[EmbeddingSpaceWithModel, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    space_id: str,
    *,
    client: AuthenticatedClient,
    body: EmbeddingSpaceUpdate,
) -> Response[Union[EmbeddingSpaceWithModel, HTTPValidationError]]:
    """Update Embedding Space

     Update an embedding space.

    Args:
        space_id (str):
        body (EmbeddingSpaceUpdate): Schema for updating an embedding space.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[EmbeddingSpaceWithModel, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        space_id=space_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    space_id: str,
    *,
    client: AuthenticatedClient,
    body: EmbeddingSpaceUpdate,
) -> Optional[Union[EmbeddingSpaceWithModel, HTTPValidationError]]:
    """Update Embedding Space

     Update an embedding space.

    Args:
        space_id (str):
        body (EmbeddingSpaceUpdate): Schema for updating an embedding space.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[EmbeddingSpaceWithModel, HTTPValidationError]
    """

    return sync_detailed(
        space_id=space_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    space_id: str,
    *,
    client: AuthenticatedClient,
    body: EmbeddingSpaceUpdate,
) -> Response[Union[EmbeddingSpaceWithModel, HTTPValidationError]]:
    """Update Embedding Space

     Update an embedding space.

    Args:
        space_id (str):
        body (EmbeddingSpaceUpdate): Schema for updating an embedding space.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[EmbeddingSpaceWithModel, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        space_id=space_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    space_id: str,
    *,
    client: AuthenticatedClient,
    body: EmbeddingSpaceUpdate,
) -> Optional[Union[EmbeddingSpaceWithModel, HTTPValidationError]]:
    """Update Embedding Space

     Update an embedding space.

    Args:
        space_id (str):
        body (EmbeddingSpaceUpdate): Schema for updating an embedding space.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[EmbeddingSpaceWithModel, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            space_id=space_id,
            client=client,
            body=body,
        )
    ).parsed
