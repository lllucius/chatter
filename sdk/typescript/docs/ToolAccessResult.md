# ToolAccessResult

Schema for tool access check result.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**allowed** | **boolean** | Whether access is allowed | [default to undefined]
**access_level** | [**ToolAccessLevel**](ToolAccessLevel.md) | Access level | [default to undefined]
**rate_limit_remaining_hour** | **number** |  | [optional] [default to undefined]
**rate_limit_remaining_day** | **number** |  | [optional] [default to undefined]
**restriction_reason** | **string** |  | [optional] [default to undefined]
**expires_at** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { ToolAccessResult } from 'chatter-sdk';

const instance: ToolAccessResult = {
    allowed,
    access_level,
    rate_limit_remaining_hour,
    rate_limit_remaining_day,
    restriction_reason,
    expires_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
