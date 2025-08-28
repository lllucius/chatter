from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.conversation_search_response import ConversationSearchResponse
from ...models.conversation_status import ConversationStatus
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    query: Union[None, Unset, str] = UNSET,
    status: Union[ConversationStatus, None, Unset] = UNSET,
    limit: Union[Unset, int] = 50,
    offset: Union[Unset, int] = 0,
    sort_by: Union[Unset, str] = "created_at",
    sort_order: Union[Unset, str] = "desc",
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_query: Union[None, Unset, str]
    if isinstance(query, Unset):
        json_query = UNSET
    else:
        json_query = query
    params["query"] = json_query

    json_status: Union[None, Unset, str]
    if isinstance(status, Unset):
        json_status = UNSET
    elif isinstance(status, ConversationStatus):
        json_status = status.value
    else:
        json_status = status
    params["status"] = json_status

    params["limit"] = limit

    params["offset"] = offset

    params["sort_by"] = sort_by

    params["sort_order"] = sort_order

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/chat/conversations",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, ConversationSearchResponse]]:
    if response.status_code == 200:
        response_200 = ConversationSearchResponse.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = cast(Any, None)
        return response_401

    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403

    if response.status_code == 422:
        response_422 = cast(Any, None)
        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, ConversationSearchResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    query: Union[None, Unset, str] = UNSET,
    status: Union[ConversationStatus, None, Unset] = UNSET,
    limit: Union[Unset, int] = 50,
    offset: Union[Unset, int] = 0,
    sort_by: Union[Unset, str] = "created_at",
    sort_order: Union[Unset, str] = "desc",
) -> Response[Union[Any, ConversationSearchResponse]]:
    """List Conversations

     List user's conversations.

    Note: Filters may be ignored if not supported by the service implementation.

    Args:
        query (Union[None, Unset, str]): Search query
        status (Union[ConversationStatus, None, Unset]): Filter by status
        limit (Union[Unset, int]): Maximum number of results Default: 50.
        offset (Union[Unset, int]): Number of results to skip Default: 0.
        sort_by (Union[Unset, str]): Sort field Default: 'created_at'.
        sort_order (Union[Unset, str]): Sort order Default: 'desc'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ConversationSearchResponse]]
    """

    kwargs = _get_kwargs(
        query=query,
        status=status,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    query: Union[None, Unset, str] = UNSET,
    status: Union[ConversationStatus, None, Unset] = UNSET,
    limit: Union[Unset, int] = 50,
    offset: Union[Unset, int] = 0,
    sort_by: Union[Unset, str] = "created_at",
    sort_order: Union[Unset, str] = "desc",
) -> Optional[Union[Any, ConversationSearchResponse]]:
    """List Conversations

     List user's conversations.

    Note: Filters may be ignored if not supported by the service implementation.

    Args:
        query (Union[None, Unset, str]): Search query
        status (Union[ConversationStatus, None, Unset]): Filter by status
        limit (Union[Unset, int]): Maximum number of results Default: 50.
        offset (Union[Unset, int]): Number of results to skip Default: 0.
        sort_by (Union[Unset, str]): Sort field Default: 'created_at'.
        sort_order (Union[Unset, str]): Sort order Default: 'desc'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ConversationSearchResponse]
    """

    return sync_detailed(
        client=client,
        query=query,
        status=status,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    query: Union[None, Unset, str] = UNSET,
    status: Union[ConversationStatus, None, Unset] = UNSET,
    limit: Union[Unset, int] = 50,
    offset: Union[Unset, int] = 0,
    sort_by: Union[Unset, str] = "created_at",
    sort_order: Union[Unset, str] = "desc",
) -> Response[Union[Any, ConversationSearchResponse]]:
    """List Conversations

     List user's conversations.

    Note: Filters may be ignored if not supported by the service implementation.

    Args:
        query (Union[None, Unset, str]): Search query
        status (Union[ConversationStatus, None, Unset]): Filter by status
        limit (Union[Unset, int]): Maximum number of results Default: 50.
        offset (Union[Unset, int]): Number of results to skip Default: 0.
        sort_by (Union[Unset, str]): Sort field Default: 'created_at'.
        sort_order (Union[Unset, str]): Sort order Default: 'desc'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ConversationSearchResponse]]
    """

    kwargs = _get_kwargs(
        query=query,
        status=status,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    query: Union[None, Unset, str] = UNSET,
    status: Union[ConversationStatus, None, Unset] = UNSET,
    limit: Union[Unset, int] = 50,
    offset: Union[Unset, int] = 0,
    sort_by: Union[Unset, str] = "created_at",
    sort_order: Union[Unset, str] = "desc",
) -> Optional[Union[Any, ConversationSearchResponse]]:
    """List Conversations

     List user's conversations.

    Note: Filters may be ignored if not supported by the service implementation.

    Args:
        query (Union[None, Unset, str]): Search query
        status (Union[ConversationStatus, None, Unset]): Filter by status
        limit (Union[Unset, int]): Maximum number of results Default: 50.
        offset (Union[Unset, int]): Number of results to skip Default: 0.
        sort_by (Union[Unset, str]): Sort field Default: 'created_at'.
        sort_order (Union[Unset, str]): Sort order Default: 'desc'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ConversationSearchResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            query=query,
            status=status,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    ).parsed
