# BodyListAgentsApiV1AgentsGet


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**pagination** | [**PaginationRequest**](PaginationRequest.md) |  | [optional] 
**sorting** | [**SortingRequest**](SortingRequest.md) |  | [optional] 
**tags** | **List[str]** |  | [optional] 

## Example

```python
from chatter_sdk.models.body_list_agents_api_v1_agents_get import BodyListAgentsApiV1AgentsGet

# TODO update the JSON string below
json = "{}"
# create an instance of BodyListAgentsApiV1AgentsGet from a JSON string
body_list_agents_api_v1_agents_get_instance = BodyListAgentsApiV1AgentsGet.from_json(json)
# print the JSON string representation of the object
print(BodyListAgentsApiV1AgentsGet.to_json())

# convert the object into a dict
body_list_agents_api_v1_agents_get_dict = body_list_agents_api_v1_agents_get_instance.to_dict()
# create an instance of BodyListAgentsApiV1AgentsGet from a dict
body_list_agents_api_v1_agents_get_from_dict = BodyListAgentsApiV1AgentsGet.from_dict(body_list_agents_api_v1_agents_get_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


