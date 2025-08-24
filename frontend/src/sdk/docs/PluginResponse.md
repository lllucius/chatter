# PluginResponse

Response schema for plugin data.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** | Plugin ID | [default to undefined]
**name** | **string** | Plugin name | [default to undefined]
**version** | **string** | Plugin version | [default to undefined]
**description** | **string** | Plugin description | [default to undefined]
**author** | **string** | Plugin author | [default to undefined]
**plugin_type** | [**PluginType**](PluginType.md) | Plugin type | [default to undefined]
**status** | [**PluginStatus**](PluginStatus.md) | Plugin status | [default to undefined]
**entry_point** | **string** | Plugin entry point | [default to undefined]
**capabilities** | **Array&lt;{ [key: string]: any; } | null&gt;** | Plugin capabilities | [default to undefined]
**dependencies** | **Array&lt;string&gt;** | Plugin dependencies | [default to undefined]
**permissions** | **Array&lt;string&gt;** | Required permissions | [default to undefined]
**enabled** | **boolean** | Whether plugin is enabled | [default to undefined]
**error_message** | **string** |  | [optional] [default to undefined]
**installed_at** | **string** | Installation timestamp | [default to undefined]
**updated_at** | **string** | Last update timestamp | [default to undefined]
**metadata** | **{ [key: string]: any; }** | Additional metadata | [default to undefined]

## Example

```typescript
import { PluginResponse } from 'chatter-sdk';

const instance: PluginResponse = {
    id,
    name,
    version,
    description,
    author,
    plugin_type,
    status,
    entry_point,
    capabilities,
    dependencies,
    permissions,
    enabled,
    error_message,
    installed_at,
    updated_at,
    metadata,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
