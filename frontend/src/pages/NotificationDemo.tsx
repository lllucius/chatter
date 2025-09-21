import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Alert,
  Divider,
} from '@mui/material';
import {
  AccountTree as WorkflowIcon,
  SmartToy as AgentIcon,
  Analytics as TestIcon,
  Speed as PerformanceIcon,
  Error as ErrorIcon,
  BugReport as BugIcon,
} from '@mui/icons-material';
import {
  useNotifications,
  useWorkflowNotifications,
  useAgentNotifications,
  useTestNotifications,
} from '../components/NotificationSystem';
import { handleError, handleErrorWithResult } from '../utils/error-handler';

const NotificationDemo: React.FC = () => {
  const { showNotification } = useNotifications();
  const {
    notifyWorkflowStarted,
    notifyWorkflowCompleted,
    notifyWorkflowFailed,
  } = useWorkflowNotifications();
  const { notifyAgentActivated, notifyAgentError } = useAgentNotifications();
  const { notifyTestSignificant, notifyTestStarted } = useTestNotifications();

  // Error handling demos
  const demoError = () => {
    const error = new Error(
      'This is a demo error with full stack trace and context'
    );
    handleError(error, {
      source: 'NotificationDemo.demoError',
      operation: 'demonstrate error handling',
      userId: 'demo-user',
      additionalData: { demoMode: true, timestamp: new Date().toISOString() },
    });
  };

  const demoApiError = () => {
    const apiError = {
      response: {
        data: {
          title: 'Validation Error',
          detail: 'Email field is required and must be valid',
          status: 400,
          type: 'https://api.example.com/problems/validation',
        },
        status: 400,
      },
      message: 'Request failed with status code 400',
    };
    handleError(apiError, {
      source: 'NotificationDemo.demoApiError',
      operation: 'API request validation',
      additionalData: { endpoint: '/api/users', method: 'POST' },
    });
  };

  const demoUnhandledError = () => {
    // This will be caught by the ErrorBoundary
    throw new Error('This error will be caught by the ErrorBoundary component');
  };

  const demoAsyncError = async () => {
    try {
      // Simulate an async operation that fails
      await new Promise((_, reject) => {
        setTimeout(
          () => reject(new Error('Async operation failed with timeout')),
          100
        );
      });
    } catch (error) {
      handleError(error, {
        source: 'NotificationDemo.demoAsyncError',
        operation: 'async operation simulation',
        additionalData: { timeout: 100, retryAttempt: 1 },
      });
    }
  };

  const demoErrorWithResult = () => {
    const error = new Error('Service temporarily unavailable');
    const _result = handleErrorWithResult(
      error,
      {
        source: 'NotificationDemo.demoErrorWithResult',
        operation: 'service availability check',
        additionalData: { service: 'payment-processor' },
      },
      {
        fallbackMessage:
          'Payment service is currently unavailable. Please try again later.',
      }
    );

    // TODO: Remove console.log in production
    // console.log('Error result:', result);
  };

  const demoNotifications = [
    {
      title: 'System Success',
      button: 'Show Success',
      action: () =>
        showNotification({
          type: 'success',
          category: 'system',
          title: 'System Update Complete',
          message:
            'All services have been successfully updated to the latest version',
        }),
    },
    {
      title: 'System Error',
      button: 'Show Error',
      action: () =>
        showNotification({
          type: 'error',
          category: 'system',
          title: 'Database Connection Failed',
          message:
            'Unable to connect to the primary database. Failover initiated.',
          persistent: true,
        }),
    },
    {
      title: 'Workflow Started',
      button: 'Start Workflow',
      action: () => notifyWorkflowStarted('Customer Onboarding Workflow'),
    },
    {
      title: 'Workflow Completed',
      button: 'Complete Workflow',
      action: () =>
        notifyWorkflowCompleted('Data Processing Workflow', '2m 34s'),
    },
    {
      title: 'Workflow Failed',
      button: 'Fail Workflow',
      action: () =>
        notifyWorkflowFailed(
          'Email Campaign Workflow',
          'API rate limit exceeded'
        ),
    },
    {
      title: 'Agent Activated',
      button: 'Activate Agent',
      action: () => notifyAgentActivated('Customer Support Agent'),
    },
    {
      title: 'Agent Error',
      button: 'Agent Error',
      action: () =>
        notifyAgentError('Sales Agent', 'Unable to access CRM integration'),
    },
    {
      title: 'A/B Test Started',
      button: 'Start Test',
      action: () => notifyTestStarted('Landing Page Copy Test'),
    },
    {
      title: 'A/B Test Significant',
      button: 'Test Winner',
      action: () =>
        notifyTestSignificant('Email Subject Line Test', 'Variant A'),
    },
    {
      title: 'Performance Warning',
      button: 'Performance Issue',
      action: () =>
        showNotification({
          type: 'warning',
          category: 'performance',
          title: 'High Memory Usage Detected',
          message: 'System memory usage is at 85%. Consider scaling resources.',
        }),
    },
    {
      title: 'System Information',
      button: 'System Info',
      action: () =>
        showNotification({
          type: 'info',
          category: 'system',
          title: 'Scheduled Maintenance',
          message: 'System maintenance scheduled for tomorrow at 2:00 AM UTC',
        }),
    },
  ];

  const errorDemos = [
    {
      title: 'Standard Error',
      button: 'Trigger Error',
      description: 'Shows how standard JavaScript errors are handled',
      action: demoError,
    },
    {
      title: 'API Error',
      button: 'API Error',
      description: 'Demonstrates RFC 9457 Problem Detail error handling',
      action: demoApiError,
    },
    {
      title: 'Async Error',
      button: 'Async Error',
      description: 'Shows handling of errors in async operations',
      action: demoAsyncError,
    },
    {
      title: 'Error with Result',
      button: 'Error Result',
      description: 'Demonstrates error handling that returns structured data',
      action: demoErrorWithResult,
    },
    {
      title: 'Unhandled Error',
      button: 'ErrorBoundary Test',
      description:
        'Triggers ErrorBoundary to show component-level error handling',
      action: demoUnhandledError,
    },
  ];

  return (
    <Box sx={{ p: 3 }}>
      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Notification & Error Handling Demo
        </Typography>
        <Typography variant="body2">
          This page demonstrates the integrated notification system and
          standardized error handling. Click the buttons below to trigger
          different types of notifications and errors. Check the notification
          icon in the top navigation to see the notification history.
        </Typography>
        <Typography variant="body2" sx={{ mt: 1 }}>
          <strong>Environment:</strong> {process.env.NODE_ENV}
          {process.env.NODE_ENV === 'development' &&
            ' (Full error details will be shown)'}
          {process.env.NODE_ENV === 'production' &&
            ' (User-friendly error messages will be shown)'}
        </Typography>
      </Alert>

      <Typography variant="h5" gutterBottom sx={{ mt: 4, mb: 2 }}>
        Notification System
      </Typography>
      <Grid container spacing={3}>
        {demoNotifications.map((demo, index) => (
          <Grid size={{ xs: 12, sm: 6, md: 4 }} key={index}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {demo.title}
                </Typography>
                <Button
                  variant="contained"
                  onClick={demo.action}
                  fullWidth
                  startIcon={
                    demo.title.includes('Workflow') ? (
                      <WorkflowIcon />
                    ) : demo.title.includes('Agent') ? (
                      <AgentIcon />
                    ) : demo.title.includes('Test') ? (
                      <TestIcon />
                    ) : (
                      <PerformanceIcon />
                    )
                  }
                >
                  {demo.button}
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Divider sx={{ my: 4 }} />

      <Typography variant="h5" gutterBottom sx={{ mb: 2 }}>
        Error Handling System
      </Typography>
      <Alert severity="warning" sx={{ mb: 3 }}>
        <Typography variant="body2">
          The error handling demos below show how errors are processed
          differently in development vs production modes. In{' '}
          <strong>development</strong>, you&apos;ll see full error details,
          stack traces, and context in both console and toasts. In{' '}
          <strong>production</strong>, only user-friendly messages are shown
          with minimal technical details.
        </Typography>
      </Alert>

      <Grid container spacing={3}>
        {errorDemos.map((demo, index) => (
          <Grid size={{ xs: 12, sm: 6, md: 4 }} key={index}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {demo.title}
                </Typography>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mb: 2 }}
                >
                  {demo.description}
                </Typography>
                <Button
                  variant="outlined"
                  color="error"
                  onClick={demo.action}
                  fullWidth
                  startIcon={
                    demo.title.includes('ErrorBoundary') ? (
                      <BugIcon />
                    ) : (
                      <ErrorIcon />
                    )
                  }
                >
                  {demo.button}
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" gutterBottom>
          Notification Features:
        </Typography>
        <Box component="ul" sx={{ pl: 2 }}>
          <Typography component="li">
            Real-time notifications with snackbar alerts
          </Typography>
          <Typography component="li">
            Persistent notification history in the menu
          </Typography>
          <Typography component="li">
            Categorized notifications (workflow, agent, test, system,
            performance)
          </Typography>
          <Typography component="li">
            Different severity levels (success, error, warning, info)
          </Typography>
          <Typography component="li">
            Unread count badge on notification icon
          </Typography>
          <Typography component="li">
            Mark all as read and clear all functionality
          </Typography>
          <Typography component="li">
            Context-specific notification hooks for different features
          </Typography>
        </Box>

        <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
          Error Handling Features:
        </Typography>
        <Box component="ul" sx={{ pl: 2 }}>
          <Typography component="li">
            Standardized error processing across all frontend components
          </Typography>
          <Typography component="li">
            Development mode: Full error details, stack traces, and context
          </Typography>
          <Typography component="li">
            Production mode: User-friendly messages with minimal technical
            details
          </Typography>
          <Typography component="li">
            Source location tracking for easy debugging
          </Typography>
          <Typography component="li">
            RFC 9457 Problem Detail support for API errors
          </Typography>
          <Typography component="li">
            Error context including operation, user, and additional data
          </Typography>
          <Typography component="li">
            Automatic console logging with environment-appropriate detail levels
          </Typography>
          <Typography component="li">
            Integration with toast notifications for user feedback
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};

export default NotificationDemo;
