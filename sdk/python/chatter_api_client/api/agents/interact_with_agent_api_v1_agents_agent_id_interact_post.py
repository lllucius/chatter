from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.agent_interact_request import AgentInteractRequest
from ...models.agent_interact_response import AgentInteractResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    agent_id: str,
    *,
    body: AgentInteractRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/api/v1/agents/{agent_id}/interact",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AgentInteractResponse, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = AgentInteractResponse.from_dict(response.json())

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
) -> Response[Union[AgentInteractResponse, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    agent_id: str,
    *,
    client: AuthenticatedClient,
    body: AgentInteractRequest,
) -> Response[Union[AgentInteractResponse, HTTPValidationError]]:
    """Interact With Agent

     Send a message to an agent and get a response.

    Args:
        agent_id: Agent ID
        interaction_data: Interaction data
        current_user: Current authenticated user
        agent_manager: Agent manager instance

    Returns:
        Agent response

    Args:
        agent_id (str):
        body (AgentInteractRequest): Request schema for interacting with an agent.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AgentInteractResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        agent_id=agent_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    agent_id: str,
    *,
    client: AuthenticatedClient,
    body: AgentInteractRequest,
) -> Optional[Union[AgentInteractResponse, HTTPValidationError]]:
    """Interact With Agent

     Send a message to an agent and get a response.

    Args:
        agent_id: Agent ID
        interaction_data: Interaction data
        current_user: Current authenticated user
        agent_manager: Agent manager instance

    Returns:
        Agent response

    Args:
        agent_id (str):
        body (AgentInteractRequest): Request schema for interacting with an agent.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AgentInteractResponse, HTTPValidationError]
    """

    return sync_detailed(
        agent_id=agent_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    agent_id: str,
    *,
    client: AuthenticatedClient,
    body: AgentInteractRequest,
) -> Response[Union[AgentInteractResponse, HTTPValidationError]]:
    """Interact With Agent

     Send a message to an agent and get a response.

    Args:
        agent_id: Agent ID
        interaction_data: Interaction data
        current_user: Current authenticated user
        agent_manager: Agent manager instance

    Returns:
        Agent response

    Args:
        agent_id (str):
        body (AgentInteractRequest): Request schema for interacting with an agent.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AgentInteractResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        agent_id=agent_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    agent_id: str,
    *,
    client: AuthenticatedClient,
    body: AgentInteractRequest,
) -> Optional[Union[AgentInteractResponse, HTTPValidationError]]:
    """Interact With Agent

     Send a message to an agent and get a response.

    Args:
        agent_id: Agent ID
        interaction_data: Interaction data
        current_user: Current authenticated user
        agent_manager: Agent manager instance

    Returns:
        Agent response

    Args:
        agent_id (str):
        body (AgentInteractRequest): Request schema for interacting with an agent.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AgentInteractResponse, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            agent_id=agent_id,
            client=client,
            body=body,
        )
    ).parsed
