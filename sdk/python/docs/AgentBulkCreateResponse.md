# AgentBulkCreateResponse

Response schema for bulk agent creation.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created** | [**List[AgentResponse]**](AgentResponse.md) | Successfully created agents | 
**failed** | **List[Dict[str, object]]** | Failed agent creations with errors | 
**total_requested** | **int** | Total agents requested | 
**total_created** | **int** | Total agents successfully created | 

## Example

```python
from chatter_sdk.models.agent_bulk_create_response import AgentBulkCreateResponse

# TODO update the JSON string below
json = "{}"
# create an instance of AgentBulkCreateResponse from a JSON string
agent_bulk_create_response_instance = AgentBulkCreateResponse.from_json(json)
# print the JSON string representation of the object
print(AgentBulkCreateResponse.to_json())

# convert the object into a dict
agent_bulk_create_response_dict = agent_bulk_create_response_instance.to_dict()
# create an instance of AgentBulkCreateResponse from a dict
agent_bulk_create_response_from_dict = AgentBulkCreateResponse.from_dict(agent_bulk_create_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


