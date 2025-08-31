# ToolPermissionUpdate

Schema for updating tool permissions.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**access_level** | [**ToolAccessLevel**](ToolAccessLevel.md) |  | [optional] [default to undefined]
**rate_limit_per_hour** | **number** |  | [optional] [default to undefined]
**rate_limit_per_day** | **number** |  | [optional] [default to undefined]
**allowed_hours** | **Array&lt;number&gt;** |  | [optional] [default to undefined]
**allowed_days** | **Array&lt;number&gt;** |  | [optional] [default to undefined]
**expires_at** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { ToolPermissionUpdate } from 'chatter-sdk';

const instance: ToolPermissionUpdate = {
    access_level,
    rate_limit_per_hour,
    rate_limit_per_day,
    allowed_hours,
    allowed_days,
    expires_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
