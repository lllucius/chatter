# UserBehaviorAnalyticsResponse

Schema for user behavior analytics response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **str** | User ID | 
**session_count** | **int** | Number of sessions | 
**page_views** | **int** | Total page views | 
**time_spent_minutes** | **float** | Total time spent in minutes | 
**most_visited_pages** | **List[str]** | Most visited pages | 
**user_journey** | **List[Dict[str, object]]** | User journey data | 
**conversion_events** | **List[Dict[str, object]]** | Conversion events | 

## Example

```python
from chatter_sdk.models.user_behavior_analytics_response import UserBehaviorAnalyticsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of UserBehaviorAnalyticsResponse from a JSON string
user_behavior_analytics_response_instance = UserBehaviorAnalyticsResponse.from_json(json)
# print the JSON string representation of the object
print(UserBehaviorAnalyticsResponse.to_json())

# convert the object into a dict
user_behavior_analytics_response_dict = user_behavior_analytics_response_instance.to_dict()
# create an instance of UserBehaviorAnalyticsResponse from a dict
user_behavior_analytics_response_from_dict = UserBehaviorAnalyticsResponse.from_dict(user_behavior_analytics_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


