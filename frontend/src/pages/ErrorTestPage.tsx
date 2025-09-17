import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  Grid,
  Alert,
  Paper,
  Divider,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  Error as ErrorIcon,
  NetworkCheck as NetworkIcon,
  BugReport as BugIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import PageLayout from '../components/PageLayout';
import SectionErrorBoundary from '../components/SectionErrorBoundary';
import { useAsyncError } from '../hooks/useAsyncError';
import { useNetwork } from '../hooks/useNetwork';
import { errorHandler } from '../utils/error-handler';

// Test component that throws errors on demand
const ErrorTestComponent: React.FC<{
  shouldThrow: boolean;
  errorType: string;
}> = ({ shouldThrow, errorType }) => {
  if (shouldThrow) {
    switch (errorType) {
      case 'javascript':
        throw new Error('Test JavaScript error from component');
      case 'async':
        throw new Error('Test async error from component');
      case 'network':
        throw new Error('Network error: fetch failed');
      default:
        throw new Error('Generic test error');
    }
  }
  return (
    <Alert severity="success">
      Component rendered successfully - no errors thrown
    </Alert>
  );
};

// Async operation test component
const AsyncErrorTestComponent: React.FC = () => {
  const { executeAsync, handleAsyncError } = useAsyncError();
  const [result, setResult] = useState<string>('');

  const testAsyncError = async () => {
    const result = await executeAsync(
      () => {
        return new Promise((_, reject) => {
          setTimeout(
            () => reject(new Error('Simulated async operation failure')),
            1000
          );
        });
      },
      {
        source: 'ErrorTestPage.AsyncErrorTestComponent',
        operation: 'Test async error handling',
      }
    );

    setResult(result.success ? 'Success!' : `Error: ${result.error}`);
  };

  const testNetworkError = async () => {
    try {
      // Simulate a network error
      await fetch('https://nonexistent-domain-12345.com/api/test');
    } catch (error) {
      handleAsyncError(error, {
        source: 'ErrorTestPage.AsyncErrorTestComponent',
        operation: 'Test network error handling',
      });
      setResult('Network error handled');
    }
  };

  const testUnhandledPromiseRejection = () => {
    // This will trigger the global unhandled promise rejection handler
    Promise.reject(new Error('Unhandled promise rejection test'));
    setResult('Unhandled promise rejection triggered');
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Async Error Testing
      </Typography>
      <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
        <Button variant="outlined" onClick={testAsyncError}>
          Test Async Error
        </Button>
        <Button variant="outlined" onClick={testNetworkError}>
          Test Network Error
        </Button>
        <Button variant="outlined" onClick={testUnhandledPromiseRejection}>
          Test Unhandled Promise
        </Button>
      </Box>
      {result && (
        <Alert
          severity={result.includes('Error') ? 'error' : 'info'}
          sx={{ mt: 1 }}
        >
          {result}
        </Alert>
      )}
    </Box>
  );
};

// Network status component
const NetworkStatusComponent: React.FC = () => {
  const { status, refreshConnectivity } = useNetwork({
    showToasts: true,
    pingInterval: 10000, // Check every 10 seconds
  });

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        <NetworkIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Network Status
      </Typography>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
        <Typography>Online: {status.isOnline ? '✅' : '❌'}</Typography>
        <Typography>Connected: {status.isConnected ? '✅' : '❌'}</Typography>
        <Button
          size="small"
          onClick={refreshConnectivity}
          startIcon={<RefreshIcon />}
        >
          Check Connection
        </Button>
      </Box>
      {status.lastConnectedAt && (
        <Typography variant="body2" color="text.secondary">
          Last connected: {status.lastConnectedAt.toLocaleString()}
        </Typography>
      )}
      {status.lastDisconnectedAt && (
        <Typography variant="body2" color="text.secondary">
          Last disconnected: {status.lastDisconnectedAt.toLocaleString()}
        </Typography>
      )}
    </Paper>
  );
};

