from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_ab_test_performance_api_v1_ab_tests_test_id_performance_get_response_get_ab_test_performance_api_v1_ab_tests_test_id_performance_get import (
    GetAbTestPerformanceApiV1AbTestsTestIdPerformanceGetResponseGetAbTestPerformanceApiV1AbTestsTestIdPerformanceGet,
)
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    test_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v1/ab-tests/{test_id}/performance",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        GetAbTestPerformanceApiV1AbTestsTestIdPerformanceGetResponseGetAbTestPerformanceApiV1AbTestsTestIdPerformanceGet,
        HTTPValidationError,
    ]
]:
    if response.status_code == 200:
        response_200 = GetAbTestPerformanceApiV1AbTestsTestIdPerformanceGetResponseGetAbTestPerformanceApiV1AbTestsTestIdPerformanceGet.from_dict(
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
        GetAbTestPerformanceApiV1AbTestsTestIdPerformanceGetResponseGetAbTestPerformanceApiV1AbTestsTestIdPerformanceGet,
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
    test_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[
    Union[
        GetAbTestPerformanceApiV1AbTestsTestIdPerformanceGetResponseGetAbTestPerformanceApiV1AbTestsTestIdPerformanceGet,
        HTTPValidationError,
    ]
]:
    """Get Ab Test Performance

     Get A/B test performance results by variant.

    Args:
        test_id: A/B test ID
        current_user: Current authenticated user
        ab_test_manager: A/B test manager instance

    Returns:
        Performance results per variant

    Args:
        test_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetAbTestPerformanceApiV1AbTestsTestIdPerformanceGetResponseGetAbTestPerformanceApiV1AbTestsTestIdPerformanceGet, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        test_id=test_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    test_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[
    Union[
        GetAbTestPerformanceApiV1AbTestsTestIdPerformanceGetResponseGetAbTestPerformanceApiV1AbTestsTestIdPerformanceGet,
        HTTPValidationError,
    ]
]:
    """Get Ab Test Performance

     Get A/B test performance results by variant.

    Args:
        test_id: A/B test ID
        current_user: Current authenticated user
        ab_test_manager: A/B test manager instance

    Returns:
        Performance results per variant

    Args:
        test_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetAbTestPerformanceApiV1AbTestsTestIdPerformanceGetResponseGetAbTestPerformanceApiV1AbTestsTestIdPerformanceGet, HTTPValidationError]
    """

    return sync_detailed(
        test_id=test_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    test_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[
    Union[
        GetAbTestPerformanceApiV1AbTestsTestIdPerformanceGetResponseGetAbTestPerformanceApiV1AbTestsTestIdPerformanceGet,
        HTTPValidationError,
    ]
]:
    """Get Ab Test Performance

     Get A/B test performance results by variant.

    Args:
        test_id: A/B test ID
        current_user: Current authenticated user
        ab_test_manager: A/B test manager instance

    Returns:
        Performance results per variant

    Args:
        test_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetAbTestPerformanceApiV1AbTestsTestIdPerformanceGetResponseGetAbTestPerformanceApiV1AbTestsTestIdPerformanceGet, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        test_id=test_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    test_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[
    Union[
        GetAbTestPerformanceApiV1AbTestsTestIdPerformanceGetResponseGetAbTestPerformanceApiV1AbTestsTestIdPerformanceGet,
        HTTPValidationError,
    ]
]:
    """Get Ab Test Performance

     Get A/B test performance results by variant.

    Args:
        test_id: A/B test ID
        current_user: Current authenticated user
        ab_test_manager: A/B test manager instance

    Returns:
        Performance results per variant

    Args:
        test_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetAbTestPerformanceApiV1AbTestsTestIdPerformanceGetResponseGetAbTestPerformanceApiV1AbTestsTestIdPerformanceGet, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            test_id=test_id,
            client=client,
        )
    ).parsed
