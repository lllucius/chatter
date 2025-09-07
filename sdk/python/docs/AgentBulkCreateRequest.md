# AgentBulkCreateRequest

Request schema for bulk agent creation.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**agents** | [**List[AgentCreateRequest]**](AgentCreateRequest.md) | List of agents to create (max 10) | 

## Example

```python
from chatter_sdk.models.agent_bulk_create_request import AgentBulkCreateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of AgentBulkCreateRequest from a JSON string
agent_bulk_create_request_instance = AgentBulkCreateRequest.from_json(json)
# print the JSON string representation of the object
print(AgentBulkCreateRequest.to_json())

# convert the object into a dict
agent_bulk_create_request_dict = agent_bulk_create_request_instance.to_dict()
# create an instance of AgentBulkCreateRequest from a dict
agent_bulk_create_request_from_dict = AgentBulkCreateRequest.from_dict(agent_bulk_create_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


