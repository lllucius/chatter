# chatter_sdk.DefaultApi

All URIs are relative to *http://localhost:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**root_get**](DefaultApi.md#root_get) | **GET** / | Root


# **root_get**
> object root_get()

Root

Root endpoint.

### Example


```python
import chatter_sdk
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
    api_instance = chatter_sdk.DefaultApi(api_client)

    try:
        # Root
        api_response = await api_instance.root_get()
        print("The response of DefaultApi->root_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->root_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

