import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { vi, describe, test, expect, beforeEach } from 'vitest';
import { fireEvent } from '@testing-library/react';
import ToolsPageRefactored from '../ToolsPageRefactored';

// Mock the getSDK function and authService
vi.mock('../../services/auth-service', () => ({
  getSDK: vi.fn(() => ({
    toolServers: {
      listToolServersApiV1ToolserversServers: vi.fn().mockResolvedValue([]),
      listAllToolsApiV1ToolserversToolsAll: vi.fn().mockResolvedValue([])
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

const renderToolsPage = () => {
  return render(
    <BrowserRouter>
      <ThemeProvider theme={theme}>
        <ToolsPageRefactored />
      </ThemeProvider>
    </BrowserRouter>
  );
};

describe('ToolsPageRefactored', () => {
  test('renders Tool Server Management page title', async () => {
    renderToolsPage();
    
    expect(await screen.findByText('Tool Server Management')).toBeInTheDocument();
  });

  test('renders toolbar with Refresh button', async () => {
    renderToolsPage();
    
    expect(await screen.findByText('Refresh')).toBeInTheDocument();
  });

  test('renders Add Remote Server button on Remote Servers tab', async () => {
    renderToolsPage();
    
    expect(await screen.findByText('Add Remote Server')).toBeInTheDocument();
  });

  test('renders Add Tool button on Available Tools tab', async () => {
    renderToolsPage();
    
    // Click on Available Tools tab
    const toolsTab = await screen.findByText('Available Tools');
    fireEvent.click(toolsTab);
    
    // Check that Add Tool button appears
    expect(await screen.findByText('Add Tool')).toBeInTheDocument();
    
    // Check that Add Remote Server button is not visible
    expect(screen.queryByText('Add Remote Server')).not.toBeInTheDocument();
  });

  test('shows correct button on tab switch back to Remote Servers', async () => {
    renderToolsPage();
    
    // Click on Available Tools tab first
    const toolsTab = await screen.findByText('Available Tools');
    fireEvent.click(toolsTab);
    
    // Then click back on Remote Servers tab
    const serversTab = await screen.findByText('Remote Servers');
    fireEvent.click(serversTab);
    
    // Check that Add Remote Server button appears again
    expect(await screen.findByText('Add Remote Server')).toBeInTheDocument();
    
    // Check that Add Tool button is not visible
    expect(screen.queryByText('Add Tool')).not.toBeInTheDocument();
  });
});