from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.ab_test_list_response import ABTestListResponse
from ...models.http_validation_error import HTTPValidationError
from ...models.test_status import TestStatus
from ...models.test_type import TestType
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: Union[None, list[str]],
    status: Union[None, TestStatus, Unset] = UNSET,
    test_type: Union[None, TestType, Unset] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    json_status: Union[None, Unset, str]
    if isinstance(status, Unset):
        json_status = UNSET
    elif isinstance(status, TestStatus):
        json_status = status.value
    else:
        json_status = status
    params["status"] = json_status

    json_test_type: Union[None, Unset, str]
    if isinstance(test_type, Unset):
        json_test_type = UNSET
    elif isinstance(test_type, TestType):
        json_test_type = test_type.value
    else:
        json_test_type = test_type
    params["test_type"] = json_test_type

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/ab-tests/",
        "params": params,
    }

    _kwargs["json"]: Union[None, list[str]]
    if isinstance(body, list):
        _kwargs["json"] = body

    else:
        _kwargs["json"] = body

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ABTestListResponse, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = ABTestListResponse.from_dict(response.json())

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
) -> Response[Union[ABTestListResponse, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: Union[None, list[str]],
    status: Union[None, TestStatus, Unset] = UNSET,
    test_type: Union[None, TestType, Unset] = UNSET,
) -> Response[Union[ABTestListResponse, HTTPValidationError]]:
    """List Ab Tests

     List A/B tests with optional filtering.

    Args:
        request: List request parameters
        current_user: Current authenticated user
        ab_test_manager: A/B test manager instance

    Returns:
        List of A/B tests

    Args:
        status (Union[None, TestStatus, Unset]):
        test_type (Union[None, TestType, Unset]):
        body (Union[None, list[str]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ABTestListResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        body=body,
        status=status,
        test_type=test_type,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: Union[None, list[str]],
    status: Union[None, TestStatus, Unset] = UNSET,
    test_type: Union[None, TestType, Unset] = UNSET,
) -> Optional[Union[ABTestListResponse, HTTPValidationError]]:
    """List Ab Tests

     List A/B tests with optional filtering.

    Args:
        request: List request parameters
        current_user: Current authenticated user
        ab_test_manager: A/B test manager instance

    Returns:
        List of A/B tests

    Args:
        status (Union[None, TestStatus, Unset]):
        test_type (Union[None, TestType, Unset]):
        body (Union[None, list[str]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ABTestListResponse, HTTPValidationError]
    """

    return sync_detailed(
        client=client,
        body=body,
        status=status,
        test_type=test_type,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: Union[None, list[str]],
    status: Union[None, TestStatus, Unset] = UNSET,
    test_type: Union[None, TestType, Unset] = UNSET,
) -> Response[Union[ABTestListResponse, HTTPValidationError]]:
    """List Ab Tests

     List A/B tests with optional filtering.

    Args:
        request: List request parameters
        current_user: Current authenticated user
        ab_test_manager: A/B test manager instance

    Returns:
        List of A/B tests

    Args:
        status (Union[None, TestStatus, Unset]):
        test_type (Union[None, TestType, Unset]):
        body (Union[None, list[str]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ABTestListResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        body=body,
        status=status,
        test_type=test_type,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: Union[None, list[str]],
    status: Union[None, TestStatus, Unset] = UNSET,
    test_type: Union[None, TestType, Unset] = UNSET,
) -> Optional[Union[ABTestListResponse, HTTPValidationError]]:
    """List Ab Tests

     List A/B tests with optional filtering.

    Args:
        request: List request parameters
        current_user: Current authenticated user
        ab_test_manager: A/B test manager instance

    Returns:
        List of A/B tests

    Args:
        status (Union[None, TestStatus, Unset]):
        test_type (Union[None, TestType, Unset]):
        body (Union[None, list[str]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ABTestListResponse, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            status=status,
            test_type=test_type,
        )
    ).parsed
