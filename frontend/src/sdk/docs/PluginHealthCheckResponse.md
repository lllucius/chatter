# PluginHealthCheckResponse

Response schema for plugin health check.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**summary** | **{ [key: string]: any; }** | Health check summary | [default to undefined]
**results** | **{ [key: string]: { [key: string]: any; } | null; }** | Detailed health check results for each plugin | [default to undefined]

## Example

```typescript
import { PluginHealthCheckResponse } from 'chatter-sdk';

const instance: PluginHealthCheckResponse = {
    summary,
    results,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
