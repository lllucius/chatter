# PromptUpdate

Schema for updating a prompt.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** |  | [optional] [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**prompt_type** | [**PromptType**](PromptType.md) |  | [optional] [default to undefined]
**category** | [**PromptCategory**](PromptCategory.md) |  | [optional] [default to undefined]
**content** | **string** |  | [optional] [default to undefined]
**variables** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**template_format** | **string** |  | [optional] [default to undefined]
**input_schema** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**output_schema** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**max_length** | **number** |  | [optional] [default to undefined]
**min_length** | **number** |  | [optional] [default to undefined]
**required_variables** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**examples** | **Array&lt;{ [key: string]: any; }&gt;** |  | [optional] [default to undefined]
**test_cases** | **Array&lt;{ [key: string]: any; }&gt;** |  | [optional] [default to undefined]
**suggested_temperature** | **number** |  | [optional] [default to undefined]
**suggested_max_tokens** | **number** |  | [optional] [default to undefined]
**suggested_providers** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**is_chain** | **boolean** |  | [optional] [default to undefined]
**chain_steps** | **Array&lt;{ [key: string]: any; }&gt;** |  | [optional] [default to undefined]
**parent_prompt_id** | **string** |  | [optional] [default to undefined]
**is_public** | **boolean** |  | [optional] [default to undefined]
**tags** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**extra_metadata** | **{ [key: string]: any; }** |  | [optional] [default to undefined]

## Example

```typescript
import { PromptUpdate } from 'chatter-sdk';

const instance: PromptUpdate = {
    name,
    description,
    prompt_type,
    category,
    content,
    variables,
    template_format,
    input_schema,
    output_schema,
    max_length,
    min_length,
    required_variables,
    examples,
    test_cases,
    suggested_temperature,
    suggested_max_tokens,
    suggested_providers,
    is_chain,
    chain_steps,
    parent_prompt_id,
    is_public,
    tags,
    extra_metadata,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
