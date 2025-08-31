# WorkflowTemplateInfo

Schema for workflow template information.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** | Template name | [default to undefined]
**workflow_type** | **string** | Workflow type | [default to undefined]
**description** | **string** | Template description | [default to undefined]
**required_tools** | **Array&lt;string&gt;** | Required tools | [default to undefined]
**required_retrievers** | **Array&lt;string&gt;** | Required retrievers | [default to undefined]
**default_params** | **{ [key: string]: any; }** | Default parameters | [default to undefined]

## Example

```typescript
import { WorkflowTemplateInfo } from 'chatter-sdk';

const instance: WorkflowTemplateInfo = {
    name,
    workflow_type,
    description,
    required_tools,
    required_retrievers,
    default_params,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
