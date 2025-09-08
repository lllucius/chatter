# chatter_sdk.AuthenticationApi

All URIs are relative to *http://localhost:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**change_password_api_v1_auth_change_password_post**](AuthenticationApi.md#change_password_api_v1_auth_change_password_post) | **POST** /api/v1/auth/change-password | Change Password
[**confirm_password_reset_api_v1_auth_password_reset_confirm_post**](AuthenticationApi.md#confirm_password_reset_api_v1_auth_password_reset_confirm_post) | **POST** /api/v1/auth/password-reset/confirm | Confirm Password Reset
[**create_api_key_api_v1_auth_api_key_post**](AuthenticationApi.md#create_api_key_api_v1_auth_api_key_post) | **POST** /api/v1/auth/api-key | Create Api Key
[**deactivate_account_api_v1_auth_account_delete**](AuthenticationApi.md#deactivate_account_api_v1_auth_account_delete) | **DELETE** /api/v1/auth/account | Deactivate Account
[**get_current_user_info_api_v1_auth_me_get**](AuthenticationApi.md#get_current_user_info_api_v1_auth_me_get) | **GET** /api/v1/auth/me | Get Current User Info
[**list_api_keys_api_v1_auth_api_keys_get**](AuthenticationApi.md#list_api_keys_api_v1_auth_api_keys_get) | **GET** /api/v1/auth/api-keys | List Api Keys
[**login_api_v1_auth_login_post**](AuthenticationApi.md#login_api_v1_auth_login_post) | **POST** /api/v1/auth/login | Login
[**logout_api_v1_auth_logout_post**](AuthenticationApi.md#logout_api_v1_auth_logout_post) | **POST** /api/v1/auth/logout | Logout
[**refresh_token_api_v1_auth_refresh_post**](AuthenticationApi.md#refresh_token_api_v1_auth_refresh_post) | **POST** /api/v1/auth/refresh | Refresh Token
[**register_api_v1_auth_register_post**](AuthenticationApi.md#register_api_v1_auth_register_post) | **POST** /api/v1/auth/register | Register
[**request_password_reset_api_v1_auth_password_reset_request_post**](AuthenticationApi.md#request_password_reset_api_v1_auth_password_reset_request_post) | **POST** /api/v1/auth/password-reset/request | Request Password Reset
[**revoke_api_key_api_v1_auth_api_key_delete**](AuthenticationApi.md#revoke_api_key_api_v1_auth_api_key_delete) | **DELETE** /api/v1/auth/api-key | Revoke Api Key
[**update_profile_api_v1_auth_me_put**](AuthenticationApi.md#update_profile_api_v1_auth_me_put) | **PUT** /api/v1/auth/me | Update Profile


# **change_password_api_v1_auth_change_password_post**
> PasswordChangeResponse change_password_api_v1_auth_change_password_post(password_change)

Change Password

Change user password with enhanced security logging.

Args:
    password_data: Password change data
    request: HTTP request for security logging
    current_user: Current authenticated user
    auth_service: Authentication service

Returns:
    Success message

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.password_change import PasswordChange
from chatter_sdk.models.password_change_response import PasswordChangeResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.AuthenticationApi(api_client)
    password_change = chatter_sdk.PasswordChange() # PasswordChange | 

    try:
        # Change Password
        api_response = await api_instance.change_password_api_v1_auth_change_password_post(password_change)
        print("The response of AuthenticationApi->change_password_api_v1_auth_change_password_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthenticationApi->change_password_api_v1_auth_change_password_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **password_change** | [**PasswordChange**](PasswordChange.md)|  | 

### Return type

[**PasswordChangeResponse**](PasswordChangeResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **confirm_password_reset_api_v1_auth_password_reset_confirm_post**
> PasswordResetConfirmResponse confirm_password_reset_api_v1_auth_password_reset_confirm_post(token, new_password)

Confirm Password Reset

Confirm password reset with enhanced security logging.

Args:
    token: Reset token
    new_password: New password
    request: HTTP request for security logging
    auth_service: Authentication service

Returns:
    Success message

### Example


```python
import chatter_sdk
from chatter_sdk.models.password_reset_confirm_response import PasswordResetConfirmResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
)


# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.AuthenticationApi(api_client)
    token = 'token_example' # str | 
    new_password = 'new_password_example' # str | 

    try:
        # Confirm Password Reset
        api_response = await api_instance.confirm_password_reset_api_v1_auth_password_reset_confirm_post(token, new_password)
        print("The response of AuthenticationApi->confirm_password_reset_api_v1_auth_password_reset_confirm_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthenticationApi->confirm_password_reset_api_v1_auth_password_reset_confirm_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token** | **str**|  | 
 **new_password** | **str**|  | 

### Return type

[**PasswordResetConfirmResponse**](PasswordResetConfirmResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_api_key_api_v1_auth_api_key_post**
> APIKeyResponse create_api_key_api_v1_auth_api_key_post(api_key_create)

Create Api Key

Create API key for current user with enhanced security.

Args:
    key_data: API key creation data
    request: HTTP request for security logging
    current_user: Current authenticated user
    auth_service: Authentication service

Returns:
    Created API key

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.api_key_create import APIKeyCreate
from chatter_sdk.models.api_key_response import APIKeyResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.AuthenticationApi(api_client)
    api_key_create = chatter_sdk.APIKeyCreate() # APIKeyCreate | 

    try:
        # Create Api Key
        api_response = await api_instance.create_api_key_api_v1_auth_api_key_post(api_key_create)
        print("The response of AuthenticationApi->create_api_key_api_v1_auth_api_key_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthenticationApi->create_api_key_api_v1_auth_api_key_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **api_key_create** | [**APIKeyCreate**](APIKeyCreate.md)|  | 

### Return type

[**APIKeyResponse**](APIKeyResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deactivate_account_api_v1_auth_account_delete**
> AccountDeactivateResponse deactivate_account_api_v1_auth_account_delete()

Deactivate Account

Deactivate current user account with enhanced security logging.

Args:
    request: HTTP request for security logging
    current_user: Current authenticated user
    auth_service: Authentication service

Returns:
    Success message

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.account_deactivate_response import AccountDeactivateResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.AuthenticationApi(api_client)

    try:
        # Deactivate Account
        api_response = await api_instance.deactivate_account_api_v1_auth_account_delete()
        print("The response of AuthenticationApi->deactivate_account_api_v1_auth_account_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthenticationApi->deactivate_account_api_v1_auth_account_delete: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**AccountDeactivateResponse**](AccountDeactivateResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_current_user_info_api_v1_auth_me_get**
> UserResponse get_current_user_info_api_v1_auth_me_get()

Get Current User Info

Get current user information.

Args:
    current_user: Current authenticated user

Returns:
    Current user data

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.user_response import UserResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.AuthenticationApi(api_client)

    try:
        # Get Current User Info
        api_response = await api_instance.get_current_user_info_api_v1_auth_me_get()
        print("The response of AuthenticationApi->get_current_user_info_api_v1_auth_me_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthenticationApi->get_current_user_info_api_v1_auth_me_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**UserResponse**](UserResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_api_keys_api_v1_auth_api_keys_get**
> List[APIKeyResponse] list_api_keys_api_v1_auth_api_keys_get()

List Api Keys

List user's API keys.

Args:
    current_user: Current authenticated user
    auth_service: Authentication service

Returns:
    List of API keys

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.api_key_response import APIKeyResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.AuthenticationApi(api_client)

    try:
        # List Api Keys
        api_response = await api_instance.list_api_keys_api_v1_auth_api_keys_get()
        print("The response of AuthenticationApi->list_api_keys_api_v1_auth_api_keys_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthenticationApi->list_api_keys_api_v1_auth_api_keys_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**List[APIKeyResponse]**](APIKeyResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **login_api_v1_auth_login_post**
> TokenResponse login_api_v1_auth_login_post(user_login)

Login

Authenticate user and return tokens with enhanced security.

Args:
    user_data: User login data
    request: HTTP request for security logging
    auth_service: Authentication service

Returns:
    User data and authentication tokens

### Example


```python
import chatter_sdk
from chatter_sdk.models.token_response import TokenResponse
from chatter_sdk.models.user_login import UserLogin
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
)


# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.AuthenticationApi(api_client)
    user_login = {"username":"user@example.com","password":"secure_password"} # UserLogin | 

    try:
        # Login
        api_response = await api_instance.login_api_v1_auth_login_post(user_login)
        print("The response of AuthenticationApi->login_api_v1_auth_login_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthenticationApi->login_api_v1_auth_login_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_login** | [**UserLogin**](UserLogin.md)|  | 

### Return type

[**TokenResponse**](TokenResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **logout_api_v1_auth_logout_post**
> LogoutResponse logout_api_v1_auth_logout_post()

Logout

Logout and revoke current token with enhanced security.

Args:
    request: HTTP request for security logging
    current_user: Current authenticated user
    auth_service: Authentication service

Returns:
    Success message

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.logout_response import LogoutResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.AuthenticationApi(api_client)

    try:
        # Logout
        api_response = await api_instance.logout_api_v1_auth_logout_post()
        print("The response of AuthenticationApi->logout_api_v1_auth_logout_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthenticationApi->logout_api_v1_auth_logout_post: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**LogoutResponse**](LogoutResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **refresh_token_api_v1_auth_refresh_post**
> TokenRefreshResponse refresh_token_api_v1_auth_refresh_post(token_refresh)

Refresh Token

Refresh access token with enhanced security validation.

Args:
    token_data: Refresh token data
    request: HTTP request for security logging
    auth_service: Authentication service

Returns:
    New access and refresh tokens

### Example


```python
import chatter_sdk
from chatter_sdk.models.token_refresh import TokenRefresh
from chatter_sdk.models.token_refresh_response import TokenRefreshResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
)


# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.AuthenticationApi(api_client)
    token_refresh = chatter_sdk.TokenRefresh() # TokenRefresh | 

    try:
        # Refresh Token
        api_response = await api_instance.refresh_token_api_v1_auth_refresh_post(token_refresh)
        print("The response of AuthenticationApi->refresh_token_api_v1_auth_refresh_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthenticationApi->refresh_token_api_v1_auth_refresh_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token_refresh** | [**TokenRefresh**](TokenRefresh.md)|  | 

### Return type

[**TokenRefreshResponse**](TokenRefreshResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **register_api_v1_auth_register_post**
> TokenResponse register_api_v1_auth_register_post(user_create)

Register

Register a new user with enhanced security validation.

Args:
    user_data: User registration data
    request: HTTP request for security logging
    auth_service: Authentication service

Returns:
    User data and authentication tokens

### Example


```python
import chatter_sdk
from chatter_sdk.models.token_response import TokenResponse
from chatter_sdk.models.user_create import UserCreate
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
)


# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.AuthenticationApi(api_client)
    user_create = {"username":"developer123","email":"developer@example.com","password":"SecurePassword123!","full_name":"John Developer"} # UserCreate | 

    try:
        # Register
        api_response = await api_instance.register_api_v1_auth_register_post(user_create)
        print("The response of AuthenticationApi->register_api_v1_auth_register_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthenticationApi->register_api_v1_auth_register_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_create** | [**UserCreate**](UserCreate.md)|  | 

### Return type

[**TokenResponse**](TokenResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **request_password_reset_api_v1_auth_password_reset_request_post**
> PasswordResetRequestResponse request_password_reset_api_v1_auth_password_reset_request_post(email)

Request Password Reset

Request password reset with enhanced security logging.

Args:
    email: User email
    request: HTTP request for security logging
    auth_service: Authentication service

Returns:
    Success message

### Example


```python
import chatter_sdk
from chatter_sdk.models.password_reset_request_response import PasswordResetRequestResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
)


# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.AuthenticationApi(api_client)
    email = 'email_example' # str | 

    try:
        # Request Password Reset
        api_response = await api_instance.request_password_reset_api_v1_auth_password_reset_request_post(email)
        print("The response of AuthenticationApi->request_password_reset_api_v1_auth_password_reset_request_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthenticationApi->request_password_reset_api_v1_auth_password_reset_request_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **email** | **str**|  | 

### Return type

[**PasswordResetRequestResponse**](PasswordResetRequestResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **revoke_api_key_api_v1_auth_api_key_delete**
> APIKeyRevokeResponse revoke_api_key_api_v1_auth_api_key_delete()

Revoke Api Key

Revoke current user's API key with security logging.

Args:
    request: HTTP request for security logging
    current_user: Current authenticated user
    auth_service: Authentication service

Returns:
    Success message

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.api_key_revoke_response import APIKeyRevokeResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.AuthenticationApi(api_client)

    try:
        # Revoke Api Key
        api_response = await api_instance.revoke_api_key_api_v1_auth_api_key_delete()
        print("The response of AuthenticationApi->revoke_api_key_api_v1_auth_api_key_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthenticationApi->revoke_api_key_api_v1_auth_api_key_delete: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**APIKeyRevokeResponse**](APIKeyRevokeResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_profile_api_v1_auth_me_put**
> UserResponse update_profile_api_v1_auth_me_put(user_update)

Update Profile

Update current user profile.

Args:
    user_data: Profile update data
    current_user: Current authenticated user
    auth_service: Authentication service

Returns:
    Updated user data

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.user_response import UserResponse
from chatter_sdk.models.user_update import UserUpdate
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.AuthenticationApi(api_client)
    user_update = chatter_sdk.UserUpdate() # UserUpdate | 

    try:
        # Update Profile
        api_response = await api_instance.update_profile_api_v1_auth_me_put(user_update)
        print("The response of AuthenticationApi->update_profile_api_v1_auth_me_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthenticationApi->update_profile_api_v1_auth_me_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_update** | [**UserUpdate**](UserUpdate.md)|  | 

### Return type

[**UserResponse**](UserResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

