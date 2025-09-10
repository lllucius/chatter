# ComplexityMetrics

Schema for workflow complexity metrics.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**score** | **int** | Overall complexity score | 
**node_count** | **int** | Number of nodes | 
**edge_count** | **int** | Number of edges | 
**depth** | **int** | Maximum path depth | 
**branching_factor** | **float** | Average branching factor | 
**loop_complexity** | **int** | Loop complexity score | [optional] [default to 0]
**conditional_complexity** | **int** | Conditional complexity score | [optional] [default to 0]

## Example

```python
from chatter_sdk.models.complexity_metrics import ComplexityMetrics

# TODO update the JSON string below
json = "{}"
# create an instance of ComplexityMetrics from a JSON string
complexity_metrics_instance = ComplexityMetrics.from_json(json)
# print the JSON string representation of the object
print(ComplexityMetrics.to_json())

# convert the object into a dict
complexity_metrics_dict = complexity_metrics_instance.to_dict()
# create an instance of ComplexityMetrics from a dict
complexity_metrics_from_dict = ComplexityMetrics.from_dict(complexity_metrics_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


