# JobActionResponse

Response schema for job actions.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** | Whether action was successful | 
**message** | **str** | Action result message | 
**job_id** | **str** | Job ID | 

## Example

```python
from chatter_sdk.models.job_action_response import JobActionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of JobActionResponse from a JSON string
job_action_response_instance = JobActionResponse.from_json(json)
# print the JSON string representation of the object
print(JobActionResponse.to_json())

# convert the object into a dict
job_action_response_dict = job_action_response_instance.to_dict()
# create an instance of JobActionResponse from a dict
job_action_response_from_dict = JobActionResponse.from_dict(job_action_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


