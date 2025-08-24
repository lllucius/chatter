# McpStatusResponse

Schema for MCP status response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **string** | MCP service status | [default to undefined]
**servers** | **Array&lt;{ [key: string]: any; } | null&gt;** | Connected servers | [default to undefined]
**last_check** | **string** |  | [optional] [default to undefined]
**errors** | **Array&lt;string&gt;** | Any error messages | [optional] [default to undefined]

## Example

```typescript
import { McpStatusResponse } from 'chatter-sdk';

const instance: McpStatusResponse = {
    status,
    servers,
    last_check,
    errors,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
