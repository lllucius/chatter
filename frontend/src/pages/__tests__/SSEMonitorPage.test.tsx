import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import SSEMonitorPage from '../SSEMonitorPage';
import { useSSE } from '../../services/sse-context';

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

    expect(mockSSEManager.addEventListener).toHaveBeenCalledWith(
      '*',
      expect.any(Function)
    );
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

    expect(mockSSEManager.removeEventListener).toHaveBeenCalledWith(
      '*',
      expect.any(Function)
    );
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

    const consoleSwitch = screen.getByRole('checkbox', {
      name: /console logging/i,
    });
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

    expect(
      screen.getByText(
        /Click "Start Monitoring" to begin capturing SSE messages/
      )
    ).toBeInTheDocument();
  });

  it('should show filter controls correctly', () => {
    render(
      <TestWrapper>
        <SSEMonitorPage />
      </TestWrapper>
    );

    // Check that filter button is present by looking for the button with FilterList icon
    expect(
      screen.getByRole('button', { name: /filters/i })
    ).toBeInTheDocument();
  });

  it('should toggle raw data view', () => {
    render(
      <TestWrapper>
        <SSEMonitorPage />
      </TestWrapper>
    );

    const toggleButton = screen.getByRole('button', {
      name: /toggle raw data view/i,
    });
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

  it('should expand and collapse advanced filters', () => {
    render(
      <TestWrapper>
        <SSEMonitorPage />
      </TestWrapper>
    );

    const filtersButton = screen.getByRole('button', { name: /filters/i });
    fireEvent.click(filtersButton);

    // Advanced filters should now be visible
    expect(screen.getByText('Filter Options')).toBeInTheDocument();
    expect(screen.getByText('Event Types')).toBeInTheDocument();

    // Click again to collapse
    fireEvent.click(filtersButton);
  });

  it('should save and load settings from localStorage', () => {
    // Mock localStorage with proper implementation
    const localStorageData: Record<string, string> = {};
    const mockLocalStorage = {
      getItem: vi.fn((key: string) => localStorageData[key] || null),
      setItem: vi.fn((key: string, value: string) => {
        localStorageData[key] = value;
      }),
    };
    Object.defineProperty(window, 'localStorage', {
      value: mockLocalStorage,
      configurable: true,
    });

    // Pre-populate with test settings
    localStorageData['sse-monitor-settings'] = JSON.stringify({
      consoleLogging: true,
      maxMessages: 250,
      showRawData: true,
      showAdvancedFilters: true,
      filters: {
        eventTypes: ['test.event'],
        categories: ['testing'],
        priorities: ['high'],
        userIds: ['user123'],
        sourceSystems: ['test-system'],
      },
    });

    render(
      <TestWrapper>
        <SSEMonitorPage />
      </TestWrapper>
    );

    // Check that settings were loaded
    expect(mockLocalStorage.getItem).toHaveBeenCalledWith(
      'sse-monitor-settings'
    );

    // Check console logging switch is checked
    const consoleSwitch = screen.getByRole('checkbox', {
      name: /console logging/i,
    });
    expect(consoleSwitch).toBeChecked();

    // Check max messages field has correct value
    const maxMessagesInput = screen.getByLabelText('Max Messages');
    expect(maxMessagesInput).toHaveValue(250);
  });

  it('should show active filter count', () => {
    render(
      <TestWrapper>
        <SSEMonitorPage />
      </TestWrapper>
    );

    // Check for Active Filters section specifically
    expect(screen.getByText('Active Filters')).toBeInTheDocument();

    // Find the Active Filters count - should be 0 with default state
    const activeFiltersText = screen.getByText('Active Filters');
    const statsCard = activeFiltersText.closest(
      '[class*="MuiCardContent-root"]'
    );
    expect(statsCard).toBeInTheDocument();
  });

  it('should update max messages in settings', () => {
    render(
      <TestWrapper>
        <SSEMonitorPage />
      </TestWrapper>
    );

    const maxMessagesInput = screen.getByLabelText('Max Messages');
    fireEvent.change(maxMessagesInput, { target: { value: '200' } });

    expect(maxMessagesInput).toHaveValue(200);
  });
});
