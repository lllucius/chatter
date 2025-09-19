/**
 * Simple test to verify the document chunks API method signature and types
 */
import type { DocumentChunksResponse, DocumentChunkResponse } from 'chatter-sdk';

// This test file verifies that our types are correctly defined and exported
describe('Document Chunks Type Verification', () => {
  it('should have correct DocumentChunkResponse interface', () => {
    // This test will fail at compile time if the interface is incorrect
    const mockChunk: DocumentChunkResponse = {
      id: 'test-chunk-id',
      document_id: 'test-doc-id', 
      content: 'Test chunk content',
      chunk_index: 0,
      start_char: 0,
      end_char: 100,
      extra_metadata: null,
      token_count: 25,
      language: 'en',
      embedding_model: null,
      embedding_provider: null,
      embedding_created_at: null,
      content_hash: 'test-hash',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z'
    };
    
    expect(mockChunk.id).toBe('test-chunk-id');
    expect(mockChunk.content).toBe('Test chunk content');
  });

  it('should have correct DocumentChunksResponse interface', () => {
    // This test will fail at compile time if the interface is incorrect
    const mockResponse: DocumentChunksResponse = {
      chunks: [],
      total_count: 0,
      limit: 10,
      offset: 0
    };
    
    expect(mockResponse.chunks).toEqual([]);
    expect(mockResponse.total_count).toBe(0);
  });
});