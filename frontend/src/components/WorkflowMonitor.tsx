import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Alert,
  Button,
  IconButton,
  Tooltip,
  CircularProgress,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  PlayArrow as RunningIcon,
  CheckCircle as CompletedIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Pause as PausedIcon,
  Speed as SpeedIcon,
  Memory as MemoryIcon,
  Storage as StorageIcon,
  Refresh as RefreshIcon,
  Stop as StopIcon,
  Visibility as ViewIcon,
} from '@mui/icons-material';
import { format, differenceInSeconds } from 'date-fns';
import {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
} from 'recharts';

interface WorkflowExecution {
  id: string;
  workflowId: string;
  workflowName: string;
  status:
    | 'queued'
    | 'running'
    | 'completed'
    | 'failed'
    | 'paused'
    | 'cancelled';
  startTime: Date;
  endTime?: Date;
  progress: number;
  currentStep?: string;
  totalSteps: number;
  completedSteps: number;
  metrics: {
    tokensUsed: number;
    apiCalls: number;
    memoryUsage: number;
    executionTime: number;
    cost: number;
  };
  logs: {
    timestamp: Date;
    level: 'info' | 'warn' | 'error' | 'debug';
    message: string;
    stepId?: string;
  }[];
  error?: {
    message: string;
    stepId: string;
    timestamp: Date;
  };
}

