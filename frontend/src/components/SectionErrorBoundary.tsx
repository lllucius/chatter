import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Box, Typography, Button, Alert, Paper } from '@mui/material';
import { Refresh as RefreshIcon, Home as HomeIcon } from '@mui/icons-material';
import { errorHandler } from '../utils/error-handler';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  level?: 'page' | 'section' | 'component';
  name?: string;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  showHomeButton?: boolean;
  autoRecover?: boolean;
  autoRecoverDelay?: number;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorDetails?: string;
  autoRecovering?: boolean;
}

/**
 * Granular ErrorBoundary component that can be used at different levels
 * Provides different UI based on the level (page, section, component)
 */
class SectionErrorBoundary extends Component<Props, State> {
  private autoRecoverTimeout?: NodeJS.Timeout;

  public state: State = {
    hasError: false,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    const { level = 'component', name = 'Unknown', onError } = this.props;

    // Use standardized error handling to log and process the error
    errorHandler.handleError(error, {
      source: `SectionErrorBoundary.${name}`,
      operation: `${level} error boundary`,
      additionalData: {
        componentStack: errorInfo.componentStack,
        errorBoundary: true,
        level,
        name
      }
    }, {
      showToast: level === 'component', // Only show toast for component-level errors
      logToConsole: true
    });

    // Store error details for development mode display
    if (process.env.NODE_ENV === 'development') {
      const errorDetails = `${error.message}\n\nComponent Stack:${errorInfo.componentStack}\n\nError Stack:\n${error.stack}`;
      this.setState({ errorDetails });
    }

    // Call custom error handler if provided
    onError?.(error, errorInfo);

    // Auto-recover if enabled
    if (this.props.autoRecover) {
      this.startAutoRecover();
    }
  }

  public componentWillUnmount() {
    if (this.autoRecoverTimeout) {
      clearTimeout(this.autoRecoverTimeout);
    }
  }

  private startAutoRecover = () => {
    const delay = this.props.autoRecoverDelay || 5000;
    this.setState({ autoRecovering: true });

    this.autoRecoverTimeout = setTimeout(() => {
      this.handleReset();
    }, delay);
  };

  private handleReset = () => {
    if (this.autoRecoverTimeout) {
      clearTimeout(this.autoRecoverTimeout);
    }
    this.setState({ 
      hasError: false, 
      error: undefined, 
      errorDetails: undefined,
      autoRecovering: false 
    });
  };

  private handleReload = () => {
    window.location.reload();
  };

  private handleGoHome = () => {
    window.location.href = '/';
  };

  private renderPageError() {
    return (
      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column', 
        alignItems: 'center', 
        justifyContent: 'center', 
        minHeight: '50vh',
        p: 3 
      }}>
        <Alert severity="error" sx={{ mb: 3, maxWidth: 600 }}>
          <Typography variant="h6" gutterBottom>
            Page Error
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {this.state.error?.message || 'This page encountered an error and cannot be displayed'}
          </Typography>
        </Alert>
        
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Button
            variant="contained"
            startIcon={<RefreshIcon />}
            onClick={this.handleReset}
          >
            Try Again
          </Button>
          {this.props.showHomeButton && (
            <Button
              variant="outlined"
              startIcon={<HomeIcon />}
              onClick={this.handleGoHome}
            >
              Go Home
            </Button>
          )}
          <Button
            variant="outlined"
            onClick={this.handleReload}
          >
            Reload Page
          </Button>
        </Box>

        {this.state.autoRecovering && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            Auto-recovering in a few seconds...
          </Typography>
        )}

        {process.env.NODE_ENV === 'development' && this.state.errorDetails && (
          <Paper sx={{ mt: 3, p: 2, maxWidth: 800, overflow: 'auto' }}>
            <Typography variant="subtitle2" gutterBottom>
              Error Details (Development Mode):
            </Typography>
            <Typography variant="body2" component="pre" sx={{ 
              fontSize: '0.75rem', 
              overflow: 'auto', 
              whiteSpace: 'pre-wrap',
              maxHeight: 300
            }}>
              {this.state.errorDetails}
            </Typography>
          </Paper>
        )}
      </Box>
    );
  }

  private renderSectionError() {
    return (
      <Paper sx={{ p: 2, m: 1, bgcolor: 'error.main', color: 'error.contrastText' }}>
        <Typography variant="subtitle1" gutterBottom>
          Section Error
        </Typography>
        <Typography variant="body2" sx={{ mb: 2 }}>
          {this.state.error?.message || 'This section encountered an error'}
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            size="small"
            variant="outlined"
            color="inherit"
            startIcon={<RefreshIcon />}
            onClick={this.handleReset}
          >
            Retry
          </Button>
        </Box>

        {this.state.autoRecovering && (
          <Typography variant="caption" sx={{ mt: 1, display: 'block' }}>
            Auto-recovering...
          </Typography>
        )}
      </Paper>
    );
  }

  private renderComponentError() {
    return (
      <Alert severity="error" sx={{ m: 1 }}>
        <Typography variant="body2">
          {this.state.error?.message || 'Component error'}
        </Typography>
        <Button 
          size="small" 
          onClick={this.handleReset}
          sx={{ mt: 1 }}
        >
          Retry
        </Button>
      </Alert>
    );
  }

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      switch (this.props.level) {
        case 'page':
          return this.renderPageError();
        case 'section':
          return this.renderSectionError();
        case 'component':
        default:
          return this.renderComponentError();
      }
    }

    return this.props.children;
  }
}

export default SectionErrorBoundary;