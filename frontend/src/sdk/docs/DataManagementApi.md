# DataManagementApi

All URIs are relative to *http://localhost:8000*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**bulkDeleteConversationsApiV1DataBulkDeleteConversationsPost**](#bulkdeleteconversationsapiv1databulkdeleteconversationspost) | **POST** /api/v1/data/bulk/delete-conversations | Bulk Delete Conversations|
|[**bulkDeleteDocumentsApiV1DataBulkDeleteDocumentsPost**](#bulkdeletedocumentsapiv1databulkdeletedocumentspost) | **POST** /api/v1/data/bulk/delete-documents | Bulk Delete Documents|
|[**bulkDeletePromptsApiV1DataBulkDeletePromptsPost**](#bulkdeletepromptsapiv1databulkdeletepromptspost) | **POST** /api/v1/data/bulk/delete-prompts | Bulk Delete Prompts|
|[**createBackupApiV1DataBackupPost**](#createbackupapiv1databackuppost) | **POST** /api/v1/data/backup | Create Backup|
|[**exportDataApiV1DataExportPost**](#exportdataapiv1dataexportpost) | **POST** /api/v1/data/export | Export Data|
|[**getStorageStatsApiV1DataStatsGet**](#getstoragestatsapiv1datastatsget) | **GET** /api/v1/data/stats | Get Storage Stats|
|[**listBackupsApiV1DataBackupsGet**](#listbackupsapiv1databackupsget) | **GET** /api/v1/data/backups | List Backups|
|[**restoreFromBackupApiV1DataRestorePost**](#restorefrombackupapiv1datarestorepost) | **POST** /api/v1/data/restore | Restore From Backup|

# **bulkDeleteConversationsApiV1DataBulkDeleteConversationsPost**
> { [key: string]: any; } bulkDeleteConversationsApiV1DataBulkDeleteConversationsPost(requestBody)

Bulk delete conversations.  Args:     conversation_ids: List of conversation IDs to delete     current_user: Current authenticated user     data_manager: Data manager instance  Returns:     Bulk operation results

### Example

```typescript
import {
    DataManagementApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new DataManagementApi(configuration);

let requestBody: Array<string | null>; //

const { status, data } = await apiInstance.bulkDeleteConversationsApiV1DataBulkDeleteConversationsPost(
    requestBody
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **requestBody** | **Array<string | null>**|  | |


### Return type

**{ [key: string]: any; }**

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

# **bulkDeleteDocumentsApiV1DataBulkDeleteDocumentsPost**
> { [key: string]: any; } bulkDeleteDocumentsApiV1DataBulkDeleteDocumentsPost(requestBody)

Bulk delete documents.  Args:     document_ids: List of document IDs to delete     current_user: Current authenticated user     data_manager: Data manager instance  Returns:     Bulk operation results

### Example

```typescript
import {
    DataManagementApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new DataManagementApi(configuration);

let requestBody: Array<string | null>; //

const { status, data } = await apiInstance.bulkDeleteDocumentsApiV1DataBulkDeleteDocumentsPost(
    requestBody
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **requestBody** | **Array<string | null>**|  | |


### Return type

**{ [key: string]: any; }**

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

# **bulkDeletePromptsApiV1DataBulkDeletePromptsPost**
> { [key: string]: any; } bulkDeletePromptsApiV1DataBulkDeletePromptsPost(requestBody)

Bulk delete prompts.  Args:     prompt_ids: List of prompt IDs to delete     current_user: Current authenticated user     data_manager: Data manager instance  Returns:     Bulk operation results

### Example

```typescript
import {
    DataManagementApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new DataManagementApi(configuration);

let requestBody: Array<string | null>; //

const { status, data } = await apiInstance.bulkDeletePromptsApiV1DataBulkDeletePromptsPost(
    requestBody
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **requestBody** | **Array<string | null>**|  | |


### Return type

**{ [key: string]: any; }**

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

# **createBackupApiV1DataBackupPost**
> BackupResponse createBackupApiV1DataBackupPost(backupRequest)

Create a data backup.  Args:     backup_request: Backup request parameters     current_user: Current authenticated user     data_manager: Data manager instance  Returns:     Backup operation details

### Example

```typescript
import {
    DataManagementApi,
    Configuration,
    BackupRequest
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new DataManagementApi(configuration);

let backupRequest: BackupRequest; //

const { status, data } = await apiInstance.createBackupApiV1DataBackupPost(
    backupRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **backupRequest** | **BackupRequest**|  | |


### Return type

**BackupResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**202** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **exportDataApiV1DataExportPost**
> ExportDataResponse exportDataApiV1DataExportPost(exportDataRequest)

Export data in specified format.  Args:     export_request: Export request parameters     current_user: Current authenticated user     data_manager: Data manager instance  Returns:     Export operation details

### Example

```typescript
import {
    DataManagementApi,
    Configuration,
    ExportDataRequest
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new DataManagementApi(configuration);

let exportDataRequest: ExportDataRequest; //

const { status, data } = await apiInstance.exportDataApiV1DataExportPost(
    exportDataRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **exportDataRequest** | **ExportDataRequest**|  | |


### Return type

**ExportDataResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**202** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getStorageStatsApiV1DataStatsGet**
> StorageStatsResponse getStorageStatsApiV1DataStatsGet()

Get storage statistics and usage information.  Args:     current_user: Current authenticated user     data_manager: Data manager instance  Returns:     Storage statistics

### Example

```typescript
import {
    DataManagementApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new DataManagementApi(configuration);

const { status, data } = await apiInstance.getStorageStatsApiV1DataStatsGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**StorageStatsResponse**

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

# **listBackupsApiV1DataBackupsGet**
> BackupListResponse listBackupsApiV1DataBackupsGet()

List available backups.  Args:     request: List request parameters     current_user: Current authenticated user     data_manager: Data manager instance  Returns:     List of backups

### Example

```typescript
import {
    DataManagementApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new DataManagementApi(configuration);

let backupType: BackupType; // (optional) (default to undefined)
let status: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listBackupsApiV1DataBackupsGet(
    backupType,
    status
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **backupType** | **BackupType** |  | (optional) defaults to undefined|
| **status** | [**string**] |  | (optional) defaults to undefined|


### Return type

**BackupListResponse**

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

# **restoreFromBackupApiV1DataRestorePost**
> RestoreResponse restoreFromBackupApiV1DataRestorePost(restoreRequest)

Restore data from a backup.  Args:     restore_request: Restore request parameters     current_user: Current authenticated user     data_manager: Data manager instance  Returns:     Restore operation details

### Example

```typescript
import {
    DataManagementApi,
    Configuration,
    RestoreRequest
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new DataManagementApi(configuration);

let restoreRequest: RestoreRequest; //

const { status, data } = await apiInstance.restoreFromBackupApiV1DataRestorePost(
    restoreRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **restoreRequest** | **RestoreRequest**|  | |


### Return type

**RestoreResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**202** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

