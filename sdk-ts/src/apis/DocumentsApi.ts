/**
 * Generated API client for Documents
 */
import { DocumentChunksResponse, DocumentDeleteResponse, DocumentListResponse, DocumentProcessingRequest, DocumentProcessingResponse, DocumentResponse, DocumentSearchRequest, DocumentSearchResponse, DocumentStatsResponse, DocumentUpdate, Record } from '../models/index';
import { BaseAPI, Configuration, RequestOptions } from '../runtime';

export class DocumentsApi extends BaseAPI {
  constructor(configuration?: Configuration) {
    super(configuration);
  }

  /**Upload Document
   * Upload a document.

Args:
    file: Document file to upload
    title: Document title
    description: Document description
    tags: Document tags (JSON array string)
    chunk_size: Text chunk size for processing
    chunk_overlap: Text chunk overlap
    is_public: Whether document is public
    current_user: Current authenticated user
    document_service: Document service

Returns:
    Created document information
   */
  public async uploadDocumentApiV1DocumentsUpload(data: FormData): Promise<DocumentResponse> {
    const requestOptions: RequestOptions = {
      method: 'POST',
      body: data,
    };

    return this.request<DocumentResponse>(`/api/v1/documents/upload`, requestOptions);
  }
  /**List Documents
   * List user's documents.

Args:
    status: Filter by document status
    document_type: Filter by document type
    tags: Filter by tags
    owner_id: Filter by owner (admin only)
    limit: Maximum number of results
    offset: Number of results to skip
    sort_by: Sort field
    sort_order: Sort order (asc/desc)
    current_user: Current authenticated user
    document_service: Document service

Returns:
    List of documents with pagination info
   */
  public async listDocumentsApiV1Documents(options?: RequestOptions): Promise<DocumentListResponse> {
    const requestOptions: RequestOptions = {
      method: 'GET',
      headers: options?.headers,
      query: {
        'status': options?.status,
        'document_type': options?.documentType,
        'tags': options?.tags,
        'owner_id': options?.ownerId,
        'limit': options?.limit,
        'offset': options?.offset,
        'sort_by': options?.sortBy,
        'sort_order': options?.sortOrder,
      },
    };

    return this.request<DocumentListResponse>(`/api/v1/documents`, requestOptions);
  }
  /**Get Document
   * Get document details.

Args:
    document_id: Document ID
    current_user: Current authenticated user
    document_service: Document service

Returns:
    Document information
   */
  public async getDocumentApiV1DocumentsDocumentId(documentId: string): Promise<DocumentResponse> {
    const requestOptions: RequestOptions = {
      method: 'GET',
    };

    return this.request<DocumentResponse>(`/api/v1/documents/${documentId}`, requestOptions);
  }
  /**Update Document
   * Update document metadata.

Args:
    document_id: Document ID
    update_data: Update data
    current_user: Current authenticated user
    document_service: Document service

Returns:
    Updated document information
   */
  public async updateDocumentApiV1DocumentsDocumentId(documentId: string, data: DocumentUpdate): Promise<DocumentResponse> {
    const requestOptions: RequestOptions = {
      method: 'PUT',
      body: data,
    };

    return this.request<DocumentResponse>(`/api/v1/documents/${documentId}`, requestOptions);
  }
  /**Delete Document
   * Delete document.

Args:
    document_id: Document ID
    request: Delete request parameters
    current_user: Current authenticated user
    document_service: Document service

Returns:
    Success message
   */
  public async deleteDocumentApiV1DocumentsDocumentId(documentId: string): Promise<DocumentDeleteResponse> {
    const requestOptions: RequestOptions = {
      method: 'DELETE',
    };

    return this.request<DocumentDeleteResponse>(`/api/v1/documents/${documentId}`, requestOptions);
  }
  /**Search Documents
   * Search documents using vector similarity.

Args:
    search_request: Search request
    current_user: Current authenticated user
    document_service: Document service

Returns:
    Search results
   */
  public async searchDocumentsApiV1DocumentsSearch(data: DocumentSearchRequest): Promise<DocumentSearchResponse> {
    const requestOptions: RequestOptions = {
      method: 'POST',
      body: data,
    };

    return this.request<DocumentSearchResponse>(`/api/v1/documents/search`, requestOptions);
  }
  /**Get Document Chunks
   * Get document chunks.

Args:
    document_id: Document ID
    limit: Maximum number of results
    offset: Number of results to skip
    current_user: Current authenticated user
    document_service: Document service

Returns:
    List of document chunks with pagination
   */
  public async getDocumentChunksApiV1DocumentsDocumentIdChunks(documentId: string, options?: RequestOptions): Promise<DocumentChunksResponse> {
    const requestOptions: RequestOptions = {
      method: 'GET',
      headers: options?.headers,
      query: {
        'limit': options?.limit,
        'offset': options?.offset,
      },
    };

    return this.request<DocumentChunksResponse>(`/api/v1/documents/${documentId}/chunks`, requestOptions);
  }
  /**Process Document
   * Trigger document processing.

Args:
    document_id: Document ID
    processing_request: Processing request
    current_user: Current authenticated user
    document_service: Document service

Returns:
    Processing status
   */
  public async processDocumentApiV1DocumentsDocumentIdProcess(documentId: string, data: DocumentProcessingRequest): Promise<DocumentProcessingResponse> {
    const requestOptions: RequestOptions = {
      method: 'POST',
      body: data,
    };

    return this.request<DocumentProcessingResponse>(`/api/v1/documents/${documentId}/process`, requestOptions);
  }
  /**Get Document Stats
   * Get document statistics.

Args:
    current_user: Current authenticated user
    document_service: Document service

Returns:
    Document statistics
   */
  public async getDocumentStatsApiV1DocumentsStatsOverview(): Promise<DocumentStatsResponse> {
    const requestOptions: RequestOptions = {
      method: 'GET',
    };

    return this.request<DocumentStatsResponse>(`/api/v1/documents/stats/overview`, requestOptions);
  }
  /**Download Document
   * Download original document file.

Args:
    document_id: Document ID
    current_user: Current authenticated user
    document_service: Document service

Returns:
    File download response
   */
  public async downloadDocumentApiV1DocumentsDocumentIdDownload(documentId: string): Promise<Record<string, unknown>> {
    const requestOptions: RequestOptions = {
      method: 'GET',
    };

    return this.request<Record<string, unknown>>(`/api/v1/documents/${documentId}/download`, requestOptions);
  }
  /**Reprocess Document
   * Reprocess an existing document.

Args:
    document_id: Document ID
    current_user: Current authenticated user
    document_service: Document service

Returns:
    Processing status
   */
  public async reprocessDocumentApiV1DocumentsDocumentIdReprocess(documentId: string): Promise<DocumentProcessingResponse> {
    const requestOptions: RequestOptions = {
      method: 'POST',
    };

    return this.request<DocumentProcessingResponse>(`/api/v1/documents/${documentId}/reprocess`, requestOptions);
  }
}