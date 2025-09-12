import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import EnhancedMessage, { ChatMessage } from '../EnhancedMessage';

describe('EnhancedMessage', () => {
  const mockProps = {
    onEdit: () => {},
    onRegenerate: () => {},
    onDelete: () => {},
    onRate: () => {},
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

      render(<EnhancedMessage message={undefinedTimestampMessage} {...mockProps} />);
      
      // Should display fallback --:-- for undefined timestamp
      expect(screen.getByText('--:--')).toBeInTheDocument();
    });
  });
});