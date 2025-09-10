# chatter_sdk.ToolServersApi

All URIs are relative to *http://localhost:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**bulk_server_operation_api_v1_toolservers_servers_bulk_post**](ToolServersApi.md#bulk_server_operation_api_v1_toolservers_servers_bulk_post) | **POST** /api/v1/toolservers/servers/bulk | Bulk Server Operation
[**check_server_health_api_v1_toolservers_servers_server_id_health_get**](ToolServersApi.md#check_server_health_api_v1_toolservers_servers_server_id_health_get) | **GET** /api/v1/toolservers/servers/{server_id}/health | Check Server Health
[**check_tool_access_api_v1_toolservers_access_check_post**](ToolServersApi.md#check_tool_access_api_v1_toolservers_access_check_post) | **POST** /api/v1/toolservers/access-check | Check Tool Access
[**create_role_access_rule_api_v1_toolservers_role_access_post**](ToolServersApi.md#create_role_access_rule_api_v1_toolservers_role_access_post) | **POST** /api/v1/toolservers/role-access | Create Role Access Rule
[**create_tool_server_api_v1_toolservers_servers_post**](ToolServersApi.md#create_tool_server_api_v1_toolservers_servers_post) | **POST** /api/v1/toolservers/servers | Create Tool Server
[**delete_tool_server_api_v1_toolservers_servers_server_id_delete**](ToolServersApi.md#delete_tool_server_api_v1_toolservers_servers_server_id_delete) | **DELETE** /api/v1/toolservers/servers/{server_id} | Delete Tool Server
[**disable_tool_api_v1_toolservers_tools_tool_id_disable_post**](ToolServersApi.md#disable_tool_api_v1_toolservers_tools_tool_id_disable_post) | **POST** /api/v1/toolservers/tools/{tool_id}/disable | Disable Tool
[**disable_tool_server_api_v1_toolservers_servers_server_id_disable_post**](ToolServersApi.md#disable_tool_server_api_v1_toolservers_servers_server_id_disable_post) | **POST** /api/v1/toolservers/servers/{server_id}/disable | Disable Tool Server
[**enable_tool_api_v1_toolservers_tools_tool_id_enable_post**](ToolServersApi.md#enable_tool_api_v1_toolservers_tools_tool_id_enable_post) | **POST** /api/v1/toolservers/tools/{tool_id}/enable | Enable Tool
[**enable_tool_server_api_v1_toolservers_servers_server_id_enable_post**](ToolServersApi.md#enable_tool_server_api_v1_toolservers_servers_server_id_enable_post) | **POST** /api/v1/toolservers/servers/{server_id}/enable | Enable Tool Server
[**get_role_access_rules_api_v1_toolservers_role_access_get**](ToolServersApi.md#get_role_access_rules_api_v1_toolservers_role_access_get) | **GET** /api/v1/toolservers/role-access | Get Role Access Rules
[**get_server_metrics_api_v1_toolservers_servers_server_id_metrics_get**](ToolServersApi.md#get_server_metrics_api_v1_toolservers_servers_server_id_metrics_get) | **GET** /api/v1/toolservers/servers/{server_id}/metrics | Get Server Metrics
[**get_server_tools_api_v1_toolservers_servers_server_id_tools_get**](ToolServersApi.md#get_server_tools_api_v1_toolservers_servers_server_id_tools_get) | **GET** /api/v1/toolservers/servers/{server_id}/tools | Get Server Tools
[**get_tool_server_api_v1_toolservers_servers_server_id_get**](ToolServersApi.md#get_tool_server_api_v1_toolservers_servers_server_id_get) | **GET** /api/v1/toolservers/servers/{server_id} | Get Tool Server
[**get_user_permissions_api_v1_toolservers_users_user_id_permissions_get**](ToolServersApi.md#get_user_permissions_api_v1_toolservers_users_user_id_permissions_get) | **GET** /api/v1/toolservers/users/{user_id}/permissions | Get User Permissions
[**grant_tool_permission_api_v1_toolservers_permissions_post**](ToolServersApi.md#grant_tool_permission_api_v1_toolservers_permissions_post) | **POST** /api/v1/toolservers/permissions | Grant Tool Permission
[**list_all_tools_api_v1_toolservers_tools_all_get**](ToolServersApi.md#list_all_tools_api_v1_toolservers_tools_all_get) | **GET** /api/v1/toolservers/tools/all | List All Tools
[**list_tool_servers_api_v1_toolservers_servers_get**](ToolServersApi.md#list_tool_servers_api_v1_toolservers_servers_get) | **GET** /api/v1/toolservers/servers | List Tool Servers
[**refresh_server_tools_api_v1_toolservers_servers_server_id_refresh_tools_post**](ToolServersApi.md#refresh_server_tools_api_v1_toolservers_servers_server_id_refresh_tools_post) | **POST** /api/v1/toolservers/servers/{server_id}/refresh-tools | Refresh Server Tools
[**restart_tool_server_api_v1_toolservers_servers_server_id_restart_post**](ToolServersApi.md#restart_tool_server_api_v1_toolservers_servers_server_id_restart_post) | **POST** /api/v1/toolservers/servers/{server_id}/restart | Restart Tool Server
[**revoke_tool_permission_api_v1_toolservers_permissions_permission_id_delete**](ToolServersApi.md#revoke_tool_permission_api_v1_toolservers_permissions_permission_id_delete) | **DELETE** /api/v1/toolservers/permissions/{permission_id} | Revoke Tool Permission
[**start_tool_server_api_v1_toolservers_servers_server_id_start_post**](ToolServersApi.md#start_tool_server_api_v1_toolservers_servers_server_id_start_post) | **POST** /api/v1/toolservers/servers/{server_id}/start | Start Tool Server
[**stop_tool_server_api_v1_toolservers_servers_server_id_stop_post**](ToolServersApi.md#stop_tool_server_api_v1_toolservers_servers_server_id_stop_post) | **POST** /api/v1/toolservers/servers/{server_id}/stop | Stop Tool Server
[**test_server_connectivity_api_v1_toolservers_servers_server_id_test_connectivity_post**](ToolServersApi.md#test_server_connectivity_api_v1_toolservers_servers_server_id_test_connectivity_post) | **POST** /api/v1/toolservers/servers/{server_id}/test-connectivity | Test Server Connectivity
[**update_tool_permission_api_v1_toolservers_permissions_permission_id_put**](ToolServersApi.md#update_tool_permission_api_v1_toolservers_permissions_permission_id_put) | **PUT** /api/v1/toolservers/permissions/{permission_id} | Update Tool Permission
[**update_tool_server_api_v1_toolservers_servers_server_id_put**](ToolServersApi.md#update_tool_server_api_v1_toolservers_servers_server_id_put) | **PUT** /api/v1/toolservers/servers/{server_id} | Update Tool Server


# **bulk_server_operation_api_v1_toolservers_servers_bulk_post**
> BulkOperationResult bulk_server_operation_api_v1_toolservers_servers_bulk_post(bulk_tool_server_operation)

Bulk Server Operation

Perform bulk operations on multiple servers.

Args:
    operation_data: Bulk operation data
    current_user: Current authenticated user
    service: Tool server service

Returns:
    Bulk operation result

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.bulk_operation_result import BulkOperationResult
from chatter_sdk.models.bulk_tool_server_operation import BulkToolServerOperation
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
    api_instance = chatter_sdk.ToolServersApi(api_client)
    bulk_tool_server_operation = chatter_sdk.BulkToolServerOperation() # BulkToolServerOperation | 

    try:
        # Bulk Server Operation
        api_response = await api_instance.bulk_server_operation_api_v1_toolservers_servers_bulk_post(bulk_tool_server_operation)
        print("The response of ToolServersApi->bulk_server_operation_api_v1_toolservers_servers_bulk_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ToolServersApi->bulk_server_operation_api_v1_toolservers_servers_bulk_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **bulk_tool_server_operation** | [**BulkToolServerOperation**](BulkToolServerOperation.md)|  | 

### Return type

[**BulkOperationResult**](BulkOperationResult.md)

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

# **check_server_health_api_v1_toolservers_servers_server_id_health_get**
> ToolServerHealthCheck check_server_health_api_v1_toolservers_servers_server_id_health_get(server_id)

Check Server Health

Perform health check on a server.

Args:
    server_id: Server ID
    current_user: Current authenticated user
    service: Tool server service

Returns:
    Health check result

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.tool_server_health_check import ToolServerHealthCheck
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
    api_instance = chatter_sdk.ToolServersApi(api_client)
    server_id = 'server_id_example' # str | 

    try:
        # Check Server Health
        api_response = await api_instance.check_server_health_api_v1_toolservers_servers_server_id_health_get(server_id)
        print("The response of ToolServersApi->check_server_health_api_v1_toolservers_servers_server_id_health_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ToolServersApi->check_server_health_api_v1_toolservers_servers_server_id_health_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **server_id** | **str**|  | 

### Return type

[**ToolServerHealthCheck**](ToolServerHealthCheck.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **check_tool_access_api_v1_toolservers_access_check_post**
> ToolAccessResult check_tool_access_api_v1_toolservers_access_check_post(user_tool_access_check)

Check Tool Access

Check if user has access to a tool.

Args:
    check_data: Access check data
    current_user: Current authenticated user
    access_service: Tool access service

Returns:
    Access check result

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.tool_access_result import ToolAccessResult
from chatter_sdk.models.user_tool_access_check import UserToolAccessCheck
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
    api_instance = chatter_sdk.ToolServersApi(api_client)
    user_tool_access_check = chatter_sdk.UserToolAccessCheck() # UserToolAccessCheck | 

    try:
        # Check Tool Access
        api_response = await api_instance.check_tool_access_api_v1_toolservers_access_check_post(user_tool_access_check)
        print("The response of ToolServersApi->check_tool_access_api_v1_toolservers_access_check_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ToolServersApi->check_tool_access_api_v1_toolservers_access_check_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_tool_access_check** | [**UserToolAccessCheck**](UserToolAccessCheck.md)|  | 

### Return type

[**ToolAccessResult**](ToolAccessResult.md)

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

# **create_role_access_rule_api_v1_toolservers_role_access_post**
> RoleToolAccessResponse create_role_access_rule_api_v1_toolservers_role_access_post(role_tool_access_create)

Create Role Access Rule

Create role-based access rule.

Args:
    rule_data: Rule data
    current_user: Current authenticated user
    access_service: Tool access service

Returns:
    Created rule

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.role_tool_access_create import RoleToolAccessCreate
from chatter_sdk.models.role_tool_access_response import RoleToolAccessResponse
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
    api_instance = chatter_sdk.ToolServersApi(api_client)
    role_tool_access_create = chatter_sdk.RoleToolAccessCreate() # RoleToolAccessCreate | 

    try:
        # Create Role Access Rule
        api_response = await api_instance.create_role_access_rule_api_v1_toolservers_role_access_post(role_tool_access_create)
        print("The response of ToolServersApi->create_role_access_rule_api_v1_toolservers_role_access_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ToolServersApi->create_role_access_rule_api_v1_toolservers_role_access_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **role_tool_access_create** | [**RoleToolAccessCreate**](RoleToolAccessCreate.md)|  | 

### Return type

[**RoleToolAccessResponse**](RoleToolAccessResponse.md)

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

# **create_tool_server_api_v1_toolservers_servers_post**
> ToolServerResponse create_tool_server_api_v1_toolservers_servers_post(tool_server_create)

Create Tool Server

Create a new tool server.

Args:
    server_data: Server creation data
    current_user: Current authenticated user
    service: Tool server service

Returns:
    Created server response

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.tool_server_create import ToolServerCreate
from chatter_sdk.models.tool_server_response import ToolServerResponse
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
    api_instance = chatter_sdk.ToolServersApi(api_client)
    tool_server_create = chatter_sdk.ToolServerCreate() # ToolServerCreate | 

    try:
        # Create Tool Server
        api_response = await api_instance.create_tool_server_api_v1_toolservers_servers_post(tool_server_create)
        print("The response of ToolServersApi->create_tool_server_api_v1_toolservers_servers_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ToolServersApi->create_tool_server_api_v1_toolservers_servers_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **tool_server_create** | [**ToolServerCreate**](ToolServerCreate.md)|  | 

### Return type

[**ToolServerResponse**](ToolServerResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_tool_server_api_v1_toolservers_servers_server_id_delete**
> ToolServerDeleteResponse delete_tool_server_api_v1_toolservers_servers_server_id_delete(server_id)

Delete Tool Server

Delete a tool server.

Args:
    server_id: Server ID
    current_user: Current authenticated user
    service: Tool server service

Returns:
    Success message

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.tool_server_delete_response import ToolServerDeleteResponse
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
    api_instance = chatter_sdk.ToolServersApi(api_client)
    server_id = 'server_id_example' # str | 

    try:
        # Delete Tool Server
        api_response = await api_instance.delete_tool_server_api_v1_toolservers_servers_server_id_delete(server_id)
        print("The response of ToolServersApi->delete_tool_server_api_v1_toolservers_servers_server_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ToolServersApi->delete_tool_server_api_v1_toolservers_servers_server_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **server_id** | **str**|  | 

### Return type

[**ToolServerDeleteResponse**](ToolServerDeleteResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **disable_tool_api_v1_toolservers_tools_tool_id_disable_post**
> ToolOperationResponse disable_tool_api_v1_toolservers_tools_tool_id_disable_post(tool_id)

Disable Tool

Disable a specific tool.

Args:
    tool_id: Tool ID
    current_user: Current authenticated user
    service: Tool server service

Returns:
    Operation result

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.tool_operation_response import ToolOperationResponse
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
    api_instance = chatter_sdk.ToolServersApi(api_client)
    tool_id = 'tool_id_example' # str | 

    try:
        # Disable Tool
        api_response = await api_instance.disable_tool_api_v1_toolservers_tools_tool_id_disable_post(tool_id)
        print("The response of ToolServersApi->disable_tool_api_v1_toolservers_tools_tool_id_disable_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ToolServersApi->disable_tool_api_v1_toolservers_tools_tool_id_disable_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **tool_id** | **str**|  | 

### Return type

[**ToolOperationResponse**](ToolOperationResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **disable_tool_server_api_v1_toolservers_servers_server_id_disable_post**
> ToolServerOperationResponse disable_tool_server_api_v1_toolservers_servers_server_id_disable_post(server_id)

Disable Tool Server

Disable a tool server.

Args:
    server_id: Server ID
    current_user: Current authenticated user
    service: Tool server service

Returns:
    Operation result

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.tool_server_operation_response import ToolServerOperationResponse
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
    api_instance = chatter_sdk.ToolServersApi(api_client)
    server_id = 'server_id_example' # str | 

    try:
        # Disable Tool Server
        api_response = await api_instance.disable_tool_server_api_v1_toolservers_servers_server_id_disable_post(server_id)
        print("The response of ToolServersApi->disable_tool_server_api_v1_toolservers_servers_server_id_disable_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ToolServersApi->disable_tool_server_api_v1_toolservers_servers_server_id_disable_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **server_id** | **str**|  | 

### Return type

[**ToolServerOperationResponse**](ToolServerOperationResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **enable_tool_api_v1_toolservers_tools_tool_id_enable_post**
> ToolOperationResponse enable_tool_api_v1_toolservers_tools_tool_id_enable_post(tool_id)

Enable Tool

Enable a specific tool.

Args:
    tool_id: Tool ID
    current_user: Current authenticated user
    service: Tool server service

Returns:
    Operation result

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.tool_operation_response import ToolOperationResponse
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
    api_instance = chatter_sdk.ToolServersApi(api_client)
    tool_id = 'tool_id_example' # str | 

    try:
        # Enable Tool
        api_response = await api_instance.enable_tool_api_v1_toolservers_tools_tool_id_enable_post(tool_id)
        print("The response of ToolServersApi->enable_tool_api_v1_toolservers_tools_tool_id_enable_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ToolServersApi->enable_tool_api_v1_toolservers_tools_tool_id_enable_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **tool_id** | **str**|  | 

### Return type

[**ToolOperationResponse**](ToolOperationResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **enable_tool_server_api_v1_toolservers_servers_server_id_enable_post**
> ToolServerOperationResponse enable_tool_server_api_v1_toolservers_servers_server_id_enable_post(server_id)

Enable Tool Server

Enable a tool server.

Args:
    server_id: Server ID
    current_user: Current authenticated user
    service: Tool server service

Returns:
    Operation result

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.tool_server_operation_response import ToolServerOperationResponse
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
    api_instance = chatter_sdk.ToolServersApi(api_client)
    server_id = 'server_id_example' # str | 

    try:
        # Enable Tool Server
        api_response = await api_instance.enable_tool_server_api_v1_toolservers_servers_server_id_enable_post(server_id)
        print("The response of ToolServersApi->enable_tool_server_api_v1_toolservers_servers_server_id_enable_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ToolServersApi->enable_tool_server_api_v1_toolservers_servers_server_id_enable_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **server_id** | **str**|  | 

### Return type

[**ToolServerOperationResponse**](ToolServerOperationResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_role_access_rules_api_v1_toolservers_role_access_get**
> List[RoleToolAccessResponse] get_role_access_rules_api_v1_toolservers_role_access_get(role=role)

Get Role Access Rules

Get role-based access rules.

Args:
    role: Optional role filter
    current_user: Current authenticated user
    access_service: Tool access service

Returns:
    List of access rules

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.role_tool_access_response import RoleToolAccessResponse
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
    api_instance = chatter_sdk.ToolServersApi(api_client)
    role = 'role_example' # str |  (optional)

    try:
        # Get Role Access Rules
        api_response = await api_instance.get_role_access_rules_api_v1_toolservers_role_access_get(role=role)
        print("The response of ToolServersApi->get_role_access_rules_api_v1_toolservers_role_access_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ToolServersApi->get_role_access_rules_api_v1_toolservers_role_access_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **role** | **str**|  | [optional] 

### Return type

[**List[RoleToolAccessResponse]**](RoleToolAccessResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_server_metrics_api_v1_toolservers_servers_server_id_metrics_get**
> ToolServerMetrics get_server_metrics_api_v1_toolservers_servers_server_id_metrics_get(server_id)

Get Server Metrics

Get analytics for a specific server.

Args:
    server_id: Server ID
    current_user: Current authenticated user
    service: Tool server service

Returns:
    Server metrics

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.tool_server_metrics import ToolServerMetrics
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
    api_instance = chatter_sdk.ToolServersApi(api_client)
    server_id = 'server_id_example' # str | 

    try:
        # Get Server Metrics
        api_response = await api_instance.get_server_metrics_api_v1_toolservers_servers_server_id_metrics_get(server_id)
        print("The response of ToolServersApi->get_server_metrics_api_v1_toolservers_servers_server_id_metrics_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ToolServersApi->get_server_metrics_api_v1_toolservers_servers_server_id_metrics_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **server_id** | **str**|  | 

### Return type

[**ToolServerMetrics**](ToolServerMetrics.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_server_tools_api_v1_toolservers_servers_server_id_tools_get**
> ServerToolsResponse get_server_tools_api_v1_toolservers_servers_server_id_tools_get(server_id, limit=limit, offset=offset)

Get Server Tools

Get tools for a specific server.

Args:
    server_id: Server ID
    request: Server tools request with pagination
    current_user: Current authenticated user
    service: Tool server service

Returns:
    List of server tools with pagination

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.server_tools_response import ServerToolsResponse
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
    api_instance = chatter_sdk.ToolServersApi(api_client)
    server_id = 'server_id_example' # str | 
    limit = 50 # int |  (optional) (default to 50)
    offset = 0 # int |  (optional) (default to 0)

    try:
        # Get Server Tools
        api_response = await api_instance.get_server_tools_api_v1_toolservers_servers_server_id_tools_get(server_id, limit=limit, offset=offset)
        print("The response of ToolServersApi->get_server_tools_api_v1_toolservers_servers_server_id_tools_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ToolServersApi->get_server_tools_api_v1_toolservers_servers_server_id_tools_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **server_id** | **str**|  | 
 **limit** | **int**|  | [optional] [default to 50]
 **offset** | **int**|  | [optional] [default to 0]

### Return type

[**ServerToolsResponse**](ServerToolsResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_tool_server_api_v1_toolservers_servers_server_id_get**
> ToolServerResponse get_tool_server_api_v1_toolservers_servers_server_id_get(server_id)

Get Tool Server

Get a tool server by ID.

Args:
    server_id: Server ID
    current_user: Current authenticated user
    service: Tool server service

Returns:
    Server response

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.tool_server_response import ToolServerResponse
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
    api_instance = chatter_sdk.ToolServersApi(api_client)
    server_id = 'server_id_example' # str | 

    try:
        # Get Tool Server
        api_response = await api_instance.get_tool_server_api_v1_toolservers_servers_server_id_get(server_id)
        print("The response of ToolServersApi->get_tool_server_api_v1_toolservers_servers_server_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ToolServersApi->get_tool_server_api_v1_toolservers_servers_server_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **server_id** | **str**|  | 

### Return type

[**ToolServerResponse**](ToolServerResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_user_permissions_api_v1_toolservers_users_user_id_permissions_get**
> List[ToolPermissionResponse] get_user_permissions_api_v1_toolservers_users_user_id_permissions_get(user_id)

Get User Permissions

Get all permissions for a user.

Args:
    user_id: User ID
    current_user: Current authenticated user
    access_service: Tool access service

Returns:
    List of user permissions

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.tool_permission_response import ToolPermissionResponse
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
    api_instance = chatter_sdk.ToolServersApi(api_client)
    user_id = 'user_id_example' # str | 

    try:
        # Get User Permissions
        api_response = await api_instance.get_user_permissions_api_v1_toolservers_users_user_id_permissions_get(user_id)
        print("The response of ToolServersApi->get_user_permissions_api_v1_toolservers_users_user_id_permissions_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ToolServersApi->get_user_permissions_api_v1_toolservers_users_user_id_permissions_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_id** | **str**|  | 

### Return type

[**List[ToolPermissionResponse]**](ToolPermissionResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **grant_tool_permission_api_v1_toolservers_permissions_post**
> ToolPermissionResponse grant_tool_permission_api_v1_toolservers_permissions_post(tool_permission_create)

Grant Tool Permission

Grant tool permission to a user.

Args:
    permission_data: Permission data
    current_user: Current authenticated user
    access_service: Tool access service

Returns:
    Created permission

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.tool_permission_create import ToolPermissionCreate
from chatter_sdk.models.tool_permission_response import ToolPermissionResponse
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
    api_instance = chatter_sdk.ToolServersApi(api_client)
    tool_permission_create = chatter_sdk.ToolPermissionCreate() # ToolPermissionCreate | 

    try:
        # Grant Tool Permission
        api_response = await api_instance.grant_tool_permission_api_v1_toolservers_permissions_post(tool_permission_create)
        print("The response of ToolServersApi->grant_tool_permission_api_v1_toolservers_permissions_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ToolServersApi->grant_tool_permission_api_v1_toolservers_permissions_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **tool_permission_create** | [**ToolPermissionCreate**](ToolPermissionCreate.md)|  | 

### Return type

[**ToolPermissionResponse**](ToolPermissionResponse.md)

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

# **list_all_tools_api_v1_toolservers_tools_all_get**
> List[Dict[str, object]] list_all_tools_api_v1_toolservers_tools_all_get()

List All Tools

List all tools across all servers.

Args:
    current_user: Current authenticated user
    tool_server_service: Tool server service

Returns:
    List of all available tools across all servers

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
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
    api_instance = chatter_sdk.ToolServersApi(api_client)

    try:
        # List All Tools
        api_response = await api_instance.list_all_tools_api_v1_toolservers_tools_all_get()
        print("The response of ToolServersApi->list_all_tools_api_v1_toolservers_tools_all_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ToolServersApi->list_all_tools_api_v1_toolservers_tools_all_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**List[Dict[str, object]]**

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

# **list_tool_servers_api_v1_toolservers_servers_get**
> List[ToolServerResponse] list_tool_servers_api_v1_toolservers_servers_get(status=status, include_builtin=include_builtin)

List Tool Servers

List tool servers with optional filtering.

Args:
    request: List request with filter parameters
    current_user: Current authenticated user
    service: Tool server service

Returns:
    List of server responses

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.server_status import ServerStatus
from chatter_sdk.models.tool_server_response import ToolServerResponse
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
    api_instance = chatter_sdk.ToolServersApi(api_client)
    status = chatter_sdk.ServerStatus() # ServerStatus |  (optional)
    include_builtin = True # bool |  (optional) (default to True)

    try:
        # List Tool Servers
        api_response = await api_instance.list_tool_servers_api_v1_toolservers_servers_get(status=status, include_builtin=include_builtin)
        print("The response of ToolServersApi->list_tool_servers_api_v1_toolservers_servers_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ToolServersApi->list_tool_servers_api_v1_toolservers_servers_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **status** | [**ServerStatus**](.md)|  | [optional] 
 **include_builtin** | **bool**|  | [optional] [default to True]

### Return type

[**List[ToolServerResponse]**](ToolServerResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **refresh_server_tools_api_v1_toolservers_servers_server_id_refresh_tools_post**
> Dict[str, object] refresh_server_tools_api_v1_toolservers_servers_server_id_refresh_tools_post(server_id)

Refresh Server Tools

Refresh tools for a remote server.

Args:
    server_id: Server ID
    current_user: Current authenticated user
    service: Tool server service

Returns:
    Refresh result

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
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
    api_instance = chatter_sdk.ToolServersApi(api_client)
    server_id = 'server_id_example' # str | 

    try:
        # Refresh Server Tools
        api_response = await api_instance.refresh_server_tools_api_v1_toolservers_servers_server_id_refresh_tools_post(server_id)
        print("The response of ToolServersApi->refresh_server_tools_api_v1_toolservers_servers_server_id_refresh_tools_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ToolServersApi->refresh_server_tools_api_v1_toolservers_servers_server_id_refresh_tools_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **server_id** | **str**|  | 

### Return type

**Dict[str, object]**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **restart_tool_server_api_v1_toolservers_servers_server_id_restart_post**
> ToolServerOperationResponse restart_tool_server_api_v1_toolservers_servers_server_id_restart_post(server_id)

Restart Tool Server

Restart a tool server.

Args:
    server_id: Server ID
    current_user: Current authenticated user
    service: Tool server service

Returns:
    Operation result

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.tool_server_operation_response import ToolServerOperationResponse
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
    api_instance = chatter_sdk.ToolServersApi(api_client)
    server_id = 'server_id_example' # str | 

    try:
        # Restart Tool Server
        api_response = await api_instance.restart_tool_server_api_v1_toolservers_servers_server_id_restart_post(server_id)
        print("The response of ToolServersApi->restart_tool_server_api_v1_toolservers_servers_server_id_restart_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ToolServersApi->restart_tool_server_api_v1_toolservers_servers_server_id_restart_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **server_id** | **str**|  | 

### Return type

[**ToolServerOperationResponse**](ToolServerOperationResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **revoke_tool_permission_api_v1_toolservers_permissions_permission_id_delete**
> Dict[str, object] revoke_tool_permission_api_v1_toolservers_permissions_permission_id_delete(permission_id)

Revoke Tool Permission

Revoke tool permission.

Args:
    permission_id: Permission ID
    current_user: Current authenticated user
    access_service: Tool access service

Returns:
    Success message

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
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
    api_instance = chatter_sdk.ToolServersApi(api_client)
    permission_id = 'permission_id_example' # str | 

    try:
        # Revoke Tool Permission
        api_response = await api_instance.revoke_tool_permission_api_v1_toolservers_permissions_permission_id_delete(permission_id)
        print("The response of ToolServersApi->revoke_tool_permission_api_v1_toolservers_permissions_permission_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ToolServersApi->revoke_tool_permission_api_v1_toolservers_permissions_permission_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **permission_id** | **str**|  | 

### Return type

**Dict[str, object]**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **start_tool_server_api_v1_toolservers_servers_server_id_start_post**
> ToolServerOperationResponse start_tool_server_api_v1_toolservers_servers_server_id_start_post(server_id)

Start Tool Server

Start a tool server.

Args:
    server_id: Server ID
    current_user: Current authenticated user
    service: Tool server service

Returns:
    Operation result

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.tool_server_operation_response import ToolServerOperationResponse
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
    api_instance = chatter_sdk.ToolServersApi(api_client)
    server_id = 'server_id_example' # str | 

    try:
        # Start Tool Server
        api_response = await api_instance.start_tool_server_api_v1_toolservers_servers_server_id_start_post(server_id)
        print("The response of ToolServersApi->start_tool_server_api_v1_toolservers_servers_server_id_start_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ToolServersApi->start_tool_server_api_v1_toolservers_servers_server_id_start_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **server_id** | **str**|  | 

### Return type

[**ToolServerOperationResponse**](ToolServerOperationResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **stop_tool_server_api_v1_toolservers_servers_server_id_stop_post**
> ToolServerOperationResponse stop_tool_server_api_v1_toolservers_servers_server_id_stop_post(server_id)

Stop Tool Server

Stop a tool server.

Args:
    server_id: Server ID
    current_user: Current authenticated user
    service: Tool server service

Returns:
    Operation result

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.tool_server_operation_response import ToolServerOperationResponse
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
    api_instance = chatter_sdk.ToolServersApi(api_client)
    server_id = 'server_id_example' # str | 

    try:
        # Stop Tool Server
        api_response = await api_instance.stop_tool_server_api_v1_toolservers_servers_server_id_stop_post(server_id)
        print("The response of ToolServersApi->stop_tool_server_api_v1_toolservers_servers_server_id_stop_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ToolServersApi->stop_tool_server_api_v1_toolservers_servers_server_id_stop_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **server_id** | **str**|  | 

### Return type

[**ToolServerOperationResponse**](ToolServerOperationResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **test_server_connectivity_api_v1_toolservers_servers_server_id_test_connectivity_post**
> Dict[str, object] test_server_connectivity_api_v1_toolservers_servers_server_id_test_connectivity_post(server_id)

Test Server Connectivity

Test connectivity to an external MCP server.

Args:
    server_id: Tool server ID
    current_user: Current authenticated user
    tool_server_service: Tool server service

Returns:
    Connectivity test results

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
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
    api_instance = chatter_sdk.ToolServersApi(api_client)
    server_id = 'server_id_example' # str | 

    try:
        # Test Server Connectivity
        api_response = await api_instance.test_server_connectivity_api_v1_toolservers_servers_server_id_test_connectivity_post(server_id)
        print("The response of ToolServersApi->test_server_connectivity_api_v1_toolservers_servers_server_id_test_connectivity_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ToolServersApi->test_server_connectivity_api_v1_toolservers_servers_server_id_test_connectivity_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **server_id** | **str**|  | 

### Return type

**Dict[str, object]**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_tool_permission_api_v1_toolservers_permissions_permission_id_put**
> ToolPermissionResponse update_tool_permission_api_v1_toolservers_permissions_permission_id_put(permission_id, tool_permission_update)

Update Tool Permission

Update tool permission.

Args:
    permission_id: Permission ID
    update_data: Update data
    current_user: Current authenticated user
    access_service: Tool access service

Returns:
    Updated permission

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.tool_permission_response import ToolPermissionResponse
from chatter_sdk.models.tool_permission_update import ToolPermissionUpdate
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
    api_instance = chatter_sdk.ToolServersApi(api_client)
    permission_id = 'permission_id_example' # str | 
    tool_permission_update = chatter_sdk.ToolPermissionUpdate() # ToolPermissionUpdate | 

    try:
        # Update Tool Permission
        api_response = await api_instance.update_tool_permission_api_v1_toolservers_permissions_permission_id_put(permission_id, tool_permission_update)
        print("The response of ToolServersApi->update_tool_permission_api_v1_toolservers_permissions_permission_id_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ToolServersApi->update_tool_permission_api_v1_toolservers_permissions_permission_id_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **permission_id** | **str**|  | 
 **tool_permission_update** | [**ToolPermissionUpdate**](ToolPermissionUpdate.md)|  | 

### Return type

[**ToolPermissionResponse**](ToolPermissionResponse.md)

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

# **update_tool_server_api_v1_toolservers_servers_server_id_put**
> ToolServerResponse update_tool_server_api_v1_toolservers_servers_server_id_put(server_id, tool_server_update)

Update Tool Server

Update a tool server.

Args:
    server_id: Server ID
    update_data: Update data
    current_user: Current authenticated user
    service: Tool server service

Returns:
    Updated server response

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.tool_server_response import ToolServerResponse
from chatter_sdk.models.tool_server_update import ToolServerUpdate
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
    api_instance = chatter_sdk.ToolServersApi(api_client)
    server_id = 'server_id_example' # str | 
    tool_server_update = chatter_sdk.ToolServerUpdate() # ToolServerUpdate | 

    try:
        # Update Tool Server
        api_response = await api_instance.update_tool_server_api_v1_toolservers_servers_server_id_put(server_id, tool_server_update)
        print("The response of ToolServersApi->update_tool_server_api_v1_toolservers_servers_server_id_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ToolServersApi->update_tool_server_api_v1_toolservers_servers_server_id_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **server_id** | **str**|  | 
 **tool_server_update** | [**ToolServerUpdate**](ToolServerUpdate.md)|  | 

### Return type

[**ToolServerResponse**](ToolServerResponse.md)

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

