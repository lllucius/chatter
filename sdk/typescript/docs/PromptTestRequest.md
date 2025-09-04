# PromptTestRequest

Schema for prompt test request.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**variables** | **{ [key: string]: any; }** | Variables to test with | [default to undefined]
**validate_only** | **boolean** | Only validate, don\&#39;t render | [optional] [default to false]
**include_performance_metrics** | **boolean** | Include detailed performance metrics | [optional] [default to false]
**timeout_ms** | **number** | Test timeout in milliseconds | [optional] [default to 30000]

## Example

```typescript
import { PromptTestRequest } from 'chatter-sdk';

const instance: PromptTestRequest = {
    variables,
    validate_only,
    include_performance_metrics,
    timeout_ms,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
