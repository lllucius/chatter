# PluginInstallRequest

Request schema for installing a plugin.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**plugin_path** | **string** | Path to plugin file or directory | [default to undefined]
**enable_on_install** | **boolean** | Enable plugin after installation | [optional] [default to true]

## Example

```typescript
import { PluginInstallRequest } from 'chatter-sdk';

const instance: PluginInstallRequest = {
    plugin_path,
    enable_on_install,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
