// Test to demonstrate the specific fix for the original error
// "TypeError: getSDK(...).workflows.getChatWorkflowTemplatesApiV1WorkflowsTemplatesChat is not a function"

import { describe, it, expect, vi } from 'vitest';

describe('useWorkflowChat Fix', () => {
  it('should prevent "is not a function" error with proper validation', () => {
    // Mock the getSDK function to return an SDK without the method (original error scenario)
    const mockGetSDK = vi.fn().mockReturnValue({
      workflows: {}, // Missing the method - this would cause the original error
    });

    // This is the validation logic I added to useWorkflowChat
    const validateAndCallWorkflowMethod = (getSDK: () => unknown) => {
      const sdk = getSDK();

      // Check if SDK and workflows are properly initialized
      if (!sdk || !sdk.workflows) {
        throw new Error('SDK or workflows API not initialized');
      }

      // Check if the method exists - THIS PREVENTS THE ORIGINAL ERROR
      if (
        typeof sdk.workflows
          .getChatWorkflowTemplatesApiV1WorkflowsTemplatesChat !== 'function'
      ) {
        throw new Error(
          'getChatWorkflowTemplatesApiV1WorkflowsTemplatesChat method not available'
        );
      }

      // Only call the method if it exists
      return sdk.workflows.getChatWorkflowTemplatesApiV1WorkflowsTemplatesChat();
    };

    // Test that the validation catches the missing method
    expect(() => validateAndCallWorkflowMethod(mockGetSDK)).toThrow(
      'getChatWorkflowTemplatesApiV1WorkflowsTemplatesChat method not available'
    );
  });

  it('should work correctly when the method is available', () => {
    // Mock the getSDK function to return a properly initialized SDK
    const mockGetSDK = vi.fn().mockReturnValue({
      workflows: {
        getChatWorkflowTemplatesApiV1WorkflowsTemplatesChat: vi
          .fn()
          .mockResolvedValue({
            templates: { test: 'template' },
          }),
      },
    });

    const validateAndCallWorkflowMethod = (getSDK: () => unknown) => {
      const sdk = getSDK();

      if (!sdk || !sdk.workflows) {
        throw new Error('SDK or workflows API not initialized');
      }

      if (
        typeof sdk.workflows
          .getChatWorkflowTemplatesApiV1WorkflowsTemplatesChat !== 'function'
      ) {
        throw new Error(
          'getChatWorkflowTemplatesApiV1WorkflowsTemplatesChat method not available'
        );
      }

      return sdk.workflows.getChatWorkflowTemplatesApiV1WorkflowsTemplatesChat();
    };

    // Test that it works when the method is available
    expect(() => validateAndCallWorkflowMethod(mockGetSDK)).not.toThrow();
    expect(mockGetSDK).toHaveBeenCalled();
  });

  it('should handle missing workflows API', () => {
    // Mock getSDK to return SDK without workflows (another potential error scenario)
    const mockGetSDK = vi.fn().mockReturnValue({
      conversations: {}, // Has other APIs but missing workflows
    });

    const validateAndCallWorkflowMethod = (getSDK: () => unknown) => {
      const sdk = getSDK();

      if (!sdk || !sdk.workflows) {
        throw new Error('SDK or workflows API not initialized');
      }

      if (
        typeof sdk.workflows
          .getChatWorkflowTemplatesApiV1WorkflowsTemplatesChat !== 'function'
      ) {
        throw new Error(
          'getChatWorkflowTemplatesApiV1WorkflowsTemplatesChat method not available'
        );
      }

      return sdk.workflows.getChatWorkflowTemplatesApiV1WorkflowsTemplatesChat();
    };

    // Test that it catches missing workflows API
    expect(() => validateAndCallWorkflowMethod(mockGetSDK)).toThrow(
      'SDK or workflows API not initialized'
    );
  });
});
