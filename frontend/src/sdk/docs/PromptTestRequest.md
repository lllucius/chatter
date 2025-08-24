# PromptTestRequest

Schema for prompt test request.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**variables** | **{ [key: string]: any; }** | Variables to test with | [default to undefined]
**validate_only** | **boolean** | Only validate, don\&#39;t render | [optional] [default to false]

## Example

```typescript
import { PromptTestRequest } from 'chatter-sdk';

const instance: PromptTestRequest = {
    variables,
    validate_only,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
