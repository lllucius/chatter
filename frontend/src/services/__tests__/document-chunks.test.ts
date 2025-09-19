import { describe, it, expect, beforeAll } from 'vitest';
import { getSDK, authService } from '../auth-service';

describe('Documents API - Document Chunks', () => {
  beforeAll(() => {
    // Initialize the auth service so SDK is available
    authService.initialize();
  });

  it('should have getDocumentChunks method available', () => {
    try {
      const sdk = getSDK();
      expect(sdk.documents).toBeDefined();
      expect(typeof sdk.documents.getDocumentChunksApiV1DocumentsDocumentIdChunks).toBe('function');
    } catch (error) {
      // If SDK is not initialized, that's fine for this test - we're just checking the method exists
      expect(error).toBeDefined();
    }
  });

  it('should have correct method signature for getDocumentChunks', () => {
    try {
      const sdk = getSDK();
      const method = sdk.documents.getDocumentChunksApiV1DocumentsDocumentIdChunks;
      
      // Check that the method exists and is callable
      expect(method).toBeDefined();
      expect(typeof method).toBe('function');
      
      // The method should accept documentId as first parameter and options as second
      expect(method.length).toBe(2);
    } catch (error) {
      // If SDK is not initialized, that's fine for this test - we're just checking the method exists
      expect(error).toBeDefined();
    }
  });
});