/**
 * Generated from OpenAPI schema: Body_upload_document_api_v1_documents_upload_post
 */
export interface Body_upload_document_api_v1_documents_upload_post {
  file: string;
  title?: string | null;
  description?: string | null;
  tags?: string | null;
  chunk_size?: number;
  chunk_overlap?: number;
  is_public?: boolean;
}
