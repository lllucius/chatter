# AgentBulkDeleteRequest

Request schema for bulk agent deletion.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**agent_ids** | **List[str]** | List of agent IDs to delete (max 50) | 

## Example

```python
from chatter_sdk.models.agent_bulk_delete_request import AgentBulkDeleteRequest

# TODO update the JSON string below
json = "{}"
# create an instance of AgentBulkDeleteRequest from a JSON string
agent_bulk_delete_request_instance = AgentBulkDeleteRequest.from_json(json)
# print the JSON string representation of the object
print(AgentBulkDeleteRequest.to_json())

# convert the object into a dict
agent_bulk_delete_request_dict = agent_bulk_delete_request_instance.to_dict()
# create an instance of AgentBulkDeleteRequest from a dict
agent_bulk_delete_request_from_dict = AgentBulkDeleteRequest.from_dict(agent_bulk_delete_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


