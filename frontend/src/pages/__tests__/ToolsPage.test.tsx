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
    
    expect(screen.getByText('Tools Management')).toBeInTheDocument();
    expect(screen.getByText('Servers')).toBeInTheDocument();
    expect(screen.getByText('Tools')).toBeInTheDocument();
  });

  test('displays servers tab by default', () => {
    renderWithProviders(<ToolsPage />);
    
    expect(screen.getByText('Add Server')).toBeInTheDocument();
    expect(screen.getByText('File Operations Server')).toBeInTheDocument();
    expect(screen.getByText('Web Search Server')).toBeInTheDocument();
  });

  test('switches to tools tab when clicked', () => {
    renderWithProviders(<ToolsPage />);
    
    const toolsTab = screen.getByText('Tools');
    fireEvent.click(toolsTab);
    
    expect(screen.getByText('Read File')).toBeInTheDocument();
    expect(screen.getByText('Write File')).toBeInTheDocument();
    expect(screen.getByText('Web Search')).toBeInTheDocument();
  });
});