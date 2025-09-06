# TestVariant

Test variant definition.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Variant name | 
**description** | **str** | Variant description | 
**configuration** | **Dict[str, object]** | Variant configuration | 
**weight** | **float** | Variant weight for allocation | [optional] [default to 1.0]

## Example

```python
from chatter_sdk.models.test_variant import TestVariant

# TODO update the JSON string below
json = "{}"
# create an instance of TestVariant from a JSON string
test_variant_instance = TestVariant.from_json(json)
# print the JSON string representation of the object
print(TestVariant.to_json())

# convert the object into a dict
test_variant_dict = test_variant_instance.to_dict()
# create an instance of TestVariant from a dict
test_variant_from_dict = TestVariant.from_dict(test_variant_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


