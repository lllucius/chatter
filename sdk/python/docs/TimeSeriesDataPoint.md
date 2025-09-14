# TimeSeriesDataPoint

Schema for time series chart data point.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_date** | **str** | Date label (e.g., &#39;Mon&#39;, &#39;Jan 01&#39;) | 
**conversations** | **int** |  | [optional] 
**tokens** | **int** |  | [optional] 
**cost** | **float** |  | [optional] 
**workflows** | **int** |  | [optional] 
**agents** | **int** |  | [optional] 
**ab_tests** | **int** |  | [optional] 

## Example

```python
from chatter_sdk.models.time_series_data_point import TimeSeriesDataPoint

# TODO update the JSON string below
json = "{}"
# create an instance of TimeSeriesDataPoint from a JSON string
time_series_data_point_instance = TimeSeriesDataPoint.from_json(json)
# print the JSON string representation of the object
print(TimeSeriesDataPoint.to_json())

# convert the object into a dict
time_series_data_point_dict = time_series_data_point_instance.to_dict()
# create an instance of TimeSeriesDataPoint from a dict
time_series_data_point_from_dict = TimeSeriesDataPoint.from_dict(time_series_data_point_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


