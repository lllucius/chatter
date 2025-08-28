from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.prompt_clone_request import PromptCloneRequest
from ...models.prompt_response import PromptResponse
from ...types import Response


def _get_kwargs(
    prompt_id: str,
    *,
    body: PromptCloneRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/api/v1/prompts/{prompt_id}/clone",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, PromptResponse]]:
    if response.status_code == 200:
        response_200 = PromptResponse.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, PromptResponse]]:
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
    body: PromptCloneRequest,
) -> Response[Union[HTTPValidationError, PromptResponse]]:
    """Clone Prompt

     Clone an existing prompt.

    Args:
        prompt_id: Source prompt ID
        clone_request: Clone request
        current_user: Current authenticated user
        prompt_service: Prompt service

    Returns:
        Cloned prompt information

    Args:
        prompt_id (str):
        body (PromptCloneRequest): Schema for prompt clone request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, PromptResponse]]
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
    body: PromptCloneRequest,
) -> Optional[Union[HTTPValidationError, PromptResponse]]:
    """Clone Prompt

     Clone an existing prompt.

    Args:
        prompt_id: Source prompt ID
        clone_request: Clone request
        current_user: Current authenticated user
        prompt_service: Prompt service

    Returns:
        Cloned prompt information

    Args:
        prompt_id (str):
        body (PromptCloneRequest): Schema for prompt clone request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, PromptResponse]
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
    body: PromptCloneRequest,
) -> Response[Union[HTTPValidationError, PromptResponse]]:
    """Clone Prompt

     Clone an existing prompt.

    Args:
        prompt_id: Source prompt ID
        clone_request: Clone request
        current_user: Current authenticated user
        prompt_service: Prompt service

    Returns:
        Cloned prompt information

    Args:
        prompt_id (str):
        body (PromptCloneRequest): Schema for prompt clone request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, PromptResponse]]
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
    body: PromptCloneRequest,
) -> Optional[Union[HTTPValidationError, PromptResponse]]:
    """Clone Prompt

     Clone an existing prompt.

    Args:
        prompt_id: Source prompt ID
        clone_request: Clone request
        current_user: Current authenticated user
        prompt_service: Prompt service

    Returns:
        Cloned prompt information

    Args:
        prompt_id (str):
        body (PromptCloneRequest): Schema for prompt clone request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, PromptResponse]
    """

    return (
        await asyncio_detailed(
            prompt_id=prompt_id,
            client=client,
            body=body,
        )
    ).parsed
