# JobStatsResponse

Response schema for job statistics.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_jobs** | **int** | Total number of jobs | 
**pending_jobs** | **int** | Number of pending jobs | 
**running_jobs** | **int** | Number of running jobs | 
**completed_jobs** | **int** | Number of completed jobs | 
**failed_jobs** | **int** | Number of failed jobs | 
**queue_size** | **int** | Current queue size | 
**active_workers** | **int** | Number of active workers | 

## Example

```python
from chatter_sdk.models.job_stats_response import JobStatsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of JobStatsResponse from a JSON string
job_stats_response_instance = JobStatsResponse.from_json(json)
# print the JSON string representation of the object
print(JobStatsResponse.to_json())

# convert the object into a dict
job_stats_response_dict = job_stats_response_instance.to_dict()
# create an instance of JobStatsResponse from a dict
job_stats_response_from_dict = JobStatsResponse.from_dict(job_stats_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


