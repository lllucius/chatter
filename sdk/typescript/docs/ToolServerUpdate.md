# ToolServerUpdate

Schema for updating a remote tool server.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**display_name** | **string** |  | [optional] [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**base_url** | **string** |  | [optional] [default to undefined]
**transport_type** | **string** |  | [optional] [default to undefined]
**oauth_config** | [**OAuthConfigSchema**](OAuthConfigSchema.md) |  | [optional] [default to undefined]
**headers** | **{ [key: string]: string; }** |  | [optional] [default to undefined]
**timeout** | **number** |  | [optional] [default to undefined]
**auto_start** | **boolean** |  | [optional] [default to undefined]
**auto_update** | **boolean** |  | [optional] [default to undefined]
**max_failures** | **number** |  | [optional] [default to undefined]

## Example

```typescript
import { ToolServerUpdate } from 'chatter-sdk';

const instance: ToolServerUpdate = {
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
