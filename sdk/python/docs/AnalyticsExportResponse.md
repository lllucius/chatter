# AnalyticsExportResponse

Schema for analytics export response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**export_id** | **str** | Export job ID | 
**status** | **str** | Export status | 
**download_url** | **str** |  | [optional] 
**created_at** | **datetime** | Export creation time | 
**expires_at** | **datetime** |  | [optional] 

## Example

```python
from chatter_sdk.models.analytics_export_response import AnalyticsExportResponse

# TODO update the JSON string below
json = "{}"
# create an instance of AnalyticsExportResponse from a JSON string
analytics_export_response_instance = AnalyticsExportResponse.from_json(json)
# print the JSON string representation of the object
print(AnalyticsExportResponse.to_json())

# convert the object into a dict
analytics_export_response_dict = analytics_export_response_instance.to_dict()
# create an instance of AnalyticsExportResponse from a dict
analytics_export_response_from_dict = AnalyticsExportResponse.from_dict(analytics_export_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


