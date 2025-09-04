# WorkflowTemplatesResponse

Schema for workflow templates response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**templates** | [**{ [key: string]: WorkflowTemplateInfo; }**](WorkflowTemplateInfo.md) | Available templates | [default to undefined]
**total_count** | **number** | Total number of templates | [default to undefined]

## Example

```typescript
import { WorkflowTemplatesResponse } from 'chatter-sdk';

const instance: WorkflowTemplatesResponse = {
    templates,
    total_count,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
