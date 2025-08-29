from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.chat_request import ChatRequest
from ...models.chat_response import ChatResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    template_name: str,
    *,
    body: ChatRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/api/v1/chat/template/{template_name}",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ChatResponse, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = ChatResponse.from_dict(response.json())

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
) -> Response[Union[ChatResponse, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    template_name: str,
    *,
    client: AuthenticatedClient,
    body: ChatRequest,
) -> Response[Union[ChatResponse, HTTPValidationError]]:
    """Chat With Template

     Chat using a specific workflow template.

    Args:
        template_name (str):
        body (ChatRequest): Schema for chat request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ChatResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        template_name=template_name,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    template_name: str,
    *,
    client: AuthenticatedClient,
    body: ChatRequest,
) -> Optional[Union[ChatResponse, HTTPValidationError]]:
    """Chat With Template

     Chat using a specific workflow template.

    Args:
        template_name (str):
        body (ChatRequest): Schema for chat request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ChatResponse, HTTPValidationError]
    """

    return sync_detailed(
        template_name=template_name,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    template_name: str,
    *,
    client: AuthenticatedClient,
    body: ChatRequest,
) -> Response[Union[ChatResponse, HTTPValidationError]]:
    """Chat With Template

     Chat using a specific workflow template.

    Args:
        template_name (str):
        body (ChatRequest): Schema for chat request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ChatResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        template_name=template_name,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    template_name: str,
    *,
    client: AuthenticatedClient,
    body: ChatRequest,
) -> Optional[Union[ChatResponse, HTTPValidationError]]:
    """Chat With Template

     Chat using a specific workflow template.

    Args:
        template_name (str):
        body (ChatRequest): Schema for chat request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ChatResponse, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            template_name=template_name,
            client=client,
            body=body,
        )
    ).parsed
