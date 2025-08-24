# ExportDataResponse

Response schema for data export.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**export_id** | **string** | Export ID | [default to undefined]
**status** | **string** | Export status | [default to undefined]
**download_url** | **string** |  | [optional] [default to undefined]
**file_size** | **number** |  | [optional] [default to undefined]
**record_count** | **number** |  | [optional] [default to undefined]
**created_at** | **string** | Export creation timestamp | [default to undefined]
**completed_at** | **string** |  | [optional] [default to undefined]
**expires_at** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { ExportDataResponse } from 'chatter-sdk';

const instance: ExportDataResponse = {
    export_id,
    status,
    download_url,
    file_size,
    record_count,
    created_at,
    completed_at,
    expires_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
