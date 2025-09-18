import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Switch,
  FormControlLabel,
  Alert,
  Box,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Button,
  CircularProgress,
} from '@mui/material';
import {
  TrendingUp as TrendingIcon,
  Speed as PerformanceIcon,
  Warning as WarningIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { getSDK, authService } from '../services/auth-service';
import { toastService } from '../services/toast-service';
import { handleError } from '../utils/error-handler';
import { IntegratedDashboardStats, ChartReadyAnalytics } from 'chatter-sdk';

interface RealTimeEvent {
  id: string;
  type: string;
  data: Record<string, unknown>;
  timestamp: string;
}

interface AlertData {
  type: string;
  severity: 'info' | 'warning' | 'error' | 'success';
  title: string;
  message: string;
  threshold?: number;
  recommendation?: string;
}

const RealTimeDashboard: React.FC = () => {
  const [realTimeEnabled, setRealTimeEnabled] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [dashboardData, setDashboardData] = useState<IntegratedDashboardStats | null>(null);
  const [chartData, setChartData] = useState<ChartReadyAnalytics | null>(null);
  const [alerts, setAlerts] = useState<AlertData[]>([]);
  const [connectionStatus, setConnectionStatus] = useState<
    'disconnected' | 'connecting' | 'connected'
  >('disconnected');
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  const handleRealTimeEvent = useCallback((event: RealTimeEvent) => {
    setLastUpdate(new Date());

    switch (event.type) {
      case 'analytics':
        if (event.data.dashboard_stats && typeof event.data.dashboard_stats === 'object') {
          setDashboardData(event.data.dashboard_stats as IntegratedDashboardStats);
        }
        if (event.data.chart_data && typeof event.data.chart_data === 'object') {
          setChartData(event.data.chart_data as ChartReadyAnalytics);
        }
        break;

      case 'notification':
        if (event.data.alert && typeof event.data.alert === 'object') {
          const alertData = event.data.alert as Record<string, unknown>;
          const alert: AlertData = {
            type: String(alertData.type || 'info'),
            severity: (alertData.severity as AlertData['severity']) || 'info',
            title: String(alertData.title || 'Notification'),
            message: String(alertData.message || 'No message'),
            threshold: alertData.threshold ? Number(alertData.threshold) : undefined,
            recommendation: alertData.recommendation ? String(alertData.recommendation) : undefined
          };
          setAlerts((prev) => [alert, ...prev.slice(0, 9)]); // Keep only last 10 alerts

          // Show toast notification for critical alerts
          if (alert.severity === 'error' || alert.severity === 'warning') {
            toastService[alert.severity](alert.message);
          }
        }
        break;

      case 'health':
        if (event.data.health && typeof event.data.health === 'object') {
          const healthData = event.data.health as Record<string, unknown>;
          toastService.info(
            `System Alert: ${healthData.status || 'Critical issue detected'}`
          );
        }
        break;

      default:
        // Handle unknown event types
        console.debug('Unknown real-time event type:', event.type);
    }
  }, []);

  const connectToSSE = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    setConnectionStatus('connecting');

    try {
      const token = authService.getToken();

      if (!token) {
        throw new Error('No authentication token available');
      }

      // Create EventSource connection to SSE endpoint
      const eventSource = new EventSource(
        `/api/v1/events/stream?token=${token}`
      );
      eventSourceRef.current = eventSource;

      eventSource.onopen = () => {
        setConnectionStatus('connected');
        reconnectAttempts.current = 0;
        // SSE connection established
      };

      eventSource.onmessage = (event) => {
        try {
          const eventData: RealTimeEvent = JSON.parse(event.data);
          handleRealTimeEvent(eventData);
        } catch {
          // Error parsing SSE event - skip invalid events
        }
      };

      eventSource.onerror = () => {
        // SSE connection error
        setConnectionStatus('disconnected');

        // Attempt to reconnect with exponential backoff
        if (reconnectAttempts.current < maxReconnectAttempts) {
          const delay = Math.pow(2, reconnectAttempts.current) * 1000; // 1s, 2s, 4s, 8s, 16s
          reconnectAttempts.current++;

          reconnectTimeoutRef.current = setTimeout(() => {
            // Attempting to reconnect
            connectToSSE();
          }, delay);
        } else {
          // Max reconnection attempts reached
          setRealTimeEnabled(false);
          toastService.error(
            'Real-time connection failed. Please refresh the page.'
          );
        }
      };
    } catch {
      // Error establishing SSE connection
      setConnectionStatus('disconnected');
      setRealTimeEnabled(false);
    }
  }, [handleRealTimeEvent]);

  const toggleRealTime = useCallback(async () => {
    if (realTimeEnabled) {
      // Stop real-time updates
      setIsConnecting(true);
      try {
        await getSDK().analytics.stopRealTimeDashboardApiV1AnalyticsRealTimeRealTimeDashboardStop();

        if (eventSourceRef.current) {
          eventSourceRef.current.close();
          eventSourceRef.current = null;
        }

        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
          reconnectTimeoutRef.current = null;
        }

        setConnectionStatus('disconnected');
        setRealTimeEnabled(false);
        toastService.success('Real-time updates stopped');
      } catch (error) {
        handleError(error, { source: 'RealTimeDashboard.toggleRealTime.stop' });
      } finally {
        setIsConnecting(false);
      }
    } else {
      // Start real-time updates
      setIsConnecting(true);
      try {
        await getSDK().analytics.startRealTimeDashboardApiV1AnalyticsRealTimeRealTimeDashboardStart();
        setRealTimeEnabled(true);

        // Connect to SSE stream
        setTimeout(() => {
          connectToSSE();
        }, 1000); // Give server time to start the background task

        toastService.success('Real-time updates started');
      } catch (error) {
        handleError(error, { source: 'RealTimeDashboard.toggleRealTime.start' });
        setRealTimeEnabled(false);
      } finally {
        setIsConnecting(false);
      }
    }
  }, [realTimeEnabled, connectToSSE]);

  const refreshData = useCallback(async () => {
    try {
      // Fetch latest data manually
      const [dashboardResponse, chartResponse] = await Promise.all([
        getSDK().analytics.getIntegratedDashboardStatsApiV1AnalyticsDashboardIntegrated(),
        getSDK().analytics.getDashboardChartDataApiV1AnalyticsDashboardChartData(),
      ]);

      setDashboardData(dashboardResponse);
      setChartData(chartResponse);
      setLastUpdate(new Date());
      toastService.success('Dashboard data refreshed');
    } catch (error) {
      handleError(error, { source: 'RealTimeDashboard.refreshData' });
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, []);

  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case 'connected':
        return 'success';
      case 'connecting':
        return 'warning';
      case 'disconnected':
        return 'error';
      default:
        return 'default';
    }
  };

  const getAlertIcon = (severity: string) => {
    switch (severity) {
      case 'error':
        return <ErrorIcon color="error" />;
      case 'warning':
        return <WarningIcon color="warning" />;
      case 'success':
        return <SuccessIcon color="success" />;
      default:
        return <TrendingIcon color="primary" />;
    }
  };

  return (
    <Card>
      <CardContent>
        <Box
          display="flex"
          justifyContent="space-between"
          alignItems="center"
          mb={2}
        >
          <Typography variant="h6" component="h2">
            Real-Time Dashboard
          </Typography>
          <Box display="flex" alignItems="center" gap={1}>
            <Chip
              label={
                connectionStatus.charAt(0).toUpperCase() +
                connectionStatus.slice(1)
              }
              color={getConnectionStatusColor()}
              size="small"
            />
            <Button
              startIcon={<RefreshIcon />}
              onClick={refreshData}
              size="small"
              variant="outlined"
            >
              Refresh
            </Button>
          </Box>
        </Box>

        <FormControlLabel
          control={
            <Switch
              checked={realTimeEnabled}
              onChange={toggleRealTime}
              disabled={isConnecting}
            />
          }
          label={
            <Box display="flex" alignItems="center" gap={1}>
              <span>Real-time Updates</span>
              {isConnecting && <CircularProgress size={16} />}
            </Box>
          }
        />

        {lastUpdate && (
          <Typography
            variant="caption"
            color="textSecondary"
            display="block"
            mt={1}
          >
            Last updated: {format(lastUpdate, 'HH:mm:ss')}
          </Typography>
        )}

        {realTimeEnabled && connectionStatus === 'disconnected' && (
          <Alert severity="warning" sx={{ mt: 2 }}>
            Real-time connection lost. Attempting to reconnect...
          </Alert>
        )}

        {dashboardData && (
          <Box mt={3}>
            <Typography variant="h6" gutterBottom>
              Current Metrics
            </Typography>
            <Box display="flex" gap={2} flexWrap="wrap">
              <Chip
                icon={<TrendingIcon />}
                label={`Active Users: ${(dashboardData.system as Record<string, unknown>)?.active_users || 0}`}
                variant="outlined"
              />
              <Chip
                icon={<PerformanceIcon />}
                label={`Conversations: ${(dashboardData.workflows as Record<string, unknown>)?.total_conversations || 0}`}
                variant="outlined"
              />
              <Chip
                icon={<TrendingIcon />}
                label={`Documents: ${(dashboardData.agents as Record<string, unknown>)?.total_documents || 0}`}
                variant="outlined"
              />
              {chartData && (
                <Chip
                  icon={<TrendingIcon />}
                  label="Chart Data Available"
                  color="primary"
                  variant="outlined"
                />
              )}
            </Box>
          </Box>
        )}

        {alerts.length > 0 && (
          <Box mt={3}>
            <Typography variant="h6" gutterBottom>
              Recent Alerts
            </Typography>
            <List dense>
              {alerts.slice(0, 5).map((alert, index) => (
                <React.Fragment key={index}>
                  <ListItem>
                    <ListItemIcon>{getAlertIcon(alert.severity)}</ListItemIcon>
                    <ListItemText
                      primary={alert.title}
                      secondary={
                        <Box>
                          <Typography variant="body2" color="textSecondary">
                            {alert.message}
                          </Typography>
                          {alert.recommendation && (
                            <Typography variant="caption" color="primary">
                              💡 {alert.recommendation}
                            </Typography>
                          )}
                        </Box>
                      }
                    />
                  </ListItem>
                  {index < alerts.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          </Box>
        )}

        {!realTimeEnabled && (
          <Alert severity="info" sx={{ mt: 2 }}>
            Enable real-time updates to see live dashboard metrics and
            notifications.
          </Alert>
        )}
      </CardContent>
    </Card>
  );
};

export default RealTimeDashboard;
