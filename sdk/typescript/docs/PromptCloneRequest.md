# PromptCloneRequest

Schema for prompt clone request.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** | New prompt name | [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**modifications** | **{ [key: string]: any; }** |  | [optional] [default to undefined]

## Example

```typescript
import { PromptCloneRequest } from 'chatter-sdk';

const instance: PromptCloneRequest = {
    name,
    description,
    modifications,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
