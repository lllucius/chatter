# ToolPermissionResponse

Schema for tool permission response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **string** | User ID | [default to undefined]
**tool_id** | **string** |  | [optional] [default to undefined]
**server_id** | **string** |  | [optional] [default to undefined]
**access_level** | [**ToolAccessLevel**](ToolAccessLevel.md) | Access level | [default to undefined]
**rate_limit_per_hour** | **number** |  | [optional] [default to undefined]
**rate_limit_per_day** | **number** |  | [optional] [default to undefined]
**allowed_hours** | **Array&lt;number&gt;** |  | [optional] [default to undefined]
**allowed_days** | **Array&lt;number&gt;** |  | [optional] [default to undefined]
**expires_at** | **string** |  | [optional] [default to undefined]
**id** | **string** | Permission ID | [default to undefined]
**granted_by** | **string** | Granter user ID | [default to undefined]
**granted_at** | **string** | Grant timestamp | [default to undefined]
**usage_count** | **number** | Usage count | [default to undefined]
**last_used** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { ToolPermissionResponse } from 'chatter-sdk';

const instance: ToolPermissionResponse = {
    user_id,
    tool_id,
    server_id,
    access_level,
    rate_limit_per_hour,
    rate_limit_per_day,
    allowed_hours,
    allowed_days,
    expires_at,
    id,
    granted_by,
    granted_at,
    usage_count,
    last_used,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
