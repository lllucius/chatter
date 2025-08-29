import React, { Component, ErrorInfo, ReactNode } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  Alert,
  AlertTitle,
  Divider,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  BugReport as BugIcon,
  Home as HomeIcon,
} from '@mui/icons-material';

interface Props {
  children: ReactNode;
  fallbackComponent?: React.ComponentType<ErrorBoundaryState>;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  resetOnPropsChange?: boolean;
  resetKeys?: Array<string | number>;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  eventId: string | null;
}

class ErrorBoundary extends Component<Props, ErrorBoundaryState> {
  private resetTimeoutId: number | null = null;
  private previousResetKeys: Array<string | number> = [];

  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      eventId: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Generate a unique error ID for tracking
    const eventId = Math.random().toString(36).substr(2, 9);
    
    this.setState({
      errorInfo,
      eventId,
    });

    // Log error to console in development
    if (process.env.NODE_ENV === 'development') {
      console.group('🚨 Error Boundary Caught Error');
      console.error('Error:', error);
      console.error('Error Info:', errorInfo);
      console.error('Component Stack:', errorInfo.componentStack);
      console.groupEnd();
    }

    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // TODO: Send error to error reporting service (e.g., Sentry)
    // this.reportError(error, errorInfo, eventId);
  }

  componentDidUpdate(prevProps: Props) {
    const { resetKeys = [], resetOnPropsChange = false } = this.props;
    const { hasError } = this.state;

    if (hasError && resetOnPropsChange && prevProps.children !== this.props.children) {
      this.resetErrorBoundary();
    }

    if (hasError && resetKeys.length > 0) {
      const hasResetKeyChanged = resetKeys.some((key, idx) => {
        return this.previousResetKeys[idx] !== key;
      });

      if (hasResetKeyChanged) {
        this.resetErrorBoundary();
      }
    }

    this.previousResetKeys = resetKeys;
  }

  resetErrorBoundary = () => {
    if (this.resetTimeoutId) {
      clearTimeout(this.resetTimeoutId);
    }

    this.resetTimeoutId = window.setTimeout(() => {
      this.setState({
        hasError: false,
        error: null,
        errorInfo: null,
        eventId: null,
      });
    }, 100);
  };

  private reportError = (error: Error, errorInfo: ErrorInfo, eventId: string) => {
    // This would integrate with error reporting service
    // For now, just store in localStorage for debugging
    try {
      const errorReport = {
        eventId,
        error: {
          message: error.message,
          stack: error.stack,
          name: error.name,
        },
        errorInfo: {
          componentStack: errorInfo.componentStack,
        },
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href,
      };

      const existingReports = JSON.parse(localStorage.getItem('errorReports') || '[]');
      existingReports.push(errorReport);
      
      // Keep only last 10 error reports
      if (existingReports.length > 10) {
        existingReports.splice(0, existingReports.length - 10);
      }
      
      localStorage.setItem('errorReports', JSON.stringify(existingReports));
    } catch (e) {
      console.error('Failed to store error report:', e);
    }
  };

  private goHome = () => {
    window.location.href = '/dashboard';
  };

  render() {
    const { hasError, error, errorInfo, eventId } = this.state;
    const { fallbackComponent: FallbackComponent, children } = this.props;

    if (hasError) {
      // Use custom fallback component if provided
      if (FallbackComponent) {
        return <FallbackComponent {...this.state} />;
      }

      // Default error UI
      return (
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '100vh',
            p: 3,
            bgcolor: 'background.default',
          }}
        >
          <Paper
            elevation={3}
            sx={{
              p: 4,
              maxWidth: 600,
              width: '100%',
              textAlign: 'center',
            }}
          >
            <BugIcon sx={{ fontSize: 64, color: 'error.main', mb: 2 }} />
            
            <Typography variant="h4" gutterBottom color="error">
              Oops! Something went wrong
            </Typography>
            
            <Typography variant="body1" color="text.secondary" paragraph>
              We're sorry, but something unexpected happened. Our team has been notified
              and is working to fix this issue.
            </Typography>

            {process.env.NODE_ENV === 'development' && error && (
              <>
                <Divider sx={{ my: 3 }} />
                <Alert severity="error" sx={{ textAlign: 'left', mb: 2 }}>
                  <AlertTitle>Error Details (Development Mode)</AlertTitle>
                  <Typography variant="body2" component="pre" sx={{ whiteSpace: 'pre-wrap', fontSize: '0.8rem' }}>
                    {error.message}
                  </Typography>
                </Alert>
                
                {errorInfo && (
                  <Alert severity="info" sx={{ textAlign: 'left', mb: 2 }}>
                    <AlertTitle>Component Stack</AlertTitle>
                    <Typography variant="body2" component="pre" sx={{ whiteSpace: 'pre-wrap', fontSize: '0.7rem' }}>
                      {errorInfo.componentStack}
                    </Typography>
                  </Alert>
                )}
              </>
            )}

            {eventId && (
              <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 3 }}>
                Error ID: {eventId}
              </Typography>
            )}

            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
              <Button
                variant="contained"
                startIcon={<RefreshIcon />}
                onClick={this.resetErrorBoundary}
                size="large"
              >
                Try Again
              </Button>
              
              <Button
                variant="outlined"
                startIcon={<HomeIcon />}
                onClick={this.goHome}
                size="large"
              >
                Go Home
              </Button>
            </Box>
          </Paper>
        </Box>
      );
    }

    return children;
  }
}

export default ErrorBoundary;