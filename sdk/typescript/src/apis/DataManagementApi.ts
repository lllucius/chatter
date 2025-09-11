/**
 * Generated API client for Data Management
 */
import { BackupListResponse, BackupRequest, BackupResponse, BackupType, BulkDeleteResponse, ExportDataRequest, ExportDataResponse, RestoreRequest, RestoreResponse, StorageStatsResponse } from '../models/index';
import { BaseAPI, Configuration, RequestOpts, HTTPMethod, HTTPQuery, HTTPHeaders } from '../runtime';

export class DataManagementApi extends BaseAPI {
  constructor(configuration?: Configuration) {
    super(configuration);
  }

  /**Export Data
   * Export data in specified format.
   */
  public async exportDataApiV1DataExport(data: ExportDataRequest): Promise<ExportDataResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/data/export`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ExportDataResponse>;
  }
  /**Create Backup
   * Create a data backup.
   */
  public async createBackupApiV1DataBackup(data: BackupRequest): Promise<BackupResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/data/backup`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<BackupResponse>;
  }
  /**List Backups
   * List available backups.
   */
  public async listBackupsApiV1DataBackups(options?: { backupType?: BackupType | null; status?: string | null; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<BackupListResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/data/backups`,
      method: 'GET' as HTTPMethod,
      headers: {
        ...options?.headers,
      },
      query: {
        'backup_type': options?.backupType,
        'status': options?.status,
        ...options?.query
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<BackupListResponse>;
  }
  /**Restore From Backup
   * Restore data from a backup.
   */
  public async restoreFromBackupApiV1DataRestore(data: RestoreRequest): Promise<RestoreResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/data/restore`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<RestoreResponse>;
  }
  /**Get Storage Stats
   * Get storage statistics and usage information.
   */
  public async getStorageStatsApiV1DataStats(): Promise<StorageStatsResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/data/stats`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<StorageStatsResponse>;
  }
  /**Bulk Delete Documents
   * Bulk delete documents.
   */
  public async bulkDeleteDocumentsApiV1DataBulkDeleteDocuments(data: string[]): Promise<BulkDeleteResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/data/bulk/delete-documents`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<BulkDeleteResponse>;
  }
  /**Bulk Delete Conversations
   * Bulk delete conversations.
   */
  public async bulkDeleteConversationsApiV1DataBulkDeleteConversations(data: string[]): Promise<BulkDeleteResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/data/bulk/delete-conversations`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<BulkDeleteResponse>;
  }
  /**Bulk Delete Prompts
   * Bulk delete prompts.
   */
  public async bulkDeletePromptsApiV1DataBulkDeletePrompts(data: string[]): Promise<BulkDeleteResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/data/bulk/delete-prompts`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<BulkDeleteResponse>;
  }
}