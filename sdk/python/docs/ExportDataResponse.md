# ExportDataResponse

Response schema for data export.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**export_id** | **str** | Export ID | 
**status** | **str** | Export status | 
**download_url** | **str** |  | [optional] 
**file_size** | **int** |  | [optional] 
**record_count** | **int** |  | [optional] 
**created_at** | **datetime** | Export creation timestamp | 
**completed_at** | **datetime** |  | [optional] 
**expires_at** | **datetime** |  | [optional] 

## Example

```python
from chatter_sdk.models.export_data_response import ExportDataResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ExportDataResponse from a JSON string
export_data_response_instance = ExportDataResponse.from_json(json)
# print the JSON string representation of the object
print(ExportDataResponse.to_json())

# convert the object into a dict
export_data_response_dict = export_data_response_instance.to_dict()
# create an instance of ExportDataResponse from a dict
export_data_response_from_dict = ExportDataResponse.from_dict(export_data_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


