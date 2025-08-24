# ToolServerUpdate

Schema for updating a tool server.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**display_name** | **string** |  | [optional] [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**command** | **string** |  | [optional] [default to undefined]
**args** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**env** | **{ [key: string]: string; }** |  | [optional] [default to undefined]
**auto_start** | **boolean** |  | [optional] [default to undefined]
**auto_update** | **boolean** |  | [optional] [default to undefined]
**max_failures** | **number** |  | [optional] [default to undefined]

## Example

```typescript
import { ToolServerUpdate } from 'chatter-sdk';

const instance: ToolServerUpdate = {
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
