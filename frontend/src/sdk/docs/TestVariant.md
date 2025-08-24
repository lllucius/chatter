# TestVariant

Test variant definition.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** | Variant name | [default to undefined]
**description** | **string** | Variant description | [default to undefined]
**configuration** | **{ [key: string]: any; }** | Variant configuration | [default to undefined]
**weight** | **number** | Variant weight for allocation | [optional] [default to 1.0]

## Example

```typescript
import { TestVariant } from 'chatter-sdk';

const instance: TestVariant = {
    name,
    description,
    configuration,
    weight,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
