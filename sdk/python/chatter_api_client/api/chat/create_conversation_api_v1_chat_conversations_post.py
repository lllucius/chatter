from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.conversation_create import ConversationCreate
from ...models.conversation_response import ConversationResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    *,
    body: ConversationCreate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/chat/conversations",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ConversationResponse, HTTPValidationError]]:
    if response.status_code == 201:
        response_201 = ConversationResponse.from_dict(response.json())

        return response_201

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[ConversationResponse, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: ConversationCreate,
) -> Response[Union[ConversationResponse, HTTPValidationError]]:
    """Create Conversation

     Create a new conversation.

    Args:
        conversation_data: Conversation creation data
        current_user: Current authenticated user
        chat_service: Chat service

    Returns:
        Created conversation

    Args:
        body (ConversationCreate): Schema for creating a conversation.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ConversationResponse, HTTPValidationError]]
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
    body: ConversationCreate,
) -> Optional[Union[ConversationResponse, HTTPValidationError]]:
    """Create Conversation

     Create a new conversation.

    Args:
        conversation_data: Conversation creation data
        current_user: Current authenticated user
        chat_service: Chat service

    Returns:
        Created conversation

    Args:
        body (ConversationCreate): Schema for creating a conversation.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ConversationResponse, HTTPValidationError]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: ConversationCreate,
) -> Response[Union[ConversationResponse, HTTPValidationError]]:
    """Create Conversation

     Create a new conversation.

    Args:
        conversation_data: Conversation creation data
        current_user: Current authenticated user
        chat_service: Chat service

    Returns:
        Created conversation

    Args:
        body (ConversationCreate): Schema for creating a conversation.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ConversationResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: ConversationCreate,
) -> Optional[Union[ConversationResponse, HTTPValidationError]]:
    """Create Conversation

     Create a new conversation.

    Args:
        conversation_data: Conversation creation data
        current_user: Current authenticated user
        chat_service: Chat service

    Returns:
        Created conversation

    Args:
        body (ConversationCreate): Schema for creating a conversation.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ConversationResponse, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
