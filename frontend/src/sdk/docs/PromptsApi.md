# PromptsApi

All URIs are relative to *http://localhost:8000*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**clonePromptApiV1PromptsPromptIdClonePost**](#clonepromptapiv1promptspromptidclonepost) | **POST** /api/v1/prompts/{prompt_id}/clone | Clone Prompt|
|[**createPromptApiV1PromptsPost**](#createpromptapiv1promptspost) | **POST** /api/v1/prompts/ | Create Prompt|
|[**deletePromptApiV1PromptsPromptIdDelete**](#deletepromptapiv1promptspromptiddelete) | **DELETE** /api/v1/prompts/{prompt_id} | Delete Prompt|
|[**getPromptApiV1PromptsPromptIdGet**](#getpromptapiv1promptspromptidget) | **GET** /api/v1/prompts/{prompt_id} | Get Prompt|
|[**getPromptStatsApiV1PromptsStatsOverviewGet**](#getpromptstatsapiv1promptsstatsoverviewget) | **GET** /api/v1/prompts/stats/overview | Get Prompt Stats|
|[**listPromptsApiV1PromptsGet**](#listpromptsapiv1promptsget) | **GET** /api/v1/prompts | List Prompts|
|[**testPromptApiV1PromptsPromptIdTestPost**](#testpromptapiv1promptspromptidtestpost) | **POST** /api/v1/prompts/{prompt_id}/test | Test Prompt|
|[**updatePromptApiV1PromptsPromptIdPut**](#updatepromptapiv1promptspromptidput) | **PUT** /api/v1/prompts/{prompt_id} | Update Prompt|

# **clonePromptApiV1PromptsPromptIdClonePost**
> PromptResponse clonePromptApiV1PromptsPromptIdClonePost(promptCloneRequest)

Clone an existing prompt.  Args:     prompt_id: Source prompt ID     clone_request: Clone request     current_user: Current authenticated user     prompt_service: Prompt service  Returns:     Cloned prompt information

### Example

```typescript
import {
    PromptsApi,
    Configuration,
    PromptCloneRequest
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new PromptsApi(configuration);

let promptId: string; // (default to undefined)
let promptCloneRequest: PromptCloneRequest; //

const { status, data } = await apiInstance.clonePromptApiV1PromptsPromptIdClonePost(
    promptId,
    promptCloneRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **promptCloneRequest** | **PromptCloneRequest**|  | |
| **promptId** | [**string**] |  | defaults to undefined|


### Return type

**PromptResponse**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createPromptApiV1PromptsPost**
> PromptResponse createPromptApiV1PromptsPost(promptCreate)

Create a new prompt.  Args:     prompt_data: Prompt creation data     current_user: Current authenticated user     prompt_service: Prompt service  Returns:     Created prompt information

### Example

```typescript
import {
    PromptsApi,
    Configuration,
    PromptCreate
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new PromptsApi(configuration);

let promptCreate: PromptCreate; //

const { status, data } = await apiInstance.createPromptApiV1PromptsPost(
    promptCreate
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **promptCreate** | **PromptCreate**|  | |


### Return type

**PromptResponse**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deletePromptApiV1PromptsPromptIdDelete**
> PromptDeleteResponse deletePromptApiV1PromptsPromptIdDelete()

Delete prompt.  Args:     prompt_id: Prompt ID     request: Delete request parameters     current_user: Current authenticated user     prompt_service: Prompt service  Returns:     Success message

### Example

```typescript
import {
    PromptsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new PromptsApi(configuration);

let promptId: string; // (default to undefined)

const { status, data } = await apiInstance.deletePromptApiV1PromptsPromptIdDelete(
    promptId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **promptId** | [**string**] |  | defaults to undefined|


### Return type

**PromptDeleteResponse**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getPromptApiV1PromptsPromptIdGet**
> PromptResponse getPromptApiV1PromptsPromptIdGet()

Get prompt details.  Args:     prompt_id: Prompt ID     request: Get request parameters     current_user: Current authenticated user     prompt_service: Prompt service  Returns:     Prompt information

### Example

```typescript
import {
    PromptsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new PromptsApi(configuration);

let promptId: string; // (default to undefined)

const { status, data } = await apiInstance.getPromptApiV1PromptsPromptIdGet(
    promptId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **promptId** | [**string**] |  | defaults to undefined|


### Return type

**PromptResponse**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getPromptStatsApiV1PromptsStatsOverviewGet**
> PromptStatsResponse getPromptStatsApiV1PromptsStatsOverviewGet()

Get prompt statistics.  Args:     current_user: Current authenticated user     prompt_service: Prompt service  Returns:     Prompt statistics

### Example

```typescript
import {
    PromptsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new PromptsApi(configuration);

const { status, data } = await apiInstance.getPromptStatsApiV1PromptsStatsOverviewGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**PromptStatsResponse**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listPromptsApiV1PromptsGet**
> PromptListResponse listPromptsApiV1PromptsGet()

List user\'s prompts.  Args:     prompt_type: Filter by prompt type     category: Filter by category     tags: Filter by tags     is_public: Filter by public status     is_chain: Filter by chain status     limit: Maximum number of results     offset: Number of results to skip     sort_by: Sort field     sort_order: Sort order (asc/desc)     current_user: Current authenticated user     prompt_service: Prompt service  Returns:     List of prompts with pagination info

### Example

```typescript
import {
    PromptsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new PromptsApi(configuration);

let promptType: PromptType; //Filter by prompt type (optional) (default to undefined)
let category: PromptCategory; //Filter by category (optional) (default to undefined)
let tags: Array<string>; //Filter by tags (optional) (default to undefined)
let isPublic: boolean; //Filter by public status (optional) (default to undefined)
let isChain: boolean; //Filter by chain status (optional) (default to undefined)
let limit: number; //Maximum number of results (optional) (default to 50)
let offset: number; //Number of results to skip (optional) (default to 0)
let sortBy: string; //Sort field (optional) (default to 'created_at')
let sortOrder: string; //Sort order (optional) (default to 'desc')

const { status, data } = await apiInstance.listPromptsApiV1PromptsGet(
    promptType,
    category,
    tags,
    isPublic,
    isChain,
    limit,
    offset,
    sortBy,
    sortOrder
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **promptType** | **PromptType** | Filter by prompt type | (optional) defaults to undefined|
| **category** | **PromptCategory** | Filter by category | (optional) defaults to undefined|
| **tags** | **Array&lt;string&gt;** | Filter by tags | (optional) defaults to undefined|
| **isPublic** | [**boolean**] | Filter by public status | (optional) defaults to undefined|
| **isChain** | [**boolean**] | Filter by chain status | (optional) defaults to undefined|
| **limit** | [**number**] | Maximum number of results | (optional) defaults to 50|
| **offset** | [**number**] | Number of results to skip | (optional) defaults to 0|
| **sortBy** | [**string**] | Sort field | (optional) defaults to 'created_at'|
| **sortOrder** | [**string**] | Sort order | (optional) defaults to 'desc'|


### Return type

**PromptListResponse**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **testPromptApiV1PromptsPromptIdTestPost**
> PromptTestResponse testPromptApiV1PromptsPromptIdTestPost(promptTestRequest)

Test prompt with given variables.  Args:     prompt_id: Prompt ID     test_request: Test request     current_user: Current authenticated user     prompt_service: Prompt service  Returns:     Test results

### Example

```typescript
import {
    PromptsApi,
    Configuration,
    PromptTestRequest
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new PromptsApi(configuration);

let promptId: string; // (default to undefined)
let promptTestRequest: PromptTestRequest; //

const { status, data } = await apiInstance.testPromptApiV1PromptsPromptIdTestPost(
    promptId,
    promptTestRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **promptTestRequest** | **PromptTestRequest**|  | |
| **promptId** | [**string**] |  | defaults to undefined|


### Return type

**PromptTestResponse**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updatePromptApiV1PromptsPromptIdPut**
> PromptResponse updatePromptApiV1PromptsPromptIdPut(promptUpdate)

Update prompt.  Args:     prompt_id: Prompt ID     update_data: Update data     current_user: Current authenticated user     prompt_service: Prompt service  Returns:     Updated prompt information

### Example

```typescript
import {
    PromptsApi,
    Configuration,
    PromptUpdate
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new PromptsApi(configuration);

let promptId: string; // (default to undefined)
let promptUpdate: PromptUpdate; //

const { status, data } = await apiInstance.updatePromptApiV1PromptsPromptIdPut(
    promptId,
    promptUpdate
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **promptUpdate** | **PromptUpdate**|  | |
| **promptId** | [**string**] |  | defaults to undefined|


### Return type

**PromptResponse**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

