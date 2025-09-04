# RoleToolAccessResponse

Schema for role-based tool access response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**role** | [**UserRole**](UserRole.md) | User role | [default to undefined]
**tool_pattern** | **string** |  | [optional] [default to undefined]
**server_pattern** | **string** |  | [optional] [default to undefined]
**access_level** | [**ToolAccessLevel**](ToolAccessLevel.md) | Access level | [default to undefined]
**default_rate_limit_per_hour** | **number** |  | [optional] [default to undefined]
**default_rate_limit_per_day** | **number** |  | [optional] [default to undefined]
**allowed_hours** | **Array&lt;number&gt;** |  | [optional] [default to undefined]
**allowed_days** | **Array&lt;number&gt;** |  | [optional] [default to undefined]
**id** | **string** | Access rule ID | [default to undefined]
**created_by** | **string** | Creator user ID | [default to undefined]
**created_at** | **string** | Creation timestamp | [default to undefined]

## Example

```typescript
import { RoleToolAccessResponse } from 'chatter-sdk';

const instance: RoleToolAccessResponse = {
    role,
    tool_pattern,
    server_pattern,
    access_level,
    default_rate_limit_per_hour,
    default_rate_limit_per_day,
    allowed_hours,
    allowed_days,
    id,
    created_by,
    created_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
