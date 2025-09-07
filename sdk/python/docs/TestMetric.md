# TestMetric

Test metric data.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**metric_type** | [**MetricType**](MetricType.md) |  | 
**variant_name** | **str** | Variant name | 
**value** | **float** | Metric value | 
**sample_size** | **int** | Sample size | 
**confidence_interval** | **List[float]** |  | [optional] 

## Example

```python
from chatter_sdk.models.test_metric import TestMetric

# TODO update the JSON string below
json = "{}"
# create an instance of TestMetric from a JSON string
test_metric_instance = TestMetric.from_json(json)
# print the JSON string representation of the object
print(TestMetric.to_json())

# convert the object into a dict
test_metric_dict = test_metric_instance.to_dict()
# create an instance of TestMetric from a dict
test_metric_from_dict = TestMetric.from_dict(test_metric_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


