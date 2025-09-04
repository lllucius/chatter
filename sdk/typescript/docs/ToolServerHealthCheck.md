# ToolServerHealthCheck

Schema for tool server health check.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**server_id** | **string** | Server ID | [default to undefined]
**server_name** | **string** | Server name | [default to undefined]
**status** | [**ServerStatus**](ServerStatus.md) | Server status | [default to undefined]
**is_running** | **boolean** | Whether server is running | [default to undefined]
**is_responsive** | **boolean** | Whether server is responsive | [default to undefined]
**tools_count** | **number** | Number of available tools | [default to undefined]
**last_check** | **string** | Last health check time | [default to undefined]
**error_message** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { ToolServerHealthCheck } from 'chatter-sdk';

const instance: ToolServerHealthCheck = {
    server_id,
    server_name,
    status,
    is_running,
    is_responsive,
    tools_count,
    last_check,
    error_message,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
