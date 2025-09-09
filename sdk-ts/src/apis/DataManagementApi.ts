/**
 * Generated API client for Data Management
 */
import { BackupListResponse, BackupRequest, BackupResponse, BulkDeleteResponse, ExportDataRequest, ExportDataResponse, RestoreRequest, RestoreResponse, StorageStatsResponse } from '../models/index';
import { BaseAPI, Configuration, RequestOptions } from '../runtime';

export class DataManagementApi extends BaseAPI {
  constructor(configuration?: Configuration) {
    super(configuration);
  }

  /**Export Data
   * Export data in specified format.
   */
  public async exportDataApiV1DataExport(data: ExportDataRequest): Promise<ExportDataResponse> {
    const requestOptions: RequestOptions = {
      method: 'POST',
      body: data,
    };

    return this.request<ExportDataResponse>(`/api/v1/data/export`, requestOptions);
  }
  /**Create Backup
   * Create a data backup.
   */
  public async createBackupApiV1DataBackup(data: BackupRequest): Promise<BackupResponse> {
    const requestOptions: RequestOptions = {
      method: 'POST',
      body: data,
    };

    return this.request<BackupResponse>(`/api/v1/data/backup`, requestOptions);
  }
  /**List Backups
   * List available backups.
   */
  public async listBackupsApiV1DataBackups(options?: RequestOptions): Promise<BackupListResponse> {
    const requestOptions: RequestOptions = {
      method: 'GET',
      headers: options?.headers,
      query: {
        'backup_type': options?.backupType,
        'status': options?.status,
      },
    };

    return this.request<BackupListResponse>(`/api/v1/data/backups`, requestOptions);
  }
  /**Restore From Backup
   * Restore data from a backup.
   */
  public async restoreFromBackupApiV1DataRestore(data: RestoreRequest): Promise<RestoreResponse> {
    const requestOptions: RequestOptions = {
      method: 'POST',
      body: data,
    };

    return this.request<RestoreResponse>(`/api/v1/data/restore`, requestOptions);
  }
  /**Get Storage Stats
   * Get storage statistics and usage information.
   */
  public async getStorageStatsApiV1DataStats(): Promise<StorageStatsResponse> {
    const requestOptions: RequestOptions = {
      method: 'GET',
    };

    return this.request<StorageStatsResponse>(`/api/v1/data/stats`, requestOptions);
  }
  /**Bulk Delete Documents
   * Bulk delete documents.
   */
  public async bulkDeleteDocumentsApiV1DataBulkDeleteDocuments(data: string[]): Promise<BulkDeleteResponse> {
    const requestOptions: RequestOptions = {
      method: 'POST',
      body: data,
    };

    return this.request<BulkDeleteResponse>(`/api/v1/data/bulk/delete-documents`, requestOptions);
  }
  /**Bulk Delete Conversations
   * Bulk delete conversations.
   */
  public async bulkDeleteConversationsApiV1DataBulkDeleteConversations(data: string[]): Promise<BulkDeleteResponse> {
    const requestOptions: RequestOptions = {
      method: 'POST',
      body: data,
    };

    return this.request<BulkDeleteResponse>(`/api/v1/data/bulk/delete-conversations`, requestOptions);
  }
  /**Bulk Delete Prompts
   * Bulk delete prompts.
   */
  public async bulkDeletePromptsApiV1DataBulkDeletePrompts(data: string[]): Promise<BulkDeleteResponse> {
    const requestOptions: RequestOptions = {
      method: 'POST',
      body: data,
    };

    return this.request<BulkDeleteResponse>(`/api/v1/data/bulk/delete-prompts`, requestOptions);
  }
}