const ErrorTestPage: React.FC = () => {
  const [throwJSError, setThrowJSError] = useState(false);
  const [throwAsyncError, setThrowAsyncError] = useState(false);
  const [throwNetworkError, setThrowNetworkError] = useState(false);

  const triggerGlobalJSError = () => {
    // This will trigger the global error handler
    setTimeout(() => {
      throw new Error('Global JavaScript error test');
    }, 100);
  };

  const triggerDirectError = () => {
    // Use the error handler directly
    errorHandler.handleError(
      new Error('Direct error handler test'),
      {
        source: 'ErrorTestPage.triggerDirectError',
        operation: 'Manual error trigger',
      },
      {
        showToast: true,
        logToConsole: true,
      }
    );
  };

  return (
    <PageLayout>
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          <BugIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Error Handling Test Page
        </Typography>

        <Typography variant="body1" sx={{ mb: 3 }}>
          This page demonstrates all the error handling capabilities implemented
          in the frontend. Try the different error scenarios to see how they are
          caught and handled.
        </Typography>

        <Grid container spacing={3}>
          {/* Global Error Testing */}
          <Grid size={{ xs: 12, md: 6 }}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Global Error Handlers
                </Typography>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mb: 2 }}
                >
                  Test global JavaScript error and unhandled promise rejection
                  handlers
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexDirection: 'column' }}>
                  <Button
                    variant="contained"
                    color="error"
                    onClick={triggerGlobalJSError}
                  >
                    Trigger Global JS Error
                  </Button>
                  <Button
                    variant="outlined"
                    color="error"
                    onClick={triggerDirectError}
                  >
                    Trigger Direct Error
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Component Error Boundaries */}
          <Grid size={{ xs: 12, md: 6 }}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Error Boundaries
                </Typography>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mb: 2 }}
                >
                  Test error boundaries at different levels
                </Typography>

                <Box sx={{ mb: 2 }}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={throwJSError}
                        onChange={(e) => setThrowJSError(e.target.checked)}
                      />
                    }
                    label="Throw JS Error"
                  />
                </Box>

                <SectionErrorBoundary
                  level="component"
                  name="ErrorTestComponent"
                  autoRecover={true}
                  autoRecoverDelay={3000}
                >
                  <ErrorTestComponent
                    shouldThrow={throwJSError}
                    errorType="javascript"
                  />
                </SectionErrorBoundary>
              </CardContent>
            </Card>
          </Grid>

          {/* Async Error Testing */}
          <Grid size={{ xs: 12 }}>
            <Card>
              <CardContent>
                <AsyncErrorTestComponent />
              </CardContent>
            </Card>
          </Grid>

          {/* Network Status */}
          <Grid size={{ xs: 12 }}>
            <NetworkStatusComponent />
          </Grid>

          {/* Section-level Error Boundary Test */}
          <Grid size={{ xs: 12 }}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Section-Level Error Boundary
                </Typography>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mb: 2 }}
                >
                  This section is wrapped in a section-level error boundary
                </Typography>

                <FormControlLabel
                  control={
                    <Switch
                      checked={throwAsyncError}
                      onChange={(e) => setThrowAsyncError(e.target.checked)}
                    />
                  }
                  label="Throw Async Error"
                />

                <SectionErrorBoundary level="section" name="AsyncErrorSection">
                  <Box sx={{ mt: 2 }}>
                    <ErrorTestComponent
                      shouldThrow={throwAsyncError}
                      errorType="async"
                    />
                  </Box>
                </SectionErrorBoundary>
              </CardContent>
            </Card>
          </Grid>

          {/* Instructions */}
          <Grid size={{ xs: 12 }}>
            <Alert severity="info" sx={{ mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                How to Test Error Handling:
              </Typography>
              <ul style={{ margin: 0, paddingLeft: '20px' }}>
                <li>Check the browser console to see error logging</li>
                <li>Watch for toast notifications when errors occur</li>
                <li>Toggle switches to trigger component errors</li>
                <li>Try the async error buttons to test promise handling</li>
                <li>Monitor network status and try disconnecting internet</li>
                <li>Observe auto-recovery behavior for component errors</li>
              </ul>
            </Alert>
          </Grid>
        </Grid>
      </Box>
    </PageLayout>
  );
};

export default ErrorTestPage;
