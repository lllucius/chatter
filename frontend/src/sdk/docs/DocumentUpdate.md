# DocumentUpdate

Schema for updating a document.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**title** | **string** |  | [optional] [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**tags** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**extra_metadata** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**is_public** | **boolean** |  | [optional] [default to undefined]

## Example

```typescript
import { DocumentUpdate } from 'chatter-sdk';

const instance: DocumentUpdate = {
    title,
    description,
    tags,
    extra_metadata,
    is_public,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
