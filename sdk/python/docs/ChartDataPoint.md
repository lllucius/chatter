# ChartDataPoint

Schema for a single chart data point.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Data point label | 
**value** | **float** | Data point value | 
**color** | **str** |  | [optional] 

## Example

```python
from chatter_sdk.models.chart_data_point import ChartDataPoint

# TODO update the JSON string below
json = "{}"
# create an instance of ChartDataPoint from a JSON string
chart_data_point_instance = ChartDataPoint.from_json(json)
# print the JSON string representation of the object
print(ChartDataPoint.to_json())

# convert the object into a dict
chart_data_point_dict = chart_data_point_instance.to_dict()
# create an instance of ChartDataPoint from a dict
chart_data_point_from_dict = ChartDataPoint.from_dict(chart_data_point_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


