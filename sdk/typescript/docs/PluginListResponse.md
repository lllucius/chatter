# PluginListResponse

Response schema for plugin list.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**plugins** | [**Array&lt;PluginResponse&gt;**](PluginResponse.md) | List of plugins | [default to undefined]
**total** | **number** | Total number of plugins | [default to undefined]

## Example

```typescript
import { PluginListResponse } from 'chatter-sdk';

const instance: PluginListResponse = {
    plugins,
    total,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
