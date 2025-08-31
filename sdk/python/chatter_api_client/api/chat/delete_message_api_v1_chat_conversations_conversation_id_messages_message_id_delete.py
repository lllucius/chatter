from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.message_delete_response import MessageDeleteResponse
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
) -> Optional[Union[HTTPValidationError, MessageDeleteResponse]]:
    if response.status_code == 200:
        response_200 = MessageDeleteResponse.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, MessageDeleteResponse]]:
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
) -> Response[Union[HTTPValidationError, MessageDeleteResponse]]:
    """Delete Message

     Delete a message from conversation.

    Args:
        conversation_id (str):
        message_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, MessageDeleteResponse]]
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
) -> Optional[Union[HTTPValidationError, MessageDeleteResponse]]:
    """Delete Message

     Delete a message from conversation.

    Args:
        conversation_id (str):
        message_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, MessageDeleteResponse]
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
) -> Response[Union[HTTPValidationError, MessageDeleteResponse]]:
    """Delete Message

     Delete a message from conversation.

    Args:
        conversation_id (str):
        message_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, MessageDeleteResponse]]
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
) -> Optional[Union[HTTPValidationError, MessageDeleteResponse]]:
    """Delete Message

     Delete a message from conversation.

    Args:
        conversation_id (str):
        message_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, MessageDeleteResponse]
    """

    return (
        await asyncio_detailed(
            conversation_id=conversation_id,
            message_id=message_id,
            client=client,
        )
    ).parsed
