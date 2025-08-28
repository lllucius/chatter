from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.delete_message_api_v1_chat_conversations_conversation_id_messages_message_id_delete_response_delete_message_api_v1_chat_conversations_conversation_id_messages_message_id_delete import (
    DeleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDeleteResponseDeleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDelete,
)
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    conversation_id: str,
    message_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": f"/api/v1/chat/conversations/{conversation_id}/messages/{message_id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        DeleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDeleteResponseDeleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDelete,
        HTTPValidationError,
    ]
]:
    if response.status_code == 200:
        response_200 = DeleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDeleteResponseDeleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDelete.from_dict(
            response.json()
        )

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
) -> Response[
    Union[
        DeleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDeleteResponseDeleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDelete,
        HTTPValidationError,
    ]
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    conversation_id: str,
    message_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[
    Union[
        DeleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDeleteResponseDeleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDelete,
        HTTPValidationError,
    ]
]:
    """Delete Message

     Delete a message from conversation.

    Args:
        conversation_id (str):
        message_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DeleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDeleteResponseDeleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDelete, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        conversation_id=conversation_id,
        message_id=message_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    conversation_id: str,
    message_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[
    Union[
        DeleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDeleteResponseDeleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDelete,
        HTTPValidationError,
    ]
]:
    """Delete Message

     Delete a message from conversation.

    Args:
        conversation_id (str):
        message_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DeleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDeleteResponseDeleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDelete, HTTPValidationError]
    """

    return sync_detailed(
        conversation_id=conversation_id,
        message_id=message_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    conversation_id: str,
    message_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[
    Union[
        DeleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDeleteResponseDeleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDelete,
        HTTPValidationError,
    ]
]:
    """Delete Message

     Delete a message from conversation.

    Args:
        conversation_id (str):
        message_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DeleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDeleteResponseDeleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDelete, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        conversation_id=conversation_id,
        message_id=message_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    conversation_id: str,
    message_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[
    Union[
        DeleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDeleteResponseDeleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDelete,
        HTTPValidationError,
    ]
]:
    """Delete Message

     Delete a message from conversation.

    Args:
        conversation_id (str):
        message_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DeleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDeleteResponseDeleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDelete, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            conversation_id=conversation_id,
            message_id=message_id,
            client=client,
        )
    ).parsed
