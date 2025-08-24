# ToolServerCreate

Schema for creating a tool server.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** | Server name | [default to undefined]
**display_name** | **string** | Display name | [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**command** | **string** | Command to start server | [default to undefined]
**args** | **Array&lt;string&gt;** | Command arguments | [optional] [default to undefined]
**env** | **{ [key: string]: string; }** |  | [optional] [default to undefined]
**auto_start** | **boolean** | Auto-start server on system startup | [optional] [default to true]
**auto_update** | **boolean** | Auto-update server capabilities | [optional] [default to true]
**max_failures** | **number** | Maximum consecutive failures before disabling | [optional] [default to 3]

## Example

```typescript
import { ToolServerCreate } from 'chatter-sdk';

const instance: ToolServerCreate = {
    name,
    display_name,
    description,
    command,
    args,
    env,
    auto_start,
    auto_update,
    max_failures,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
