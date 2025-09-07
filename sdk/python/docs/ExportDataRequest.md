# ExportDataRequest

Request schema for data export API.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**scope** | [**ExportScope**](ExportScope.md) |  | 
**format** | [**DataFormat**](DataFormat.md) |  | [optional] 
**user_id** | **str** |  | [optional] 
**conversation_id** | **str** |  | [optional] 
**date_from** | **datetime** |  | [optional] 
**date_to** | **datetime** |  | [optional] 
**include_metadata** | **bool** | Include metadata | [optional] [default to True]
**compress** | **bool** | Compress export file | [optional] [default to True]
**encrypt** | **bool** | Encrypt export file | [optional] [default to False]
**custom_query** | **Dict[str, object]** |  | [optional] 

## Example

```python
from chatter_sdk.models.export_data_request import ExportDataRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ExportDataRequest from a JSON string
export_data_request_instance = ExportDataRequest.from_json(json)
# print the JSON string representation of the object
print(ExportDataRequest.to_json())

# convert the object into a dict
export_data_request_dict = export_data_request_instance.to_dict()
# create an instance of ExportDataRequest from a dict
export_data_request_from_dict = ExportDataRequest.from_dict(export_data_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


