import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { describe, test, expect } from 'vitest';
import AgentsPage from '../AgentsPage';

// Mock the getSDK function and authService
vi.mock('../../services/auth-service', () => ({
  getSDK: vi.fn(() => ({
    agents: {
      listAgentsApiV1Agents: vi.fn().mockResolvedValue({
        data: [],
      }),
    },
  })),
  authService: {
    isAuthenticated: vi.fn(() => true),
  },
}));

// Mock the toast service
vi.mock('../../services/toast-service', () => ({
  toastService: {
    error: vi.fn(),
    success: vi.fn(),
  },
}));

const theme = createTheme();

const renderAgentsPage = () => {
  return render(
    <BrowserRouter>
      <ThemeProvider theme={theme}>
        <AgentsPage />
      </ThemeProvider>
    </BrowserRouter>
  );
};

describe('AgentsPage', () => {
  test('renders AI Agents page title', async () => {
    renderAgentsPage();

    expect(await screen.findByText('AI Agents')).toBeInTheDocument();
  });

  test('renders toolbar with Add Agent button', async () => {
    renderAgentsPage();

    expect(await screen.findByText('Add Agent')).toBeInTheDocument();
  });

  test('renders toolbar with Refresh button', async () => {
    renderAgentsPage();

    expect(await screen.findByText('Refresh')).toBeInTheDocument();
  });

  test('passes correct pagination parameters to SDK', async () => {
    const mockListAgents = vi.fn().mockResolvedValue({
      data: [],
    });

    // Import the module to get the mock
    const { getSDK } = await import('../../services/auth-service');
    vi.mocked(getSDK).mockReturnValue({
      agents: {
        listAgentsApiV1Agents: mockListAgents,
      },
    } as { agents: { listAgentsApiV1Agents: unknown } });

    renderAgentsPage();

    // Wait for the component to call the API
    await new Promise((resolve) => setTimeout(resolve, 100));

    // Verify the API was called with correct pagination structure
    expect(mockListAgents).toHaveBeenCalledWith({
      pagination: {
        limit: 10,
        offset: 0,
      },
    });
  });
});
