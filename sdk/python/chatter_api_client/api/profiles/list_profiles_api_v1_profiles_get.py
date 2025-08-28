from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.profile_list_response import ProfileListResponse
from ...models.profile_type import ProfileType
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    profile_type: Union[None, ProfileType, Unset] = UNSET,
    llm_provider: Union[None, Unset, str] = UNSET,
    tags: Union[None, Unset, list[str]] = UNSET,
    is_public: Union[None, Unset, bool] = UNSET,
    limit: Union[Unset, int] = 50,
    offset: Union[Unset, int] = 0,
    sort_by: Union[Unset, str] = "created_at",
    sort_order: Union[Unset, str] = "desc",
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_profile_type: Union[None, Unset, str]
    if isinstance(profile_type, Unset):
        json_profile_type = UNSET
    elif isinstance(profile_type, ProfileType):
        json_profile_type = profile_type.value
    else:
        json_profile_type = profile_type
    params["profile_type"] = json_profile_type

    json_llm_provider: Union[None, Unset, str]
    if isinstance(llm_provider, Unset):
        json_llm_provider = UNSET
    else:
        json_llm_provider = llm_provider
    params["llm_provider"] = json_llm_provider

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
        "url": "/api/v1/profiles",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, ProfileListResponse]]:
    if response.status_code == 200:
        response_200 = ProfileListResponse.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, ProfileListResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    profile_type: Union[None, ProfileType, Unset] = UNSET,
    llm_provider: Union[None, Unset, str] = UNSET,
    tags: Union[None, Unset, list[str]] = UNSET,
    is_public: Union[None, Unset, bool] = UNSET,
    limit: Union[Unset, int] = 50,
    offset: Union[Unset, int] = 0,
    sort_by: Union[Unset, str] = "created_at",
    sort_order: Union[Unset, str] = "desc",
) -> Response[Union[HTTPValidationError, ProfileListResponse]]:
    """List Profiles

     List user's profiles.

    Args:
        profile_type: Filter by profile type
        llm_provider: Filter by LLM provider
        tags: Filter by tags
        is_public: Filter by public status
        limit: Maximum number of results
        offset: Number of results to skip
        sort_by: Sort field
        sort_order: Sort order (asc/desc)
        current_user: Current authenticated user
        profile_service: Profile service

    Returns:
        List of profiles with pagination info

    Args:
        profile_type (Union[None, ProfileType, Unset]): Filter by profile type
        llm_provider (Union[None, Unset, str]): Filter by LLM provider
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
        Response[Union[HTTPValidationError, ProfileListResponse]]
    """

    kwargs = _get_kwargs(
        profile_type=profile_type,
        llm_provider=llm_provider,
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
    profile_type: Union[None, ProfileType, Unset] = UNSET,
    llm_provider: Union[None, Unset, str] = UNSET,
    tags: Union[None, Unset, list[str]] = UNSET,
    is_public: Union[None, Unset, bool] = UNSET,
    limit: Union[Unset, int] = 50,
    offset: Union[Unset, int] = 0,
    sort_by: Union[Unset, str] = "created_at",
    sort_order: Union[Unset, str] = "desc",
) -> Optional[Union[HTTPValidationError, ProfileListResponse]]:
    """List Profiles

     List user's profiles.

    Args:
        profile_type: Filter by profile type
        llm_provider: Filter by LLM provider
        tags: Filter by tags
        is_public: Filter by public status
        limit: Maximum number of results
        offset: Number of results to skip
        sort_by: Sort field
        sort_order: Sort order (asc/desc)
        current_user: Current authenticated user
        profile_service: Profile service

    Returns:
        List of profiles with pagination info

    Args:
        profile_type (Union[None, ProfileType, Unset]): Filter by profile type
        llm_provider (Union[None, Unset, str]): Filter by LLM provider
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
        Union[HTTPValidationError, ProfileListResponse]
    """

    return sync_detailed(
        client=client,
        profile_type=profile_type,
        llm_provider=llm_provider,
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
    profile_type: Union[None, ProfileType, Unset] = UNSET,
    llm_provider: Union[None, Unset, str] = UNSET,
    tags: Union[None, Unset, list[str]] = UNSET,
    is_public: Union[None, Unset, bool] = UNSET,
    limit: Union[Unset, int] = 50,
    offset: Union[Unset, int] = 0,
    sort_by: Union[Unset, str] = "created_at",
    sort_order: Union[Unset, str] = "desc",
) -> Response[Union[HTTPValidationError, ProfileListResponse]]:
    """List Profiles

     List user's profiles.

    Args:
        profile_type: Filter by profile type
        llm_provider: Filter by LLM provider
        tags: Filter by tags
        is_public: Filter by public status
        limit: Maximum number of results
        offset: Number of results to skip
        sort_by: Sort field
        sort_order: Sort order (asc/desc)
        current_user: Current authenticated user
        profile_service: Profile service

    Returns:
        List of profiles with pagination info

    Args:
        profile_type (Union[None, ProfileType, Unset]): Filter by profile type
        llm_provider (Union[None, Unset, str]): Filter by LLM provider
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
        Response[Union[HTTPValidationError, ProfileListResponse]]
    """

    kwargs = _get_kwargs(
        profile_type=profile_type,
        llm_provider=llm_provider,
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
    profile_type: Union[None, ProfileType, Unset] = UNSET,
    llm_provider: Union[None, Unset, str] = UNSET,
    tags: Union[None, Unset, list[str]] = UNSET,
    is_public: Union[None, Unset, bool] = UNSET,
    limit: Union[Unset, int] = 50,
    offset: Union[Unset, int] = 0,
    sort_by: Union[Unset, str] = "created_at",
    sort_order: Union[Unset, str] = "desc",
) -> Optional[Union[HTTPValidationError, ProfileListResponse]]:
    """List Profiles

     List user's profiles.

    Args:
        profile_type: Filter by profile type
        llm_provider: Filter by LLM provider
        tags: Filter by tags
        is_public: Filter by public status
        limit: Maximum number of results
        offset: Number of results to skip
        sort_by: Sort field
        sort_order: Sort order (asc/desc)
        current_user: Current authenticated user
        profile_service: Profile service

    Returns:
        List of profiles with pagination info

    Args:
        profile_type (Union[None, ProfileType, Unset]): Filter by profile type
        llm_provider (Union[None, Unset, str]): Filter by LLM provider
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
        Union[HTTPValidationError, ProfileListResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            profile_type=profile_type,
            llm_provider=llm_provider,
            tags=tags,
            is_public=is_public,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    ).parsed
