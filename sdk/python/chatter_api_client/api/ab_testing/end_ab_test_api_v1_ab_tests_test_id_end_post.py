from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.ab_test_action_response import ABTestActionResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response


def _get_kwargs(
    test_id: str,
    *,
    winner_variant: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["winner_variant"] = winner_variant

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/api/v1/ab-tests/{test_id}/end",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ABTestActionResponse, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = ABTestActionResponse.from_dict(response.json())

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
) -> Response[Union[ABTestActionResponse, HTTPValidationError]]:
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
    winner_variant: str,
) -> Response[Union[ABTestActionResponse, HTTPValidationError]]:
    """End Ab Test

     End A/B test and declare winner.

    Args:
        test_id: A/B test ID
        winner_variant: Winning variant identifier
        current_user: Current authenticated user
        ab_test_manager: A/B test manager instance

    Returns:
        Action response

    Args:
        test_id (str):
        winner_variant (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ABTestActionResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        test_id=test_id,
        winner_variant=winner_variant,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    test_id: str,
    *,
    client: AuthenticatedClient,
    winner_variant: str,
) -> Optional[Union[ABTestActionResponse, HTTPValidationError]]:
    """End Ab Test

     End A/B test and declare winner.

    Args:
        test_id: A/B test ID
        winner_variant: Winning variant identifier
        current_user: Current authenticated user
        ab_test_manager: A/B test manager instance

    Returns:
        Action response

    Args:
        test_id (str):
        winner_variant (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ABTestActionResponse, HTTPValidationError]
    """

    return sync_detailed(
        test_id=test_id,
        client=client,
        winner_variant=winner_variant,
    ).parsed


async def asyncio_detailed(
    test_id: str,
    *,
    client: AuthenticatedClient,
    winner_variant: str,
) -> Response[Union[ABTestActionResponse, HTTPValidationError]]:
    """End Ab Test

     End A/B test and declare winner.

    Args:
        test_id: A/B test ID
        winner_variant: Winning variant identifier
        current_user: Current authenticated user
        ab_test_manager: A/B test manager instance

    Returns:
        Action response

    Args:
        test_id (str):
        winner_variant (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ABTestActionResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        test_id=test_id,
        winner_variant=winner_variant,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    test_id: str,
    *,
    client: AuthenticatedClient,
    winner_variant: str,
) -> Optional[Union[ABTestActionResponse, HTTPValidationError]]:
    """End Ab Test

     End A/B test and declare winner.

    Args:
        test_id: A/B test ID
        winner_variant: Winning variant identifier
        current_user: Current authenticated user
        ab_test_manager: A/B test manager instance

    Returns:
        Action response

    Args:
        test_id (str):
        winner_variant (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ABTestActionResponse, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            test_id=test_id,
            client=client,
            winner_variant=winner_variant,
        )
    ).parsed
