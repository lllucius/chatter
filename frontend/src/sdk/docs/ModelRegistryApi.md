# ModelRegistryApi

All URIs are relative to *http://localhost:8000*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**createEmbeddingSpaceApiV1ModelsEmbeddingSpacesPost**](#createembeddingspaceapiv1modelsembeddingspacespost) | **POST** /api/v1/models/embedding-spaces | Create Embedding Space|
|[**createModelApiV1ModelsModelsPost**](#createmodelapiv1modelsmodelspost) | **POST** /api/v1/models/models | Create Model|
|[**createProviderApiV1ModelsProvidersPost**](#createproviderapiv1modelsproviderspost) | **POST** /api/v1/models/providers | Create Provider|
|[**deleteEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdDelete**](#deleteembeddingspaceapiv1modelsembeddingspacesspaceiddelete) | **DELETE** /api/v1/models/embedding-spaces/{space_id} | Delete Embedding Space|
|[**deleteModelApiV1ModelsModelsModelIdDelete**](#deletemodelapiv1modelsmodelsmodeliddelete) | **DELETE** /api/v1/models/models/{model_id} | Delete Model|
|[**deleteProviderApiV1ModelsProvidersProviderIdDelete**](#deleteproviderapiv1modelsprovidersprovideriddelete) | **DELETE** /api/v1/models/providers/{provider_id} | Delete Provider|
|[**getDefaultEmbeddingSpaceApiV1ModelsDefaultsEmbeddingSpaceGet**](#getdefaultembeddingspaceapiv1modelsdefaultsembeddingspaceget) | **GET** /api/v1/models/defaults/embedding-space | Get Default Embedding Space|
|[**getDefaultModelApiV1ModelsDefaultsModelModelTypeGet**](#getdefaultmodelapiv1modelsdefaultsmodelmodeltypeget) | **GET** /api/v1/models/defaults/model/{model_type} | Get Default Model|
|[**getDefaultProviderApiV1ModelsDefaultsProviderModelTypeGet**](#getdefaultproviderapiv1modelsdefaultsprovidermodeltypeget) | **GET** /api/v1/models/defaults/provider/{model_type} | Get Default Provider|
|[**getEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdGet**](#getembeddingspaceapiv1modelsembeddingspacesspaceidget) | **GET** /api/v1/models/embedding-spaces/{space_id} | Get Embedding Space|
|[**getModelApiV1ModelsModelsModelIdGet**](#getmodelapiv1modelsmodelsmodelidget) | **GET** /api/v1/models/models/{model_id} | Get Model|
|[**getProviderApiV1ModelsProvidersProviderIdGet**](#getproviderapiv1modelsprovidersprovideridget) | **GET** /api/v1/models/providers/{provider_id} | Get Provider|
|[**listEmbeddingSpacesApiV1ModelsEmbeddingSpacesGet**](#listembeddingspacesapiv1modelsembeddingspacesget) | **GET** /api/v1/models/embedding-spaces | List Embedding Spaces|
|[**listModelsApiV1ModelsModelsGet**](#listmodelsapiv1modelsmodelsget) | **GET** /api/v1/models/models | List Models|
|[**listProvidersApiV1ModelsProvidersGet**](#listprovidersapiv1modelsprovidersget) | **GET** /api/v1/models/providers | List Providers|
|[**setDefaultEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdSetDefaultPost**](#setdefaultembeddingspaceapiv1modelsembeddingspacesspaceidsetdefaultpost) | **POST** /api/v1/models/embedding-spaces/{space_id}/set-default | Set Default Embedding Space|
|[**setDefaultModelApiV1ModelsModelsModelIdSetDefaultPost**](#setdefaultmodelapiv1modelsmodelsmodelidsetdefaultpost) | **POST** /api/v1/models/models/{model_id}/set-default | Set Default Model|
|[**setDefaultProviderApiV1ModelsProvidersProviderIdSetDefaultPost**](#setdefaultproviderapiv1modelsprovidersprovideridsetdefaultpost) | **POST** /api/v1/models/providers/{provider_id}/set-default | Set Default Provider|
|[**updateEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdPut**](#updateembeddingspaceapiv1modelsembeddingspacesspaceidput) | **PUT** /api/v1/models/embedding-spaces/{space_id} | Update Embedding Space|
|[**updateModelApiV1ModelsModelsModelIdPut**](#updatemodelapiv1modelsmodelsmodelidput) | **PUT** /api/v1/models/models/{model_id} | Update Model|
|[**updateProviderApiV1ModelsProvidersProviderIdPut**](#updateproviderapiv1modelsprovidersprovideridput) | **PUT** /api/v1/models/providers/{provider_id} | Update Provider|

# **createEmbeddingSpaceApiV1ModelsEmbeddingSpacesPost**
> EmbeddingSpaceWithModel createEmbeddingSpaceApiV1ModelsEmbeddingSpacesPost(embeddingSpaceCreate)

Create a new embedding space with backing table and index.

### Example

```typescript
import {
    ModelRegistryApi,
    Configuration,
    EmbeddingSpaceCreate
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ModelRegistryApi(configuration);

let embeddingSpaceCreate: EmbeddingSpaceCreate; //

const { status, data } = await apiInstance.createEmbeddingSpaceApiV1ModelsEmbeddingSpacesPost(
    embeddingSpaceCreate
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **embeddingSpaceCreate** | **EmbeddingSpaceCreate**|  | |


### Return type

**EmbeddingSpaceWithModel**

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

# **createModelApiV1ModelsModelsPost**
> ModelDefWithProvider createModelApiV1ModelsModelsPost(modelDefCreate)

Create a new model definition.

### Example

```typescript
import {
    ModelRegistryApi,
    Configuration,
    ModelDefCreate
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ModelRegistryApi(configuration);

let modelDefCreate: ModelDefCreate; //

const { status, data } = await apiInstance.createModelApiV1ModelsModelsPost(
    modelDefCreate
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **modelDefCreate** | **ModelDefCreate**|  | |


### Return type

**ModelDefWithProvider**

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

# **createProviderApiV1ModelsProvidersPost**
> Provider createProviderApiV1ModelsProvidersPost(providerCreate)

Create a new provider.

### Example

```typescript
import {
    ModelRegistryApi,
    Configuration,
    ProviderCreate
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ModelRegistryApi(configuration);

let providerCreate: ProviderCreate; //

const { status, data } = await apiInstance.createProviderApiV1ModelsProvidersPost(
    providerCreate
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **providerCreate** | **ProviderCreate**|  | |


### Return type

**Provider**

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

# **deleteEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdDelete**
> EmbeddingSpaceDeleteResponse deleteEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdDelete()

Delete an embedding space (does not drop the table).

### Example

```typescript
import {
    ModelRegistryApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ModelRegistryApi(configuration);

let spaceId: string; // (default to undefined)

const { status, data } = await apiInstance.deleteEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdDelete(
    spaceId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **spaceId** | [**string**] |  | defaults to undefined|


### Return type

**EmbeddingSpaceDeleteResponse**

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

# **deleteModelApiV1ModelsModelsModelIdDelete**
> ModelDeleteResponse deleteModelApiV1ModelsModelsModelIdDelete()

Delete a model definition and its dependent embedding spaces.

### Example

```typescript
import {
    ModelRegistryApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ModelRegistryApi(configuration);

let modelId: string; // (default to undefined)

const { status, data } = await apiInstance.deleteModelApiV1ModelsModelsModelIdDelete(
    modelId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **modelId** | [**string**] |  | defaults to undefined|


### Return type

**ModelDeleteResponse**

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

# **deleteProviderApiV1ModelsProvidersProviderIdDelete**
> ProviderDeleteResponse deleteProviderApiV1ModelsProvidersProviderIdDelete()

Delete a provider and all its dependent models and embedding spaces.

### Example

```typescript
import {
    ModelRegistryApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ModelRegistryApi(configuration);

let providerId: string; // (default to undefined)

const { status, data } = await apiInstance.deleteProviderApiV1ModelsProvidersProviderIdDelete(
    providerId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **providerId** | [**string**] |  | defaults to undefined|


### Return type

**ProviderDeleteResponse**

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

# **getDefaultEmbeddingSpaceApiV1ModelsDefaultsEmbeddingSpaceGet**
> EmbeddingSpaceWithModel getDefaultEmbeddingSpaceApiV1ModelsDefaultsEmbeddingSpaceGet()

Get the default embedding space.

### Example

```typescript
import {
    ModelRegistryApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ModelRegistryApi(configuration);

const { status, data } = await apiInstance.getDefaultEmbeddingSpaceApiV1ModelsDefaultsEmbeddingSpaceGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**EmbeddingSpaceWithModel**

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

# **getDefaultModelApiV1ModelsDefaultsModelModelTypeGet**
> ModelDefWithProvider getDefaultModelApiV1ModelsDefaultsModelModelTypeGet()

Get the default model for a type.

### Example

```typescript
import {
    ModelRegistryApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ModelRegistryApi(configuration);

let modelType: ModelType; // (default to undefined)

const { status, data } = await apiInstance.getDefaultModelApiV1ModelsDefaultsModelModelTypeGet(
    modelType
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **modelType** | **ModelType** |  | defaults to undefined|


### Return type

**ModelDefWithProvider**

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

# **getDefaultProviderApiV1ModelsDefaultsProviderModelTypeGet**
> Provider getDefaultProviderApiV1ModelsDefaultsProviderModelTypeGet()

Get the default provider for a model type.

### Example

```typescript
import {
    ModelRegistryApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ModelRegistryApi(configuration);

let modelType: ModelType; // (default to undefined)

const { status, data } = await apiInstance.getDefaultProviderApiV1ModelsDefaultsProviderModelTypeGet(
    modelType
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **modelType** | **ModelType** |  | defaults to undefined|


### Return type

**Provider**

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

# **getEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdGet**
> EmbeddingSpaceWithModel getEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdGet()

Get a specific embedding space.

### Example

```typescript
import {
    ModelRegistryApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ModelRegistryApi(configuration);

let spaceId: string; // (default to undefined)

const { status, data } = await apiInstance.getEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdGet(
    spaceId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **spaceId** | [**string**] |  | defaults to undefined|


### Return type

**EmbeddingSpaceWithModel**

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

# **getModelApiV1ModelsModelsModelIdGet**
> ModelDefWithProvider getModelApiV1ModelsModelsModelIdGet()

Get a specific model definition.

### Example

```typescript
import {
    ModelRegistryApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ModelRegistryApi(configuration);

let modelId: string; // (default to undefined)

const { status, data } = await apiInstance.getModelApiV1ModelsModelsModelIdGet(
    modelId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **modelId** | [**string**] |  | defaults to undefined|


### Return type

**ModelDefWithProvider**

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

# **getProviderApiV1ModelsProvidersProviderIdGet**
> Provider getProviderApiV1ModelsProvidersProviderIdGet()

Get a specific provider.

### Example

```typescript
import {
    ModelRegistryApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ModelRegistryApi(configuration);

let providerId: string; // (default to undefined)

const { status, data } = await apiInstance.getProviderApiV1ModelsProvidersProviderIdGet(
    providerId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **providerId** | [**string**] |  | defaults to undefined|


### Return type

**Provider**

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

# **listEmbeddingSpacesApiV1ModelsEmbeddingSpacesGet**
> EmbeddingSpaceList listEmbeddingSpacesApiV1ModelsEmbeddingSpacesGet()

List all embedding spaces.

### Example

```typescript
import {
    ModelRegistryApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ModelRegistryApi(configuration);

let modelId: string; //Filter by model ID (optional) (default to undefined)
let page: number; //Page number (optional) (default to 1)
let perPage: number; //Items per page (optional) (default to 20)
let activeOnly: boolean; //Show only active spaces (optional) (default to true)

const { status, data } = await apiInstance.listEmbeddingSpacesApiV1ModelsEmbeddingSpacesGet(
    modelId,
    page,
    perPage,
    activeOnly
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **modelId** | [**string**] | Filter by model ID | (optional) defaults to undefined|
| **page** | [**number**] | Page number | (optional) defaults to 1|
| **perPage** | [**number**] | Items per page | (optional) defaults to 20|
| **activeOnly** | [**boolean**] | Show only active spaces | (optional) defaults to true|


### Return type

**EmbeddingSpaceList**

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

# **listModelsApiV1ModelsModelsGet**
> ModelDefList listModelsApiV1ModelsModelsGet()

List all model definitions.

### Example

```typescript
import {
    ModelRegistryApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ModelRegistryApi(configuration);

let providerId: string; //Filter by provider ID (optional) (default to undefined)
let modelType: ModelType; //Filter by model type (optional) (default to undefined)
let page: number; //Page number (optional) (default to 1)
let perPage: number; //Items per page (optional) (default to 20)
let activeOnly: boolean; //Show only active models (optional) (default to true)

const { status, data } = await apiInstance.listModelsApiV1ModelsModelsGet(
    providerId,
    modelType,
    page,
    perPage,
    activeOnly
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **providerId** | [**string**] | Filter by provider ID | (optional) defaults to undefined|
| **modelType** | **ModelType** | Filter by model type | (optional) defaults to undefined|
| **page** | [**number**] | Page number | (optional) defaults to 1|
| **perPage** | [**number**] | Items per page | (optional) defaults to 20|
| **activeOnly** | [**boolean**] | Show only active models | (optional) defaults to true|


### Return type

**ModelDefList**

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

# **listProvidersApiV1ModelsProvidersGet**
> ProviderList listProvidersApiV1ModelsProvidersGet()

List all providers.

### Example

```typescript
import {
    ModelRegistryApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ModelRegistryApi(configuration);

let page: number; //Page number (optional) (default to 1)
let perPage: number; //Items per page (optional) (default to 20)
let activeOnly: boolean; //Show only active providers (optional) (default to true)

const { status, data } = await apiInstance.listProvidersApiV1ModelsProvidersGet(
    page,
    perPage,
    activeOnly
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **page** | [**number**] | Page number | (optional) defaults to 1|
| **perPage** | [**number**] | Items per page | (optional) defaults to 20|
| **activeOnly** | [**boolean**] | Show only active providers | (optional) defaults to true|


### Return type

**ProviderList**

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

# **setDefaultEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdSetDefaultPost**
> EmbeddingSpaceDefaultResponse setDefaultEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdSetDefaultPost()

Set an embedding space as default.

### Example

```typescript
import {
    ModelRegistryApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ModelRegistryApi(configuration);

let spaceId: string; // (default to undefined)

const { status, data } = await apiInstance.setDefaultEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdSetDefaultPost(
    spaceId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **spaceId** | [**string**] |  | defaults to undefined|


### Return type

**EmbeddingSpaceDefaultResponse**

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

# **setDefaultModelApiV1ModelsModelsModelIdSetDefaultPost**
> ModelDefaultResponse setDefaultModelApiV1ModelsModelsModelIdSetDefaultPost()

Set a model as default for its type.

### Example

```typescript
import {
    ModelRegistryApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ModelRegistryApi(configuration);

let modelId: string; // (default to undefined)

const { status, data } = await apiInstance.setDefaultModelApiV1ModelsModelsModelIdSetDefaultPost(
    modelId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **modelId** | [**string**] |  | defaults to undefined|


### Return type

**ModelDefaultResponse**

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

# **setDefaultProviderApiV1ModelsProvidersProviderIdSetDefaultPost**
> ProviderDefaultResponse setDefaultProviderApiV1ModelsProvidersProviderIdSetDefaultPost(defaultProvider)

Set a provider as default for a model type.

### Example

```typescript
import {
    ModelRegistryApi,
    Configuration,
    DefaultProvider
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ModelRegistryApi(configuration);

let providerId: string; // (default to undefined)
let defaultProvider: DefaultProvider; //

const { status, data } = await apiInstance.setDefaultProviderApiV1ModelsProvidersProviderIdSetDefaultPost(
    providerId,
    defaultProvider
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **defaultProvider** | **DefaultProvider**|  | |
| **providerId** | [**string**] |  | defaults to undefined|


### Return type

**ProviderDefaultResponse**

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

# **updateEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdPut**
> EmbeddingSpaceWithModel updateEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdPut(embeddingSpaceUpdate)

Update an embedding space.

### Example

```typescript
import {
    ModelRegistryApi,
    Configuration,
    EmbeddingSpaceUpdate
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ModelRegistryApi(configuration);

let spaceId: string; // (default to undefined)
let embeddingSpaceUpdate: EmbeddingSpaceUpdate; //

const { status, data } = await apiInstance.updateEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdPut(
    spaceId,
    embeddingSpaceUpdate
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **embeddingSpaceUpdate** | **EmbeddingSpaceUpdate**|  | |
| **spaceId** | [**string**] |  | defaults to undefined|


### Return type

**EmbeddingSpaceWithModel**

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

# **updateModelApiV1ModelsModelsModelIdPut**
> ModelDefWithProvider updateModelApiV1ModelsModelsModelIdPut(modelDefUpdate)

Update a model definition.

### Example

```typescript
import {
    ModelRegistryApi,
    Configuration,
    ModelDefUpdate
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ModelRegistryApi(configuration);

let modelId: string; // (default to undefined)
let modelDefUpdate: ModelDefUpdate; //

const { status, data } = await apiInstance.updateModelApiV1ModelsModelsModelIdPut(
    modelId,
    modelDefUpdate
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **modelDefUpdate** | **ModelDefUpdate**|  | |
| **modelId** | [**string**] |  | defaults to undefined|


### Return type

**ModelDefWithProvider**

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

# **updateProviderApiV1ModelsProvidersProviderIdPut**
> Provider updateProviderApiV1ModelsProvidersProviderIdPut(providerUpdate)

Update a provider.

### Example

```typescript
import {
    ModelRegistryApi,
    Configuration,
    ProviderUpdate
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ModelRegistryApi(configuration);

let providerId: string; // (default to undefined)
let providerUpdate: ProviderUpdate; //

const { status, data } = await apiInstance.updateProviderApiV1ModelsProvidersProviderIdPut(
    providerId,
    providerUpdate
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **providerUpdate** | **ProviderUpdate**|  | |
| **providerId** | [**string**] |  | defaults to undefined|


### Return type

**Provider**

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

