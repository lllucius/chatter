# DatabaseHealthResponse

Schema for database health response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**connected** | **bool** | Database connection status | 
**response_time_ms** | **float** | Database response time in milliseconds | 
**active_connections** | **int** | Active database connections | 
**query_performance** | **Dict[str, float]** | Query performance metrics | 
**disk_usage_mb** | **float** | Database disk usage in MB | 
**last_backup** | **datetime** |  | [optional] 

## Example

```python
from chatter_sdk.models.database_health_response import DatabaseHealthResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DatabaseHealthResponse from a JSON string
database_health_response_instance = DatabaseHealthResponse.from_json(json)
# print the JSON string representation of the object
print(DatabaseHealthResponse.to_json())

# convert the object into a dict
database_health_response_dict = database_health_response_instance.to_dict()
# create an instance of DatabaseHealthResponse from a dict
database_health_response_from_dict = DatabaseHealthResponse.from_dict(database_health_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


