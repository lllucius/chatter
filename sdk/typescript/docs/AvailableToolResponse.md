# AvailableToolResponse

Schema for individual available tool.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** | Tool name | [default to undefined]
**description** | **string** | Tool description | [default to undefined]
**type** | **string** | Tool type (mcp, builtin) | [default to undefined]
**args_schema** | **{ [key: string]: any; }** | Tool arguments schema | [default to undefined]

## Example

```typescript
import { AvailableToolResponse } from 'chatter-sdk';

const instance: AvailableToolResponse = {
    name,
    description,
    type,
    args_schema,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
