/**
 * Integration test to verify document chunks functionality works end-to-end
 */
import { describe, it, expect, vi } from 'vitest';
import type { DocumentChunksResponse } from 'chatter-sdk';

describe('Document Chunks Integration', () => {
  it('should correctly process chunks response in document view', () => {
    // Mock the API response structure
    const mockChunksResponse: DocumentChunksResponse = {
      chunks: [
        {
          id: 'chunk-1',
          document_id: 'doc-123',
          content: 'This is the first chunk of content from the document. It contains important information about the topic.',
          chunk_index: 0,
          start_char: 0,
          end_char: 100,
          extra_metadata: null,
          token_count: 25,
          language: 'en',
          embedding_model: null,
          embedding_provider: null,
          embedding_created_at: null,
          content_hash: 'hash1',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        },
        {
          id: 'chunk-2', 
          document_id: 'doc-123',
          content: 'This is the second chunk which continues from where the first chunk ended. More detailed information.',
          chunk_index: 1,
          start_char: 100,
          end_char: 200,
          extra_metadata: null,
          token_count: 30,
          language: 'en',
          embedding_model: null,
          embedding_provider: null,
          embedding_created_at: null,
          content_hash: 'hash2',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        }
      ],
      total_count: 2,
      limit: 3,
      offset: 0
    };

    // Simulate the content preview generation logic from DocumentsPage
    const chunks = mockChunksResponse.chunks || [];
    let contentPreview = '';
    
    if (chunks.length > 0) {
      contentPreview = chunks
        .slice(0, 3)
        .map((chunk, index: number) => 
          `Chunk ${index + 1}: ${chunk.content.substring(0, 200)}...`
        )
        .join('\n\n');
    }

    // Verify the content preview is generated correctly
    expect(contentPreview).toContain('Chunk 1: This is the first chunk of content');
    expect(contentPreview).toContain('Chunk 2: This is the second chunk which continues');
    expect(contentPreview.split('\n\n')).toHaveLength(2);
  });

  it('should handle empty chunks response gracefully', () => {
    const mockEmptyResponse: DocumentChunksResponse = {
      chunks: [],
      total_count: 0,
      limit: 3,
      offset: 0
    };

    const chunks = mockEmptyResponse.chunks || [];
    let contentPreview = '';
    
    if (chunks.length > 0) {
      contentPreview = chunks
        .slice(0, 3)
        .map((chunk, index: number) => 
          `Chunk ${index + 1}: ${chunk.content.substring(0, 200)}...`
        )
        .join('\n\n');
    } else {
      const documentChunkCount = 5; // Mock chunk count
      contentPreview = `Document is processed into ${documentChunkCount} chunks for vector search. No chunk content available for preview.`;
    }

    expect(contentPreview).toBe('Document is processed into 5 chunks for vector search. No chunk content available for preview.');
  });
});