interface WorkflowMonitorProps {
  executions: WorkflowExecution[];
  onRefresh: () => void;
  onStop: (executionId: string) => void;
  onRetry: (executionId: string) => void;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

const WorkflowMonitor: React.FC<WorkflowMonitorProps> = ({
  executions,
  onRefresh,
  onStop,
  onRetry,
  autoRefresh = true,
  refreshInterval = 5000,
}) => {
  const [selectedExecution, setSelectedExecution] =
    useState<WorkflowExecution | null>(null);
  const [detailDialogOpen, setDetailDialogOpen] = useState(false);
  const [performanceData, setPerformanceData] = useState<
    Array<{ timestamp: string; tokensPerSecond: number; latency: number }>
  >([]);

  // Auto-refresh functionality
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      onRefresh();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, onRefresh]);

  // Generate performance data for visualization
  useEffect(() => {
    const runningExecutions = executions.filter((e) => e.status === 'running');
    if (runningExecutions.length === 0) return;

    const newData = runningExecutions.map((execution) => ({
      timestamp: new Date().toISOString(),
      tokensPerSecond:
        execution.metrics.tokensUsed /
        Math.max(execution.metrics.executionTime, 1),
      latency: execution.metrics.executionTime,
    }));

    setPerformanceData((prev) => [...prev.slice(-20), ...newData]);
  }, [executions]);

  const getStatusIcon = (status: WorkflowExecution['status']) => {
    switch (status) {
      case 'running':
        return <RunningIcon color="primary" />;
      case 'completed':
        return <CompletedIcon color="success" />;
      case 'failed':
        return <ErrorIcon color="error" />;
      case 'paused':
        return <PausedIcon color="warning" />;
      case 'cancelled':
        return <StopIcon color="action" />;
      case 'queued':
        return <CircularProgress size={20} />;
      default:
        return <WarningIcon color="warning" />;
    }
  };

  const getStatusColor = (status: WorkflowExecution['status']) => {
    switch (status) {
      case 'running':
        return 'info' as const;
      case 'completed':
        return 'success' as const;
      case 'failed':
        return 'error' as const;
      case 'paused':
        return 'warning' as const;
      case 'cancelled':
        return 'default' as const;
      case 'queued':
        return 'default' as const;
      default:
        return 'default' as const;
    }
  };

  const formatDuration = (startTime: Date, endTime?: Date) => {
    const end = endTime || new Date();
    const duration = differenceInSeconds(end, startTime);

    if (duration < 60) return `${duration}s`;
    if (duration < 3600)
      return `${Math.floor(duration / 60)}m ${duration % 60}s`;
    return `${Math.floor(duration / 3600)}h ${Math.floor((duration % 3600) / 60)}m`;
  };

  const openExecutionDetails = (execution: WorkflowExecution) => {
    setSelectedExecution(execution);
    setDetailDialogOpen(true);
  };

  const runningExecutions = executions.filter((e) =>
    ['running', 'queued'].includes(e.status)
  );

  return (
    <Box>
      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Active Executions
              </Typography>
              <Typography variant="h4" color="primary">
                {runningExecutions.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Total Today
              </Typography>
              <Typography variant="h4">
                {
                  executions.filter(
                    (e) =>
                      format(e.startTime, 'yyyy-MM-dd') ===
                      format(new Date(), 'yyyy-MM-dd')
                  ).length
                }
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Success Rate
              </Typography>
              <Typography variant="h4" color="success">
                {executions.length > 0
                  ? Math.round(
                      (executions.filter((e) => e.status === 'completed')
                        .length /
                        executions.length) *
                        100
                    )
                  : 0}
                %
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Avg Duration
              </Typography>
              <Typography variant="h4">
                {executions.filter((e) => e.endTime).length > 0
                  ? `${Math.round(
                      executions
                        .filter((e) => e.endTime)
                        .reduce(
                          (acc, e) =>
                            acc + differenceInSeconds(e.endTime!, e.startTime),
                          0
                        ) / executions.filter((e) => e.endTime).length
                    )}s`
                  : 'N/A'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Running Executions */}
        <Grid size={{ xs: 12, lg: 8 }}>
          <Card>
            <CardContent>
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  mb: 2,
                }}
              >
                <Typography variant="h6">Active Workflow Executions</Typography>
                <Button
                  startIcon={<RefreshIcon />}
                  onClick={onRefresh}
                  size="small"
                  variant="outlined"
                >
                  Refresh
                </Button>
              </Box>

              {runningExecutions.length === 0 ? (
                <Alert severity="info">No active workflow executions.</Alert>
              ) : (
                <List>
                  {runningExecutions.map((execution) => (
                    <React.Fragment key={execution.id}>
                      <ListItem sx={{ px: 0 }}>
                        <ListItemIcon>
                          {getStatusIcon(execution.status)}
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Box
                              sx={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: 1,
                              }}
                            >
                              <Typography variant="subtitle1">
                                {execution.workflowName}
                              </Typography>
                              <Chip
                                label={execution.status}
                                size="small"
                                color={getStatusColor(execution.status)}
                              />
                            </Box>
                          }
                          secondary={
                            <Box>
                              <Typography
                                variant="body2"
                                color="text.secondary"
                              >
                                Started:{' '}
                                {format(execution.startTime, 'HH:mm:ss')} •
                                Duration: {formatDuration(execution.startTime)}
                              </Typography>
                              <Typography
                                variant="body2"
                                color="text.secondary"
                              >
                                Step {execution.completedSteps} of{' '}
                                {execution.totalSteps} •{execution.currentStep}
                              </Typography>
                              <LinearProgress
                                variant="determinate"
                                value={execution.progress}
                                sx={{ mt: 1, height: 6, borderRadius: 3 }}
                              />
                            </Box>
                          }
                        />
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Tooltip title="View Details">
                            <IconButton
                              onClick={() => openExecutionDetails(execution)}
                            >
                              <ViewIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Stop Execution">
                            <IconButton
                              onClick={() => onStop(execution.id)}
                              color="error"
                            >
                              <StopIcon />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </ListItem>
                      <Divider />
                    </React.Fragment>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* System Metrics */}
        <Grid size={{ xs: 12, lg: 4 }}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Metrics
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <SpeedIcon color="primary" />
                    <Typography variant="body2">Avg Tokens/sec</Typography>
                  </Box>
                  <Typography variant="h6">
                    {runningExecutions.length > 0
                      ? Math.round(
                          runningExecutions.reduce(
                            (acc, e) =>
                              acc +
                              e.metrics.tokensUsed /
                                Math.max(e.metrics.executionTime, 1),
                            0
                          ) / runningExecutions.length
                        )
                      : 0}
                  </Typography>
                </Box>

                <Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <MemoryIcon color="warning" />
                    <Typography variant="body2">Memory Usage</Typography>
                  </Box>
                  <Typography variant="h6">
                    {runningExecutions.length > 0
                      ? Math.round(
                          runningExecutions.reduce(
                            (acc, e) => acc + e.metrics.memoryUsage,
                            0
                          ) / runningExecutions.length
                        )
                      : 0}{' '}
                    MB
                  </Typography>
                </Box>

                <Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <StorageIcon color="info" />
                    <Typography variant="body2">API Calls/min</Typography>
                  </Box>
                  <Typography variant="h6">
                    {runningExecutions.length > 0
                      ? Math.round(
                          runningExecutions.reduce(
                            (acc, e) =>
                              acc +
                              e.metrics.apiCalls /
                                Math.max(e.metrics.executionTime / 60, 1),
                            0
                          ) / runningExecutions.length
                        )
                      : 0}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>

          {/* Performance Chart */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Performance Trend
              </Typography>
              <ResponsiveContainer width="100%" height={200}>
                <AreaChart data={performanceData.slice(-10)}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="time"
                    tickFormatter={(time) => format(new Date(time), 'HH:mm')}
                  />
                  <YAxis />
                  <RechartsTooltip
                    labelFormatter={(time) =>
                      format(new Date(time), 'HH:mm:ss')
                    }
                    formatter={(value: number, name: string) => [
                      Math.round(value),
                      name,
                    ]}
                  />
                  <Area
                    type="monotone"
                    dataKey="tokensPerSecond"
                    stackId="1"
                    stroke="#8884d8"
                    fill="#8884d8"
                    name="Tokens/sec"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Execution Details Dialog */}
      <Dialog
        open={detailDialogOpen}
        onClose={() => setDetailDialogOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          Workflow Execution Details
          {selectedExecution && (
            <Typography variant="subtitle1" color="text.secondary">
              {selectedExecution.workflowName} • {selectedExecution.id}
            </Typography>
          )}
        </DialogTitle>
        <DialogContent>
          {selectedExecution && (
            <Grid container spacing={3}>
              <Grid size={{ xs: 12, md: 6 }}>
                <Paper variant="outlined" sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    Execution Status
                  </Typography>
                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 1,
                      mb: 2,
                    }}
                  >
                    {getStatusIcon(selectedExecution.status)}
                    <Chip
                      label={selectedExecution.status}
                      color={getStatusColor(selectedExecution.status)}
                    />
                  </Box>
                  <Typography variant="body2">
                    Started:{' '}
                    {format(
                      selectedExecution.startTime,
                      'MMM dd, yyyy HH:mm:ss'
                    )}
                  </Typography>
                  {selectedExecution.endTime && (
                    <Typography variant="body2">
                      Ended:{' '}
                      {format(
                        selectedExecution.endTime,
                        'MMM dd, yyyy HH:mm:ss'
                      )}
                    </Typography>
                  )}
                  <Typography variant="body2">
                    Duration:{' '}
                    {formatDuration(
                      selectedExecution.startTime,
                      selectedExecution.endTime
                    )}
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={selectedExecution.progress}
                    sx={{ mt: 2, height: 8, borderRadius: 4 }}
                  />
                  <Typography variant="caption" color="text.secondary">
                    {selectedExecution.completedSteps} of{' '}
                    {selectedExecution.totalSteps} steps completed
                  </Typography>
                </Paper>
              </Grid>

              <Grid size={{ xs: 12, md: 6 }}>
                <Paper variant="outlined" sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    Metrics
                  </Typography>
                  <Box
                    sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}
                  >
                    <Typography variant="body2">
                      Tokens Used:{' '}
                      {selectedExecution.metrics.tokensUsed.toLocaleString()}
                    </Typography>
                    <Typography variant="body2">
                      API Calls:{' '}
                      {selectedExecution.metrics.apiCalls.toLocaleString()}
                    </Typography>
                    <Typography variant="body2">
                      Memory Usage: {selectedExecution.metrics.memoryUsage} MB
                    </Typography>
                    <Typography variant="body2">
                      Estimated Cost: $
                      {selectedExecution.metrics.cost.toFixed(4)}
                    </Typography>
                  </Box>
                </Paper>
              </Grid>

              {selectedExecution.error && (
                <Grid size={{ xs: 12 }}>
                  <Alert severity="error">
                    <Typography variant="subtitle2">
                      Error in step: {selectedExecution.error.stepId}
                    </Typography>
                    <Typography variant="body2">
                      {selectedExecution.error.message}
                    </Typography>
                    <Typography variant="caption">
                      {format(selectedExecution.error.timestamp, 'HH:mm:ss')}
                    </Typography>
                  </Alert>
                </Grid>
              )}

              <Grid size={{ xs: 12 }}>
                <Paper variant="outlined" sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    Execution Logs
                  </Typography>
                  <Box sx={{ maxHeight: 300, overflow: 'auto' }}>
                    {selectedExecution.logs.map((log, index) => (
                      <Box key={index} sx={{ mb: 1 }}>
                        <Typography
                          variant="body2"
                          component="pre"
                          sx={{
                            color:
                              log.level === 'error'
                                ? 'error.main'
                                : log.level === 'warn'
                                  ? 'warning.main'
                                  : 'text.primary',
                            fontFamily: 'monospace',
                            fontSize: '0.875rem',
                          }}
                        >
                          [{format(log.timestamp, 'HH:mm:ss')}]{' '}
                          {log.level.toUpperCase()}: {log.message}
                        </Typography>
                      </Box>
                    ))}
                  </Box>
                </Paper>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          {selectedExecution?.status === 'failed' && (
            <Button
              onClick={() => selectedExecution && onRetry(selectedExecution.id)}
              color="primary"
            >
              Retry
            </Button>
          )}
          <Button onClick={() => setDetailDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default WorkflowMonitor;
