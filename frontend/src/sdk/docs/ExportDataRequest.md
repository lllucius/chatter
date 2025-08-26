# ExportDataRequest

Request schema for data export API.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**scope** | [**ExportScope**](ExportScope.md) | Export scope | [default to undefined]
**format** | [**DataFormat**](DataFormat.md) | Export format | [optional] [default to undefined]
**user_id** | **string** |  | [optional] [default to undefined]
**conversation_id** | **string** |  | [optional] [default to undefined]
**date_from** | **string** |  | [optional] [default to undefined]
**date_to** | **string** |  | [optional] [default to undefined]
**include_metadata** | **boolean** | Include metadata | [optional] [default to true]
**compress** | **boolean** | Compress export file | [optional] [default to true]
**encrypt** | **boolean** | Encrypt export file | [optional] [default to false]
**custom_query** | **{ [key: string]: any; }** |  | [optional] [default to undefined]

## Example

```typescript
import { ExportDataRequest } from 'chatter-sdk';

const instance: ExportDataRequest = {
    scope,
    format,
    user_id,
    conversation_id,
    date_from,
    date_to,
    include_metadata,
    compress,
    encrypt,
    custom_query,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
