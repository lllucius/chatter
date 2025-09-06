# DocumentsApi

All URIs are relative to *http://localhost:8000*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**deleteDocumentApiV1DocumentsDocumentIdDelete**](#deletedocumentapiv1documentsdocumentiddelete) | **DELETE** /api/v1/documents/{document_id} | Delete Document|
|[**downloadDocumentApiV1DocumentsDocumentIdDownloadGet**](#downloaddocumentapiv1documentsdocumentiddownloadget) | **GET** /api/v1/documents/{document_id}/download | Download Document|
|[**getDocumentApiV1DocumentsDocumentIdGet**](#getdocumentapiv1documentsdocumentidget) | **GET** /api/v1/documents/{document_id} | Get Document|
|[**getDocumentChunksApiV1DocumentsDocumentIdChunksGet**](#getdocumentchunksapiv1documentsdocumentidchunksget) | **GET** /api/v1/documents/{document_id}/chunks | Get Document Chunks|
|[**getDocumentStatsApiV1DocumentsStatsOverviewGet**](#getdocumentstatsapiv1documentsstatsoverviewget) | **GET** /api/v1/documents/stats/overview | Get Document Stats|
|[**listDocumentsApiV1DocumentsGet**](#listdocumentsapiv1documentsget) | **GET** /api/v1/documents | List Documents|
|[**processDocumentApiV1DocumentsDocumentIdProcessPost**](#processdocumentapiv1documentsdocumentidprocesspost) | **POST** /api/v1/documents/{document_id}/process | Process Document|
|[**reprocessDocumentApiV1DocumentsDocumentIdReprocessPost**](#reprocessdocumentapiv1documentsdocumentidreprocesspost) | **POST** /api/v1/documents/{document_id}/reprocess | Reprocess Document|
|[**searchDocumentsApiV1DocumentsSearchPost**](#searchdocumentsapiv1documentssearchpost) | **POST** /api/v1/documents/search | Search Documents|
|[**updateDocumentApiV1DocumentsDocumentIdPut**](#updatedocumentapiv1documentsdocumentidput) | **PUT** /api/v1/documents/{document_id} | Update Document|
|[**uploadDocumentApiV1DocumentsUploadPost**](#uploaddocumentapiv1documentsuploadpost) | **POST** /api/v1/documents/upload | Upload Document|

# **deleteDocumentApiV1DocumentsDocumentIdDelete**
> DocumentDeleteResponse deleteDocumentApiV1DocumentsDocumentIdDelete()

Delete document.  Args:     document_id: Document ID     request: Delete request parameters     current_user: Current authenticated user     document_service: Document service  Returns:     Success message

### Example

```typescript
import {
    DocumentsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)

const { status, data } = await apiInstance.deleteDocumentApiV1DocumentsDocumentIdDelete(
    documentId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **documentId** | [**string**] |  | defaults to undefined|


### Return type

**DocumentDeleteResponse**

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

# **downloadDocumentApiV1DocumentsDocumentIdDownloadGet**
> any downloadDocumentApiV1DocumentsDocumentIdDownloadGet()

Download original document file.  Args:     document_id: Document ID     current_user: Current authenticated user     document_service: Document service  Returns:     File download response

### Example

```typescript
import {
    DocumentsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)

const { status, data } = await apiInstance.downloadDocumentApiV1DocumentsDocumentIdDownloadGet(
    documentId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **documentId** | [**string**] |  | defaults to undefined|


### Return type

**any**

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

# **getDocumentApiV1DocumentsDocumentIdGet**
> DocumentResponse getDocumentApiV1DocumentsDocumentIdGet()

Get document details.  Args:     document_id: Document ID     current_user: Current authenticated user     document_service: Document service  Returns:     Document information

### Example

```typescript
import {
    DocumentsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)

const { status, data } = await apiInstance.getDocumentApiV1DocumentsDocumentIdGet(
    documentId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **documentId** | [**string**] |  | defaults to undefined|


### Return type

**DocumentResponse**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**401** | Unauthorized - Invalid or missing authentication token |  -  |
|**403** | Forbidden - User lacks permission to access this document |  -  |
|**404** | Not Found - Document does not exist |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getDocumentChunksApiV1DocumentsDocumentIdChunksGet**
> DocumentChunksResponse getDocumentChunksApiV1DocumentsDocumentIdChunksGet()

Get document chunks.  Args:     document_id: Document ID     limit: Maximum number of results     offset: Number of results to skip     current_user: Current authenticated user     document_service: Document service  Returns:     List of document chunks with pagination

### Example

```typescript
import {
    DocumentsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let limit: number; //Maximum number of results (optional) (default to 50)
let offset: number; //Number of results to skip (optional) (default to 0)

const { status, data } = await apiInstance.getDocumentChunksApiV1DocumentsDocumentIdChunksGet(
    documentId,
    limit,
    offset
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **documentId** | [**string**] |  | defaults to undefined|
| **limit** | [**number**] | Maximum number of results | (optional) defaults to 50|
| **offset** | [**number**] | Number of results to skip | (optional) defaults to 0|


### Return type

**DocumentChunksResponse**

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

# **getDocumentStatsApiV1DocumentsStatsOverviewGet**
> DocumentStatsResponse getDocumentStatsApiV1DocumentsStatsOverviewGet()

Get document statistics.  Args:     current_user: Current authenticated user     document_service: Document service  Returns:     Document statistics

### Example

```typescript
import {
    DocumentsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

const { status, data } = await apiInstance.getDocumentStatsApiV1DocumentsStatsOverviewGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**DocumentStatsResponse**

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

# **listDocumentsApiV1DocumentsGet**
> DocumentListResponse listDocumentsApiV1DocumentsGet()

List user\'s documents.  Args:     status: Filter by document status     document_type: Filter by document type     tags: Filter by tags     owner_id: Filter by owner (admin only)     limit: Maximum number of results     offset: Number of results to skip     sort_by: Sort field     sort_order: Sort order (asc/desc)     current_user: Current authenticated user     document_service: Document service  Returns:     List of documents with pagination info

### Example

```typescript
import {
    DocumentsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let status: DocumentStatus; //Filter by status (optional) (default to undefined)
let documentType: DocumentType; //Filter by document type (optional) (default to undefined)
let tags: Array<string>; //Filter by tags (optional) (default to undefined)
let ownerId: string; //Filter by owner (admin only) (optional) (default to undefined)
let limit: number; //Maximum number of results (optional) (default to 50)
let offset: number; //Number of results to skip (optional) (default to 0)
let sortBy: string; //Sort field (optional) (default to 'created_at')
let sortOrder: string; //Sort order (optional) (default to 'desc')

const { status, data } = await apiInstance.listDocumentsApiV1DocumentsGet(
    status,
    documentType,
    tags,
    ownerId,
    limit,
    offset,
    sortBy,
    sortOrder
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **status** | **DocumentStatus** | Filter by status | (optional) defaults to undefined|
| **documentType** | **DocumentType** | Filter by document type | (optional) defaults to undefined|
| **tags** | **Array&lt;string&gt;** | Filter by tags | (optional) defaults to undefined|
| **ownerId** | [**string**] | Filter by owner (admin only) | (optional) defaults to undefined|
| **limit** | [**number**] | Maximum number of results | (optional) defaults to 50|
| **offset** | [**number**] | Number of results to skip | (optional) defaults to 0|
| **sortBy** | [**string**] | Sort field | (optional) defaults to 'created_at'|
| **sortOrder** | [**string**] | Sort order | (optional) defaults to 'desc'|


### Return type

**DocumentListResponse**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**401** | Unauthorized - Invalid or missing authentication token |  -  |
|**403** | Forbidden - User lacks permission to access documents |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **processDocumentApiV1DocumentsDocumentIdProcessPost**
> DocumentProcessingResponse processDocumentApiV1DocumentsDocumentIdProcessPost(documentProcessingRequest)

Trigger document processing.  Args:     document_id: Document ID     processing_request: Processing request     current_user: Current authenticated user     document_service: Document service  Returns:     Processing status

### Example

```typescript
import {
    DocumentsApi,
    Configuration,
    DocumentProcessingRequest
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let documentProcessingRequest: DocumentProcessingRequest; //

const { status, data } = await apiInstance.processDocumentApiV1DocumentsDocumentIdProcessPost(
    documentId,
    documentProcessingRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **documentProcessingRequest** | **DocumentProcessingRequest**|  | |
| **documentId** | [**string**] |  | defaults to undefined|


### Return type

**DocumentProcessingResponse**

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

# **reprocessDocumentApiV1DocumentsDocumentIdReprocessPost**
> DocumentProcessingResponse reprocessDocumentApiV1DocumentsDocumentIdReprocessPost()

Reprocess an existing document.  Args:     document_id: Document ID     current_user: Current authenticated user     document_service: Document service  Returns:     Processing status

### Example

```typescript
import {
    DocumentsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)

const { status, data } = await apiInstance.reprocessDocumentApiV1DocumentsDocumentIdReprocessPost(
    documentId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **documentId** | [**string**] |  | defaults to undefined|


### Return type

**DocumentProcessingResponse**

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

# **searchDocumentsApiV1DocumentsSearchPost**
> DocumentSearchResponse searchDocumentsApiV1DocumentsSearchPost(documentSearchRequest)

Search documents using vector similarity.  Args:     search_request: Search request     current_user: Current authenticated user     document_service: Document service  Returns:     Search results

### Example

```typescript
import {
    DocumentsApi,
    Configuration,
    DocumentSearchRequest
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentSearchRequest: DocumentSearchRequest; //

const { status, data } = await apiInstance.searchDocumentsApiV1DocumentsSearchPost(
    documentSearchRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **documentSearchRequest** | **DocumentSearchRequest**|  | |


### Return type

**DocumentSearchResponse**

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

# **updateDocumentApiV1DocumentsDocumentIdPut**
> DocumentResponse updateDocumentApiV1DocumentsDocumentIdPut(documentUpdate)

Update document metadata.  Args:     document_id: Document ID     update_data: Update data     current_user: Current authenticated user     document_service: Document service  Returns:     Updated document information

### Example

```typescript
import {
    DocumentsApi,
    Configuration,
    DocumentUpdate
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let documentUpdate: DocumentUpdate; //

const { status, data } = await apiInstance.updateDocumentApiV1DocumentsDocumentIdPut(
    documentId,
    documentUpdate
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **documentUpdate** | **DocumentUpdate**|  | |
| **documentId** | [**string**] |  | defaults to undefined|


### Return type

**DocumentResponse**

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

# **uploadDocumentApiV1DocumentsUploadPost**
> DocumentResponse uploadDocumentApiV1DocumentsUploadPost()

Upload a document.  Args:     file: Document file to upload     title: Document title     description: Document description     tags: Document tags (JSON array string)     chunk_size: Text chunk size for processing     chunk_overlap: Text chunk overlap     is_public: Whether document is public     current_user: Current authenticated user     document_service: Document service  Returns:     Created document information

### Example

```typescript
import {
    DocumentsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let file: File; // (default to undefined)
let title: string; // (optional) (default to undefined)
let description: string; // (optional) (default to undefined)
let tags: string; // (optional) (default to undefined)
let chunkSize: number; // (optional) (default to 1000)
let chunkOverlap: number; // (optional) (default to 200)
let isPublic: boolean; // (optional) (default to false)

const { status, data } = await apiInstance.uploadDocumentApiV1DocumentsUploadPost(
    file,
    title,
    description,
    tags,
    chunkSize,
    chunkOverlap,
    isPublic
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **file** | [**File**] |  | defaults to undefined|
| **title** | [**string**] |  | (optional) defaults to undefined|
| **description** | [**string**] |  | (optional) defaults to undefined|
| **tags** | [**string**] |  | (optional) defaults to undefined|
| **chunkSize** | [**number**] |  | (optional) defaults to 1000|
| **chunkOverlap** | [**number**] |  | (optional) defaults to 200|
| **isPublic** | [**boolean**] |  | (optional) defaults to false|


### Return type

**DocumentResponse**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

