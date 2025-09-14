# IntegratedDashboardStats

Schema for integrated dashboard statistics.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**workflows** | **Dict[str, object]** | Workflow statistics | 
**agents** | **Dict[str, object]** | Agent statistics | 
**ab_testing** | **Dict[str, object]** | A/B testing statistics | 
**system** | **Dict[str, object]** | System statistics | 

## Example

```python
from chatter_sdk.models.integrated_dashboard_stats import IntegratedDashboardStats

# TODO update the JSON string below
json = "{}"
# create an instance of IntegratedDashboardStats from a JSON string
integrated_dashboard_stats_instance = IntegratedDashboardStats.from_json(json)
# print the JSON string representation of the object
print(IntegratedDashboardStats.to_json())

# convert the object into a dict
integrated_dashboard_stats_dict = integrated_dashboard_stats_instance.to_dict()
# create an instance of IntegratedDashboardStats from a dict
integrated_dashboard_stats_from_dict = IntegratedDashboardStats.from_dict(integrated_dashboard_stats_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


