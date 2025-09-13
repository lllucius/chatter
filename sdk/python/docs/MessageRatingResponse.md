# MessageRatingResponse

Response schema for message rating update.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** | Rating update result message | 
**rating** | **float** | Updated rating value | 
**rating_count** | **int** | Total number of ratings | 

## Example

```python
from chatter_sdk.models.message_rating_response import MessageRatingResponse

# TODO update the JSON string below
json = "{}"
# create an instance of MessageRatingResponse from a JSON string
message_rating_response_instance = MessageRatingResponse.from_json(json)
# print the JSON string representation of the object
print(MessageRatingResponse.to_json())

# convert the object into a dict
message_rating_response_dict = message_rating_response_instance.to_dict()
# create an instance of MessageRatingResponse from a dict
message_rating_response_from_dict = MessageRatingResponse.from_dict(message_rating_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


