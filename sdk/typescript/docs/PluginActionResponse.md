# PluginActionResponse

Response schema for plugin actions.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **boolean** | Whether action was successful | [default to undefined]
**message** | **string** | Action result message | [default to undefined]
**plugin_id** | **string** | Plugin ID | [default to undefined]

## Example

```typescript
import { PluginActionResponse } from 'chatter-sdk';

const instance: PluginActionResponse = {
    success,
    message,
    plugin_id,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
