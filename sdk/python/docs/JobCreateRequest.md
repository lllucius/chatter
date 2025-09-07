# JobCreateRequest

Request schema for creating a job.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Job name | 
**function_name** | **str** | Function to execute | 
**args** | **List[object]** | Function arguments | [optional] 
**kwargs** | **Dict[str, object]** | Function keyword arguments | [optional] 
**priority** | [**JobPriority**](JobPriority.md) |  | [optional] 
**max_retries** | **int** | Maximum retry attempts | [optional] [default to 3]
**schedule_at** | **datetime** |  | [optional] 

## Example

```python
from chatter_sdk.models.job_create_request import JobCreateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of JobCreateRequest from a JSON string
job_create_request_instance = JobCreateRequest.from_json(json)
# print the JSON string representation of the object
print(JobCreateRequest.to_json())

# convert the object into a dict
job_create_request_dict = job_create_request_instance.to_dict()
# create an instance of JobCreateRequest from a dict
job_create_request_from_dict = JobCreateRequest.from_dict(job_create_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


