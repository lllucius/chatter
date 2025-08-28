from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.ab_test_results_response import ABTestResultsResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    test_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v1/ab-tests/{test_id}/results",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ABTestResultsResponse, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = ABTestResultsResponse.from_dict(response.json())

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
) -> Response[Union[ABTestResultsResponse, HTTPValidationError]]:
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
) -> Response[Union[ABTestResultsResponse, HTTPValidationError]]:
    """Get Ab Test Results

     Get A/B test results and analysis.

    Args:
        test_id: Test ID
        current_user: Current authenticated user
        ab_test_manager: A/B test manager instance

    Returns:
        Test results and analysis

    Args:
        test_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ABTestResultsResponse, HTTPValidationError]]
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
) -> Optional[Union[ABTestResultsResponse, HTTPValidationError]]:
    """Get Ab Test Results

     Get A/B test results and analysis.

    Args:
        test_id: Test ID
        current_user: Current authenticated user
        ab_test_manager: A/B test manager instance

    Returns:
        Test results and analysis

    Args:
        test_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ABTestResultsResponse, HTTPValidationError]
    """

    return sync_detailed(
        test_id=test_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    test_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[ABTestResultsResponse, HTTPValidationError]]:
    """Get Ab Test Results

     Get A/B test results and analysis.

    Args:
        test_id: Test ID
        current_user: Current authenticated user
        ab_test_manager: A/B test manager instance

    Returns:
        Test results and analysis

    Args:
        test_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ABTestResultsResponse, HTTPValidationError]]
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
) -> Optional[Union[ABTestResultsResponse, HTTPValidationError]]:
    """Get Ab Test Results

     Get A/B test results and analysis.

    Args:
        test_id: Test ID
        current_user: Current authenticated user
        ab_test_manager: A/B test manager instance

    Returns:
        Test results and analysis

    Args:
        test_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ABTestResultsResponse, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            test_id=test_id,
            client=client,
        )
    ).parsed
