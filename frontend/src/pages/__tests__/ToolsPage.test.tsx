import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter as Router } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import ToolsPage from '../ToolsPage';

const theme = createTheme();

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <Router>
      <ThemeProvider theme={theme}>
        {component}
      </ThemeProvider>
    </Router>
  );
};

describe('ToolsPage', () => {
  test('renders tools management page with tabs', () => {
    renderWithProviders(<ToolsPage />);
    
    expect(screen.getByText('Tool Server Management')).toBeInTheDocument();
    expect(screen.getByText('Remote Servers')).toBeInTheDocument();
    expect(screen.getByText('Available Tools')).toBeInTheDocument();
  });

  test('displays servers tab by default', () => {
    renderWithProviders(<ToolsPage />);
    
    expect(screen.getByText('Add Remote Server')).toBeInTheDocument();
    expect(screen.getByText('Remote MCP Servers')).toBeInTheDocument();
  });

  test('switches to tools tab when clicked', () => {
    renderWithProviders(<ToolsPage />);
    
    const toolsTab = screen.getByText('Available Tools');
    fireEvent.click(toolsTab);
    
    // Verify tab switched correctly by checking tab is selected
    expect(toolsTab).toHaveAttribute('aria-selected', 'true');
  });
});