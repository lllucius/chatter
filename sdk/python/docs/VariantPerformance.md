# VariantPerformance

Performance data for a specific variant.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Variant name | 
**participants** | **int** | Number of participants | 
**conversions** | **int** | Number of conversions | 
**conversion_rate** | **float** | Conversion rate | 
**revenue** | **float** | Total revenue | [optional] [default to 0.0]
**cost** | **float** | Total cost | [optional] [default to 0.0]
**roi** | **float** | Return on investment | [optional] [default to 0.0]

## Example

```python
from chatter_sdk.models.variant_performance import VariantPerformance

# TODO update the JSON string below
json = "{}"
# create an instance of VariantPerformance from a JSON string
variant_performance_instance = VariantPerformance.from_json(json)
# print the JSON string representation of the object
print(VariantPerformance.to_json())

# convert the object into a dict
variant_performance_dict = variant_performance_instance.to_dict()
# create an instance of VariantPerformance from a dict
variant_performance_from_dict = VariantPerformance.from_dict(variant_performance_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


