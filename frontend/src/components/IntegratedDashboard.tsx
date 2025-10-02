import React, { useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  LinearProgress,
  Button,
  Tabs,
  Tab,
  TabPanel,
  Divider,
  Stack,
} from '../utils/mui';
import {
  WorkflowIcon,
  AgentIcon,
  AnalyticsIcon,
  TrendingUpIcon,
  WarningIcon,
  CheckIcon as SuccessIcon,
  SpeedIcon,
  GroupIcon,
  TimelineIcon,
  AssessmentIcon,
  LaunchIcon,
} from '../utils/icons';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { format, subDays } from 'date-fns';
import { useNavigate } from 'react-router-dom';
import { getSDK } from '../services/auth-service';
import { useApi } from '../hooks/useApi';

// Type definitions for chart data
interface HourlyPerformanceItem {
  workflows?: number;
  agents?: number;
  tests?: number;
  [key: string]: unknown;
}

// Interface for dashboard stats
interface DashboardStats {
  workflows?: {
    active?: number;
    total?: number;
    completedToday?: number;
    avgExecutionTime?: number;
    failureRate?: number;
  };
  agents?: {
    active?: number;
    total?: number;
    conversationsToday?: number;
    avgResponseTime?: number;
  };
  ab_testing?: {
    activeTests?: number;
    totalImprovement?: number;
  };
  system?: {
    cost?: number;
    tokensUsed?: number;
  };
}

interface IntegrationDataEntry {
  name?: string;
  value?: number;
  color?: string | null;
}

interface IntegratedDashboardProps {
  onNavigate?: (path: string) => void;
}

