# PluginStatsResponse

Response schema for plugin statistics.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_plugins** | **number** | Total number of plugins | [default to undefined]
**active_plugins** | **number** | Number of active plugins | [default to undefined]
**inactive_plugins** | **number** | Number of inactive plugins | [default to undefined]
**plugin_types** | **{ [key: string]: number; }** | Plugin count by type | [default to undefined]
**plugins_directory** | **string** | Plugin installation directory | [default to undefined]

## Example

```typescript
import { PluginStatsResponse } from 'chatter-sdk';

const instance: PluginStatsResponse = {
    total_plugins,
    active_plugins,
    inactive_plugins,
    plugin_types,
    plugins_directory,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
