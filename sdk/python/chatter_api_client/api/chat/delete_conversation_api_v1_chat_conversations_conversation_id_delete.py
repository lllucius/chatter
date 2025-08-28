from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.conversation_delete_response import ConversationDeleteResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    conversation_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": f"/api/v1/chat/conversations/{conversation_id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ConversationDeleteResponse, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = ConversationDeleteResponse.from_dict(response.json())

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
) -> Response[Union[ConversationDeleteResponse, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    conversation_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[ConversationDeleteResponse, HTTPValidationError]]:
    """Delete Conversation

     Delete conversation.

    Args:
        conversation_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ConversationDeleteResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        conversation_id=conversation_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    conversation_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[ConversationDeleteResponse, HTTPValidationError]]:
    """Delete Conversation

     Delete conversation.

    Args:
        conversation_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ConversationDeleteResponse, HTTPValidationError]
    """

    return sync_detailed(
        conversation_id=conversation_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    conversation_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[ConversationDeleteResponse, HTTPValidationError]]:
    """Delete Conversation

     Delete conversation.

    Args:
        conversation_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ConversationDeleteResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        conversation_id=conversation_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    conversation_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[ConversationDeleteResponse, HTTPValidationError]]:
    """Delete Conversation

     Delete conversation.

    Args:
        conversation_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ConversationDeleteResponse, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            conversation_id=conversation_id,
            client=client,
        )
    ).parsed
