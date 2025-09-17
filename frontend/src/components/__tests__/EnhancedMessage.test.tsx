import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import EnhancedMessage, { ChatMessage } from '../EnhancedMessage';

describe('EnhancedMessage', () => {
  const mockProps = {
    onEdit: () => {
      // Mock function for testing
    },
    onRegenerate: () => {
      // Mock function for testing
    },
    onDelete: () => {
      // Mock function for testing
    },
    onRate: () => {
      // Mock function for testing
    },
  };

  describe('timestamp formatting', () => {
    it('should display formatted time for valid timestamps', () => {
      const validMessage: ChatMessage = {
        id: '1',
        role: 'user',
        content: 'Test message',
        timestamp: new Date('2023-01-01T10:30:00Z'),
      };

      render(<EnhancedMessage message={validMessage} {...mockProps} />);

      // The exact time displayed depends on timezone, but it should not be --:--
      const timeElement = screen.getByText(/\d{2}:\d{2}/);
      expect(timeElement).toBeInTheDocument();
    });

    it('should display fallback time for invalid timestamps', () => {
      const invalidMessage: ChatMessage = {
        id: '2',
        role: 'user',
        content: 'Test message with invalid timestamp',
        timestamp: new Date('invalid-date'),
      };

      render(<EnhancedMessage message={invalidMessage} {...mockProps} />);

      // Should display fallback --:-- for invalid date
      expect(screen.getByText('--:--')).toBeInTheDocument();
    });

    it('should display fallback time for null timestamps', () => {
      const nullTimestampMessage: ChatMessage = {
        id: '3',
        role: 'user',
        content: 'Test message with null timestamp',
        timestamp: null as unknown as Date, // Simulating null timestamp from API
      };

      render(<EnhancedMessage message={nullTimestampMessage} {...mockProps} />);

      // Should display fallback --:-- for null timestamp
      expect(screen.getByText('--:--')).toBeInTheDocument();
    });

    it('should display fallback time for undefined timestamps', () => {
      const undefinedTimestampMessage: ChatMessage = {
        id: '4',
        role: 'user',
        content: 'Test message with undefined timestamp',
        timestamp: undefined as unknown as Date, // Simulating undefined timestamp from API
      };

      render(
        <EnhancedMessage message={undefinedTimestampMessage} {...mockProps} />
      );

      // Should display fallback --:-- for undefined timestamp
      expect(screen.getByText('--:--')).toBeInTheDocument();
    });
  });

  describe('Layout and Token/Time Display', () => {
    it('should display timestamp in top-right for user messages', () => {
      const userMessage: ChatMessage = {
        id: 'user1',
        role: 'user',
        content: 'Hello there',
        timestamp: new Date('2024-01-01T12:00:00Z'),
      };

      render(<EnhancedMessage message={userMessage} {...mockProps} />);

      // Should show timestamp in top area
      expect(screen.getByText(/12:00/)).toBeInTheDocument();
      // Should not show rating section for user messages
      expect(screen.queryByText('Rate this response:')).not.toBeInTheDocument();
    });

    it('should display timestamp in top-right and tokens/time with rating for assistant messages', () => {
      const assistantMessage: ChatMessage = {
        id: 'assistant1',
        role: 'assistant',
        content: 'Hello! How can I help you?',
        timestamp: new Date('2024-01-01T12:05:00Z'),
        metadata: {
          model: 'GPT-4',
          tokens: 25,
          processingTime: 500,
        },
      };

      render(<EnhancedMessage message={assistantMessage} {...mockProps} />);

      // Should show timestamp in top area
      expect(screen.getByText(/12:05/)).toBeInTheDocument();

      // Should show rating section
      expect(screen.getByText('Rate this response:')).toBeInTheDocument();

      // Should show tokens and processing time in the same area as rating
      expect(screen.getByText('25 tokens')).toBeInTheDocument();
      expect(screen.getByText('500ms')).toBeInTheDocument();
    });

    it('should display timestamp and rating without tokens/time when metadata is missing', () => {
      const assistantMessage: ChatMessage = {
        id: 'assistant2',
        role: 'assistant',
        content: 'Response without metadata',
        timestamp: new Date('2024-01-01T12:10:00Z'),
      };

      render(<EnhancedMessage message={assistantMessage} {...mockProps} />);

      // Should show timestamp in top area
      expect(screen.getByText(/12:10/)).toBeInTheDocument();

      // Should show rating section
      expect(screen.getByText('Rate this response:')).toBeInTheDocument();

      // Should not show tokens or processing time
      expect(screen.queryByText(/tokens/)).not.toBeInTheDocument();
      expect(screen.queryByText(/ms/)).not.toBeInTheDocument();
    });

    it('should display only some metadata when partially available', () => {
      const assistantMessage: ChatMessage = {
        id: 'assistant3',
        role: 'assistant',
        content: 'Response with partial metadata',
        timestamp: new Date('2024-01-01T12:15:00Z'),
        metadata: {
          tokens: 42,
          // processingTime is missing
        },
      };

      render(<EnhancedMessage message={assistantMessage} {...mockProps} />);

      // Should show timestamp in top area
      expect(screen.getByText(/12:15/)).toBeInTheDocument();

      // Should show rating section
      expect(screen.getByText('Rate this response:')).toBeInTheDocument();

      // Should show only tokens
      expect(screen.getByText('42 tokens')).toBeInTheDocument();
      expect(screen.queryByText(/\d+ms/)).not.toBeInTheDocument();
    });
  });
});
