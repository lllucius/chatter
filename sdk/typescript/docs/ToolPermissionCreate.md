# ToolPermissionCreate

Schema for creating tool permissions.

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

## Example

```typescript
import { ToolPermissionCreate } from 'chatter-sdk';

const instance: ToolPermissionCreate = {
    user_id,
    tool_id,
    server_id,
    access_level,
    rate_limit_per_hour,
    rate_limit_per_day,
    allowed_hours,
    allowed_days,
    expires_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
