# ToolServerResponse

Schema for tool server response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** | Server name | [default to undefined]
**display_name** | **string** | Display name | [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**base_url** | **string** |  | [optional] [default to undefined]
**transport_type** | **string** | Transport type: http, sse, stdio, or websocket | [optional] [default to 'http']
**oauth_config** | [**OAuthConfigSchema**](OAuthConfigSchema.md) |  | [optional] [default to undefined]
**headers** | **{ [key: string]: string; }** |  | [optional] [default to undefined]
**timeout** | **number** | Request timeout in seconds | [optional] [default to 30]
**auto_start** | **boolean** | Auto-connect to server on system startup | [optional] [default to true]
**auto_update** | **boolean** | Auto-update server capabilities | [optional] [default to true]
**max_failures** | **number** | Maximum consecutive failures before disabling | [optional] [default to 3]
**id** | **string** | Server ID | [default to undefined]
**status** | [**ServerStatus**](ServerStatus.md) | Server status | [default to undefined]
**is_builtin** | **boolean** | Whether server is built-in | [default to undefined]
**last_health_check** | **string** |  | [optional] [default to undefined]
**last_startup_success** | **string** |  | [optional] [default to undefined]
**last_startup_error** | **string** |  | [optional] [default to undefined]
**consecutive_failures** | **number** | Consecutive failure count | [default to undefined]
**created_at** | **string** | Creation timestamp | [default to undefined]
**updated_at** | **string** | Last update timestamp | [default to undefined]
**created_by** | **string** |  | [optional] [default to undefined]
**tools** | [**Array&lt;ServerToolResponse&gt;**](ServerToolResponse.md) | Server tools | [optional] [default to undefined]

## Example

```typescript
import { ToolServerResponse } from 'chatter-sdk';

const instance: ToolServerResponse = {
    name,
    display_name,
    description,
    base_url,
    transport_type,
    oauth_config,
    headers,
    timeout,
    auto_start,
    auto_update,
    max_failures,
    id,
    status,
    is_builtin,
    last_health_check,
    last_startup_success,
    last_startup_error,
    consecutive_failures,
    created_at,
    updated_at,
    created_by,
    tools,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
