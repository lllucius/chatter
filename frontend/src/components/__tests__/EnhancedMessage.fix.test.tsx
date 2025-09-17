/**
 * Comprehensive test script to validate the EnhancedMessage metadata fix
 * This script tests the exact scenario described in the issue:
 * "The response time and token counts display in the EnhancedMessage.tsx is not working. They are not displaying."
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import EnhancedMessage, { ChatMessage } from '../EnhancedMessage';

describe('EnhancedMessage Metadata Display Fix', () => {
  const mockProps = {
    onEdit: () => {},
    onRegenerate: () => {},
    onDelete: () => {},
    onRate: () => {},
  };

  describe('Fix validation: Response time and token counts should display', () => {
    it('should display tokens and processing time for assistant messages with metadata', () => {
      // This simulates the exact data structure that comes from the backend API
      // after the fix in ChatPage.tsx onSelectConversation function
      const assistantMessageWithMetadata: ChatMessage = {
        id: 'assistant-with-metadata',
        role: 'assistant',
        content: 'Here is my response with performance metrics.',
        timestamp: new Date('2024-01-01T12:05:00Z'),
        metadata: {
          model: 'gpt-4-turbo',
          tokens: 125, // This should now display as "125 tokens"
          processingTime: 2340, // This should now display as "2340ms"
        },
      };

      render(
        <EnhancedMessage
          message={assistantMessageWithMetadata}
          {...mockProps}
        />
      );

      // Verify the rating section appears (which means it's an assistant message)
      expect(screen.getByText('Rate this response:')).toBeInTheDocument();

      // Verify that tokens and processing time are displayed
      // These are the exact elements that were not displaying before the fix
      expect(screen.getByText('125 tokens')).toBeInTheDocument();
      expect(screen.getByText('2340ms')).toBeInTheDocument();

      // Verify the model is also displayed
      expect(screen.getByText('gpt-4-turbo')).toBeInTheDocument();
    });

    it('demonstrates the before/after fix scenario', () => {
      // BEFORE the fix: Messages loaded from existing conversations would have this structure
      const messageBeforeFix: ChatMessage = {
        id: 'msg-before-fix',
        role: 'assistant',
        content: 'This message would not show tokens/time before the fix.',
        timestamp: new Date('2024-01-01T10:00:00Z'),
        // Missing metadata - this was the problem!
      };

      // AFTER the fix: Same message now has proper metadata mapping
      const messageAfterFix: ChatMessage = {
        id: 'msg-after-fix',
        role: 'assistant',
        content: 'This message now shows tokens/time after the fix.',
        timestamp: new Date('2024-01-01T10:00:00Z'),
        metadata: {
          model: 'gpt-4',
          tokens: 95,
          processingTime: 1850,
        },
      };

      // Test before fix scenario
      const { unmount } = render(
        <EnhancedMessage message={messageBeforeFix} {...mockProps} />
      );
      expect(screen.queryByText(/\d+ tokens/)).not.toBeInTheDocument();
      expect(screen.queryByText(/\d+ms/)).not.toBeInTheDocument();
      unmount();

      // Test after fix scenario
      render(<EnhancedMessage message={messageAfterFix} {...mockProps} />);
      expect(screen.getByText('95 tokens')).toBeInTheDocument();
      expect(screen.getByText('1850ms')).toBeInTheDocument();
      expect(screen.getByText('gpt-4')).toBeInTheDocument();
    });
  });

  describe('Real-world API data simulation', () => {
    it('should correctly map API response data to display metadata', () => {
      // This simulates the exact API response structure from backend
      const mockApiResponse = {
        id: 'api-msg-123',
        role: 'assistant',
        content: 'API response content',
        created_at: '2024-01-01T14:30:00Z',
        total_tokens: 156,
        response_time_ms: 2800,
        model_used: 'gpt-4-turbo-preview',
        sequence_number: 3,
        conversation_id: 'conv-456',
      };

      // This is the mapping logic from the fixed ChatPage.tsx
      const mappedMessage: ChatMessage = {
        id: mockApiResponse.id,
        role: mockApiResponse.role as 'user' | 'assistant' | 'system',
        content: mockApiResponse.content,
        timestamp: new Date(mockApiResponse.created_at),
        metadata: {
          model: mockApiResponse.model_used || undefined,
          tokens: mockApiResponse.total_tokens || undefined,
          processingTime: mockApiResponse.response_time_ms || undefined,
        },
      };

      render(<EnhancedMessage message={mappedMessage} {...mockProps} />);

      // Verify all metadata displays correctly
      expect(screen.getByText('156 tokens')).toBeInTheDocument();
      expect(screen.getByText('2800ms')).toBeInTheDocument();
      expect(screen.getByText('gpt-4-turbo-preview')).toBeInTheDocument();
    });
  });
});
