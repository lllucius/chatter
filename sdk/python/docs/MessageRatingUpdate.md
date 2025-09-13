# MessageRatingUpdate

Schema for updating message rating.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**rating** | **float** | Rating value from 0.0 to 5.0 | 

## Example

```python
from chatter_sdk.models.message_rating_update import MessageRatingUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of MessageRatingUpdate from a JSON string
message_rating_update_instance = MessageRatingUpdate.from_json(json)
# print the JSON string representation of the object
print(MessageRatingUpdate.to_json())

# convert the object into a dict
message_rating_update_dict = message_rating_update_instance.to_dict()
# create an instance of MessageRatingUpdate from a dict
message_rating_update_from_dict = MessageRatingUpdate.from_dict(message_rating_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