const IntegratedDashboard: React.FC<IntegratedDashboardProps> = ({
  onNavigate,
}) => {
  const navigate = useNavigate();
  const [selectedTab, setSelectedTab] = useState(0);

  // Use backend API for integrated dashboard stats (with fallback)
  const statsApi = useApi(
    async () => {
      try {
        // Try the new endpoint, fall back if not available
        if (
          getSDK().analytics
            .getIntegratedDashboardStatsApiV1AnalyticsDashboardIntegrated
        ) {
          return getSDK().analytics.getIntegratedDashboardStatsApiV1AnalyticsDashboardIntegrated();
        }
        return null;
      } catch {
        // Integrated dashboard stats API not available yet
        return null;
      }
    },
    { immediate: true }
  );

  // Use backend API for chart data (with fallback)
  const chartDataApi = useApi(
    async () => {
      try {
        // Try the new endpoint, fall back if not available
        if (
          getSDK().analytics
            .getDashboardChartDataApiV1AnalyticsDashboardChartData
        ) {
          return getSDK().analytics.getDashboardChartDataApiV1AnalyticsDashboardChartData();
        }
        return null;
      } catch {
        // Chart data API not available yet
        return null;
      }
    },
    { immediate: true }
  );

  // Get stats from API - no fallback, show loading/error states instead
  const stats = React.useMemo(() => {
    return statsApi.data || null;
  }, [statsApi.data]);

  // Use chart data from backend API - no fallback mock data
  const timeSeriesData = React.useMemo(() => {
    if (chartDataApi.data?.hourly_performance_data) {
      // Transform backend data to frontend format
      return chartDataApi.data.hourly_performance_data
        .slice(0, 7)
        .map((item: HourlyPerformanceItem, index: number) => ({
          date: format(subDays(new Date(), 6 - index), 'MMM dd'),
          workflows: item.workflows || 0,
          agents: item.agents || 0,
          abTests: item.tests || 0,
          tokens: (item.workflows || 0) * 10000,
          cost: (item.workflows || 0) * 2,
        }));
    }

    // No data available - return empty array to show no data state
    return [];
  }, [chartDataApi.data]);

  // Use integration data from backend - no fallback
  const integrationData = React.useMemo(() => {
    if (chartDataApi.data?.integration_data) {
      return chartDataApi.data.integration_data;
    }

    // No data available
    return [];
  }, [chartDataApi.data]);

  const performanceData = React.useMemo(() => {
    if (chartDataApi.data?.hourly_performance_data) {
      return chartDataApi.data.hourly_performance_data;
    }

    // No data available
    return [];
  }, [chartDataApi.data]);

  const handleNavigate = (path: string) => {
    if (onNavigate) {
      onNavigate(path);
    } else {
      navigate(path);
    }
  };

  return (
    <Box>
      {/* Loading State */}
      {(statsApi.loading || chartDataApi.loading) && (
        <Box sx={{ mb: 4 }}>
          <LinearProgress />
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{ mt: 2, textAlign: 'center' }}
          >
            Loading dashboard data...
          </Typography>
        </Box>
      )}

      {/* Error State */}
      {(statsApi.error || chartDataApi.error) && !stats && (
        <Card sx={{ mb: 4, bgcolor: 'error.light' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <WarningIcon color="error" />
              <div>
                <Typography variant="h6" color="error">
                  Unable to Load Dashboard Data
                </Typography>
                <Typography variant="body2" color="error">
                  {statsApi.error ||
                    chartDataApi.error ||
                    'Failed to fetch dashboard data. Please try refreshing the page.'}
                </Typography>
              </div>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Summary Statistics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card
            sx={{ cursor: 'pointer' }}
            onClick={() => handleNavigate('/workflows')}
          >
            <CardContent>
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'flex-start',
                }}
              >
                <div>
                  <Typography color="text.secondary" gutterBottom>
                    Active Workflows
                  </Typography>
                  <Typography variant="h4" color="primary">
                    {(stats as DashboardStats)?.workflows?.active || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    of {(stats as DashboardStats)?.workflows?.total || 0} total
                  </Typography>
                </div>
                <WorkflowIcon color="primary" sx={{ fontSize: 40 }} />
              </Box>
              <Box sx={{ mt: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <SuccessIcon color="success" sx={{ fontSize: 16, mr: 0.5 }} />
                  <Typography variant="body2" color="success.main">
                    {(stats as DashboardStats)?.workflows?.completedToday || 0}{' '}
                    completed today
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card
            sx={{ cursor: 'pointer' }}
            onClick={() => handleNavigate('/agents')}
          >
            <CardContent>
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'flex-start',
                }}
              >
                <div>
                  <Typography color="text.secondary" gutterBottom>
                    Active Agents
                  </Typography>
                  <Typography variant="h4" color="success">
                    {(stats as DashboardStats)?.agents?.active || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    of {(stats as DashboardStats)?.agents?.total || 0} total
                  </Typography>
                </div>
                <AgentIcon color="success" sx={{ fontSize: 40 }} />
              </Box>
              <Box sx={{ mt: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <GroupIcon color="info" sx={{ fontSize: 16, mr: 0.5 }} />
                  <Typography variant="body2" color="info.main">
                    {(stats as DashboardStats)?.agents?.conversationsToday || 0}{' '}
                    conversations today
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card
            sx={{ cursor: 'pointer' }}
            onClick={() => handleNavigate('/ab-testing')}
          >
            <CardContent>
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'flex-start',
                }}
              >
                <div>
                  <Typography color="text.secondary" gutterBottom>
                    A/B Tests
                  </Typography>
                  <Typography variant="h4" color="warning">
                    {(stats as DashboardStats)?.ab_testing?.activeTests || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    active experiments
                  </Typography>
                </div>
                <AnalyticsIcon color="warning" sx={{ fontSize: 40 }} />
              </Box>
              <Box sx={{ mt: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <TrendingUpIcon
                    color="success"
                    sx={{ fontSize: 16, mr: 0.5 }}
                  />
                  <Typography variant="body2" color="success.main">
                    +
                    {(
                      ((stats as DashboardStats)?.ab_testing
                        ?.totalImprovement || 0) * 100
                    ).toFixed(1)}
                    % avg improvement
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'flex-start',
                }}
              >
                <div>
                  <Typography color="text.secondary" gutterBottom>
                    Today&apos;s Cost
                  </Typography>
                  <Typography variant="h4" color="error">
                    $
                    {(stats as DashboardStats)?.system?.cost?.toFixed(2) ||
                      '0.00'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {(
                      stats as DashboardStats
                    )?.system?.tokensUsed?.toLocaleString() || '0'}{' '}
                    tokens
                  </Typography>
                </div>
                <SpeedIcon color="error" sx={{ fontSize: 40 }} />
              </Box>
              <Box sx={{ mt: 2 }}>
                <LinearProgress
                  variant="determinate"
                  value={
                    (((stats as DashboardStats)?.system?.cost || 0) / 200) * 100
                  }
                  sx={{ height: 6, borderRadius: 3 }}
                />
                <Typography variant="caption" color="text.secondary">
                  {(
                    (((stats as DashboardStats)?.system?.cost || 0) / 200) *
                    100
                  ).toFixed(1)}
                  % of daily budget
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Detailed Analytics */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
            <Tabs
              value={selectedTab}
              onChange={(_, newValue) => setSelectedTab(newValue)}
            >
              <Tab
                label="Activity Overview"
                icon={<TimelineIcon />}
                iconPosition="start"
              />
              <Tab
                label="Integration Flow"
                icon={<AssessmentIcon />}
                iconPosition="start"
              />
              <Tab
                label="Performance"
                icon={<SpeedIcon />}
                iconPosition="start"
              />
            </Tabs>
          </Box>

          <TabPanel value={selectedTab} index={0} idPrefix="dashboard">
            <Grid container spacing={3}>
              <Grid size={{ xs: 12, lg: 8 }}>
                <Typography variant="h6" gutterBottom>
                  7-Day Activity Trend
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={timeSeriesData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <RechartsTooltip />
                    <Legend />
                    <Area
                      type="monotone"
                      dataKey="workflows"
                      stackId="1"
                      stroke="#8884d8"
                      fill="#8884d8"
                      name="Workflows"
                    />
                    <Area
                      type="monotone"
                      dataKey="agents"
                      stackId="1"
                      stroke="#82ca9d"
                      fill="#82ca9d"
                      name="Agent Conversations"
                    />
                    <Area
                      type="monotone"
                      dataKey="abTests"
                      stackId="1"
                      stroke="#ffc658"
                      fill="#ffc658"
                      name="A/B Test Interactions"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </Grid>

              <Grid size={{ xs: 12, lg: 4 }}>
                <Typography variant="h6" gutterBottom>
                  Recent Activity
                </Typography>
                <List>
                  <ListItem>
                    <ListItemIcon>
                      <WorkflowIcon color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Customer Support Workflow"
                      secondary="Completed 15 minutes ago"
                    />
                    <Chip label="Success" color="success" size="small" />
                  </ListItem>
                  <Divider />
                  <ListItem>
                    <ListItemIcon>
                      <AgentIcon color="success" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Sales Agent activated"
                      secondary="Started handling inquiries"
                    />
                    <Chip label="Active" color="info" size="small" />
                  </ListItem>
                  <Divider />
                  <ListItem>
                    <ListItemIcon>
                      <AnalyticsIcon color="warning" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Prompt A/B Test"
                      secondary="Reached statistical significance"
                    />
                    <Chip label="Complete" color="success" size="small" />
                  </ListItem>
                  <Divider />
                  <ListItem>
                    <ListItemIcon>
                      <WarningIcon color="error" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Data Processing Workflow"
                      secondary="Failed due to timeout"
                    />
                    <Chip label="Failed" color="error" size="small" />
                  </ListItem>
                </List>
              </Grid>
            </Grid>
          </TabPanel>

          <TabPanel value={selectedTab} index={1} idPrefix="dashboard">
            <Grid container spacing={3}>
              <Grid size={{ xs: 12, md: 6 }}>
                <Typography variant="h6" gutterBottom>
                  Feature Integration Usage
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={integrationData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({
                        name,
                        percent,
                      }: {
                        name?: string;
                        percent?: number;
                      }) => `${name}: ${((percent || 0) * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {integrationData.map(
                        (entry: IntegrationDataEntry, index: number) => (
                          <Cell
                            key={`cell-${index}`}
                            fill={entry.color || '#8884d8'}
                          />
                        )
                      )}
                    </Pie>
                    <RechartsTooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Grid>

              <Grid size={{ xs: 12, md: 6 }}>
                <Typography variant="h6" gutterBottom>
                  Integration Benefits
                </Typography>
                <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Workflow → Agent Integration
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    35% of workflows automatically trigger agent responses,
                    improving response time by 40%
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={75}
                    sx={{ mt: 1 }}
                  />
                </Paper>

                <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Agent → A/B Testing Integration
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    25% of agent interactions participate in A/B tests, driving
                    18% improvement in satisfaction
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={60}
                    sx={{ mt: 1 }}
                  />
                </Paper>

                <Paper variant="outlined" sx={{ p: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    A/B Test → Workflow Integration
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    15% of test results automatically update workflow
                    configurations
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={85}
                    sx={{ mt: 1 }}
                  />
                </Paper>
              </Grid>
            </Grid>
          </TabPanel>

          <TabPanel value={selectedTab} index={2} idPrefix="dashboard">
            <Typography variant="h6" gutterBottom>
              24-Hour Performance Overview
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={performanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="hour" />
                <YAxis />
                <RechartsTooltip />
                <Legend />
                <Bar
                  dataKey="workflows"
                  fill="#8884d8"
                  name="Workflow Executions"
                />
                <Bar
                  dataKey="agents"
                  fill="#82ca9d"
                  name="Agent Interactions"
                />
                <Bar dataKey="tests" fill="#ffc658" name="Test Events" />
              </BarChart>
            </ResponsiveContainer>

            <Grid container spacing={2} sx={{ mt: 2 }}>
              <Grid size={{ xs: 6, sm: 3 }}>
                <Paper variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h6" color="primary">
                    {(stats as DashboardStats)?.workflows?.avgExecutionTime ||
                      0}
                    s
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Avg Workflow Time
                  </Typography>
                </Paper>
              </Grid>
              <Grid size={{ xs: 6, sm: 3 }}>
                <Paper variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h6" color="success">
                    {(stats as DashboardStats)?.agents?.avgResponseTime || 0}s
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Avg Agent Response
                  </Typography>
                </Paper>
              </Grid>
              <Grid size={{ xs: 6, sm: 3 }}>
                <Paper variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h6" color="warning">
                    {(
                      (1 -
                        ((stats as DashboardStats)?.workflows?.failureRate ||
                          0)) *
                      100
                    ).toFixed(1)}
                    %
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Success Rate
                  </Typography>
                </Paper>
              </Grid>
              <Grid size={{ xs: 6, sm: 3 }}>
                <Paper variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                  <Stack spacing={0.5} alignItems="center">
                    <Typography
                      variant="h6"
                      color="info"
                    >{`${stats?.system?.uptime || 0}%`}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      System Uptime
                    </Typography>
                  </Stack>
                </Paper>
              </Grid>
            </Grid>
          </TabPanel>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Grid container spacing={3}>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Button
                  variant="outlined"
                  startIcon={<WorkflowIcon />}
                  endIcon={<LaunchIcon />}
                  onClick={() => handleNavigate('/workflows')}
                  fullWidth
                >
                  Create New Workflow
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<AgentIcon />}
                  endIcon={<LaunchIcon />}
                  onClick={() => handleNavigate('/agents')}
                  fullWidth
                >
                  Deploy New Agent
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<AnalyticsIcon />}
                  endIcon={<LaunchIcon />}
                  onClick={() => handleNavigate('/ab-testing')}
                  fullWidth
                >
                  Start A/B Test
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Health
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <SuccessIcon color="success" />
                  </ListItemIcon>
                  <ListItemText
                    primary="API Services"
                    secondary="All systems operational"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <SuccessIcon color="success" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Database"
                    secondary="Response time: 45ms"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <WarningIcon color="warning" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Queue Processing"
                    secondary="Some delays expected"
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 12, md: 4 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Achievements
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <TrendingUpIcon color="success" />
                  </ListItemIcon>
                  <ListItemText
                    primary="18% improvement"
                    secondary="Agent response quality this week"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <SpeedIcon color="info" />
                  </ListItemIcon>
                  <ListItemText
                    primary="25% faster execution"
                    secondary="Workflow processing optimization"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <AnalyticsIcon color="warning" />
                  </ListItemIcon>
                  <ListItemText
                    primary="5 successful tests"
                    secondary="Completed A/B experiments this month"
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default IntegratedDashboard;
