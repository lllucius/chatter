from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.tool_operation_response import ToolOperationResponse
from ...types import Response


def _get_kwargs(
    tool_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/api/v1/toolservers/tools/{tool_id}/enable",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, ToolOperationResponse]]:
    if response.status_code == 200:
        response_200 = ToolOperationResponse.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, ToolOperationResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    tool_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[HTTPValidationError, ToolOperationResponse]]:
    """Enable Tool

     Enable a specific tool.

    Args:
        tool_id: Tool ID
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        Operation result

    Args:
        tool_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, ToolOperationResponse]]
    """

    kwargs = _get_kwargs(
        tool_id=tool_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    tool_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[HTTPValidationError, ToolOperationResponse]]:
    """Enable Tool

     Enable a specific tool.

    Args:
        tool_id: Tool ID
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        Operation result

    Args:
        tool_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, ToolOperationResponse]
    """

    return sync_detailed(
        tool_id=tool_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    tool_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[HTTPValidationError, ToolOperationResponse]]:
    """Enable Tool

     Enable a specific tool.

    Args:
        tool_id: Tool ID
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        Operation result

    Args:
        tool_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, ToolOperationResponse]]
    """

    kwargs = _get_kwargs(
        tool_id=tool_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    tool_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[HTTPValidationError, ToolOperationResponse]]:
    """Enable Tool

     Enable a specific tool.

    Args:
        tool_id: Tool ID
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        Operation result

    Args:
        tool_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, ToolOperationResponse]
    """

    return (
        await asyncio_detailed(
            tool_id=tool_id,
            client=client,
        )
    ).parsed
