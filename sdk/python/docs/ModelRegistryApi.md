# chatter_sdk.ModelRegistryApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_embedding_space_api_v1_models_embedding_spaces_post**](ModelRegistryApi.md#create_embedding_space_api_v1_models_embedding_spaces_post) | **POST** /api/v1/models/embedding-spaces | Create Embedding Space
[**create_model_api_v1_models_models_post**](ModelRegistryApi.md#create_model_api_v1_models_models_post) | **POST** /api/v1/models/models | Create Model
[**create_provider_api_v1_models_providers_post**](ModelRegistryApi.md#create_provider_api_v1_models_providers_post) | **POST** /api/v1/models/providers | Create Provider
[**delete_embedding_space_api_v1_models_embedding_spaces_space_id_delete**](ModelRegistryApi.md#delete_embedding_space_api_v1_models_embedding_spaces_space_id_delete) | **DELETE** /api/v1/models/embedding-spaces/{space_id} | Delete Embedding Space
[**delete_model_api_v1_models_models_model_id_delete**](ModelRegistryApi.md#delete_model_api_v1_models_models_model_id_delete) | **DELETE** /api/v1/models/models/{model_id} | Delete Model
[**delete_provider_api_v1_models_providers_provider_id_delete**](ModelRegistryApi.md#delete_provider_api_v1_models_providers_provider_id_delete) | **DELETE** /api/v1/models/providers/{provider_id} | Delete Provider
[**get_default_embedding_space_api_v1_models_defaults_embedding_space_get**](ModelRegistryApi.md#get_default_embedding_space_api_v1_models_defaults_embedding_space_get) | **GET** /api/v1/models/defaults/embedding-space | Get Default Embedding Space
[**get_default_model_api_v1_models_defaults_model_model_type_get**](ModelRegistryApi.md#get_default_model_api_v1_models_defaults_model_model_type_get) | **GET** /api/v1/models/defaults/model/{model_type} | Get Default Model
[**get_default_provider_api_v1_models_defaults_provider_model_type_get**](ModelRegistryApi.md#get_default_provider_api_v1_models_defaults_provider_model_type_get) | **GET** /api/v1/models/defaults/provider/{model_type} | Get Default Provider
[**get_embedding_space_api_v1_models_embedding_spaces_space_id_get**](ModelRegistryApi.md#get_embedding_space_api_v1_models_embedding_spaces_space_id_get) | **GET** /api/v1/models/embedding-spaces/{space_id} | Get Embedding Space
[**get_model_api_v1_models_models_model_id_get**](ModelRegistryApi.md#get_model_api_v1_models_models_model_id_get) | **GET** /api/v1/models/models/{model_id} | Get Model
[**get_provider_api_v1_models_providers_provider_id_get**](ModelRegistryApi.md#get_provider_api_v1_models_providers_provider_id_get) | **GET** /api/v1/models/providers/{provider_id} | Get Provider
[**list_embedding_spaces_api_v1_models_embedding_spaces_get**](ModelRegistryApi.md#list_embedding_spaces_api_v1_models_embedding_spaces_get) | **GET** /api/v1/models/embedding-spaces | List Embedding Spaces
[**list_models_api_v1_models_models_get**](ModelRegistryApi.md#list_models_api_v1_models_models_get) | **GET** /api/v1/models/models | List Models
[**list_providers_api_v1_models_providers_get**](ModelRegistryApi.md#list_providers_api_v1_models_providers_get) | **GET** /api/v1/models/providers | List Providers
[**set_default_embedding_space_api_v1_models_embedding_spaces_space_id_set_default_post**](ModelRegistryApi.md#set_default_embedding_space_api_v1_models_embedding_spaces_space_id_set_default_post) | **POST** /api/v1/models/embedding-spaces/{space_id}/set-default | Set Default Embedding Space
[**set_default_model_api_v1_models_models_model_id_set_default_post**](ModelRegistryApi.md#set_default_model_api_v1_models_models_model_id_set_default_post) | **POST** /api/v1/models/models/{model_id}/set-default | Set Default Model
[**set_default_provider_api_v1_models_providers_provider_id_set_default_post**](ModelRegistryApi.md#set_default_provider_api_v1_models_providers_provider_id_set_default_post) | **POST** /api/v1/models/providers/{provider_id}/set-default | Set Default Provider
[**update_embedding_space_api_v1_models_embedding_spaces_space_id_put**](ModelRegistryApi.md#update_embedding_space_api_v1_models_embedding_spaces_space_id_put) | **PUT** /api/v1/models/embedding-spaces/{space_id} | Update Embedding Space
[**update_model_api_v1_models_models_model_id_put**](ModelRegistryApi.md#update_model_api_v1_models_models_model_id_put) | **PUT** /api/v1/models/models/{model_id} | Update Model
[**update_provider_api_v1_models_providers_provider_id_put**](ModelRegistryApi.md#update_provider_api_v1_models_providers_provider_id_put) | **PUT** /api/v1/models/providers/{provider_id} | Update Provider


# **create_embedding_space_api_v1_models_embedding_spaces_post**
> EmbeddingSpaceWithModel create_embedding_space_api_v1_models_embedding_spaces_post(embedding_space_create)

Create Embedding Space

Create a new embedding space with backing table and index.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.embedding_space_create import EmbeddingSpaceCreate
from chatter_sdk.models.embedding_space_with_model import EmbeddingSpaceWithModel
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
    api_instance = chatter_sdk.ModelRegistryApi(api_client)
    embedding_space_create = chatter_sdk.EmbeddingSpaceCreate() # EmbeddingSpaceCreate | 

    try:
        # Create Embedding Space
        api_response = await api_instance.create_embedding_space_api_v1_models_embedding_spaces_post(embedding_space_create)
        print("The response of ModelRegistryApi->create_embedding_space_api_v1_models_embedding_spaces_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelRegistryApi->create_embedding_space_api_v1_models_embedding_spaces_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **embedding_space_create** | [**EmbeddingSpaceCreate**](EmbeddingSpaceCreate.md)|  | 

### Return type

[**EmbeddingSpaceWithModel**](EmbeddingSpaceWithModel.md)

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

# **create_model_api_v1_models_models_post**
> ModelDefWithProvider create_model_api_v1_models_models_post(model_def_create)

Create Model

Create a new model definition.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.model_def_create import ModelDefCreate
from chatter_sdk.models.model_def_with_provider import ModelDefWithProvider
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
    api_instance = chatter_sdk.ModelRegistryApi(api_client)
    model_def_create = chatter_sdk.ModelDefCreate() # ModelDefCreate | 

    try:
        # Create Model
        api_response = await api_instance.create_model_api_v1_models_models_post(model_def_create)
        print("The response of ModelRegistryApi->create_model_api_v1_models_models_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelRegistryApi->create_model_api_v1_models_models_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_def_create** | [**ModelDefCreate**](ModelDefCreate.md)|  | 

### Return type

[**ModelDefWithProvider**](ModelDefWithProvider.md)

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

# **create_provider_api_v1_models_providers_post**
> Provider create_provider_api_v1_models_providers_post(provider_create)

Create Provider

Create a new provider.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.provider import Provider
from chatter_sdk.models.provider_create import ProviderCreate
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
    api_instance = chatter_sdk.ModelRegistryApi(api_client)
    provider_create = chatter_sdk.ProviderCreate() # ProviderCreate | 

    try:
        # Create Provider
        api_response = await api_instance.create_provider_api_v1_models_providers_post(provider_create)
        print("The response of ModelRegistryApi->create_provider_api_v1_models_providers_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelRegistryApi->create_provider_api_v1_models_providers_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **provider_create** | [**ProviderCreate**](ProviderCreate.md)|  | 

### Return type

[**Provider**](Provider.md)

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

# **delete_embedding_space_api_v1_models_embedding_spaces_space_id_delete**
> EmbeddingSpaceDeleteResponse delete_embedding_space_api_v1_models_embedding_spaces_space_id_delete(space_id)

Delete Embedding Space

Delete an embedding space (does not drop the table).

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.embedding_space_delete_response import EmbeddingSpaceDeleteResponse
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
    api_instance = chatter_sdk.ModelRegistryApi(api_client)
    space_id = 'space_id_example' # str | 

    try:
        # Delete Embedding Space
        api_response = await api_instance.delete_embedding_space_api_v1_models_embedding_spaces_space_id_delete(space_id)
        print("The response of ModelRegistryApi->delete_embedding_space_api_v1_models_embedding_spaces_space_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelRegistryApi->delete_embedding_space_api_v1_models_embedding_spaces_space_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **space_id** | **str**|  | 

### Return type

[**EmbeddingSpaceDeleteResponse**](EmbeddingSpaceDeleteResponse.md)

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

# **delete_model_api_v1_models_models_model_id_delete**
> ModelDeleteResponse delete_model_api_v1_models_models_model_id_delete(model_id)

Delete Model

Delete a model definition and its dependent embedding spaces.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.model_delete_response import ModelDeleteResponse
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
    api_instance = chatter_sdk.ModelRegistryApi(api_client)
    model_id = 'model_id_example' # str | 

    try:
        # Delete Model
        api_response = await api_instance.delete_model_api_v1_models_models_model_id_delete(model_id)
        print("The response of ModelRegistryApi->delete_model_api_v1_models_models_model_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelRegistryApi->delete_model_api_v1_models_models_model_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_id** | **str**|  | 

### Return type

[**ModelDeleteResponse**](ModelDeleteResponse.md)

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

# **delete_provider_api_v1_models_providers_provider_id_delete**
> ProviderDeleteResponse delete_provider_api_v1_models_providers_provider_id_delete(provider_id)

Delete Provider

Delete a provider and all its dependent models and embedding spaces.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.provider_delete_response import ProviderDeleteResponse
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
    api_instance = chatter_sdk.ModelRegistryApi(api_client)
    provider_id = 'provider_id_example' # str | 

    try:
        # Delete Provider
        api_response = await api_instance.delete_provider_api_v1_models_providers_provider_id_delete(provider_id)
        print("The response of ModelRegistryApi->delete_provider_api_v1_models_providers_provider_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelRegistryApi->delete_provider_api_v1_models_providers_provider_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **provider_id** | **str**|  | 

### Return type

[**ProviderDeleteResponse**](ProviderDeleteResponse.md)

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

# **get_default_embedding_space_api_v1_models_defaults_embedding_space_get**
> EmbeddingSpaceWithModel get_default_embedding_space_api_v1_models_defaults_embedding_space_get()

Get Default Embedding Space

Get the default embedding space.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.embedding_space_with_model import EmbeddingSpaceWithModel
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
    api_instance = chatter_sdk.ModelRegistryApi(api_client)

    try:
        # Get Default Embedding Space
        api_response = await api_instance.get_default_embedding_space_api_v1_models_defaults_embedding_space_get()
        print("The response of ModelRegistryApi->get_default_embedding_space_api_v1_models_defaults_embedding_space_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelRegistryApi->get_default_embedding_space_api_v1_models_defaults_embedding_space_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**EmbeddingSpaceWithModel**](EmbeddingSpaceWithModel.md)

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

# **get_default_model_api_v1_models_defaults_model_model_type_get**
> ModelDefWithProvider get_default_model_api_v1_models_defaults_model_model_type_get(model_type)

Get Default Model

Get the default model for a type.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.model_def_with_provider import ModelDefWithProvider
from chatter_sdk.models.model_type import ModelType
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
    api_instance = chatter_sdk.ModelRegistryApi(api_client)
    model_type = chatter_sdk.ModelType() # ModelType | 

    try:
        # Get Default Model
        api_response = await api_instance.get_default_model_api_v1_models_defaults_model_model_type_get(model_type)
        print("The response of ModelRegistryApi->get_default_model_api_v1_models_defaults_model_model_type_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelRegistryApi->get_default_model_api_v1_models_defaults_model_model_type_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_type** | [**ModelType**](.md)|  | 

### Return type

[**ModelDefWithProvider**](ModelDefWithProvider.md)

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

# **get_default_provider_api_v1_models_defaults_provider_model_type_get**
> Provider get_default_provider_api_v1_models_defaults_provider_model_type_get(model_type)

Get Default Provider

Get the default provider for a model type.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.model_type import ModelType
from chatter_sdk.models.provider import Provider
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
    api_instance = chatter_sdk.ModelRegistryApi(api_client)
    model_type = chatter_sdk.ModelType() # ModelType | 

    try:
        # Get Default Provider
        api_response = await api_instance.get_default_provider_api_v1_models_defaults_provider_model_type_get(model_type)
        print("The response of ModelRegistryApi->get_default_provider_api_v1_models_defaults_provider_model_type_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelRegistryApi->get_default_provider_api_v1_models_defaults_provider_model_type_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_type** | [**ModelType**](.md)|  | 

### Return type

[**Provider**](Provider.md)

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

# **get_embedding_space_api_v1_models_embedding_spaces_space_id_get**
> EmbeddingSpaceWithModel get_embedding_space_api_v1_models_embedding_spaces_space_id_get(space_id)

Get Embedding Space

Get a specific embedding space.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.embedding_space_with_model import EmbeddingSpaceWithModel
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
    api_instance = chatter_sdk.ModelRegistryApi(api_client)
    space_id = 'space_id_example' # str | 

    try:
        # Get Embedding Space
        api_response = await api_instance.get_embedding_space_api_v1_models_embedding_spaces_space_id_get(space_id)
        print("The response of ModelRegistryApi->get_embedding_space_api_v1_models_embedding_spaces_space_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelRegistryApi->get_embedding_space_api_v1_models_embedding_spaces_space_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **space_id** | **str**|  | 

### Return type

[**EmbeddingSpaceWithModel**](EmbeddingSpaceWithModel.md)

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

# **get_model_api_v1_models_models_model_id_get**
> ModelDefWithProvider get_model_api_v1_models_models_model_id_get(model_id)

Get Model

Get a specific model definition.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.model_def_with_provider import ModelDefWithProvider
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
    api_instance = chatter_sdk.ModelRegistryApi(api_client)
    model_id = 'model_id_example' # str | 

    try:
        # Get Model
        api_response = await api_instance.get_model_api_v1_models_models_model_id_get(model_id)
        print("The response of ModelRegistryApi->get_model_api_v1_models_models_model_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelRegistryApi->get_model_api_v1_models_models_model_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_id** | **str**|  | 

### Return type

[**ModelDefWithProvider**](ModelDefWithProvider.md)

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

# **get_provider_api_v1_models_providers_provider_id_get**
> Provider get_provider_api_v1_models_providers_provider_id_get(provider_id)

Get Provider

Get a specific provider.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.provider import Provider
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
    api_instance = chatter_sdk.ModelRegistryApi(api_client)
    provider_id = 'provider_id_example' # str | 

    try:
        # Get Provider
        api_response = await api_instance.get_provider_api_v1_models_providers_provider_id_get(provider_id)
        print("The response of ModelRegistryApi->get_provider_api_v1_models_providers_provider_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelRegistryApi->get_provider_api_v1_models_providers_provider_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **provider_id** | **str**|  | 

### Return type

[**Provider**](Provider.md)

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

# **list_embedding_spaces_api_v1_models_embedding_spaces_get**
> EmbeddingSpaceList list_embedding_spaces_api_v1_models_embedding_spaces_get(model_id=model_id, page=page, per_page=per_page, active_only=active_only)

List Embedding Spaces

List all embedding spaces.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.embedding_space_list import EmbeddingSpaceList
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
    api_instance = chatter_sdk.ModelRegistryApi(api_client)
    model_id = 'model_id_example' # str | Filter by model ID (optional)
    page = 1 # int | Page number (optional) (default to 1)
    per_page = 20 # int | Items per page (optional) (default to 20)
    active_only = True # bool | Show only active spaces (optional) (default to True)

    try:
        # List Embedding Spaces
        api_response = await api_instance.list_embedding_spaces_api_v1_models_embedding_spaces_get(model_id=model_id, page=page, per_page=per_page, active_only=active_only)
        print("The response of ModelRegistryApi->list_embedding_spaces_api_v1_models_embedding_spaces_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelRegistryApi->list_embedding_spaces_api_v1_models_embedding_spaces_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_id** | **str**| Filter by model ID | [optional] 
 **page** | **int**| Page number | [optional] [default to 1]
 **per_page** | **int**| Items per page | [optional] [default to 20]
 **active_only** | **bool**| Show only active spaces | [optional] [default to True]

### Return type

[**EmbeddingSpaceList**](EmbeddingSpaceList.md)

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

# **list_models_api_v1_models_models_get**
> ModelDefList list_models_api_v1_models_models_get(provider_id=provider_id, model_type=model_type, page=page, per_page=per_page, active_only=active_only)

List Models

List all model definitions.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.model_def_list import ModelDefList
from chatter_sdk.models.model_type import ModelType
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
    api_instance = chatter_sdk.ModelRegistryApi(api_client)
    provider_id = 'provider_id_example' # str | Filter by provider ID (optional)
    model_type = chatter_sdk.ModelType() # ModelType | Filter by model type (optional)
    page = 1 # int | Page number (optional) (default to 1)
    per_page = 20 # int | Items per page (optional) (default to 20)
    active_only = True # bool | Show only active models (optional) (default to True)

    try:
        # List Models
        api_response = await api_instance.list_models_api_v1_models_models_get(provider_id=provider_id, model_type=model_type, page=page, per_page=per_page, active_only=active_only)
        print("The response of ModelRegistryApi->list_models_api_v1_models_models_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelRegistryApi->list_models_api_v1_models_models_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **provider_id** | **str**| Filter by provider ID | [optional] 
 **model_type** | [**ModelType**](.md)| Filter by model type | [optional] 
 **page** | **int**| Page number | [optional] [default to 1]
 **per_page** | **int**| Items per page | [optional] [default to 20]
 **active_only** | **bool**| Show only active models | [optional] [default to True]

### Return type

[**ModelDefList**](ModelDefList.md)

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

# **list_providers_api_v1_models_providers_get**
> ProviderList list_providers_api_v1_models_providers_get(page=page, per_page=per_page, active_only=active_only)

List Providers

List all providers.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.provider_list import ProviderList
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
    api_instance = chatter_sdk.ModelRegistryApi(api_client)
    page = 1 # int | Page number (optional) (default to 1)
    per_page = 20 # int | Items per page (optional) (default to 20)
    active_only = True # bool | Show only active providers (optional) (default to True)

    try:
        # List Providers
        api_response = await api_instance.list_providers_api_v1_models_providers_get(page=page, per_page=per_page, active_only=active_only)
        print("The response of ModelRegistryApi->list_providers_api_v1_models_providers_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelRegistryApi->list_providers_api_v1_models_providers_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page** | **int**| Page number | [optional] [default to 1]
 **per_page** | **int**| Items per page | [optional] [default to 20]
 **active_only** | **bool**| Show only active providers | [optional] [default to True]

### Return type

[**ProviderList**](ProviderList.md)

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

# **set_default_embedding_space_api_v1_models_embedding_spaces_space_id_set_default_post**
> EmbeddingSpaceDefaultResponse set_default_embedding_space_api_v1_models_embedding_spaces_space_id_set_default_post(space_id)

Set Default Embedding Space

Set an embedding space as default.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.embedding_space_default_response import EmbeddingSpaceDefaultResponse
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
    api_instance = chatter_sdk.ModelRegistryApi(api_client)
    space_id = 'space_id_example' # str | 

    try:
        # Set Default Embedding Space
        api_response = await api_instance.set_default_embedding_space_api_v1_models_embedding_spaces_space_id_set_default_post(space_id)
        print("The response of ModelRegistryApi->set_default_embedding_space_api_v1_models_embedding_spaces_space_id_set_default_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelRegistryApi->set_default_embedding_space_api_v1_models_embedding_spaces_space_id_set_default_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **space_id** | **str**|  | 

### Return type

[**EmbeddingSpaceDefaultResponse**](EmbeddingSpaceDefaultResponse.md)

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

# **set_default_model_api_v1_models_models_model_id_set_default_post**
> ModelDefaultResponse set_default_model_api_v1_models_models_model_id_set_default_post(model_id)

Set Default Model

Set a model as default for its type.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.model_default_response import ModelDefaultResponse
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
    api_instance = chatter_sdk.ModelRegistryApi(api_client)
    model_id = 'model_id_example' # str | 

    try:
        # Set Default Model
        api_response = await api_instance.set_default_model_api_v1_models_models_model_id_set_default_post(model_id)
        print("The response of ModelRegistryApi->set_default_model_api_v1_models_models_model_id_set_default_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelRegistryApi->set_default_model_api_v1_models_models_model_id_set_default_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_id** | **str**|  | 

### Return type

[**ModelDefaultResponse**](ModelDefaultResponse.md)

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

# **set_default_provider_api_v1_models_providers_provider_id_set_default_post**
> ProviderDefaultResponse set_default_provider_api_v1_models_providers_provider_id_set_default_post(provider_id, default_provider)

Set Default Provider

Set a provider as default for a model type.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.default_provider import DefaultProvider
from chatter_sdk.models.provider_default_response import ProviderDefaultResponse
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
    api_instance = chatter_sdk.ModelRegistryApi(api_client)
    provider_id = 'provider_id_example' # str | 
    default_provider = chatter_sdk.DefaultProvider() # DefaultProvider | 

    try:
        # Set Default Provider
        api_response = await api_instance.set_default_provider_api_v1_models_providers_provider_id_set_default_post(provider_id, default_provider)
        print("The response of ModelRegistryApi->set_default_provider_api_v1_models_providers_provider_id_set_default_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelRegistryApi->set_default_provider_api_v1_models_providers_provider_id_set_default_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **provider_id** | **str**|  | 
 **default_provider** | [**DefaultProvider**](DefaultProvider.md)|  | 

### Return type

[**ProviderDefaultResponse**](ProviderDefaultResponse.md)

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

# **update_embedding_space_api_v1_models_embedding_spaces_space_id_put**
> EmbeddingSpaceWithModel update_embedding_space_api_v1_models_embedding_spaces_space_id_put(space_id, embedding_space_update)

Update Embedding Space

Update an embedding space.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.embedding_space_update import EmbeddingSpaceUpdate
from chatter_sdk.models.embedding_space_with_model import EmbeddingSpaceWithModel
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
    api_instance = chatter_sdk.ModelRegistryApi(api_client)
    space_id = 'space_id_example' # str | 
    embedding_space_update = chatter_sdk.EmbeddingSpaceUpdate() # EmbeddingSpaceUpdate | 

    try:
        # Update Embedding Space
        api_response = await api_instance.update_embedding_space_api_v1_models_embedding_spaces_space_id_put(space_id, embedding_space_update)
        print("The response of ModelRegistryApi->update_embedding_space_api_v1_models_embedding_spaces_space_id_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelRegistryApi->update_embedding_space_api_v1_models_embedding_spaces_space_id_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **space_id** | **str**|  | 
 **embedding_space_update** | [**EmbeddingSpaceUpdate**](EmbeddingSpaceUpdate.md)|  | 

### Return type

[**EmbeddingSpaceWithModel**](EmbeddingSpaceWithModel.md)

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

# **update_model_api_v1_models_models_model_id_put**
> ModelDefWithProvider update_model_api_v1_models_models_model_id_put(model_id, model_def_update)

Update Model

Update a model definition.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.model_def_update import ModelDefUpdate
from chatter_sdk.models.model_def_with_provider import ModelDefWithProvider
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
    api_instance = chatter_sdk.ModelRegistryApi(api_client)
    model_id = 'model_id_example' # str | 
    model_def_update = chatter_sdk.ModelDefUpdate() # ModelDefUpdate | 

    try:
        # Update Model
        api_response = await api_instance.update_model_api_v1_models_models_model_id_put(model_id, model_def_update)
        print("The response of ModelRegistryApi->update_model_api_v1_models_models_model_id_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelRegistryApi->update_model_api_v1_models_models_model_id_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_id** | **str**|  | 
 **model_def_update** | [**ModelDefUpdate**](ModelDefUpdate.md)|  | 

### Return type

[**ModelDefWithProvider**](ModelDefWithProvider.md)

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

# **update_provider_api_v1_models_providers_provider_id_put**
> Provider update_provider_api_v1_models_providers_provider_id_put(provider_id, provider_update)

Update Provider

Update a provider.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.provider import Provider
from chatter_sdk.models.provider_update import ProviderUpdate
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
    api_instance = chatter_sdk.ModelRegistryApi(api_client)
    provider_id = 'provider_id_example' # str | 
    provider_update = chatter_sdk.ProviderUpdate() # ProviderUpdate | 

    try:
        # Update Provider
        api_response = await api_instance.update_provider_api_v1_models_providers_provider_id_put(provider_id, provider_update)
        print("The response of ModelRegistryApi->update_provider_api_v1_models_providers_provider_id_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelRegistryApi->update_provider_api_v1_models_providers_provider_id_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **provider_id** | **str**|  | 
 **provider_update** | [**ProviderUpdate**](ProviderUpdate.md)|  | 

### Return type

[**Provider**](Provider.md)

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

