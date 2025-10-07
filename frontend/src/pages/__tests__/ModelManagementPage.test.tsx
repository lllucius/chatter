import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { describe, test, expect, vi } from 'vitest';
import ModelManagementPage from '../ModelManagementPage';

// Mock the getSDK function and authService
vi.mock('../../services/auth-service', () => ({
  getSDK: vi.fn(() => ({
    modelRegistry: {
      listProvidersApiV1ModelsProviders: vi.fn().mockResolvedValue({
        providers: [],
        total: 0,
        page: 1,
        per_page: 10,
      }),
      listModelsApiV1ModelsModels: vi.fn().mockResolvedValue({
        models: [],
        total: 0,
        page: 1,
        per_page: 10,
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

const renderModelManagementPage = () => {
  return render(
    <BrowserRouter>
      <ThemeProvider theme={theme}>
        <ModelManagementPage />
      </ThemeProvider>
    </BrowserRouter>
  );
};

describe('ModelManagementPage', () => {
  test('renders Model Management page title', async () => {
    renderModelManagementPage();

    expect(await screen.findByText('Model Management')).toBeInTheDocument();
  });

  test('renders Providers and Models tabs', async () => {
    renderModelManagementPage();

    expect(await screen.findByText('Providers')).toBeInTheDocument();
    expect(await screen.findByText('Models')).toBeInTheDocument();
  });

  test('passes correct pagination parameters to SDK for providers (1-based page number)', async () => {
    const mockListProviders = vi.fn().mockResolvedValue({
      providers: [],
      total: 0,
      page: 1,
      per_page: 10,
    });

    // Import the module to get the mock
    const { getSDK } = await import('../../services/auth-service');
    vi.mocked(getSDK).mockReturnValue({
      modelRegistry: {
        listProvidersApiV1ModelsProviders: mockListProviders,
        listModelsApiV1ModelsModels: vi.fn().mockResolvedValue({
          models: [],
          total: 0,
        }),
      },
    } as unknown as ReturnType<typeof getSDK>);

    renderModelManagementPage();

    // Wait for the component to call the API
    await new Promise((resolve) => setTimeout(resolve, 100));

    // Verify the API was called with page=1 (not page=0)
    // CrudDataTable starts with page=0, but we convert it to page=1 for the API
    expect(mockListProviders).toHaveBeenCalledWith({
      activeOnly: false,
      page: 1, // This should be 1, not 0
      perPage: 10,
    });
  });

  test('converts 0-based page index to 1-based page number for API', async () => {
    // This test verifies the fix for the pagination issue where:
    // - CrudDataTable uses 0-based page indexing (page starts at 0)
    // - The API expects 1-based page numbers (page >= 1)
    // - We need to add 1 to the page index when calling the API
    
    const mockListProviders = vi.fn().mockResolvedValue({
      providers: [],
      total: 0,
      page: 1,
      per_page: 10,
    });

    // Import the module to get the mock
    const { getSDK } = await import('../../services/auth-service');
    vi.mocked(getSDK).mockReturnValue({
      modelRegistry: {
        listProvidersApiV1ModelsProviders: mockListProviders,
        listModelsApiV1ModelsModels: vi.fn().mockResolvedValue({
          models: [],
          total: 0,
        }),
      },
    } as unknown as ReturnType<typeof getSDK>);

    renderModelManagementPage();

    // Wait for the component to call the API
    await new Promise((resolve) => setTimeout(resolve, 100));

    // Verify the API was called with page=1 when CrudDataTable page index is 0
    // This confirms the fix: page: page + 1
    expect(mockListProviders).toHaveBeenCalledWith({
      activeOnly: false,
      page: 1, // This should be 1 (not 0), confirming page index + 1 conversion
      perPage: 10,
    });
  });
});
