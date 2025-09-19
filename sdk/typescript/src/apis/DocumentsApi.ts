/**
 * Generated API client for Documents
 */
import { DocumentListRequest, DocumentResponse, DocumentSearchRequest, DocumentStatsResponse, SearchResultResponse, DocumentChunksResponse } from '../models/index';
import { BaseAPI, Configuration, RequestOpts, HTTPMethod, HTTPQuery, HTTPHeaders } from '../runtime';

export class DocumentsApi extends BaseAPI {
  constructor(configuration?: Configuration) {
    super(configuration);
  }

  /**Upload Document
   * Upload and process a new document.

This endpoint uploads a file, creates a document record, and starts
the embedding processing pipeline asynchronously.
   */
  public async uploadDocumentApiV1DocumentsUpload(data: FormData): Promise<DocumentResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/documents/upload`,
      method: 'POST' as HTTPMethod,
      headers: {
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<DocumentResponse>;
  }
  /**Get Document
   * Get a document by ID.
   */
  public async getDocumentApiV1DocumentsDocumentId(documentId: string): Promise<DocumentResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/documents/${documentId}`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<DocumentResponse>;
  }
  /**Delete Document
   * Delete a document.
   */
  public async deleteDocumentApiV1DocumentsDocumentId(documentId: string): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/documents/${documentId}`,
      method: 'DELETE' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
  }
  /**List Documents Get
   * List documents with pagination (GET endpoint for frontend compatibility).
   */
  public async listDocumentsGetApiV1Documents(options?: { limit?: number; offset?: number; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/documents`,
      method: 'GET' as HTTPMethod,
      headers: {
        ...options?.headers,
      },
      query: {
        'limit': options?.limit,
        'offset': options?.offset,
        ...options?.query
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
  }
  /**List Documents Post
   * List documents with filtering and pagination (POST endpoint for advanced filtering).
   */
  public async listDocumentsPostApiV1DocumentsList(data: DocumentListRequest): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/documents/list`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
  }
  /**Search Documents
   * Search documents using semantic similarity.
   */
  public async searchDocumentsApiV1DocumentsSearch(data: DocumentSearchRequest): Promise<SearchResultResponse[]> {
    const requestContext: RequestOpts = {
      path: `/api/v1/documents/search`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<SearchResultResponse[]>;
  }
  /**Reprocess Document
   * Reprocess a document through the embedding pipeline.
   */
  public async reprocessDocumentApiV1DocumentsDocumentIdReprocess(documentId: string): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/documents/${documentId}/reprocess`,
      method: 'POST' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
  }
  /**Get User Document Stats
   * Get document statistics for the current user.
   */
  public async getUserDocumentStatsApiV1DocumentsStatsUser(): Promise<DocumentStatsResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/documents/stats/user`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<DocumentStatsResponse>;
  }
  /**Get Document Chunks
   * Get document chunks with pagination.
   */
  public async getDocumentChunksApiV1DocumentsDocumentIdChunks(documentId: string, options?: { limit?: number; offset?: number; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<DocumentChunksResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/documents/${documentId}/chunks`,
      method: 'GET' as HTTPMethod,
      headers: {
        ...options?.headers,
      },
      query: {
        'limit': options?.limit,
        'offset': options?.offset,
        ...options?.query
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<DocumentChunksResponse>;
  }
}