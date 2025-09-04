# AvailableProvidersResponse

Schema for available providers response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**providers** | **{ [key: string]: any; }** | Available LLM providers with their configurations | [default to undefined]
**total_providers** | **number** | Total number of available providers | [default to undefined]
**supported_features** | **{ [key: string]: Array&lt;string&gt;; }** | Features supported by each provider | [default to undefined]

## Example

```typescript
import { AvailableProvidersResponse } from 'chatter-sdk';

const instance: AvailableProvidersResponse = {
    providers,
    total_providers,
    supported_features,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
