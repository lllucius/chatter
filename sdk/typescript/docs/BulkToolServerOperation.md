# BulkToolServerOperation

Schema for bulk operations on tool servers.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**server_ids** | **Array&lt;string&gt;** | List of server IDs | [default to undefined]
**operation** | **string** | Operation to perform | [default to undefined]
**parameters** | **{ [key: string]: any; }** |  | [optional] [default to undefined]

## Example

```typescript
import { BulkToolServerOperation } from 'chatter-sdk';

const instance: BulkToolServerOperation = {
    server_ids,
    operation,
    parameters,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
