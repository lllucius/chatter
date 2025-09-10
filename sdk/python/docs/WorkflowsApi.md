# chatter_sdk.WorkflowsApi

All URIs are relative to *http://localhost:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_workflow_definition_api_v1_workflows_workflows_definitions_post**](WorkflowsApi.md#create_workflow_definition_api_v1_workflows_workflows_definitions_post) | **POST** /api/v1/workflows/workflows/definitions | Create Workflow Definition
[**create_workflow_template_api_v1_workflows_workflows_templates_post**](WorkflowsApi.md#create_workflow_template_api_v1_workflows_workflows_templates_post) | **POST** /api/v1/workflows/workflows/templates | Create Workflow Template
[**delete_workflow_definition_api_v1_workflows_workflows_definitions_workflow_id_delete**](WorkflowsApi.md#delete_workflow_definition_api_v1_workflows_workflows_definitions_workflow_id_delete) | **DELETE** /api/v1/workflows/workflows/definitions/{workflow_id} | Delete Workflow Definition
[**execute_workflow_api_v1_workflows_workflows_definitions_workflow_id_execute_post**](WorkflowsApi.md#execute_workflow_api_v1_workflows_workflows_definitions_workflow_id_execute_post) | **POST** /api/v1/workflows/workflows/definitions/{workflow_id}/execute | Execute Workflow
[**get_supported_node_types_api_v1_workflows_workflows_node_types_get**](WorkflowsApi.md#get_supported_node_types_api_v1_workflows_workflows_node_types_get) | **GET** /api/v1/workflows/workflows/node-types | Get Supported Node Types
[**get_workflow_analytics_api_v1_workflows_workflows_definitions_workflow_id_analytics_get**](WorkflowsApi.md#get_workflow_analytics_api_v1_workflows_workflows_definitions_workflow_id_analytics_get) | **GET** /api/v1/workflows/workflows/definitions/{workflow_id}/analytics | Get Workflow Analytics
[**get_workflow_definition_api_v1_workflows_workflows_definitions_workflow_id_get**](WorkflowsApi.md#get_workflow_definition_api_v1_workflows_workflows_definitions_workflow_id_get) | **GET** /api/v1/workflows/workflows/definitions/{workflow_id} | Get Workflow Definition
[**list_workflow_definitions_api_v1_workflows_workflows_definitions_get**](WorkflowsApi.md#list_workflow_definitions_api_v1_workflows_workflows_definitions_get) | **GET** /api/v1/workflows/workflows/definitions | List Workflow Definitions
[**list_workflow_executions_api_v1_workflows_workflows_definitions_workflow_id_executions_get**](WorkflowsApi.md#list_workflow_executions_api_v1_workflows_workflows_definitions_workflow_id_executions_get) | **GET** /api/v1/workflows/workflows/definitions/{workflow_id}/executions | List Workflow Executions
[**list_workflow_templates_api_v1_workflows_workflows_templates_get**](WorkflowsApi.md#list_workflow_templates_api_v1_workflows_workflows_templates_get) | **GET** /api/v1/workflows/workflows/templates | List Workflow Templates
[**update_workflow_definition_api_v1_workflows_workflows_definitions_workflow_id_put**](WorkflowsApi.md#update_workflow_definition_api_v1_workflows_workflows_definitions_workflow_id_put) | **PUT** /api/v1/workflows/workflows/definitions/{workflow_id} | Update Workflow Definition
[**update_workflow_template_api_v1_workflows_workflows_templates_template_id_put**](WorkflowsApi.md#update_workflow_template_api_v1_workflows_workflows_templates_template_id_put) | **PUT** /api/v1/workflows/workflows/templates/{template_id} | Update Workflow Template
[**validate_workflow_definition_api_v1_workflows_workflows_definitions_validate_post**](WorkflowsApi.md#validate_workflow_definition_api_v1_workflows_workflows_definitions_validate_post) | **POST** /api/v1/workflows/workflows/definitions/validate | Validate Workflow Definition


# **create_workflow_definition_api_v1_workflows_workflows_definitions_post**
> WorkflowDefinitionResponse create_workflow_definition_api_v1_workflows_workflows_definitions_post(workflow_definition_create)

Create Workflow Definition

Create a new workflow definition.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.workflow_definition_create import WorkflowDefinitionCreate
from chatter_sdk.models.workflow_definition_response import WorkflowDefinitionResponse
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
    api_instance = chatter_sdk.WorkflowsApi(api_client)
    workflow_definition_create = chatter_sdk.WorkflowDefinitionCreate() # WorkflowDefinitionCreate | 

    try:
        # Create Workflow Definition
        api_response = await api_instance.create_workflow_definition_api_v1_workflows_workflows_definitions_post(workflow_definition_create)
        print("The response of WorkflowsApi->create_workflow_definition_api_v1_workflows_workflows_definitions_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowsApi->create_workflow_definition_api_v1_workflows_workflows_definitions_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workflow_definition_create** | [**WorkflowDefinitionCreate**](WorkflowDefinitionCreate.md)|  | 

### Return type

[**WorkflowDefinitionResponse**](WorkflowDefinitionResponse.md)

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

# **create_workflow_template_api_v1_workflows_workflows_templates_post**
> WorkflowTemplateResponse create_workflow_template_api_v1_workflows_workflows_templates_post(workflow_template_create)

Create Workflow Template

Create a new workflow template.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.workflow_template_create import WorkflowTemplateCreate
from chatter_sdk.models.workflow_template_response import WorkflowTemplateResponse
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
    api_instance = chatter_sdk.WorkflowsApi(api_client)
    workflow_template_create = chatter_sdk.WorkflowTemplateCreate() # WorkflowTemplateCreate | 

    try:
        # Create Workflow Template
        api_response = await api_instance.create_workflow_template_api_v1_workflows_workflows_templates_post(workflow_template_create)
        print("The response of WorkflowsApi->create_workflow_template_api_v1_workflows_workflows_templates_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowsApi->create_workflow_template_api_v1_workflows_workflows_templates_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workflow_template_create** | [**WorkflowTemplateCreate**](WorkflowTemplateCreate.md)|  | 

### Return type

[**WorkflowTemplateResponse**](WorkflowTemplateResponse.md)

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

# **delete_workflow_definition_api_v1_workflows_workflows_definitions_workflow_id_delete**
> Dict[str, str] delete_workflow_definition_api_v1_workflows_workflows_definitions_workflow_id_delete(workflow_id)

Delete Workflow Definition

Delete a workflow definition.

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
    api_instance = chatter_sdk.WorkflowsApi(api_client)
    workflow_id = 'workflow_id_example' # str | Workflow ID

    try:
        # Delete Workflow Definition
        api_response = await api_instance.delete_workflow_definition_api_v1_workflows_workflows_definitions_workflow_id_delete(workflow_id)
        print("The response of WorkflowsApi->delete_workflow_definition_api_v1_workflows_workflows_definitions_workflow_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowsApi->delete_workflow_definition_api_v1_workflows_workflows_definitions_workflow_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workflow_id** | **str**| Workflow ID | 

### Return type

**Dict[str, str]**

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

# **execute_workflow_api_v1_workflows_workflows_definitions_workflow_id_execute_post**
> WorkflowExecutionResponse execute_workflow_api_v1_workflows_workflows_definitions_workflow_id_execute_post(workflow_id, workflow_execution_request)

Execute Workflow

Execute a workflow definition.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.workflow_execution_request import WorkflowExecutionRequest
from chatter_sdk.models.workflow_execution_response import WorkflowExecutionResponse
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
    api_instance = chatter_sdk.WorkflowsApi(api_client)
    workflow_id = 'workflow_id_example' # str | Workflow ID
    workflow_execution_request = chatter_sdk.WorkflowExecutionRequest() # WorkflowExecutionRequest | 

    try:
        # Execute Workflow
        api_response = await api_instance.execute_workflow_api_v1_workflows_workflows_definitions_workflow_id_execute_post(workflow_id, workflow_execution_request)
        print("The response of WorkflowsApi->execute_workflow_api_v1_workflows_workflows_definitions_workflow_id_execute_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowsApi->execute_workflow_api_v1_workflows_workflows_definitions_workflow_id_execute_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workflow_id** | **str**| Workflow ID | 
 **workflow_execution_request** | [**WorkflowExecutionRequest**](WorkflowExecutionRequest.md)|  | 

### Return type

[**WorkflowExecutionResponse**](WorkflowExecutionResponse.md)

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

# **get_supported_node_types_api_v1_workflows_workflows_node_types_get**
> List[NodeTypeResponse] get_supported_node_types_api_v1_workflows_workflows_node_types_get()

Get Supported Node Types

Get list of supported workflow node types.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.node_type_response import NodeTypeResponse
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
    api_instance = chatter_sdk.WorkflowsApi(api_client)

    try:
        # Get Supported Node Types
        api_response = await api_instance.get_supported_node_types_api_v1_workflows_workflows_node_types_get()
        print("The response of WorkflowsApi->get_supported_node_types_api_v1_workflows_workflows_node_types_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowsApi->get_supported_node_types_api_v1_workflows_workflows_node_types_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**List[NodeTypeResponse]**](NodeTypeResponse.md)

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

# **get_workflow_analytics_api_v1_workflows_workflows_definitions_workflow_id_analytics_get**
> WorkflowAnalyticsResponse get_workflow_analytics_api_v1_workflows_workflows_definitions_workflow_id_analytics_get(workflow_id)

Get Workflow Analytics

Get analytics for a specific workflow definition.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.workflow_analytics_response import WorkflowAnalyticsResponse
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
    api_instance = chatter_sdk.WorkflowsApi(api_client)
    workflow_id = 'workflow_id_example' # str | Workflow ID

    try:
        # Get Workflow Analytics
        api_response = await api_instance.get_workflow_analytics_api_v1_workflows_workflows_definitions_workflow_id_analytics_get(workflow_id)
        print("The response of WorkflowsApi->get_workflow_analytics_api_v1_workflows_workflows_definitions_workflow_id_analytics_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowsApi->get_workflow_analytics_api_v1_workflows_workflows_definitions_workflow_id_analytics_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workflow_id** | **str**| Workflow ID | 

### Return type

[**WorkflowAnalyticsResponse**](WorkflowAnalyticsResponse.md)

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

# **get_workflow_definition_api_v1_workflows_workflows_definitions_workflow_id_get**
> WorkflowDefinitionResponse get_workflow_definition_api_v1_workflows_workflows_definitions_workflow_id_get(workflow_id)

Get Workflow Definition

Get a specific workflow definition.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.workflow_definition_response import WorkflowDefinitionResponse
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
    api_instance = chatter_sdk.WorkflowsApi(api_client)
    workflow_id = 'workflow_id_example' # str | Workflow ID

    try:
        # Get Workflow Definition
        api_response = await api_instance.get_workflow_definition_api_v1_workflows_workflows_definitions_workflow_id_get(workflow_id)
        print("The response of WorkflowsApi->get_workflow_definition_api_v1_workflows_workflows_definitions_workflow_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowsApi->get_workflow_definition_api_v1_workflows_workflows_definitions_workflow_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workflow_id** | **str**| Workflow ID | 

### Return type

[**WorkflowDefinitionResponse**](WorkflowDefinitionResponse.md)

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

# **list_workflow_definitions_api_v1_workflows_workflows_definitions_get**
> WorkflowDefinitionsResponse list_workflow_definitions_api_v1_workflows_workflows_definitions_get()

List Workflow Definitions

List all workflow definitions for the current user.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.workflow_definitions_response import WorkflowDefinitionsResponse
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
    api_instance = chatter_sdk.WorkflowsApi(api_client)

    try:
        # List Workflow Definitions
        api_response = await api_instance.list_workflow_definitions_api_v1_workflows_workflows_definitions_get()
        print("The response of WorkflowsApi->list_workflow_definitions_api_v1_workflows_workflows_definitions_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowsApi->list_workflow_definitions_api_v1_workflows_workflows_definitions_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**WorkflowDefinitionsResponse**](WorkflowDefinitionsResponse.md)

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

# **list_workflow_executions_api_v1_workflows_workflows_definitions_workflow_id_executions_get**
> List[WorkflowExecutionResponse] list_workflow_executions_api_v1_workflows_workflows_definitions_workflow_id_executions_get(workflow_id)

List Workflow Executions

List executions for a workflow definition.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.workflow_execution_response import WorkflowExecutionResponse
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
    api_instance = chatter_sdk.WorkflowsApi(api_client)
    workflow_id = 'workflow_id_example' # str | Workflow ID

    try:
        # List Workflow Executions
        api_response = await api_instance.list_workflow_executions_api_v1_workflows_workflows_definitions_workflow_id_executions_get(workflow_id)
        print("The response of WorkflowsApi->list_workflow_executions_api_v1_workflows_workflows_definitions_workflow_id_executions_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowsApi->list_workflow_executions_api_v1_workflows_workflows_definitions_workflow_id_executions_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workflow_id** | **str**| Workflow ID | 

### Return type

[**List[WorkflowExecutionResponse]**](WorkflowExecutionResponse.md)

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

# **list_workflow_templates_api_v1_workflows_workflows_templates_get**
> ChatterSchemasWorkflowsWorkflowTemplatesResponse list_workflow_templates_api_v1_workflows_workflows_templates_get()

List Workflow Templates

List all workflow templates accessible to the current user.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.chatter_schemas_workflows_workflow_templates_response import ChatterSchemasWorkflowsWorkflowTemplatesResponse
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
    api_instance = chatter_sdk.WorkflowsApi(api_client)

    try:
        # List Workflow Templates
        api_response = await api_instance.list_workflow_templates_api_v1_workflows_workflows_templates_get()
        print("The response of WorkflowsApi->list_workflow_templates_api_v1_workflows_workflows_templates_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowsApi->list_workflow_templates_api_v1_workflows_workflows_templates_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**ChatterSchemasWorkflowsWorkflowTemplatesResponse**](ChatterSchemasWorkflowsWorkflowTemplatesResponse.md)

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

# **update_workflow_definition_api_v1_workflows_workflows_definitions_workflow_id_put**
> WorkflowDefinitionResponse update_workflow_definition_api_v1_workflows_workflows_definitions_workflow_id_put(workflow_id, workflow_definition_update)

Update Workflow Definition

Update a workflow definition.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.workflow_definition_response import WorkflowDefinitionResponse
from chatter_sdk.models.workflow_definition_update import WorkflowDefinitionUpdate
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
    api_instance = chatter_sdk.WorkflowsApi(api_client)
    workflow_id = 'workflow_id_example' # str | Workflow ID
    workflow_definition_update = chatter_sdk.WorkflowDefinitionUpdate() # WorkflowDefinitionUpdate | 

    try:
        # Update Workflow Definition
        api_response = await api_instance.update_workflow_definition_api_v1_workflows_workflows_definitions_workflow_id_put(workflow_id, workflow_definition_update)
        print("The response of WorkflowsApi->update_workflow_definition_api_v1_workflows_workflows_definitions_workflow_id_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowsApi->update_workflow_definition_api_v1_workflows_workflows_definitions_workflow_id_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workflow_id** | **str**| Workflow ID | 
 **workflow_definition_update** | [**WorkflowDefinitionUpdate**](WorkflowDefinitionUpdate.md)|  | 

### Return type

[**WorkflowDefinitionResponse**](WorkflowDefinitionResponse.md)

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

# **update_workflow_template_api_v1_workflows_workflows_templates_template_id_put**
> WorkflowTemplateResponse update_workflow_template_api_v1_workflows_workflows_templates_template_id_put(template_id, workflow_template_update)

Update Workflow Template

Update a workflow template.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.workflow_template_response import WorkflowTemplateResponse
from chatter_sdk.models.workflow_template_update import WorkflowTemplateUpdate
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
    api_instance = chatter_sdk.WorkflowsApi(api_client)
    template_id = 'template_id_example' # str | 
    workflow_template_update = chatter_sdk.WorkflowTemplateUpdate() # WorkflowTemplateUpdate | 

    try:
        # Update Workflow Template
        api_response = await api_instance.update_workflow_template_api_v1_workflows_workflows_templates_template_id_put(template_id, workflow_template_update)
        print("The response of WorkflowsApi->update_workflow_template_api_v1_workflows_workflows_templates_template_id_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowsApi->update_workflow_template_api_v1_workflows_workflows_templates_template_id_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **template_id** | **str**|  | 
 **workflow_template_update** | [**WorkflowTemplateUpdate**](WorkflowTemplateUpdate.md)|  | 

### Return type

[**WorkflowTemplateResponse**](WorkflowTemplateResponse.md)

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

# **validate_workflow_definition_api_v1_workflows_workflows_definitions_validate_post**
> WorkflowValidationResponse validate_workflow_definition_api_v1_workflows_workflows_definitions_validate_post(workflow_definition_create)

Validate Workflow Definition

Validate a workflow definition.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.workflow_definition_create import WorkflowDefinitionCreate
from chatter_sdk.models.workflow_validation_response import WorkflowValidationResponse
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
    api_instance = chatter_sdk.WorkflowsApi(api_client)
    workflow_definition_create = chatter_sdk.WorkflowDefinitionCreate() # WorkflowDefinitionCreate | 

    try:
        # Validate Workflow Definition
        api_response = await api_instance.validate_workflow_definition_api_v1_workflows_workflows_definitions_validate_post(workflow_definition_create)
        print("The response of WorkflowsApi->validate_workflow_definition_api_v1_workflows_workflows_definitions_validate_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowsApi->validate_workflow_definition_api_v1_workflows_workflows_definitions_validate_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workflow_definition_create** | [**WorkflowDefinitionCreate**](WorkflowDefinitionCreate.md)|  | 

### Return type

[**WorkflowValidationResponse**](WorkflowValidationResponse.md)

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

