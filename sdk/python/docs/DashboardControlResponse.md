# DashboardControlResponse

Schema for dashboard control responses.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** | Status of the operation | 
**user_id** | **str** | User ID | 
**message** | **str** | Operation message | 

## Example

```python
from chatter_sdk.models.dashboard_control_response import DashboardControlResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DashboardControlResponse from a JSON string
dashboard_control_response_instance = DashboardControlResponse.from_json(json)
# print the JSON string representation of the object
print(DashboardControlResponse.to_json())

# convert the object into a dict
dashboard_control_response_dict = dashboard_control_response_instance.to_dict()
# create an instance of DashboardControlResponse from a dict
dashboard_control_response_from_dict = DashboardControlResponse.from_dict(dashboard_control_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


