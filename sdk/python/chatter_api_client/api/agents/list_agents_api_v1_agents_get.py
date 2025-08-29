from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.agent_list_response import AgentListResponse
from ...models.agent_status import AgentStatus
from ...models.agent_type import AgentType
from ...models.body_list_agents_api_v1_agents_get import BodyListAgentsApiV1AgentsGet
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: BodyListAgentsApiV1AgentsGet,
    agent_type: Union[AgentType, None, Unset] = UNSET,
    status: Union[AgentStatus, None, Unset] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    json_agent_type: Union[None, Unset, str]
    if isinstance(agent_type, Unset):
        json_agent_type = UNSET
    elif isinstance(agent_type, AgentType):
        json_agent_type = agent_type.value
    else:
        json_agent_type = agent_type
    params["agent_type"] = json_agent_type

    json_status: Union[None, Unset, str]
    if isinstance(status, Unset):
        json_status = UNSET
    elif isinstance(status, AgentStatus):
        json_status = status.value
    else:
        json_status = status
    params["status"] = json_status

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/agents/",
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AgentListResponse, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = AgentListResponse.from_dict(response.json())

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
) -> Response[Union[AgentListResponse, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: BodyListAgentsApiV1AgentsGet,
    agent_type: Union[AgentType, None, Unset] = UNSET,
    status: Union[AgentStatus, None, Unset] = UNSET,
) -> Response[Union[AgentListResponse, HTTPValidationError]]:
    """List Agents

     List all agents with optional filtering and pagination.

    Args:
        request: List request parameters with pagination
        current_user: Current authenticated user
        agent_manager: Agent manager instance

    Returns:
        Paginated list of agents

    Args:
        agent_type (Union[AgentType, None, Unset]):
        status (Union[AgentStatus, None, Unset]):
        body (BodyListAgentsApiV1AgentsGet):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AgentListResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        body=body,
        agent_type=agent_type,
        status=status,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: BodyListAgentsApiV1AgentsGet,
    agent_type: Union[AgentType, None, Unset] = UNSET,
    status: Union[AgentStatus, None, Unset] = UNSET,
) -> Optional[Union[AgentListResponse, HTTPValidationError]]:
    """List Agents

     List all agents with optional filtering and pagination.

    Args:
        request: List request parameters with pagination
        current_user: Current authenticated user
        agent_manager: Agent manager instance

    Returns:
        Paginated list of agents

    Args:
        agent_type (Union[AgentType, None, Unset]):
        status (Union[AgentStatus, None, Unset]):
        body (BodyListAgentsApiV1AgentsGet):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AgentListResponse, HTTPValidationError]
    """

    return sync_detailed(
        client=client,
        body=body,
        agent_type=agent_type,
        status=status,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: BodyListAgentsApiV1AgentsGet,
    agent_type: Union[AgentType, None, Unset] = UNSET,
    status: Union[AgentStatus, None, Unset] = UNSET,
) -> Response[Union[AgentListResponse, HTTPValidationError]]:
    """List Agents

     List all agents with optional filtering and pagination.

    Args:
        request: List request parameters with pagination
        current_user: Current authenticated user
        agent_manager: Agent manager instance

    Returns:
        Paginated list of agents

    Args:
        agent_type (Union[AgentType, None, Unset]):
        status (Union[AgentStatus, None, Unset]):
        body (BodyListAgentsApiV1AgentsGet):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AgentListResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        body=body,
        agent_type=agent_type,
        status=status,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: BodyListAgentsApiV1AgentsGet,
    agent_type: Union[AgentType, None, Unset] = UNSET,
    status: Union[AgentStatus, None, Unset] = UNSET,
) -> Optional[Union[AgentListResponse, HTTPValidationError]]:
    """List Agents

     List all agents with optional filtering and pagination.

    Args:
        request: List request parameters with pagination
        current_user: Current authenticated user
        agent_manager: Agent manager instance

    Returns:
        Paginated list of agents

    Args:
        agent_type (Union[AgentType, None, Unset]):
        status (Union[AgentStatus, None, Unset]):
        body (BodyListAgentsApiV1AgentsGet):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AgentListResponse, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            agent_type=agent_type,
            status=status,
        )
    ).parsed
