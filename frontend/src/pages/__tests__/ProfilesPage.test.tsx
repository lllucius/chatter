import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { vi, describe, test, expect } from 'vitest';
import ProfilesPage from '../ProfilesPage';

// Mock the getSDK function and authService
vi.mock('../../services/auth-service', (): void => ({
  getSDK: vi.fn((): void => ({
    profiles: {
      listProfilesApiV1Profiles: vi.fn().mockResolvedValue({
        profiles: [],
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

const renderProfilesPage = () => {
  return render(
    <BrowserRouter>
      <ThemeProvider theme={theme}>
        <ProfilesPage />
      </ThemeProvider>
    </BrowserRouter>
  );
};

describe('ProfilesPage', () => {
  test('renders Profile Management page title', async () => {
    renderProfilesPage();

    expect(await screen.findByText('Profile Management')).toBeInTheDocument();
  });

  test('renders toolbar with Add Profile button', async () => {
    renderProfilesPage();

    expect(await screen.findByText('Add Profile')).toBeInTheDocument();
  });

  test('renders toolbar with Refresh button', async () => {
    renderProfilesPage();

    expect(await screen.findByText('Refresh')).toBeInTheDocument();
  });
});
