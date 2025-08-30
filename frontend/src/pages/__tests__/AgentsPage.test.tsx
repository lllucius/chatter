import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import AgentsPage from '../AgentsPage';
import { chatterSDK } from '../../services/chatter-sdk';

// Mock dependencies
vi.mock('../../services/chatter-sdk', () => ({
  chatterSDK: {
    isAuthenticated: vi.fn(() => true),
    agents: {
      listAgentsApiV1AgentsGet: vi.fn(),
      createAgentApiV1AgentsPost: vi.fn(),
      updateAgentApiV1AgentsAgentIdPut: vi.fn(),
      deleteAgentApiV1AgentsAgentIdDelete: vi.fn(),
      getAgentApiV1AgentsAgentIdGet: vi.fn(),
    }
  }
}));

const theme = createTheme();

const mockAgents = [
  {
    id: '1',
    name: 'Customer Support Agent',
    description: 'Handles customer inquiries',
    agent_type: 'conversational',
    status: 'active',
    config: {},
    created_at: '2024-01-01T10:00:00Z',
    updated_at: '2024-01-01T10:00:00Z',
  }
];

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>
    <ThemeProvider theme={theme}>
      {children}
    </ThemeProvider>
  </BrowserRouter>
);

describe('AgentsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(chatterSDK.agents.listAgentsApiV1AgentsGet).mockResolvedValue({
      data: { agents: mockAgents }
    } as any);
  });

  it('renders agents page correctly', async () => {
    render(
      <TestWrapper>
        <AgentsPage />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('AI Agents Management')).toBeInTheDocument();
    });
  });

  it('loads and displays agents', async () => {
    render(
      <TestWrapper>
        <AgentsPage />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Customer Support Agent')).toBeInTheDocument();
    });

    expect(chatterSDK.agents.listAgentsApiV1AgentsGet).toHaveBeenCalledTimes(1);
  });

  it('handles API errors gracefully', async () => {
    vi.mocked(chatterSDK.agents.listAgentsApiV1AgentsGet).mockRejectedValue(
      new Error('API Error')
    );

    render(
      <TestWrapper>
        <AgentsPage />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/Failed to load agents/)).toBeInTheDocument();
    });
  });
});