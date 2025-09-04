# ToolServerCreate

Schema for creating a tool server.

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

## Example

```typescript
import { ToolServerCreate } from 'chatter-sdk';

const instance: ToolServerCreate = {
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
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
