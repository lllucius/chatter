# JobResponse

Response schema for job data.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Job ID | 
**name** | **str** | Job name | 
**function_name** | **str** | Function name | 
**priority** | [**JobPriority**](JobPriority.md) |  | 
**status** | [**JobStatus**](JobStatus.md) |  | 
**created_at** | **datetime** | Creation timestamp | 
**started_at** | **datetime** |  | [optional] 
**completed_at** | **datetime** |  | [optional] 
**scheduled_at** | **datetime** |  | [optional] 
**retry_count** | **int** | Number of retry attempts | 
**max_retries** | **int** | Maximum retry attempts | 
**error_message** | **str** |  | [optional] 
**result** | [**AnyOf**](AnyOf.md) | Job result if completed | [optional] 
**progress** | **int** | Job progress percentage | [optional] [default to 0]
**progress_message** | **str** |  | [optional] 

## Example

```python
from chatter_sdk.models.job_response import JobResponse

# TODO update the JSON string below
json = "{}"
# create an instance of JobResponse from a JSON string
job_response_instance = JobResponse.from_json(json)
# print the JSON string representation of the object
print(JobResponse.to_json())

# convert the object into a dict
job_response_dict = job_response_instance.to_dict()
# create an instance of JobResponse from a dict
job_response_from_dict = JobResponse.from_dict(job_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


