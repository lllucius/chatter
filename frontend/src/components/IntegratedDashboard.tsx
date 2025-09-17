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
          getSDK().analytics.getIntegratedDashboardStatsApiV1AnalyticsIntegrated
        ) {
          return getSDK().analytics.getIntegratedDashboardStatsApiV1AnalyticsIntegrated();
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
        if (getSDK().analytics.getDashboardChartDataApiV1AnalyticsChartData) {
          return getSDK().analytics.getDashboardChartDataApiV1AnalyticsChartData();
        }
        return null;
      } catch {
        // Chart data API not available yet
        return null;
      }
    },
    { immediate: true }
  );

  // Get stats from API or use fallback
  const stats = React.useMemo(() => {
    if (statsApi.data?.data) {
      return statsApi.data.data;
    }

    // Fallback data if API not available
    return {
      workflows: {
        total: 42,
        active: 8,
        completedToday: 15,
        failureRate: 0.05,
        avgExecutionTime: 2.5,
      },
      agents: {
        total: 200,
        active: 8,
        conversationsToday: 234,
        avgResponseTime: 1.2,
        satisfactionScore: 4.6,
      },
      abTesting: {
        activeTests: 5,
        significantResults: 3,
        totalImprovement: 0.18,
        testsThisMonth: 12,
      },
      system: {
        tokensUsed: 1250000,
        apiCalls: 8520,
        cost: 125.5,
        uptime: 99.8,
      },
    };
  }, [statsApi.data]);

  // Use chart data from backend API instead of generating mock data
  const timeSeriesData = React.useMemo(() => {
    if (chartDataApi.data?.data?.hourly_performance_data) {
      // Transform backend data to frontend format
      return chartDataApi.data.data.hourly_performance_data
        .slice(0, 7)
        .map((item, index) => ({
          date: format(subDays(new Date(), 6 - index), 'MMM dd'),
          workflows: item.workflows || 40,
          agents: item.agents || 180,
          abTests: item.tests || 8,
          tokens: 800000 + (item.workflows || 0) * 10000,
          cost: 80 + (item.workflows || 0) * 2,
        }));
    }

    // Fallback to generating data if API not available
    const days = 7;
    const data = [];

    for (let i = days - 1; i >= 0; i--) {
      const date = subDays(new Date(), i);
      data.push({
        date: format(date, 'MMM dd'),
        workflows: 40 + Math.floor(Math.random() * 20),
        agents: 180 + Math.floor(Math.random() * 60),
        abTests: 8 + Math.floor(Math.random() * 4),
        tokens: 800000 + Math.floor(Math.random() * 400000),
        cost: 80 + Math.random() * 40,
      });
    }

    return data;
  }, [chartDataApi.data]);

  // Use integration data from backend if available
  const integrationData = React.useMemo(() => {
    if (chartDataApi.data?.data?.integration_data) {
      return chartDataApi.data.data.integration_data;
    }

    // Fallback data
    return [
      { name: 'Workflow → Agent', value: 35, color: '#8884d8' },
      { name: 'Agent → A/B Test', value: 25, color: '#82ca9d' },
      { name: 'A/B Test → Workflow', value: 15, color: '#ffc658' },
      { name: 'Standalone', value: 25, color: '#ff7300' },
    ];
  }, [chartDataApi.data]);

  const performanceData = React.useMemo(() => {
    if (chartDataApi.data?.data?.hourly_performance_data) {
      return chartDataApi.data.data.hourly_performance_data;
    }

    // Fallback to generating data
    return Array.from({ length: 24 }, (_, i): void => ({
      hour: `${i}:00`,
      workflows: 5 + Math.floor(Math.random() * 15),
      agents: 20 + Math.floor(Math.random() * 30),
      tests: 1 + Math.floor(Math.random() * 3),
    }));
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
                    {stats.workflows.active}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    of {stats.workflows.total} total
                  </Typography>
                </div>
                <WorkflowIcon color="primary" sx={{ fontSize: 40 }} />
              </Box>
              <Box sx={{ mt: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <SuccessIcon color="success" sx={{ fontSize: 16, mr: 0.5 }} />
                  <Typography variant="body2" color="success.main">
                    {stats.workflows.completedToday} completed today
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
                    {stats.agents.active}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    of {stats.agents.total} total
                  </Typography>
                </div>
                <AgentIcon color="success" sx={{ fontSize: 40 }} />
              </Box>
              <Box sx={{ mt: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <GroupIcon color="info" sx={{ fontSize: 16, mr: 0.5 }} />
                  <Typography variant="body2" color="info.main">
                    {stats.agents.conversationsToday} conversations today
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
                    {stats.abTesting.activeTests}
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
                    +{(stats.abTesting.totalImprovement * 100).toFixed(1)}% avg
                    improvement
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
                    ${stats.system.cost.toFixed(2)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {stats.system.tokensUsed.toLocaleString()} tokens
                  </Typography>
                </div>
                <SpeedIcon color="error" sx={{ fontSize: 40 }} />
              </Box>
              <Box sx={{ mt: 2 }}>
                <LinearProgress
                  variant="determinate"
                  value={(stats.system.cost / 200) * 100}
                  sx={{ height: 6, borderRadius: 3 }}
                />
                <Typography variant="caption" color="text.secondary">
                  {((stats.system.cost / 200) * 100).toFixed(1)}% of daily
                  budget
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
              <Grid size={{ xs: 12 }} lg={8}>
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

              <Grid size={{ xs: 12 }} lg={4}>
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
              <Grid size={{ xs: 12 }} md={6}>
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
                      label={({ name, percent }) =>
                        `${name}: ${(percent * 100).toFixed(0)}%`
                      }
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {integrationData.map((entry, index): void => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <RechartsTooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Grid>

              <Grid size={{ xs: 12 }} md={6}>
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
                    {stats.workflows.avgExecutionTime}s
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Avg Workflow Time
                  </Typography>
                </Paper>
              </Grid>
              <Grid size={{ xs: 6, sm: 3 }}>
                <Paper variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h6" color="success">
                    {stats.agents.avgResponseTime}s
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Avg Agent Response
                  </Typography>
                </Paper>
              </Grid>
              <Grid size={{ xs: 6, sm: 3 }}>
                <Paper variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h6" color="warning">
                    {((1 - stats.workflows.failureRate) * 100).toFixed(1)}%
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Success Rate
                  </Typography>
                </Paper>
              </Grid>
              <Grid size={{ xs: 6, sm: 3 }}>
                <Paper variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h6" color="info">
                    {stats.system.uptime}%
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    System Uptime
                  </Typography>
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
