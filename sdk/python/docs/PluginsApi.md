# chatter_sdk.PluginsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**bulk_disable_plugins_api_v1_plugins_bulk_disable_post**](PluginsApi.md#bulk_disable_plugins_api_v1_plugins_bulk_disable_post) | **POST** /api/v1/plugins/bulk/disable | Bulk Disable Plugins
[**bulk_enable_plugins_api_v1_plugins_bulk_enable_post**](PluginsApi.md#bulk_enable_plugins_api_v1_plugins_bulk_enable_post) | **POST** /api/v1/plugins/bulk/enable | Bulk Enable Plugins
[**check_plugin_dependencies_api_v1_plugins_plugin_id_dependencies_get**](PluginsApi.md#check_plugin_dependencies_api_v1_plugins_plugin_id_dependencies_get) | **GET** /api/v1/plugins/{plugin_id}/dependencies | Check Plugin Dependencies
[**disable_plugin_api_v1_plugins_plugin_id_disable_post**](PluginsApi.md#disable_plugin_api_v1_plugins_plugin_id_disable_post) | **POST** /api/v1/plugins/{plugin_id}/disable | Disable Plugin
[**enable_plugin_api_v1_plugins_plugin_id_enable_post**](PluginsApi.md#enable_plugin_api_v1_plugins_plugin_id_enable_post) | **POST** /api/v1/plugins/{plugin_id}/enable | Enable Plugin
[**get_plugin_api_v1_plugins_plugin_id_get**](PluginsApi.md#get_plugin_api_v1_plugins_plugin_id_get) | **GET** /api/v1/plugins/{plugin_id} | Get Plugin
[**get_plugin_stats_api_v1_plugins_stats_get**](PluginsApi.md#get_plugin_stats_api_v1_plugins_stats_get) | **GET** /api/v1/plugins/stats | Get Plugin Stats
[**health_check_plugins_api_v1_plugins_health_get**](PluginsApi.md#health_check_plugins_api_v1_plugins_health_get) | **GET** /api/v1/plugins/health | Health Check Plugins
[**install_plugin_api_v1_plugins_install_post**](PluginsApi.md#install_plugin_api_v1_plugins_install_post) | **POST** /api/v1/plugins/install | Install Plugin
[**list_plugins_api_v1_plugins_get**](PluginsApi.md#list_plugins_api_v1_plugins_get) | **GET** /api/v1/plugins/ | List Plugins
[**uninstall_plugin_api_v1_plugins_plugin_id_delete**](PluginsApi.md#uninstall_plugin_api_v1_plugins_plugin_id_delete) | **DELETE** /api/v1/plugins/{plugin_id} | Uninstall Plugin
[**update_plugin_api_v1_plugins_plugin_id_put**](PluginsApi.md#update_plugin_api_v1_plugins_plugin_id_put) | **PUT** /api/v1/plugins/{plugin_id} | Update Plugin


# **bulk_disable_plugins_api_v1_plugins_bulk_disable_post**
> Dict[str, object] bulk_disable_plugins_api_v1_plugins_bulk_disable_post(request_body)

Bulk Disable Plugins

Disable multiple plugins.

Args:
    plugin_ids: List of plugin IDs to disable
    current_user: Current authenticated user
    plugin_manager: Plugin manager instance

Returns:
    Bulk operation results

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost"
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
    api_instance = chatter_sdk.PluginsApi(api_client)
    request_body = ['request_body_example'] # List[str] | 

    try:
        # Bulk Disable Plugins
        api_response = await api_instance.bulk_disable_plugins_api_v1_plugins_bulk_disable_post(request_body)
        print("The response of PluginsApi->bulk_disable_plugins_api_v1_plugins_bulk_disable_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PluginsApi->bulk_disable_plugins_api_v1_plugins_bulk_disable_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_body** | [**List[str]**](str.md)|  | 

### Return type

**Dict[str, object]**

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

# **bulk_enable_plugins_api_v1_plugins_bulk_enable_post**
> Dict[str, object] bulk_enable_plugins_api_v1_plugins_bulk_enable_post(request_body)

Bulk Enable Plugins

Enable multiple plugins.

Args:
    plugin_ids: List of plugin IDs to enable
    current_user: Current authenticated user
    plugin_manager: Plugin manager instance

Returns:
    Bulk operation results

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost"
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
    api_instance = chatter_sdk.PluginsApi(api_client)
    request_body = ['request_body_example'] # List[str] | 

    try:
        # Bulk Enable Plugins
        api_response = await api_instance.bulk_enable_plugins_api_v1_plugins_bulk_enable_post(request_body)
        print("The response of PluginsApi->bulk_enable_plugins_api_v1_plugins_bulk_enable_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PluginsApi->bulk_enable_plugins_api_v1_plugins_bulk_enable_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_body** | [**List[str]**](str.md)|  | 

### Return type

**Dict[str, object]**

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

# **check_plugin_dependencies_api_v1_plugins_plugin_id_dependencies_get**
> Dict[str, object] check_plugin_dependencies_api_v1_plugins_plugin_id_dependencies_get(plugin_id)

Check Plugin Dependencies

Check plugin dependencies.

Args:
    plugin_id: Plugin ID
    current_user: Current authenticated user
    plugin_manager: Plugin manager instance

Returns:
    Dependency check results

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost"
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
    api_instance = chatter_sdk.PluginsApi(api_client)
    plugin_id = 'plugin_id_example' # str | 

    try:
        # Check Plugin Dependencies
        api_response = await api_instance.check_plugin_dependencies_api_v1_plugins_plugin_id_dependencies_get(plugin_id)
        print("The response of PluginsApi->check_plugin_dependencies_api_v1_plugins_plugin_id_dependencies_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PluginsApi->check_plugin_dependencies_api_v1_plugins_plugin_id_dependencies_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **plugin_id** | **str**|  | 

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

# **disable_plugin_api_v1_plugins_plugin_id_disable_post**
> PluginActionResponse disable_plugin_api_v1_plugins_plugin_id_disable_post(plugin_id)

Disable Plugin

Disable a plugin.

Args:
    plugin_id: Plugin ID
    current_user: Current authenticated user
    plugin_manager: Plugin manager instance

Returns:
    Action result

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.plugin_action_response import PluginActionResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost"
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
    api_instance = chatter_sdk.PluginsApi(api_client)
    plugin_id = 'plugin_id_example' # str | 

    try:
        # Disable Plugin
        api_response = await api_instance.disable_plugin_api_v1_plugins_plugin_id_disable_post(plugin_id)
        print("The response of PluginsApi->disable_plugin_api_v1_plugins_plugin_id_disable_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PluginsApi->disable_plugin_api_v1_plugins_plugin_id_disable_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **plugin_id** | **str**|  | 

### Return type

[**PluginActionResponse**](PluginActionResponse.md)

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

# **enable_plugin_api_v1_plugins_plugin_id_enable_post**
> PluginActionResponse enable_plugin_api_v1_plugins_plugin_id_enable_post(plugin_id)

Enable Plugin

Enable a plugin.

Args:
    plugin_id: Plugin ID
    current_user: Current authenticated user
    plugin_manager: Plugin manager instance

Returns:
    Action result

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.plugin_action_response import PluginActionResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost"
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
    api_instance = chatter_sdk.PluginsApi(api_client)
    plugin_id = 'plugin_id_example' # str | 

    try:
        # Enable Plugin
        api_response = await api_instance.enable_plugin_api_v1_plugins_plugin_id_enable_post(plugin_id)
        print("The response of PluginsApi->enable_plugin_api_v1_plugins_plugin_id_enable_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PluginsApi->enable_plugin_api_v1_plugins_plugin_id_enable_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **plugin_id** | **str**|  | 

### Return type

[**PluginActionResponse**](PluginActionResponse.md)

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

# **get_plugin_api_v1_plugins_plugin_id_get**
> PluginResponse get_plugin_api_v1_plugins_plugin_id_get(plugin_id)

Get Plugin

Get plugin by ID.

Args:
    plugin_id: Plugin ID
    current_user: Current authenticated user
    plugin_manager: Plugin manager instance

Returns:
    Plugin data

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.plugin_response import PluginResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost"
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
    api_instance = chatter_sdk.PluginsApi(api_client)
    plugin_id = 'plugin_id_example' # str | 

    try:
        # Get Plugin
        api_response = await api_instance.get_plugin_api_v1_plugins_plugin_id_get(plugin_id)
        print("The response of PluginsApi->get_plugin_api_v1_plugins_plugin_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PluginsApi->get_plugin_api_v1_plugins_plugin_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **plugin_id** | **str**|  | 

### Return type

[**PluginResponse**](PluginResponse.md)

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

# **get_plugin_stats_api_v1_plugins_stats_get**
> PluginStatsResponse get_plugin_stats_api_v1_plugins_stats_get()

Get Plugin Stats

Get plugin system statistics.

Args:
    current_user: Current authenticated user
    plugin_manager: Plugin manager instance

Returns:
    Plugin system statistics

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.plugin_stats_response import PluginStatsResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost"
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
    api_instance = chatter_sdk.PluginsApi(api_client)

    try:
        # Get Plugin Stats
        api_response = await api_instance.get_plugin_stats_api_v1_plugins_stats_get()
        print("The response of PluginsApi->get_plugin_stats_api_v1_plugins_stats_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PluginsApi->get_plugin_stats_api_v1_plugins_stats_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**PluginStatsResponse**](PluginStatsResponse.md)

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

# **health_check_plugins_api_v1_plugins_health_get**
> PluginHealthCheckResponse health_check_plugins_api_v1_plugins_health_get(auto_disable_unhealthy=auto_disable_unhealthy)

Health Check Plugins

Perform health check on all plugins.

Args:
    auto_disable_unhealthy: Whether to automatically disable unhealthy plugins
    current_user: Current authenticated user
    plugin_manager: Plugin manager instance

Returns:
    Health check results

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.plugin_health_check_response import PluginHealthCheckResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost"
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
    api_instance = chatter_sdk.PluginsApi(api_client)
    auto_disable_unhealthy = False # bool |  (optional) (default to False)

    try:
        # Health Check Plugins
        api_response = await api_instance.health_check_plugins_api_v1_plugins_health_get(auto_disable_unhealthy=auto_disable_unhealthy)
        print("The response of PluginsApi->health_check_plugins_api_v1_plugins_health_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PluginsApi->health_check_plugins_api_v1_plugins_health_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **auto_disable_unhealthy** | **bool**|  | [optional] [default to False]

### Return type

[**PluginHealthCheckResponse**](PluginHealthCheckResponse.md)

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

# **install_plugin_api_v1_plugins_install_post**
> PluginResponse install_plugin_api_v1_plugins_install_post(plugin_install_request)

Install Plugin

Install a new plugin.

Args:
    install_data: Plugin installation data
    current_user: Current authenticated user
    plugin_manager: Plugin manager instance

Returns:
    Installed plugin data

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.plugin_install_request import PluginInstallRequest
from chatter_sdk.models.plugin_response import PluginResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost"
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
    api_instance = chatter_sdk.PluginsApi(api_client)
    plugin_install_request = chatter_sdk.PluginInstallRequest() # PluginInstallRequest | 

    try:
        # Install Plugin
        api_response = await api_instance.install_plugin_api_v1_plugins_install_post(plugin_install_request)
        print("The response of PluginsApi->install_plugin_api_v1_plugins_install_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PluginsApi->install_plugin_api_v1_plugins_install_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **plugin_install_request** | [**PluginInstallRequest**](PluginInstallRequest.md)|  | 

### Return type

[**PluginResponse**](PluginResponse.md)

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

# **list_plugins_api_v1_plugins_get**
> PluginListResponse list_plugins_api_v1_plugins_get(plugin_type=plugin_type, status=status, enabled=enabled)

List Plugins

List installed plugins with optional filtering.

Args:
    request: List request parameters
    current_user: Current authenticated user
    plugin_manager: Plugin manager instance

Returns:
    List of installed plugins

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.plugin_list_response import PluginListResponse
from chatter_sdk.models.plugin_status import PluginStatus
from chatter_sdk.models.plugin_type import PluginType
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost"
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
    api_instance = chatter_sdk.PluginsApi(api_client)
    plugin_type = chatter_sdk.PluginType() # PluginType |  (optional)
    status = chatter_sdk.PluginStatus() # PluginStatus |  (optional)
    enabled = True # bool |  (optional)

    try:
        # List Plugins
        api_response = await api_instance.list_plugins_api_v1_plugins_get(plugin_type=plugin_type, status=status, enabled=enabled)
        print("The response of PluginsApi->list_plugins_api_v1_plugins_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PluginsApi->list_plugins_api_v1_plugins_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **plugin_type** | [**PluginType**](.md)|  | [optional] 
 **status** | [**PluginStatus**](.md)|  | [optional] 
 **enabled** | **bool**|  | [optional] 

### Return type

[**PluginListResponse**](PluginListResponse.md)

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

# **uninstall_plugin_api_v1_plugins_plugin_id_delete**
> PluginDeleteResponse uninstall_plugin_api_v1_plugins_plugin_id_delete(plugin_id)

Uninstall Plugin

Uninstall a plugin.

Args:
    plugin_id: Plugin ID
    current_user: Current authenticated user
    plugin_manager: Plugin manager instance

Returns:
    Uninstall result

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.plugin_delete_response import PluginDeleteResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost"
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
    api_instance = chatter_sdk.PluginsApi(api_client)
    plugin_id = 'plugin_id_example' # str | 

    try:
        # Uninstall Plugin
        api_response = await api_instance.uninstall_plugin_api_v1_plugins_plugin_id_delete(plugin_id)
        print("The response of PluginsApi->uninstall_plugin_api_v1_plugins_plugin_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PluginsApi->uninstall_plugin_api_v1_plugins_plugin_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **plugin_id** | **str**|  | 

### Return type

[**PluginDeleteResponse**](PluginDeleteResponse.md)

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

# **update_plugin_api_v1_plugins_plugin_id_put**
> PluginResponse update_plugin_api_v1_plugins_plugin_id_put(plugin_id, plugin_update_request)

Update Plugin

Update a plugin.

Args:
    plugin_id: Plugin ID
    update_data: Plugin update data
    current_user: Current authenticated user
    plugin_manager: Plugin manager instance

Returns:
    Updated plugin data

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.plugin_response import PluginResponse
from chatter_sdk.models.plugin_update_request import PluginUpdateRequest
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost"
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
    api_instance = chatter_sdk.PluginsApi(api_client)
    plugin_id = 'plugin_id_example' # str | 
    plugin_update_request = chatter_sdk.PluginUpdateRequest() # PluginUpdateRequest | 

    try:
        # Update Plugin
        api_response = await api_instance.update_plugin_api_v1_plugins_plugin_id_put(plugin_id, plugin_update_request)
        print("The response of PluginsApi->update_plugin_api_v1_plugins_plugin_id_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PluginsApi->update_plugin_api_v1_plugins_plugin_id_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **plugin_id** | **str**|  | 
 **plugin_update_request** | [**PluginUpdateRequest**](PluginUpdateRequest.md)|  | 

### Return type

[**PluginResponse**](PluginResponse.md)

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

