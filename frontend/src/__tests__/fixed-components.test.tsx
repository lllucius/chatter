import React from 'react';
import { render, screen } from '@testing-library/react';
import { vi } from 'vitest';
import WorkflowManagementPage from '../pages/WorkflowManagementPage';
import ChatConfigPanel from '../pages/ChatConfigPanel';

// Mock the client to prevent actual API calls
vi.mock('../services/auth-service', () => ({
  getSDK: vi.fn(() => ({
    chat: {
      getWorkflowTemplatesApiV1ChatTemplatesGet: vi
        .fn()
        .mockResolvedValue({ templates: {} }),
      getAvailableToolsApiV1ChatToolsAvailableGet: vi
        .fn()
        .mockResolvedValue({ data: { tools: [] } }),
      listConversationsApiV1ChatConversationsGet: vi
        .fn()
        .mockResolvedValue({ conversations: [] }),
    },
  })),
  authService: {
    isAuthenticated: vi.fn(() => true),
  },
}));

// Mock toast service
vi.mock('../services/toast-service', () => ({
  toastService: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

// Mock PageLayout
vi.mock('../components/PageLayout', () => ({
  default: ({
    children,
    title,
  }: {
    children: React.ReactNode;
    title: string;
  }) => (
    <div data-testid="page-layout" title={title}>
      {children}
    </div>
  ),
}));

// Mock WorkflowEditor
vi.mock('../components/workflow/WorkflowEditor', (): void => ({
  default: (): void => (
    <div data-testid="workflow-editor">WorkflowEditor Mock</div>
  ),
}));

// Mock RightSidebarContext
vi.mock('../components/RightSidebarContext', (): void => ({
  useRightSidebar: (): void => ({ collapsed: false, setCollapsed: vi.fn() }),
}));

describe('Fixed Components - No Infinite Loops', () => {
  test('WorkflowManagementPage renders without infinite loop', async () => {
    const { unmount } = render(<WorkflowManagementPage />);

    // Wait a bit to ensure no infinite loops occur
    await new Promise((resolve) => setTimeout(resolve, 100));

    expect(screen.getByTestId('page-layout')).toBeInTheDocument();

    // Component should not crash or cause infinite re-renders
    unmount();
  });

  test('ChatConfigPanel renders without infinite loop', async () => {
    const mockProps = {
      profiles: [],
      prompts: [],
      documents: [],
      currentConversation: null,
      selectedProfile: '',
      setSelectedProfile: vi.fn(),
      selectedPrompt: '',
      setSelectedPrompt: vi.fn(),
      selectedDocuments: [],
      setSelectedDocuments: vi.fn(),
      temperature: 0.7,
      setTemperature: vi.fn(),
      maxTokens: 1000,
      setMaxTokens: vi.fn(),
      enableRetrieval: false,
      setEnableRetrieval: vi.fn(),
      onSelectConversation: vi.fn(),
    };

    const { unmount } = render(<ChatConfigPanel {...mockProps} />);

    // Wait a bit to ensure no infinite loops occur
    await new Promise((resolve) => setTimeout(resolve, 100));

    expect(screen.getByText('Conversations')).toBeInTheDocument();

    // Component should not crash or cause infinite re-renders
    unmount();
  });
});
