import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { describe, test, expect, beforeEach } from 'vitest';
import ABTestingPage from '../ABTestingPage';

// Mock the getSDK function and authService
vi.mock('../../services/auth-service', (): void => ({
  getSDK: vi.fn((): void => ({
    abTesting: {
      listAbTestsApiV1AbTests: vi.fn().mockResolvedValue({
        tests: [],
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

const renderABTestingPage = () => {
  return render(
    <BrowserRouter>
      <ThemeProvider theme={theme}>
        <ABTestingPage />
      </ThemeProvider>
    </BrowserRouter>
  );
};

describe('ABTestingPage', () => {
  test('renders AB Testing page title', async () => {
    renderABTestingPage();

    // Wait for the component to load
    expect(await screen.findByText('A/B Testing')).toBeInTheDocument();
  });

  test('renders create test button', async () => {
    renderABTestingPage();

    expect(await screen.findByText('Create Test')).toBeInTheDocument();
  });

  test('renders refresh button', async () => {
    renderABTestingPage();

    expect(await screen.findByText('Refresh')).toBeInTheDocument();
  });

  test('shows empty state when no tests exist', async () => {
    renderABTestingPage();

    expect(await screen.findByText(/No AB tests found/)).toBeInTheDocument();
  });
});
