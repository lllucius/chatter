from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.prompt_category import PromptCategory
from ...models.prompt_list_response import PromptListResponse
from ...models.prompt_type import PromptType
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    prompt_type: Union[None, PromptType, Unset] = UNSET,
    category: Union[None, PromptCategory, Unset] = UNSET,
    tags: Union[None, Unset, list[str]] = UNSET,
    is_public: Union[None, Unset, bool] = UNSET,
    limit: Union[Unset, int] = 50,
    offset: Union[Unset, int] = 0,
    sort_by: Union[Unset, str] = "created_at",
    sort_order: Union[Unset, str] = "desc",
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_prompt_type: Union[None, Unset, str]
    if isinstance(prompt_type, Unset):
        json_prompt_type = UNSET
    elif isinstance(prompt_type, PromptType):
        json_prompt_type = prompt_type.value
    else:
        json_prompt_type = prompt_type
    params["prompt_type"] = json_prompt_type

    json_category: Union[None, Unset, str]
    if isinstance(category, Unset):
        json_category = UNSET
    elif isinstance(category, PromptCategory):
        json_category = category.value
    else:
        json_category = category
    params["category"] = json_category

    json_tags: Union[None, Unset, list[str]]
    if isinstance(tags, Unset):
        json_tags = UNSET
    elif isinstance(tags, list):
        json_tags = tags

    else:
        json_tags = tags
    params["tags"] = json_tags

    json_is_public: Union[None, Unset, bool]
    if isinstance(is_public, Unset):
        json_is_public = UNSET
    else:
        json_is_public = is_public
    params["is_public"] = json_is_public

    params["limit"] = limit

    params["offset"] = offset

    params["sort_by"] = sort_by

    params["sort_order"] = sort_order

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/prompts",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, PromptListResponse]]:
    if response.status_code == 200:
        response_200 = PromptListResponse.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, PromptListResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    prompt_type: Union[None, PromptType, Unset] = UNSET,
    category: Union[None, PromptCategory, Unset] = UNSET,
    tags: Union[None, Unset, list[str]] = UNSET,
    is_public: Union[None, Unset, bool] = UNSET,
    limit: Union[Unset, int] = 50,
    offset: Union[Unset, int] = 0,
    sort_by: Union[Unset, str] = "created_at",
    sort_order: Union[Unset, str] = "desc",
) -> Response[Union[HTTPValidationError, PromptListResponse]]:
    """List Prompts

     List user's prompts.

    Args:
        prompt_type: Filter by prompt type
        category: Filter by category
        tags: Filter by tags
        is_public: Filter by public status
        limit: Maximum number of results
        offset: Number of results to skip
        sort_by: Sort field
        sort_order: Sort order (asc/desc)
        current_user: Current authenticated user
        prompt_service: Prompt service

    Returns:
        List of prompts with pagination info

    Args:
        prompt_type (Union[None, PromptType, Unset]): Filter by prompt type
        category (Union[None, PromptCategory, Unset]): Filter by category
        tags (Union[None, Unset, list[str]]): Filter by tags
        is_public (Union[None, Unset, bool]): Filter by public status
        limit (Union[Unset, int]): Maximum number of results Default: 50.
        offset (Union[Unset, int]): Number of results to skip Default: 0.
        sort_by (Union[Unset, str]): Sort field Default: 'created_at'.
        sort_order (Union[Unset, str]): Sort order Default: 'desc'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, PromptListResponse]]
    """

    kwargs = _get_kwargs(
        prompt_type=prompt_type,
        category=category,
        tags=tags,
        is_public=is_public,
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
    prompt_type: Union[None, PromptType, Unset] = UNSET,
    category: Union[None, PromptCategory, Unset] = UNSET,
    tags: Union[None, Unset, list[str]] = UNSET,
    is_public: Union[None, Unset, bool] = UNSET,
    limit: Union[Unset, int] = 50,
    offset: Union[Unset, int] = 0,
    sort_by: Union[Unset, str] = "created_at",
    sort_order: Union[Unset, str] = "desc",
) -> Optional[Union[HTTPValidationError, PromptListResponse]]:
    """List Prompts

     List user's prompts.

    Args:
        prompt_type: Filter by prompt type
        category: Filter by category
        tags: Filter by tags
        is_public: Filter by public status
        limit: Maximum number of results
        offset: Number of results to skip
        sort_by: Sort field
        sort_order: Sort order (asc/desc)
        current_user: Current authenticated user
        prompt_service: Prompt service

    Returns:
        List of prompts with pagination info

    Args:
        prompt_type (Union[None, PromptType, Unset]): Filter by prompt type
        category (Union[None, PromptCategory, Unset]): Filter by category
        tags (Union[None, Unset, list[str]]): Filter by tags
        is_public (Union[None, Unset, bool]): Filter by public status
        limit (Union[Unset, int]): Maximum number of results Default: 50.
        offset (Union[Unset, int]): Number of results to skip Default: 0.
        sort_by (Union[Unset, str]): Sort field Default: 'created_at'.
        sort_order (Union[Unset, str]): Sort order Default: 'desc'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, PromptListResponse]
    """

    return sync_detailed(
        client=client,
        prompt_type=prompt_type,
        category=category,
        tags=tags,
        is_public=is_public,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    prompt_type: Union[None, PromptType, Unset] = UNSET,
    category: Union[None, PromptCategory, Unset] = UNSET,
    tags: Union[None, Unset, list[str]] = UNSET,
    is_public: Union[None, Unset, bool] = UNSET,
    limit: Union[Unset, int] = 50,
    offset: Union[Unset, int] = 0,
    sort_by: Union[Unset, str] = "created_at",
    sort_order: Union[Unset, str] = "desc",
) -> Response[Union[HTTPValidationError, PromptListResponse]]:
    """List Prompts

     List user's prompts.

    Args:
        prompt_type: Filter by prompt type
        category: Filter by category
        tags: Filter by tags
        is_public: Filter by public status
        limit: Maximum number of results
        offset: Number of results to skip
        sort_by: Sort field
        sort_order: Sort order (asc/desc)
        current_user: Current authenticated user
        prompt_service: Prompt service

    Returns:
        List of prompts with pagination info

    Args:
        prompt_type (Union[None, PromptType, Unset]): Filter by prompt type
        category (Union[None, PromptCategory, Unset]): Filter by category
        tags (Union[None, Unset, list[str]]): Filter by tags
        is_public (Union[None, Unset, bool]): Filter by public status
        limit (Union[Unset, int]): Maximum number of results Default: 50.
        offset (Union[Unset, int]): Number of results to skip Default: 0.
        sort_by (Union[Unset, str]): Sort field Default: 'created_at'.
        sort_order (Union[Unset, str]): Sort order Default: 'desc'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, PromptListResponse]]
    """

    kwargs = _get_kwargs(
        prompt_type=prompt_type,
        category=category,
        tags=tags,
        is_public=is_public,
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
    prompt_type: Union[None, PromptType, Unset] = UNSET,
    category: Union[None, PromptCategory, Unset] = UNSET,
    tags: Union[None, Unset, list[str]] = UNSET,
    is_public: Union[None, Unset, bool] = UNSET,
    limit: Union[Unset, int] = 50,
    offset: Union[Unset, int] = 0,
    sort_by: Union[Unset, str] = "created_at",
    sort_order: Union[Unset, str] = "desc",
) -> Optional[Union[HTTPValidationError, PromptListResponse]]:
    """List Prompts

     List user's prompts.

    Args:
        prompt_type: Filter by prompt type
        category: Filter by category
        tags: Filter by tags
        is_public: Filter by public status
        limit: Maximum number of results
        offset: Number of results to skip
        sort_by: Sort field
        sort_order: Sort order (asc/desc)
        current_user: Current authenticated user
        prompt_service: Prompt service

    Returns:
        List of prompts with pagination info

    Args:
        prompt_type (Union[None, PromptType, Unset]): Filter by prompt type
        category (Union[None, PromptCategory, Unset]): Filter by category
        tags (Union[None, Unset, list[str]]): Filter by tags
        is_public (Union[None, Unset, bool]): Filter by public status
        limit (Union[Unset, int]): Maximum number of results Default: 50.
        offset (Union[Unset, int]): Number of results to skip Default: 0.
        sort_by (Union[Unset, str]): Sort field Default: 'created_at'.
        sort_order (Union[Unset, str]): Sort order Default: 'desc'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, PromptListResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            prompt_type=prompt_type,
            category=category,
            tags=tags,
            is_public=is_public,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    ).parsed
