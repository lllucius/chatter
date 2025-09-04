# ServerToolResponse

Schema for server tool response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** | Tool name | [default to undefined]
**display_name** | **string** | Display name | [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**args_schema** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**bypass_when_unavailable** | **boolean** | Bypass when tool is unavailable | [optional] [default to false]
**id** | **string** | Tool ID | [default to undefined]
**server_id** | **string** | Server ID | [default to undefined]
**status** | [**ToolStatus**](ToolStatus.md) | Tool status | [default to undefined]
**is_available** | **boolean** | Tool availability | [default to undefined]
**total_calls** | **number** | Total number of calls | [default to undefined]
**total_errors** | **number** | Total number of errors | [default to undefined]
**last_called** | **string** |  | [optional] [default to undefined]
**last_error** | **string** |  | [optional] [default to undefined]
**avg_response_time_ms** | **number** |  | [optional] [default to undefined]
**created_at** | **string** | Creation timestamp | [default to undefined]
**updated_at** | **string** | Last update timestamp | [default to undefined]

## Example

```typescript
import { ServerToolResponse } from 'chatter-sdk';

const instance: ServerToolResponse = {
    name,
    display_name,
    description,
    args_schema,
    bypass_when_unavailable,
    id,
    server_id,
    status,
    is_available,
    total_calls,
    total_errors,
    last_called,
    last_error,
    avg_response_time_ms,
    created_at,
    updated_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
