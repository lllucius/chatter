# UserResponse

Schema for user response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**email** | **string** | User email address | [default to undefined]
**username** | **string** | Username | [default to undefined]
**full_name** | **string** |  | [optional] [default to undefined]
**bio** | **string** |  | [optional] [default to undefined]
**avatar_url** | **string** |  | [optional] [default to undefined]
**phone_number** | **string** |  | [optional] [default to undefined]
**id** | **string** | User ID | [default to undefined]
**is_active** | **boolean** | Is user active | [default to undefined]
**is_verified** | **boolean** | Is user email verified | [default to undefined]
**is_superuser** | **boolean** | Is user a superuser | [default to undefined]
**default_llm_provider** | **string** |  | [optional] [default to undefined]
**default_profile_id** | **string** |  | [optional] [default to undefined]
**daily_message_limit** | **number** |  | [optional] [default to undefined]
**monthly_message_limit** | **number** |  | [optional] [default to undefined]
**max_file_size_mb** | **number** |  | [optional] [default to undefined]
**api_key_name** | **string** |  | [optional] [default to undefined]
**created_at** | **string** | Account creation date | [default to undefined]
**updated_at** | **string** | Last update date | [default to undefined]
**last_login_at** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { UserResponse } from 'chatter-sdk';

const instance: UserResponse = {
    email,
    username,
    full_name,
    bio,
    avatar_url,
    phone_number,
    id,
    is_active,
    is_verified,
    is_superuser,
    default_llm_provider,
    default_profile_id,
    daily_message_limit,
    monthly_message_limit,
    max_file_size_mb,
    api_key_name,
    created_at,
    updated_at,
    last_login_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
