# PluginUpdateRequest

Request schema for updating a plugin.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**enabled** | **boolean** |  | [optional] [default to undefined]
**configuration** | **{ [key: string]: any; }** |  | [optional] [default to undefined]

## Example

```typescript
import { PluginUpdateRequest } from 'chatter-sdk';

const instance: PluginUpdateRequest = {
    enabled,
    configuration,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
