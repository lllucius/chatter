from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_workflow_templates_api_v1_chat_templates_get_response_get_workflow_templates_api_v1_chat_templates_get import (
    GetWorkflowTemplatesApiV1ChatTemplatesGetResponseGetWorkflowTemplatesApiV1ChatTemplatesGet,
)
from ...types import Response


def _get_kwargs() -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/chat/templates",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[GetWorkflowTemplatesApiV1ChatTemplatesGetResponseGetWorkflowTemplatesApiV1ChatTemplatesGet]:
    if response.status_code == 200:
        response_200 = (
            GetWorkflowTemplatesApiV1ChatTemplatesGetResponseGetWorkflowTemplatesApiV1ChatTemplatesGet.from_dict(
                response.json()
            )
        )

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[GetWorkflowTemplatesApiV1ChatTemplatesGetResponseGetWorkflowTemplatesApiV1ChatTemplatesGet]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[GetWorkflowTemplatesApiV1ChatTemplatesGetResponseGetWorkflowTemplatesApiV1ChatTemplatesGet]:
    """Get Workflow Templates

     Get available workflow templates.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetWorkflowTemplatesApiV1ChatTemplatesGetResponseGetWorkflowTemplatesApiV1ChatTemplatesGet]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
) -> Optional[GetWorkflowTemplatesApiV1ChatTemplatesGetResponseGetWorkflowTemplatesApiV1ChatTemplatesGet]:
    """Get Workflow Templates

     Get available workflow templates.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetWorkflowTemplatesApiV1ChatTemplatesGetResponseGetWorkflowTemplatesApiV1ChatTemplatesGet
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[GetWorkflowTemplatesApiV1ChatTemplatesGetResponseGetWorkflowTemplatesApiV1ChatTemplatesGet]:
    """Get Workflow Templates

     Get available workflow templates.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetWorkflowTemplatesApiV1ChatTemplatesGetResponseGetWorkflowTemplatesApiV1ChatTemplatesGet]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
) -> Optional[GetWorkflowTemplatesApiV1ChatTemplatesGetResponseGetWorkflowTemplatesApiV1ChatTemplatesGet]:
    """Get Workflow Templates

     Get available workflow templates.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetWorkflowTemplatesApiV1ChatTemplatesGetResponseGetWorkflowTemplatesApiV1ChatTemplatesGet
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
