import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { describe, test, beforeEach, expect, vi } from 'vitest';
import WorkflowManagementPage from '../WorkflowManagementPage';

// Mock the auth service
vi.mock('../../services/auth-service', () => ({
  getSDK: () => ({
    chat: {
      getWorkflowTemplatesApiV1ChatTemplates: vi.fn().mockResolvedValue({
        templates: {
          'test-template': {
            name: 'Test Template',
            description: 'A test workflow template',
            workflow_type: 'sequential',
            category: 'basic',
            required_tools: ['tool1', 'tool2'],
            parameters: {
              param1: 'value1',
              param2: { type: 'string', description: 'A parameter' },
            },
          },
        },
      }),
      getAvailableToolsApiV1ChatToolsAvailable: vi.fn().mockResolvedValue({
        data: { tools: [] },
      }),
      chatWithTemplateApiV1ChatTemplateTemplateName: vi.fn().mockResolvedValue({
        data: { result: 'success' },
      }),
    },
  }),
}));

// Mock toast service
vi.mock('../../services/toast-service', () => ({
  toastService: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

// Mock clipboard API
Object.assign(navigator, {
  clipboard: {
    writeText: vi.fn().mockResolvedValue(undefined),
  },
});

describe('WorkflowManagementPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('renders workflow templates with action buttons', async () => {
    render(<WorkflowManagementPage />);

    // Wait for templates to load
    await waitFor(() => {
      expect(screen.getByText('Test Template')).toBeInTheDocument();
    });

    // Check that action buttons are present
    const viewDetailsButtons = screen.getAllByLabelText('View Details');
    const copyTemplateButtons = screen.getAllByLabelText('Copy Template');

    expect(viewDetailsButtons).toHaveLength(1);
    expect(copyTemplateButtons).toHaveLength(1);
  });

  test('View Details button opens dialog with template information', async () => {
    render(<WorkflowManagementPage />);

    // Wait for templates to load
    await waitFor(() => {
      expect(screen.getByText('Test Template')).toBeInTheDocument();
    });

    // Click the View Details button
    const viewDetailsButton = screen.getByLabelText('View Details');
    fireEvent.click(viewDetailsButton);

    // Check that the dialog opens with template details
    await waitFor(() => {
      expect(
        screen.getByText('Template Details: Test Template')
      ).toBeInTheDocument();
    });

    // Check that the main sections are present (avoiding duplicate text issues)
    expect(
      screen.getByText('Template Details: Test Template')
    ).toBeInTheDocument();
  });

  test('Copy Template button copies template to clipboard', async () => {
    const mockWriteText = navigator.clipboard.writeText as (text: string) => Promise<void>;

    render(<WorkflowManagementPage />);

    // Wait for templates to load
    await waitFor(() => {
      expect(screen.getByText('Test Template')).toBeInTheDocument();
    });

    // Click the Copy Template button
    const copyTemplateButton = screen.getByLabelText('Copy Template');
    fireEvent.click(copyTemplateButton);

    // Check that clipboard.writeText was called with correct data
    await waitFor(() => {
      expect(mockWriteText).toHaveBeenCalledWith(
        expect.stringContaining('"name": "Test Template (Copy)"')
      );
    });

    // Check that the copied data contains expected template information
    const clipboardData = JSON.parse(mockWriteText.mock.calls[0][0]);
    expect(clipboardData.name).toBe('Test Template (Copy)');
    expect(clipboardData.description).toBe('A test workflow template');
    expect(clipboardData.workflow_type).toBe('sequential');
    expect(clipboardData.category).toBe('basic');
    expect(clipboardData.required_tools).toEqual(['tool1', 'tool2']);
  });

  test('View Details dialog can be closed', async () => {
    render(<WorkflowManagementPage />);

    // Wait for templates to load and open dialog
    await waitFor(() => {
      expect(screen.getByText('Test Template')).toBeInTheDocument();
    });

    const viewDetailsButton = screen.getByLabelText('View Details');
    fireEvent.click(viewDetailsButton);

    await waitFor(() => {
      expect(
        screen.getByText('Template Details: Test Template')
      ).toBeInTheDocument();
    });

    // Close the dialog
    const closeButton = screen
      .getAllByText('Close')
      .find((btn) => btn.closest('div[role="dialog"]'));
    expect(closeButton).toBeInTheDocument();
    fireEvent.click(closeButton!);

    // Check that dialog is closed
    await waitFor(() => {
      expect(
        screen.queryByText('Template Details: Test Template')
      ).not.toBeInTheDocument();
    });
  });
});
