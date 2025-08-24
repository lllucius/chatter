# PromptTestResponse

Schema for prompt test response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**rendered_content** | **string** |  | [optional] [default to undefined]
**validation_result** | **{ [key: string]: any; }** | Validation results | [default to undefined]
**estimated_tokens** | **number** |  | [optional] [default to undefined]
**test_duration_ms** | **number** | Test execution time | [default to undefined]

## Example

```typescript
import { PromptTestResponse } from 'chatter-sdk';

const instance: PromptTestResponse = {
    rendered_content,
    validation_result,
    estimated_tokens,
    test_duration_ms,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
