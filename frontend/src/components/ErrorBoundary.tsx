import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Box, Typography, Button, Alert, Container } from '@mui/material';
import { Refresh as RefreshIcon } from '@mui/icons-material';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
     
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: undefined });
  };

  private handleReload = () => {
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <Container maxWidth="md" sx={{ mt: 4 }}>
          <Alert severity="error" sx={{ mb: 2 }}>
            <Typography variant="h6" gutterBottom>
              Something went wrong
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              {this.state.error?.message || 'An unexpected error occurred'}
            </Typography>
          </Alert>
          
          <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
            <Button
              variant="contained"
              startIcon={<RefreshIcon />}
              onClick={this.handleReset}
            >
              Try Again
            </Button>
            <Button
              variant="outlined"
              onClick={this.handleReload}
            >
              Reload Page
            </Button>
          </Box>

          {process.env.NODE_ENV === 'development' && this.state.error && (
            <Box sx={{ mt: 3, p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
              <Typography variant="subtitle2" gutterBottom>
                Error Details (Development Mode):
              </Typography>
              <Typography variant="body2" component="pre" sx={{ fontSize: '0.75rem', overflow: 'auto' }}>
                {this.state.error.stack}
              </Typography>
            </Box>
          )}
        </Container>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;