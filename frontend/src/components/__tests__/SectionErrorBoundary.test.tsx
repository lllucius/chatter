import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import SectionErrorBoundary from '../SectionErrorBoundary';
import { errorHandler } from '../../utils/error-handler';

// Mock the error handler
vi.mock('../../utils/error-handler', () => ({
  errorHandler: {
    handleError: vi.fn(),
  },
}));

// Test component that throws an error
const ThrowError: React.FC<{ shouldThrow: boolean; errorMessage?: string }> = ({
  shouldThrow,
  errorMessage = 'Test error',
}) => {
  if (shouldThrow) {
    throw new Error(errorMessage);
  }
  return <div>No error</div>;
};

// Wrapper with theme for proper MUI rendering
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const theme = createTheme();
  return <ThemeProvider theme={theme}>{children}</ThemeProvider>;
};

describe('SectionErrorBoundary', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Suppress console.error during tests
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Normal Operation', () => {
    it('should render children when no error occurs', () => {
      render(
        <TestWrapper>
          <SectionErrorBoundary>
            <ThrowError shouldThrow={false} />
          </SectionErrorBoundary>
        </TestWrapper>
      );

      expect(screen.getByText('No error')).toBeInTheDocument();
    });

    it('should render custom fallback when provided and error occurs', () => {
      const customFallback = <div>Custom fallback</div>;

      render(
        <TestWrapper>
          <SectionErrorBoundary fallback={customFallback}>
            <ThrowError shouldThrow={true} />
          </SectionErrorBoundary>
        </TestWrapper>
      );

      expect(screen.getByText('Custom fallback')).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('should call errorHandler when an error occurs', () => {
      const testError = new Error('Test error');

      render(
        <TestWrapper>
          <SectionErrorBoundary name="TestComponent">
            <ThrowError shouldThrow={true} errorMessage="Test error" />
          </SectionErrorBoundary>
        </TestWrapper>
      );

      expect(errorHandler.handleError).toHaveBeenCalledWith(
        testError,
        expect.objectContaining({
          source: 'SectionErrorBoundary.TestComponent',
          operation: 'component error boundary',
          additionalData: expect.objectContaining({
            errorBoundary: true,
            level: 'component',
            name: 'TestComponent',
          }),
        }),
        expect.objectContaining({
          showToast: true,
          logToConsole: true,
        })
      );
    });

    it('should call custom onError handler when provided', () => {
      const onErrorSpy = vi.fn();

      render(
        <TestWrapper>
          <SectionErrorBoundary onError={onErrorSpy}>
            <ThrowError shouldThrow={true} />
          </SectionErrorBoundary>
        </TestWrapper>
      );

      expect(onErrorSpy).toHaveBeenCalledWith(
        expect.any(Error),
        expect.objectContaining({
          componentStack: expect.any(String),
        })
      );
    });
  });

  describe('Level-specific Rendering', () => {
    it('should render page-level error UI', () => {
      render(
        <TestWrapper>
          <SectionErrorBoundary
            level="page"
            name="TestPage"
            showHomeButton={true}
          >
            <ThrowError shouldThrow={true} errorMessage="Page error" />
          </SectionErrorBoundary>
        </TestWrapper>
      );

      expect(screen.getByText('Page Error')).toBeInTheDocument();
      expect(
        screen.getByText(/This page encountered an error/)
      ).toBeInTheDocument();
      expect(
        screen.getByRole('button', { name: /try again/i })
      ).toBeInTheDocument();
      expect(
        screen.getByRole('button', { name: /go home/i })
      ).toBeInTheDocument();
      expect(
        screen.getByRole('button', { name: /reload page/i })
      ).toBeInTheDocument();
    });

    it('should render section-level error UI', () => {
      render(
        <TestWrapper>
          <SectionErrorBoundary level="section" name="TestSection">
            <ThrowError shouldThrow={true} errorMessage="Section error" />
          </SectionErrorBoundary>
        </TestWrapper>
      );

      expect(screen.getByText('Section Error')).toBeInTheDocument();
      expect(screen.getByText('Section error')).toBeInTheDocument();
      expect(
        screen.getByRole('button', { name: /retry/i })
      ).toBeInTheDocument();
    });

    it('should render component-level error UI', () => {
      render(
        <TestWrapper>
          <SectionErrorBoundary level="component" name="TestComponent">
            <ThrowError shouldThrow={true} errorMessage="Component error" />
          </SectionErrorBoundary>
        </TestWrapper>
      );

      expect(screen.getByText('Component error')).toBeInTheDocument();
      expect(
        screen.getByRole('button', { name: /retry/i })
      ).toBeInTheDocument();
    });

    it('should not show home button when showHomeButton is false', () => {
      render(
        <TestWrapper>
          <SectionErrorBoundary
            level="page"
            name="TestPage"
            showHomeButton={false}
          >
            <ThrowError shouldThrow={true} />
          </SectionErrorBoundary>
        </TestWrapper>
      );

      expect(
        screen.queryByRole('button', { name: /go home/i })
      ).not.toBeInTheDocument();
    });
  });

  describe('Error Recovery', () => {
    it('should reset error state when retry button is clicked', async () => {
      const TestComponent = () => {
        const [shouldThrow, setShouldThrow] = React.useState(true);
        const [retryCount, setRetryCount] = React.useState(0);

        React.useEffect(() => {
          // After the first retry, stop throwing errors
          if (retryCount > 0) {
            setShouldThrow(false);
          }
        }, [retryCount]);

        // Listen for the retry button click by checking if the component re-renders
        React.useEffect(() => {
          const handleRetry = () => {
            setRetryCount((prev) => prev + 1);
          };

          // Simulate detecting a retry attempt
          if (shouldThrow && retryCount === 0) {
            setTimeout(() => {
              if (retryCount === 0) {
                handleRetry();
              }
            }, 10);
          }
        }, [shouldThrow, retryCount]);

        return <ThrowError shouldThrow={shouldThrow} />;
      };

      render(
        <TestWrapper>
          <SectionErrorBoundary level="component">
            <TestComponent />
          </SectionErrorBoundary>
        </TestWrapper>
      );

      // Should show error initially
      expect(
        screen.getByRole('button', { name: /retry/i })
      ).toBeInTheDocument();

      // Click retry
      fireEvent.click(screen.getByRole('button', { name: /retry/i }));

      // Should show success after retry
      await waitFor(
        () => {
          expect(screen.getByText('No error')).toBeInTheDocument();
        },
        { timeout: 1000 }
      );
    }, 10000);

    it('should auto-recover when autoRecover is enabled', async () => {
      vi.useFakeTimers();

      const TestComponent = () => {
        const [shouldThrow, setShouldThrow] = React.useState(true);

        React.useEffect(() => {
          // After a short delay, stop throwing errors
          const timer = setTimeout(() => setShouldThrow(false), 50);
          return () => clearTimeout(timer);
        }, []);

        return <ThrowError shouldThrow={shouldThrow} />;
      };

      render(
        <TestWrapper>
          <SectionErrorBoundary
            level="section"
            autoRecover={true}
            autoRecoverDelay={1000}
          >
            <TestComponent />
          </SectionErrorBoundary>
        </TestWrapper>
      );

      // Should show error and auto-recovering message
      expect(screen.getByText('Section Error')).toBeInTheDocument();
      expect(screen.getByText('Auto-recovering...')).toBeInTheDocument();

      // Fast-forward time to trigger auto-recovery
      vi.advanceTimersByTime(1100);

      await waitFor(
        () => {
          expect(screen.getByText('No error')).toBeInTheDocument();
        },
        { timeout: 1000 }
      );

      vi.useRealTimers();
    }, 10000); // Increase timeout for this test
  });

  describe('Error Boundary Configuration', () => {
    it('should not show toast for page-level errors', () => {
      render(
        <TestWrapper>
          <SectionErrorBoundary level="page">
            <ThrowError shouldThrow={true} />
          </SectionErrorBoundary>
        </TestWrapper>
      );

      expect(errorHandler.handleError).toHaveBeenCalledWith(
        expect.any(Error),
        expect.any(Object),
        expect.objectContaining({
          showToast: false, // Page-level errors don't show toast
        })
      );
    });

    it('should show toast for component-level errors', () => {
      render(
        <TestWrapper>
          <SectionErrorBoundary level="component">
            <ThrowError shouldThrow={true} />
          </SectionErrorBoundary>
        </TestWrapper>
      );

      expect(errorHandler.handleError).toHaveBeenCalledWith(
        expect.any(Error),
        expect.any(Object),
        expect.objectContaining({
          showToast: true, // Component-level errors show toast
        })
      );
    });
  });

  describe('Development Mode', () => {
    it('should show error details in development mode', () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'development';

      render(
        <TestWrapper>
          <SectionErrorBoundary level="page">
            <ThrowError shouldThrow={true} errorMessage="Detailed error" />
          </SectionErrorBoundary>
        </TestWrapper>
      );

      expect(
        screen.getByText('Error Details (Development Mode):')
      ).toBeInTheDocument();

      process.env.NODE_ENV = originalEnv;
    });

    it('should not show error details in production mode', () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'production';

      render(
        <TestWrapper>
          <SectionErrorBoundary level="page">
            <ThrowError shouldThrow={true} errorMessage="Detailed error" />
          </SectionErrorBoundary>
        </TestWrapper>
      );

      expect(
        screen.queryByText('Error Details (Development Mode):')
      ).not.toBeInTheDocument();

      process.env.NODE_ENV = originalEnv;
    });
  });
});
