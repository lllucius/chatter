import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { describe, test, expect } from 'vitest';
import PromptsPage from '../PromptsPage';

// Mock the getSDK function and authService
vi.mock('../../services/auth-service', (): void => ({
  getSDK: vi.fn((): void => ({
    prompts: {
      listPromptsApiV1Prompts: vi.fn().mockResolvedValue({
        prompts: [],
        total_count: 0,
      }),
    },
  })),
  authService: {
    isAuthenticated: vi.fn(() => true),
  },
}));

// Mock the toast service
vi.mock('../../services/toast-service', (): void => ({
  toastService: {
    error: vi.fn(),
    success: vi.fn(),
  },
}));

const theme = createTheme();

const renderPromptsPage = () => {
  return render(
    <BrowserRouter>
      <ThemeProvider theme={theme}>
        <PromptsPage />
      </ThemeProvider>
    </BrowserRouter>
  );
};

describe('PromptsPage', () => {
  test('renders Prompts page title', async () => {
    renderPromptsPage();

    expect(await screen.findByText('Prompts')).toBeInTheDocument();
  });

  test('renders toolbar with Add Prompt button', async () => {
    renderPromptsPage();

    expect(await screen.findByText('Add Prompt')).toBeInTheDocument();
  });

  test('renders toolbar with Refresh button', async () => {
    renderPromptsPage();

    expect(await screen.findByText('Refresh')).toBeInTheDocument();
  });
});
