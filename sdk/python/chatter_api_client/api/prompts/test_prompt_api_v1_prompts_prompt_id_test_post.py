from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.prompt_test_request import PromptTestRequest
from ...models.prompt_test_response import PromptTestResponse
from ...types import Response


def _get_kwargs(
    prompt_id: str,
    *,
    body: PromptTestRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/api/v1/prompts/{prompt_id}/test",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, PromptTestResponse]]:
    if response.status_code == 200:
        response_200 = PromptTestResponse.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, PromptTestResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    prompt_id: str,
    *,
    client: AuthenticatedClient,
    body: PromptTestRequest,
) -> Response[Union[HTTPValidationError, PromptTestResponse]]:
    """Test Prompt

     Test prompt with given variables.

    Args:
        prompt_id: Prompt ID
        test_request: Test request
        current_user: Current authenticated user
        prompt_service: Prompt service

    Returns:
        Test results

    Args:
        prompt_id (str):
        body (PromptTestRequest): Schema for prompt test request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, PromptTestResponse]]
    """

    kwargs = _get_kwargs(
        prompt_id=prompt_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    prompt_id: str,
    *,
    client: AuthenticatedClient,
    body: PromptTestRequest,
) -> Optional[Union[HTTPValidationError, PromptTestResponse]]:
    """Test Prompt

     Test prompt with given variables.

    Args:
        prompt_id: Prompt ID
        test_request: Test request
        current_user: Current authenticated user
        prompt_service: Prompt service

    Returns:
        Test results

    Args:
        prompt_id (str):
        body (PromptTestRequest): Schema for prompt test request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, PromptTestResponse]
    """

    return sync_detailed(
        prompt_id=prompt_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    prompt_id: str,
    *,
    client: AuthenticatedClient,
    body: PromptTestRequest,
) -> Response[Union[HTTPValidationError, PromptTestResponse]]:
    """Test Prompt

     Test prompt with given variables.

    Args:
        prompt_id: Prompt ID
        test_request: Test request
        current_user: Current authenticated user
        prompt_service: Prompt service

    Returns:
        Test results

    Args:
        prompt_id (str):
        body (PromptTestRequest): Schema for prompt test request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, PromptTestResponse]]
    """

    kwargs = _get_kwargs(
        prompt_id=prompt_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    prompt_id: str,
    *,
    client: AuthenticatedClient,
    body: PromptTestRequest,
) -> Optional[Union[HTTPValidationError, PromptTestResponse]]:
    """Test Prompt

     Test prompt with given variables.

    Args:
        prompt_id: Prompt ID
        test_request: Test request
        current_user: Current authenticated user
        prompt_service: Prompt service

    Returns:
        Test results

    Args:
        prompt_id (str):
        body (PromptTestRequest): Schema for prompt test request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, PromptTestResponse]
    """

    return (
        await asyncio_detailed(
            prompt_id=prompt_id,
            client=client,
            body=body,
        )
    ).parsed
