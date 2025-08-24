# WebhooksApi

All URIs are relative to *http://localhost:8000*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**createWebhookApiV1WebhooksPost**](#createwebhookapiv1webhookspost) | **POST** /api/v1/webhooks/ | Create Webhook|
|[**deleteWebhookApiV1WebhooksWebhookIdDelete**](#deletewebhookapiv1webhookswebhookiddelete) | **DELETE** /api/v1/webhooks/{webhook_id} | Delete Webhook|
|[**getWebhookApiV1WebhooksWebhookIdGet**](#getwebhookapiv1webhookswebhookidget) | **GET** /api/v1/webhooks/{webhook_id} | Get Webhook|
|[**listWebhookDeliveriesApiV1WebhooksDeliveriesListGet**](#listwebhookdeliveriesapiv1webhooksdeliverieslistget) | **GET** /api/v1/webhooks/deliveries/list | List Webhook Deliveries|
|[**listWebhookEventsApiV1WebhooksEventsListGet**](#listwebhookeventsapiv1webhookseventslistget) | **GET** /api/v1/webhooks/events/list | List Webhook Events|
|[**listWebhooksApiV1WebhooksGet**](#listwebhooksapiv1webhooksget) | **GET** /api/v1/webhooks/ | List Webhooks|
|[**testWebhookApiV1WebhooksWebhookIdTestPost**](#testwebhookapiv1webhookswebhookidtestpost) | **POST** /api/v1/webhooks/{webhook_id}/test | Test Webhook|
|[**updateWebhookApiV1WebhooksWebhookIdPut**](#updatewebhookapiv1webhookswebhookidput) | **PUT** /api/v1/webhooks/{webhook_id} | Update Webhook|

# **createWebhookApiV1WebhooksPost**
> WebhookResponse createWebhookApiV1WebhooksPost(webhookCreateRequest)

Create a new webhook endpoint.  Args:     webhook_data: Webhook creation data     current_user: Current authenticated user     webhook_manager: Webhook manager instance  Returns:     Created webhook data

### Example

```typescript
import {
    WebhooksApi,
    Configuration,
    WebhookCreateRequest
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new WebhooksApi(configuration);

let webhookCreateRequest: WebhookCreateRequest; //

const { status, data } = await apiInstance.createWebhookApiV1WebhooksPost(
    webhookCreateRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **webhookCreateRequest** | **WebhookCreateRequest**|  | |


### Return type

**WebhookResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteWebhookApiV1WebhooksWebhookIdDelete**
> WebhookDeleteResponse deleteWebhookApiV1WebhooksWebhookIdDelete()

Delete a webhook endpoint.  Args:     webhook_id: Webhook ID     current_user: Current authenticated user     webhook_manager: Webhook manager instance  Returns:     Deletion result

### Example

```typescript
import {
    WebhooksApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new WebhooksApi(configuration);

let webhookId: string; // (default to undefined)

const { status, data } = await apiInstance.deleteWebhookApiV1WebhooksWebhookIdDelete(
    webhookId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **webhookId** | [**string**] |  | defaults to undefined|


### Return type

**WebhookDeleteResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getWebhookApiV1WebhooksWebhookIdGet**
> WebhookResponse getWebhookApiV1WebhooksWebhookIdGet()

Get webhook endpoint by ID.  Args:     webhook_id: Webhook ID     current_user: Current authenticated user     webhook_manager: Webhook manager instance  Returns:     Webhook endpoint data

### Example

```typescript
import {
    WebhooksApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new WebhooksApi(configuration);

let webhookId: string; // (default to undefined)

const { status, data } = await apiInstance.getWebhookApiV1WebhooksWebhookIdGet(
    webhookId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **webhookId** | [**string**] |  | defaults to undefined|


### Return type

**WebhookResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listWebhookDeliveriesApiV1WebhooksDeliveriesListGet**
> WebhookDeliveriesListResponse listWebhookDeliveriesApiV1WebhooksDeliveriesListGet()

List webhook delivery attempts.  Args:     webhook_id: Optional webhook ID to filter by     current_user: Current authenticated user     webhook_manager: Webhook manager instance  Returns:     List of webhook deliveries

### Example

```typescript
import {
    WebhooksApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new WebhooksApi(configuration);

let webhookId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listWebhookDeliveriesApiV1WebhooksDeliveriesListGet(
    webhookId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **webhookId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**WebhookDeliveriesListResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listWebhookEventsApiV1WebhooksEventsListGet**
> WebhookEventsListResponse listWebhookEventsApiV1WebhooksEventsListGet()

List recent webhook events.  Args:     current_user: Current authenticated user     webhook_manager: Webhook manager instance  Returns:     List of recent webhook events

### Example

```typescript
import {
    WebhooksApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new WebhooksApi(configuration);

const { status, data } = await apiInstance.listWebhookEventsApiV1WebhooksEventsListGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**WebhookEventsListResponse**

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

# **listWebhooksApiV1WebhooksGet**
> WebhookListResponse listWebhooksApiV1WebhooksGet()

List webhook endpoints with optional filtering.  Args:     request: List request parameters     current_user: Current authenticated user     webhook_manager: Webhook manager instance  Returns:     List of webhook endpoints

### Example

```typescript
import {
    WebhooksApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new WebhooksApi(configuration);

let active: boolean; // (optional) (default to undefined)
let eventType: WebhookEventType; // (optional) (default to undefined)

const { status, data } = await apiInstance.listWebhooksApiV1WebhooksGet(
    active,
    eventType
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **active** | [**boolean**] |  | (optional) defaults to undefined|
| **eventType** | **WebhookEventType** |  | (optional) defaults to undefined|


### Return type

**WebhookListResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **testWebhookApiV1WebhooksWebhookIdTestPost**
> WebhookTestResponse testWebhookApiV1WebhooksWebhookIdTestPost()

Test a webhook endpoint by sending a test event.  Args:     webhook_id: Webhook ID     current_user: Current authenticated user     webhook_manager: Webhook manager instance  Returns:     Test result

### Example

```typescript
import {
    WebhooksApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new WebhooksApi(configuration);

let webhookId: string; // (default to undefined)

const { status, data } = await apiInstance.testWebhookApiV1WebhooksWebhookIdTestPost(
    webhookId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **webhookId** | [**string**] |  | defaults to undefined|


### Return type

**WebhookTestResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateWebhookApiV1WebhooksWebhookIdPut**
> WebhookResponse updateWebhookApiV1WebhooksWebhookIdPut(webhookUpdateRequest)

Update a webhook endpoint.  Args:     webhook_id: Webhook ID     webhook_data: Webhook update data     current_user: Current authenticated user     webhook_manager: Webhook manager instance  Returns:     Updated webhook data

### Example

```typescript
import {
    WebhooksApi,
    Configuration,
    WebhookUpdateRequest
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new WebhooksApi(configuration);

let webhookId: string; // (default to undefined)
let webhookUpdateRequest: WebhookUpdateRequest; //

const { status, data } = await apiInstance.updateWebhookApiV1WebhooksWebhookIdPut(
    webhookId,
    webhookUpdateRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **webhookUpdateRequest** | **WebhookUpdateRequest**|  | |
| **webhookId** | [**string**] |  | defaults to undefined|


### Return type

**WebhookResponse**

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

