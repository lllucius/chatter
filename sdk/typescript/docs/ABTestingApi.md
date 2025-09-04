# ABTestingApi

All URIs are relative to *http://localhost:8000*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**completeAbTestApiV1AbTestsTestIdCompletePost**](#completeabtestapiv1abteststestidcompletepost) | **POST** /api/v1/ab-tests/{test_id}/complete | Complete Ab Test|
|[**createAbTestApiV1AbTestsPost**](#createabtestapiv1abtestspost) | **POST** /api/v1/ab-tests/ | Create Ab Test|
|[**deleteAbTestApiV1AbTestsTestIdDelete**](#deleteabtestapiv1abteststestiddelete) | **DELETE** /api/v1/ab-tests/{test_id} | Delete Ab Test|
|[**endAbTestApiV1AbTestsTestIdEndPost**](#endabtestapiv1abteststestidendpost) | **POST** /api/v1/ab-tests/{test_id}/end | End Ab Test|
|[**getAbTestApiV1AbTestsTestIdGet**](#getabtestapiv1abteststestidget) | **GET** /api/v1/ab-tests/{test_id} | Get Ab Test|
|[**getAbTestMetricsApiV1AbTestsTestIdMetricsGet**](#getabtestmetricsapiv1abteststestidmetricsget) | **GET** /api/v1/ab-tests/{test_id}/metrics | Get Ab Test Metrics|
|[**getAbTestPerformanceApiV1AbTestsTestIdPerformanceGet**](#getabtestperformanceapiv1abteststestidperformanceget) | **GET** /api/v1/ab-tests/{test_id}/performance | Get Ab Test Performance|
|[**getAbTestRecommendationsApiV1AbTestsTestIdRecommendationsGet**](#getabtestrecommendationsapiv1abteststestidrecommendationsget) | **GET** /api/v1/ab-tests/{test_id}/recommendations | Get Ab Test Recommendations|
|[**getAbTestResultsApiV1AbTestsTestIdResultsGet**](#getabtestresultsapiv1abteststestidresultsget) | **GET** /api/v1/ab-tests/{test_id}/results | Get Ab Test Results|
|[**listAbTestsApiV1AbTestsGet**](#listabtestsapiv1abtestsget) | **GET** /api/v1/ab-tests/ | List Ab Tests|
|[**pauseAbTestApiV1AbTestsTestIdPausePost**](#pauseabtestapiv1abteststestidpausepost) | **POST** /api/v1/ab-tests/{test_id}/pause | Pause Ab Test|
|[**startAbTestApiV1AbTestsTestIdStartPost**](#startabtestapiv1abteststestidstartpost) | **POST** /api/v1/ab-tests/{test_id}/start | Start Ab Test|
|[**updateAbTestApiV1AbTestsTestIdPut**](#updateabtestapiv1abteststestidput) | **PUT** /api/v1/ab-tests/{test_id} | Update Ab Test|

# **completeAbTestApiV1AbTestsTestIdCompletePost**
> ABTestActionResponse completeAbTestApiV1AbTestsTestIdCompletePost()

Complete an A/B test.  Args:     test_id: Test ID     current_user: Current authenticated user     ab_test_manager: A/B test manager instance  Returns:     Action result

### Example

```typescript
import {
    ABTestingApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ABTestingApi(configuration);

let testId: string; // (default to undefined)

const { status, data } = await apiInstance.completeAbTestApiV1AbTestsTestIdCompletePost(
    testId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **testId** | [**string**] |  | defaults to undefined|


### Return type

**ABTestActionResponse**

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

# **createAbTestApiV1AbTestsPost**
> ABTestResponse createAbTestApiV1AbTestsPost(aBTestCreateRequest)

Create a new A/B test.  Args:     test_data: A/B test creation data     current_user: Current authenticated user     ab_test_manager: A/B test manager instance  Returns:     Created test data

### Example

```typescript
import {
    ABTestingApi,
    Configuration,
    ABTestCreateRequest
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ABTestingApi(configuration);

let aBTestCreateRequest: ABTestCreateRequest; //

const { status, data } = await apiInstance.createAbTestApiV1AbTestsPost(
    aBTestCreateRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **aBTestCreateRequest** | **ABTestCreateRequest**|  | |


### Return type

**ABTestResponse**

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

# **deleteAbTestApiV1AbTestsTestIdDelete**
> ABTestDeleteResponse deleteAbTestApiV1AbTestsTestIdDelete()

Delete an A/B test.  Args:     test_id: Test ID     current_user: Current authenticated user     ab_test_manager: A/B test manager instance  Returns:     Deletion result

### Example

```typescript
import {
    ABTestingApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ABTestingApi(configuration);

let testId: string; // (default to undefined)

const { status, data } = await apiInstance.deleteAbTestApiV1AbTestsTestIdDelete(
    testId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **testId** | [**string**] |  | defaults to undefined|


### Return type

**ABTestDeleteResponse**

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

# **endAbTestApiV1AbTestsTestIdEndPost**
> ABTestActionResponse endAbTestApiV1AbTestsTestIdEndPost()

End A/B test and declare winner.  Args:     test_id: A/B test ID     winner_variant: Winning variant identifier     current_user: Current authenticated user     ab_test_manager: A/B test manager instance  Returns:     Action response

### Example

```typescript
import {
    ABTestingApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ABTestingApi(configuration);

let testId: string; // (default to undefined)
let winnerVariant: string; // (default to undefined)

const { status, data } = await apiInstance.endAbTestApiV1AbTestsTestIdEndPost(
    testId,
    winnerVariant
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **testId** | [**string**] |  | defaults to undefined|
| **winnerVariant** | [**string**] |  | defaults to undefined|


### Return type

**ABTestActionResponse**

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

# **getAbTestApiV1AbTestsTestIdGet**
> ABTestResponse getAbTestApiV1AbTestsTestIdGet()

Get A/B test by ID.  Args:     test_id: Test ID     current_user: Current authenticated user     ab_test_manager: A/B test manager instance  Returns:     A/B test data

### Example

```typescript
import {
    ABTestingApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ABTestingApi(configuration);

let testId: string; // (default to undefined)

const { status, data } = await apiInstance.getAbTestApiV1AbTestsTestIdGet(
    testId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **testId** | [**string**] |  | defaults to undefined|


### Return type

**ABTestResponse**

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

# **getAbTestMetricsApiV1AbTestsTestIdMetricsGet**
> ABTestMetricsResponse getAbTestMetricsApiV1AbTestsTestIdMetricsGet()

Get current A/B test metrics.  Args:     test_id: Test ID     current_user: Current authenticated user     ab_test_manager: A/B test manager instance  Returns:     Current test metrics

### Example

```typescript
import {
    ABTestingApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ABTestingApi(configuration);

let testId: string; // (default to undefined)

const { status, data } = await apiInstance.getAbTestMetricsApiV1AbTestsTestIdMetricsGet(
    testId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **testId** | [**string**] |  | defaults to undefined|


### Return type

**ABTestMetricsResponse**

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

# **getAbTestPerformanceApiV1AbTestsTestIdPerformanceGet**
> { [key: string]: any; } getAbTestPerformanceApiV1AbTestsTestIdPerformanceGet()

Get A/B test performance results by variant.  Args:     test_id: A/B test ID     current_user: Current authenticated user     ab_test_manager: A/B test manager instance  Returns:     Performance results per variant

### Example

```typescript
import {
    ABTestingApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ABTestingApi(configuration);

let testId: string; // (default to undefined)

const { status, data } = await apiInstance.getAbTestPerformanceApiV1AbTestsTestIdPerformanceGet(
    testId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **testId** | [**string**] |  | defaults to undefined|


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
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getAbTestRecommendationsApiV1AbTestsTestIdRecommendationsGet**
> { [key: string]: any; } getAbTestRecommendationsApiV1AbTestsTestIdRecommendationsGet()

Get comprehensive recommendations for an A/B test.  Args:     test_id: A/B test ID     current_user: Current authenticated user     ab_test_manager: A/B test manager instance  Returns:     Recommendations and insights for the test

### Example

```typescript
import {
    ABTestingApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ABTestingApi(configuration);

let testId: string; // (default to undefined)

const { status, data } = await apiInstance.getAbTestRecommendationsApiV1AbTestsTestIdRecommendationsGet(
    testId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **testId** | [**string**] |  | defaults to undefined|


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
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getAbTestResultsApiV1AbTestsTestIdResultsGet**
> ABTestResultsResponse getAbTestResultsApiV1AbTestsTestIdResultsGet()

Get A/B test results and analysis.  Args:     test_id: Test ID     current_user: Current authenticated user     ab_test_manager: A/B test manager instance  Returns:     Test results and analysis

### Example

```typescript
import {
    ABTestingApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ABTestingApi(configuration);

let testId: string; // (default to undefined)

const { status, data } = await apiInstance.getAbTestResultsApiV1AbTestsTestIdResultsGet(
    testId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **testId** | [**string**] |  | defaults to undefined|


### Return type

**ABTestResultsResponse**

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

# **listAbTestsApiV1AbTestsGet**
> ABTestListResponse listAbTestsApiV1AbTestsGet()

List A/B tests with optional filtering.  Args:     request: List request parameters     current_user: Current authenticated user     ab_test_manager: A/B test manager instance  Returns:     List of A/B tests

### Example

```typescript
import {
    ABTestingApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ABTestingApi(configuration);

let status: TestStatus; // (optional) (default to undefined)
let testType: TestType; // (optional) (default to undefined)
let requestBody: Array<string>; // (optional)

const { status, data } = await apiInstance.listAbTestsApiV1AbTestsGet(
    status,
    testType,
    requestBody
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **requestBody** | **Array<string>**|  | |
| **status** | **TestStatus** |  | (optional) defaults to undefined|
| **testType** | **TestType** |  | (optional) defaults to undefined|


### Return type

**ABTestListResponse**

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

# **pauseAbTestApiV1AbTestsTestIdPausePost**
> ABTestActionResponse pauseAbTestApiV1AbTestsTestIdPausePost()

Pause an A/B test.  Args:     test_id: Test ID     current_user: Current authenticated user     ab_test_manager: A/B test manager instance  Returns:     Action result

### Example

```typescript
import {
    ABTestingApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ABTestingApi(configuration);

let testId: string; // (default to undefined)

const { status, data } = await apiInstance.pauseAbTestApiV1AbTestsTestIdPausePost(
    testId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **testId** | [**string**] |  | defaults to undefined|


### Return type

**ABTestActionResponse**

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

# **startAbTestApiV1AbTestsTestIdStartPost**
> ABTestActionResponse startAbTestApiV1AbTestsTestIdStartPost()

Start an A/B test.  Args:     test_id: Test ID     current_user: Current authenticated user     ab_test_manager: A/B test manager instance  Returns:     Action result

### Example

```typescript
import {
    ABTestingApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ABTestingApi(configuration);

let testId: string; // (default to undefined)

const { status, data } = await apiInstance.startAbTestApiV1AbTestsTestIdStartPost(
    testId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **testId** | [**string**] |  | defaults to undefined|


### Return type

**ABTestActionResponse**

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

# **updateAbTestApiV1AbTestsTestIdPut**
> ABTestResponse updateAbTestApiV1AbTestsTestIdPut(aBTestUpdateRequest)

Update an A/B test.  Args:     test_id: Test ID     test_data: Test update data     current_user: Current authenticated user     ab_test_manager: A/B test manager instance  Returns:     Updated test data

### Example

```typescript
import {
    ABTestingApi,
    Configuration,
    ABTestUpdateRequest
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ABTestingApi(configuration);

let testId: string; // (default to undefined)
let aBTestUpdateRequest: ABTestUpdateRequest; //

const { status, data } = await apiInstance.updateAbTestApiV1AbTestsTestIdPut(
    testId,
    aBTestUpdateRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **aBTestUpdateRequest** | **ABTestUpdateRequest**|  | |
| **testId** | [**string**] |  | defaults to undefined|


### Return type

**ABTestResponse**

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

