from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.job_list_response import JobListResponse
from ...models.job_priority import JobPriority
from ...models.job_status import JobStatus
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    status: Union[JobStatus, None, Unset] = UNSET,
    priority: Union[JobPriority, None, Unset] = UNSET,
    function_name: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_status: Union[None, Unset, str]
    if isinstance(status, Unset):
        json_status = UNSET
    elif isinstance(status, JobStatus):
        json_status = status.value
    else:
        json_status = status
    params["status"] = json_status

    json_priority: Union[None, Unset, str]
    if isinstance(priority, Unset):
        json_priority = UNSET
    elif isinstance(priority, JobPriority):
        json_priority = priority.value
    else:
        json_priority = priority
    params["priority"] = json_priority

    json_function_name: Union[None, Unset, str]
    if isinstance(function_name, Unset):
        json_function_name = UNSET
    else:
        json_function_name = function_name
    params["function_name"] = json_function_name

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/jobs/",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, JobListResponse]]:
    if response.status_code == 200:
        response_200 = JobListResponse.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, JobListResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    status: Union[JobStatus, None, Unset] = UNSET,
    priority: Union[JobPriority, None, Unset] = UNSET,
    function_name: Union[None, Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, JobListResponse]]:
    """List Jobs

     List jobs with optional filtering.

    Args:
        request: List request parameters
        current_user: Current authenticated user

    Returns:
        List of jobs

    Args:
        status (Union[JobStatus, None, Unset]):
        priority (Union[JobPriority, None, Unset]):
        function_name (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, JobListResponse]]
    """

    kwargs = _get_kwargs(
        status=status,
        priority=priority,
        function_name=function_name,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    status: Union[JobStatus, None, Unset] = UNSET,
    priority: Union[JobPriority, None, Unset] = UNSET,
    function_name: Union[None, Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, JobListResponse]]:
    """List Jobs

     List jobs with optional filtering.

    Args:
        request: List request parameters
        current_user: Current authenticated user

    Returns:
        List of jobs

    Args:
        status (Union[JobStatus, None, Unset]):
        priority (Union[JobPriority, None, Unset]):
        function_name (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, JobListResponse]
    """

    return sync_detailed(
        client=client,
        status=status,
        priority=priority,
        function_name=function_name,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    status: Union[JobStatus, None, Unset] = UNSET,
    priority: Union[JobPriority, None, Unset] = UNSET,
    function_name: Union[None, Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, JobListResponse]]:
    """List Jobs

     List jobs with optional filtering.

    Args:
        request: List request parameters
        current_user: Current authenticated user

    Returns:
        List of jobs

    Args:
        status (Union[JobStatus, None, Unset]):
        priority (Union[JobPriority, None, Unset]):
        function_name (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, JobListResponse]]
    """

    kwargs = _get_kwargs(
        status=status,
        priority=priority,
        function_name=function_name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    status: Union[JobStatus, None, Unset] = UNSET,
    priority: Union[JobPriority, None, Unset] = UNSET,
    function_name: Union[None, Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, JobListResponse]]:
    """List Jobs

     List jobs with optional filtering.

    Args:
        request: List request parameters
        current_user: Current authenticated user

    Returns:
        List of jobs

    Args:
        status (Union[JobStatus, None, Unset]):
        priority (Union[JobPriority, None, Unset]):
        function_name (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, JobListResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            status=status,
            priority=priority,
            function_name=function_name,
        )
    ).parsed
