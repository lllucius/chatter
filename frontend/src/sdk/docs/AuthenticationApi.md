# AuthenticationApi

All URIs are relative to *http://localhost:8000*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**changePasswordApiV1AuthChangePasswordPost**](#changepasswordapiv1authchangepasswordpost) | **POST** /api/v1/auth/change-password | Change Password|
|[**confirmPasswordResetApiV1AuthPasswordResetConfirmPost**](#confirmpasswordresetapiv1authpasswordresetconfirmpost) | **POST** /api/v1/auth/password-reset/confirm | Confirm Password Reset|
|[**createApiKeyApiV1AuthApiKeyPost**](#createapikeyapiv1authapikeypost) | **POST** /api/v1/auth/api-key | Create Api Key|
|[**deactivateAccountApiV1AuthAccountDelete**](#deactivateaccountapiv1authaccountdelete) | **DELETE** /api/v1/auth/account | Deactivate Account|
|[**getCurrentUserInfoApiV1AuthMeGet**](#getcurrentuserinfoapiv1authmeget) | **GET** /api/v1/auth/me | Get Current User Info|
|[**listApiKeysApiV1AuthApiKeysGet**](#listapikeysapiv1authapikeysget) | **GET** /api/v1/auth/api-keys | List Api Keys|
|[**loginApiV1AuthLoginPost**](#loginapiv1authloginpost) | **POST** /api/v1/auth/login | Login|
|[**logoutApiV1AuthLogoutPost**](#logoutapiv1authlogoutpost) | **POST** /api/v1/auth/logout | Logout|
|[**refreshTokenApiV1AuthRefreshPost**](#refreshtokenapiv1authrefreshpost) | **POST** /api/v1/auth/refresh | Refresh Token|
|[**registerApiV1AuthRegisterPost**](#registerapiv1authregisterpost) | **POST** /api/v1/auth/register | Register|
|[**requestPasswordResetApiV1AuthPasswordResetRequestPost**](#requestpasswordresetapiv1authpasswordresetrequestpost) | **POST** /api/v1/auth/password-reset/request | Request Password Reset|
|[**revokeApiKeyApiV1AuthApiKeyDelete**](#revokeapikeyapiv1authapikeydelete) | **DELETE** /api/v1/auth/api-key | Revoke Api Key|
|[**updateProfileApiV1AuthMePut**](#updateprofileapiv1authmeput) | **PUT** /api/v1/auth/me | Update Profile|

# **changePasswordApiV1AuthChangePasswordPost**
> PasswordChangeResponse changePasswordApiV1AuthChangePasswordPost(passwordChange)

Change user password.  Args:     password_data: Password change data     current_user: Current authenticated user     auth_service: Authentication service  Returns:     Success message

### Example

```typescript
import {
    AuthenticationApi,
    Configuration,
    PasswordChange
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AuthenticationApi(configuration);

let passwordChange: PasswordChange; //

const { status, data } = await apiInstance.changePasswordApiV1AuthChangePasswordPost(
    passwordChange
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **passwordChange** | **PasswordChange**|  | |


### Return type

**PasswordChangeResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **confirmPasswordResetApiV1AuthPasswordResetConfirmPost**
> { [key: string]: any; } confirmPasswordResetApiV1AuthPasswordResetConfirmPost()

Confirm password reset.  Args:     token: Reset token     new_password: New password     auth_service: Authentication service  Returns:     Success message

### Example

```typescript
import {
    AuthenticationApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AuthenticationApi(configuration);

let token: string; // (default to undefined)
let newPassword: string; // (default to undefined)

const { status, data } = await apiInstance.confirmPasswordResetApiV1AuthPasswordResetConfirmPost(
    token,
    newPassword
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **token** | [**string**] |  | defaults to undefined|
| **newPassword** | [**string**] |  | defaults to undefined|


### Return type

**{ [key: string]: any; }**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createApiKeyApiV1AuthApiKeyPost**
> APIKeyResponse createApiKeyApiV1AuthApiKeyPost(aPIKeyCreate)

Create API key for current user.  Args:     key_data: API key creation data     current_user: Current authenticated user     auth_service: Authentication service  Returns:     Created API key

### Example

```typescript
import {
    AuthenticationApi,
    Configuration,
    APIKeyCreate
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AuthenticationApi(configuration);

let aPIKeyCreate: APIKeyCreate; //

const { status, data } = await apiInstance.createApiKeyApiV1AuthApiKeyPost(
    aPIKeyCreate
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **aPIKeyCreate** | **APIKeyCreate**|  | |


### Return type

**APIKeyResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deactivateAccountApiV1AuthAccountDelete**
> AccountDeactivateResponse deactivateAccountApiV1AuthAccountDelete()

Deactivate current user account.  Args:     current_user: Current authenticated user     auth_service: Authentication service  Returns:     Success message

### Example

```typescript
import {
    AuthenticationApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AuthenticationApi(configuration);

const { status, data } = await apiInstance.deactivateAccountApiV1AuthAccountDelete();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**AccountDeactivateResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getCurrentUserInfoApiV1AuthMeGet**
> UserResponse getCurrentUserInfoApiV1AuthMeGet()

Get current user information.  Args:     current_user: Current authenticated user  Returns:     Current user data

### Example

```typescript
import {
    AuthenticationApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AuthenticationApi(configuration);

const { status, data } = await apiInstance.getCurrentUserInfoApiV1AuthMeGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**UserResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listApiKeysApiV1AuthApiKeysGet**
> Array<APIKeyResponse> listApiKeysApiV1AuthApiKeysGet()

List user\'s API keys.  Args:     current_user: Current authenticated user     auth_service: Authentication service  Returns:     List of API keys

### Example

```typescript
import {
    AuthenticationApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AuthenticationApi(configuration);

const { status, data } = await apiInstance.listApiKeysApiV1AuthApiKeysGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**Array<APIKeyResponse>**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **loginApiV1AuthLoginPost**
> TokenResponse loginApiV1AuthLoginPost(userLogin)

Authenticate user and return tokens.  Args:     user_data: User login data     auth_service: Authentication service  Returns:     User data and authentication tokens

### Example

```typescript
import {
    AuthenticationApi,
    Configuration,
    UserLogin
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AuthenticationApi(configuration);

let userLogin: UserLogin; //

const { status, data } = await apiInstance.loginApiV1AuthLoginPost(
    userLogin
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **userLogin** | **UserLogin**|  | |


### Return type

**TokenResponse**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **logoutApiV1AuthLogoutPost**
> { [key: string]: any; } logoutApiV1AuthLogoutPost()

Logout and revoke current token.  Args:     current_user: Current authenticated user     auth_service: Authentication service  Returns:     Success message

### Example

```typescript
import {
    AuthenticationApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AuthenticationApi(configuration);

const { status, data } = await apiInstance.logoutApiV1AuthLogoutPost();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**{ [key: string]: any; }**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **refreshTokenApiV1AuthRefreshPost**
> TokenRefreshResponse refreshTokenApiV1AuthRefreshPost(tokenRefresh)

Refresh access token.  Args:     token_data: Refresh token data     auth_service: Authentication service  Returns:     New access and refresh tokens

### Example

```typescript
import {
    AuthenticationApi,
    Configuration,
    TokenRefresh
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AuthenticationApi(configuration);

let tokenRefresh: TokenRefresh; //

const { status, data } = await apiInstance.refreshTokenApiV1AuthRefreshPost(
    tokenRefresh
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **tokenRefresh** | **TokenRefresh**|  | |


### Return type

**TokenRefreshResponse**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **registerApiV1AuthRegisterPost**
> TokenResponse registerApiV1AuthRegisterPost(userCreate)

Register a new user.  Args:     user_data: User registration data     auth_service: Authentication service  Returns:     User data and authentication tokens

### Example

```typescript
import {
    AuthenticationApi,
    Configuration,
    UserCreate
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AuthenticationApi(configuration);

let userCreate: UserCreate; //

const { status, data } = await apiInstance.registerApiV1AuthRegisterPost(
    userCreate
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **userCreate** | **UserCreate**|  | |


### Return type

**TokenResponse**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **requestPasswordResetApiV1AuthPasswordResetRequestPost**
> { [key: string]: any; } requestPasswordResetApiV1AuthPasswordResetRequestPost()

Request password reset.  Args:     email: User email     auth_service: Authentication service  Returns:     Success message

### Example

```typescript
import {
    AuthenticationApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AuthenticationApi(configuration);

let email: string; // (default to undefined)

const { status, data } = await apiInstance.requestPasswordResetApiV1AuthPasswordResetRequestPost(
    email
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **email** | [**string**] |  | defaults to undefined|


### Return type

**{ [key: string]: any; }**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **revokeApiKeyApiV1AuthApiKeyDelete**
> APIKeyRevokeResponse revokeApiKeyApiV1AuthApiKeyDelete()

Revoke current user\'s API key.  Args:     current_user: Current authenticated user     auth_service: Authentication service  Returns:     Success message

### Example

```typescript
import {
    AuthenticationApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AuthenticationApi(configuration);

const { status, data } = await apiInstance.revokeApiKeyApiV1AuthApiKeyDelete();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**APIKeyRevokeResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateProfileApiV1AuthMePut**
> UserResponse updateProfileApiV1AuthMePut(userUpdate)

Update current user profile.  Args:     user_data: Profile update data     current_user: Current authenticated user     auth_service: Authentication service  Returns:     Updated user data

### Example

```typescript
import {
    AuthenticationApi,
    Configuration,
    UserUpdate
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AuthenticationApi(configuration);

let userUpdate: UserUpdate; //

const { status, data } = await apiInstance.updateProfileApiV1AuthMePut(
    userUpdate
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **userUpdate** | **UserUpdate**|  | |


### Return type

**UserResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

