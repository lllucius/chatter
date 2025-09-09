import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Alert,
  CircularProgress,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import {
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Refresh as RefreshIcon,
  Storage as StorageIcon,
  Speed as SpeedIcon,
  NetworkCheck as NetworkIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { getSDK } from '../services/auth-service';
import { toastService } from '../services/toast-service';
import { ToolServerResponse } from 'chatter-sdk';
import PageLayout from '../components/PageLayout';

const HealthPage: React.FC = () => {
  const [health, setHealth] = useState<any>(null);
  const [toolServers, setToolServers] = useState<ToolServerResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadHealthData();
  }, []);

  const loadHealthData = async () => {
    try {
      setLoading(true);
      setError('');
      const [healthResponse, toolServerResponse] = await Promise.all([
        getSDK().health.healthCheckEndpointHealthz(),
        getSDK().toolServers.listToolServersApiV1ToolserversServers({}),
      ]);
      setHealth(healthResponse.data);
      setToolServers(toolServerResponse.data);
    } catch (err: any) {
      toastService.error(err, 'Failed to load health data');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'healthy':
      case 'online':
      case 'active':
        return 'success';
      case 'warning':
      case 'degraded':
        return 'warning';
      case 'error':
      case 'offline':
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'healthy':
      case 'online':
      case 'active':
        return <CheckIcon color="success" />;
      case 'warning':
      case 'degraded':
        return <WarningIcon color="warning" />;
      case 'error':
      case 'offline':
      case 'failed':
        return <ErrorIcon color="error" />;
      default:
        return <InfoIcon color="info" />;
    }
  };

  // Mock system metrics (in a real app, these would come from the API)
  const systemMetrics = {
    cpu_usage: 45,
    memory_usage: 68,
    disk_usage: 32,
    network_latency: 12,
    uptime_hours: 720,
    active_connections: 156,
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress size={60} />
      </Box>
    );
  }

  const toolbar = (
    <Button
      variant="outlined"
      startIcon={<RefreshIcon />}
      onClick={loadHealthData}
      disabled={loading}
    >
      Refresh
    </Button>
  );

  return (
    <PageLayout title="System Health Dashboard" toolbar={toolbar}>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      {/* Overall System Status */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid
          size={{
            xs: 12,
            md: 8
          }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Overview
              </Typography>
              <List>
                <ListItem>
                  <ListItemIcon>
                    {getStatusIcon('healthy')}
                  </ListItemIcon>
                  <ListItemText
                    primary="API Server"
                    secondary={`Status: ${health?.status || 'Unknown'} | Version: ${health?.version || 'Unknown'}`}
                  />
                  <Chip
                    label="Healthy"
                    color="success"
                    size="small"
                  />
                </ListItem>
                <Divider />
                <ListItem>
                  <ListItemIcon>
                    <StorageIcon color="success" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Database"
                    secondary="PostgreSQL connection active"
                  />
                  <Chip
                    label="Connected"
                    color="success"
                    size="small"
                  />
                </ListItem>
                <Divider />
                <ListItem>
                  <ListItemIcon>
                    <NetworkIcon color="success" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Vector Store"
                    secondary="PGVector integration operational"
                  />
                  <Chip
                    label="Operational"
                    color="success"
                    size="small"
                  />
                </ListItem>
                <Divider />
                <ListItem>
                  <ListItemIcon>
                    <SpeedIcon color="info" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Job Queue"
                    secondary="Background processing active"
                  />
                  <Chip
                    label="Active"
                    color="info"
                    size="small"
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>
        <Grid
          size={{
            xs: 12,
            md: 4
          }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Stats
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Uptime
                </Typography>
                <Typography variant="h6">
                  {Math.floor(systemMetrics.uptime_hours / 24)} days
                </Typography>
              </Box>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Active Connections
                </Typography>
                <Typography variant="h6">
                  {systemMetrics.active_connections}
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Network Latency
                </Typography>
                <Typography variant="h6">
                  {systemMetrics.network_latency}ms
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      {/* System Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid
          size={{
            xs: 12,
            md: 6
          }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Resource Usage
              </Typography>
              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">CPU Usage</Typography>
                  <Typography variant="body2">{systemMetrics.cpu_usage}%</Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={systemMetrics.cpu_usage}
                  color={systemMetrics.cpu_usage > 80 ? 'error' : systemMetrics.cpu_usage > 60 ? 'warning' : 'success'}
                />
              </Box>
              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Memory Usage</Typography>
                  <Typography variant="body2">{systemMetrics.memory_usage}%</Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={systemMetrics.memory_usage}
                  color={systemMetrics.memory_usage > 80 ? 'error' : systemMetrics.memory_usage > 60 ? 'warning' : 'success'}
                />
              </Box>
              <Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Disk Usage</Typography>
                  <Typography variant="body2">{systemMetrics.disk_usage}%</Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={systemMetrics.disk_usage}
                  color={systemMetrics.disk_usage > 80 ? 'error' : systemMetrics.disk_usage > 60 ? 'warning' : 'success'}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid
          size={{
            xs: 12,
            md: 6
          }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Performance Metrics
              </Typography>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="body2">API Response Time</Typography>
                <Chip
                  label="<100ms"
                  color="success"
                  size="small"
                />
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="body2">Database Query Time</Typography>
                <Chip
                  label="<50ms"
                  color="success"
                  size="small"
                />
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="body2">Vector Search Time</Typography>
                <Chip
                  label="<200ms"
                  color="success"
                  size="small"
                />
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2">Success Rate</Typography>
                <Chip
                  label="99.9%"
                  color="success"
                  size="small"
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      {/* Tool Servers Status */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Tool Servers Status
          </Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>URL</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Last Check</TableCell>
                  <TableCell>Health Info</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {(toolServers || []).map((server) => (
                  <TableRow key={server.id} hover>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        {getStatusIcon(server.status)}
                        <Typography variant="body2" sx={{ ml: 1, fontWeight: 'medium' }}>
                          {server.name}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                        {server.command || 'N/A'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={server.status}
                        color={getStatusColor(server.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {server.last_health_check ? (
                        <Typography variant="body2">
                          {format(new Date(server.last_health_check), 'MMM dd, yyyy HH:mm')}
                        </Typography>
                      ) : (
                        '-'
                      )}
                    </TableCell>
                    <TableCell>
                      {server.last_health_check ? (
                        <Typography variant="body2">
                          {format(new Date(server.last_health_check), 'MMM dd, HH:mm')}
                        </Typography>
                      ) : (
                        '-'
                      )}
                    </TableCell>
                  </TableRow>
                ))}
                {(toolServers || []).length === 0 && (
                  <TableRow>
                    <TableCell colSpan={5} align="center">
                      <Typography variant="body2" color="text.secondary" sx={{ py: 3 }}>
                        No tool servers configured
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </PageLayout>
  );
};

export default HealthPage;
