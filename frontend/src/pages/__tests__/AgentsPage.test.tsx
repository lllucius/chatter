import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { vi, describe, test, expect } from 'vitest';
import AgentsPage from '../AgentsPage';

// Mock the getSDK function and authService
vi.mock('../../services/auth-service', () => ({
  getSDK: vi.fn(() => ({
    agents: {
      listAgentsApiV1Agents: vi.fn().mockResolvedValue({
        data: []
      })
    }
  })),
  authService: {
    isAuthenticated: vi.fn(() => true)
  }
}));

// Mock the toast service
vi.mock('../../services/toast-service', () => ({
  toastService: {
    error: vi.fn(),
    success: vi.fn(),
  }
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
});
