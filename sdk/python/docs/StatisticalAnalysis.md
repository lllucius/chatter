# StatisticalAnalysis

Statistical analysis results.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**confidence_level** | **float** | Confidence level used | 
**statistical_significance** | **bool** | Is result statistically significant | 
**p_value** | **float** | P-value | 
**effect_size** | **float** | Effect size | 
**power** | **float** | Statistical power | 
**confidence_intervals** | **Dict[str, List[float]]** | Confidence intervals by variant | 

## Example

```python
from chatter_sdk.models.statistical_analysis import StatisticalAnalysis

# TODO update the JSON string below
json = "{}"
# create an instance of StatisticalAnalysis from a JSON string
statistical_analysis_instance = StatisticalAnalysis.from_json(json)
# print the JSON string representation of the object
print(StatisticalAnalysis.to_json())

# convert the object into a dict
statistical_analysis_dict = statistical_analysis_instance.to_dict()
# create an instance of StatisticalAnalysis from a dict
statistical_analysis_from_dict = StatisticalAnalysis.from_dict(statistical_analysis_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


