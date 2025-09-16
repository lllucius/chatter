import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import SSEMonitorPage from '../SSEMonitorPage';
import { useSSE } from '../../services/sse-context';
import { AnySSEEvent } from '../../services/sse-types';

// Mock the SSE context
vi.mock('../../services/sse-context', () => ({
  useSSE: vi.fn(),
}));

// Mock date-fns
vi.mock('date-fns', () => ({
  format: vi.fn((date, formatStr) => {
    if (formatStr === 'HH:mm:ss.SSS') {
      return '12:34:56.789';
    }
    if (formatStr === 'yyyy-MM-dd-HH-mm-ss') {
      return '2024-01-01-12-34-56';
    }
    return '2024-01-01 12:34:56';
  }),
}));

const mockSSEManager = {
  connect: vi.fn(),
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
};

const mockUseSSE = {
  manager: mockSSEManager,
  isConnected: false,
};

const theme = createTheme();

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider theme={theme}>{children}</ThemeProvider>
);

describe('SSEMonitorPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (useSSE as ReturnType<typeof vi.fn>).mockReturnValue(mockUseSSE);
  });

  it('should render monitor page with initial state', () => {
    render(
      <TestWrapper>
        <SSEMonitorPage />
      </TestWrapper>
    );

    expect(screen.getByText('SSE Monitor')).toBeInTheDocument();
    expect(screen.getByText('Start Monitoring')).toBeInTheDocument();
    expect(screen.getByText('Disconnected')).toBeInTheDocument();
    expect(screen.getByText('0')).toBeInTheDocument(); // Total Messages
  });

  it('should start monitoring when start button is clicked', () => {
    render(
      <TestWrapper>
        <SSEMonitorPage />
      </TestWrapper>
    );

    const startButton = screen.getByText('Start Monitoring');
    fireEvent.click(startButton);

    expect(mockSSEManager.addEventListener).toHaveBeenCalledWith('*', expect.any(Function));
    expect(screen.getByText('Stop Monitoring')).toBeInTheDocument();
  });

  it('should stop monitoring when stop button is clicked', () => {
    render(
      <TestWrapper>
        <SSEMonitorPage />
      </TestWrapper>
    );

    // Start monitoring first
    const startButton = screen.getByText('Start Monitoring');
    fireEvent.click(startButton);

    // Then stop monitoring
    const stopButton = screen.getByText('Stop Monitoring');
    fireEvent.click(stopButton);

    expect(mockSSEManager.removeEventListener).toHaveBeenCalledWith('*', expect.any(Function));
    expect(screen.getByText('Start Monitoring')).toBeInTheDocument();
  });

  it('should show connected status when SSE is connected', () => {
    (useSSE as ReturnType<typeof vi.fn>).mockReturnValue({
      ...mockUseSSE,
      isConnected: true,
    });

    render(
      <TestWrapper>
        <SSEMonitorPage />
      </TestWrapper>
    );

    expect(screen.getByText('Connected')).toBeInTheDocument();
  });

  it('should clear messages when clear button is clicked', () => {
    render(
      <TestWrapper>
        <SSEMonitorPage />
      </TestWrapper>
    );

    const clearButton = screen.getByRole('button', { name: /clear messages/i });
    fireEvent.click(clearButton);

    // Should not throw any errors
    expect(screen.getByText('0')).toBeInTheDocument(); // Total Messages remains 0
  });

  it('should toggle console logging when switch is clicked', () => {
    render(
      <TestWrapper>
        <SSEMonitorPage />
      </TestWrapper>
    );

    const consoleSwitch = screen.getByRole('checkbox', { name: /console logging/i });
    expect(consoleSwitch).not.toBeChecked();

    fireEvent.click(consoleSwitch);
    expect(consoleSwitch).toBeChecked();
  });

  it('should update max messages setting', () => {
    render(
      <TestWrapper>
        <SSEMonitorPage />
      </TestWrapper>
    );

    const maxMessagesInput = screen.getByLabelText('Max Messages');
    fireEvent.change(maxMessagesInput, { target: { value: '50' } });

    expect(maxMessagesInput).toHaveValue(50);
  });

  it('should show info alert when not monitoring and no messages', () => {
    render(
      <TestWrapper>
        <SSEMonitorPage />
      </TestWrapper>
    );

    expect(screen.getByText(/Click "Start Monitoring" to begin capturing SSE messages/)).toBeInTheDocument();
  });

  it('should show filter controls correctly', () => {
    render(
      <TestWrapper>
        <SSEMonitorPage />
      </TestWrapper>
    );

    // Check that filter button is present by looking for the button with FilterList icon
    expect(screen.getByRole('button', { name: /filters/i })).toBeInTheDocument();
  });

  it('should toggle raw data view', () => {
    render(
      <TestWrapper>
        <SSEMonitorPage />
      </TestWrapper>
    );

    const toggleButton = screen.getByRole('button', { name: /toggle raw data view/i });
    fireEvent.click(toggleButton);

    // Should not throw any errors - visual change only
    expect(toggleButton).toBeInTheDocument();
  });

  it('should handle SSE manager not available', () => {
    (useSSE as ReturnType<typeof vi.fn>).mockReturnValue({
      manager: null,
      isConnected: false,
    });

    render(
      <TestWrapper>
        <SSEMonitorPage />
      </TestWrapper>
    );

    const startButton = screen.getByText('Start Monitoring');
    expect(startButton).toBeDisabled();
  });

  it('should connect SSE when not connected and monitoring starts', () => {
    render(
      <TestWrapper>
        <SSEMonitorPage />
      </TestWrapper>
    );

    const startButton = screen.getByText('Start Monitoring');
    fireEvent.click(startButton);

    expect(mockSSEManager.connect).toHaveBeenCalled();
  });

  it('should not connect SSE when already connected and monitoring starts', () => {
    (useSSE as ReturnType<typeof vi.fn>).mockReturnValue({
      ...mockUseSSE,
      isConnected: true,
    });

    render(
      <TestWrapper>
        <SSEMonitorPage />
      </TestWrapper>
    );

    const startButton = screen.getByText('Start Monitoring');
    fireEvent.click(startButton);

    expect(mockSSEManager.connect).not.toHaveBeenCalled();
  });
});