import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Alert,
} from '@mui/material';
import {
  AccountTree as WorkflowIcon,
  SmartToy as AgentIcon,
  Analytics as TestIcon,
  Speed as PerformanceIcon,
} from '@mui/icons-material';
import { useNotifications, useWorkflowNotifications, useAgentNotifications, useTestNotifications } from '../components/NotificationSystem';

const NotificationDemo: React.FC = () => {
  const { showNotification } = useNotifications();
  const { notifyWorkflowStarted, notifyWorkflowCompleted, notifyWorkflowFailed } = useWorkflowNotifications();
  const { notifyAgentActivated, notifyAgentError } = useAgentNotifications();
  const { notifyTestSignificant, notifyTestStarted } = useTestNotifications();

  const demoNotifications = [
    {
      title: 'System Success',
      button: 'Show Success',
      action: () => showNotification({
        type: 'success',
        category: 'system',
        title: 'System Update Complete',
        message: 'All services have been successfully updated to the latest version',
      }),
    },
    {
      title: 'System Error',
      button: 'Show Error',
      action: () => showNotification({
        type: 'error',
        category: 'system',
        title: 'Database Connection Failed',
        message: 'Unable to connect to the primary database. Failover initiated.',
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
      action: () => notifyWorkflowCompleted('Data Processing Workflow', '2m 34s'),
    },
    {
      title: 'Workflow Failed',
      button: 'Fail Workflow',
      action: () => notifyWorkflowFailed('Email Campaign Workflow', 'API rate limit exceeded'),
    },
    {
      title: 'Agent Activated',
      button: 'Activate Agent',
      action: () => notifyAgentActivated('Customer Support Agent'),
    },
    {
      title: 'Agent Error',
      button: 'Agent Error',
      action: () => notifyAgentError('Sales Agent', 'Unable to access CRM integration'),
    },
    {
      title: 'A/B Test Started',
      button: 'Start Test',
      action: () => notifyTestStarted('Landing Page Copy Test'),
    },
    {
      title: 'A/B Test Significant',
      button: 'Test Winner',
      action: () => notifyTestSignificant('Email Subject Line Test', 'Variant A'),
    },
    {
      title: 'Performance Warning',
      button: 'Performance Issue',
      action: () => showNotification({
        type: 'warning',
        category: 'performance',
        title: 'High Memory Usage Detected',
        message: 'System memory usage is at 85%. Consider scaling resources.',
      }),
    },
    {
      title: 'System Information',
      button: 'System Info',
      action: () => showNotification({
        type: 'info',
        category: 'system',
        title: 'Scheduled Maintenance',
        message: 'System maintenance scheduled for tomorrow at 2:00 AM UTC',
      }),
    },
  ];

  return (
    <Box sx={{ p: 3 }}>
      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Notification System Demo
        </Typography>
        <Typography variant="body2">
          This page demonstrates the integrated notification system. Click the buttons below to trigger different types of notifications.
          Check the notification icon in the top navigation to see the notification history.
        </Typography>
      </Alert>

      <Grid container spacing={3}>
        {demoNotifications.map((demo, index): void => (
          <Grid item xs={12} sm={6} md={4} key={index}>
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
                    demo.title.includes('Workflow') ? <WorkflowIcon /> :
                    demo.title.includes('Agent') ? <AgentIcon /> :
                    demo.title.includes('Test') ? <TestIcon /> :
                    <PerformanceIcon />
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
          <Typography component="li">Real-time notifications with snackbar alerts</Typography>
          <Typography component="li">Persistent notification history in the menu</Typography>
          <Typography component="li">Categorized notifications (workflow, agent, test, system, performance)</Typography>
          <Typography component="li">Different severity levels (success, error, warning, info)</Typography>
          <Typography component="li">Unread count badge on notification icon</Typography>
          <Typography component="li">Mark all as read and clear all functionality</Typography>
          <Typography component="li">Context-specific notification hooks for different features</Typography>
        </Box>
      </Box>
    </Box>
  );
};

export default NotificationDemo;