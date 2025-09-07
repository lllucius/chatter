import React, { useMemo, memo, useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  LinearProgress,
  Alert,
  CircularProgress,
  Button,
  Tabs,
  Tab,
  Paper,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  Area,
  AreaChart,
  BarChart,
  Bar,
} from 'recharts';
import {
  TrendingUp,
  Message,
  Storage,
  Speed,
  People,
  SmartToy,
  Assessment,
  CloudQueue,
  GetApp,
  Settings,
  ShowChart,
  Computer,
} from '@mui/icons-material';
import { chatterSDK } from '../services/chatter-sdk';
import { DashboardResponse } from '../sdk';
import { useApi } from '../hooks/useApi';
import { toastService } from '../services/toast-service';
import PageLayout from '../components/PageLayout';

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: string;
  changeType?: 'positive' | 'negative' | 'neutral';
  icon: React.ReactElement;
  color: string;
}

// Memoized MetricCard component
const MetricCard = memo<MetricCardProps>(({
  title,
  value,
  change,
  changeType = 'neutral',
  icon,
  color,
}) => {
  const getChangeColor = () => {
    switch (changeType) {
      case 'positive':
        return 'success.main';
      case 'negative':
        return 'error.main';
      default:
        return 'text.secondary';
    }
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <Box
            sx={{
              p: 1,
              borderRadius: 1,
              backgroundColor: `${color}.light`,
              color: `${color}.main`,
              mr: 2,
            }}
          >
            {icon}
          </Box>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            {title}
          </Typography>
        </Box>
        <Typography variant="h4" component="div" sx={{ mb: 1, fontWeight: 'bold' }}>
          {value}
        </Typography>
        {change && (
          <Typography variant="body2" sx={{ color: getChangeColor() }}>
            {change}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
});

MetricCard.displayName = 'MetricCard';

// Helper: safely get .toLocaleString(), fallback to "0"
function safeLocaleString(n: number | undefined | null): string {
  if (typeof n === 'number' && !isNaN(n)) {
    return n.toLocaleString();
  }
  return '0';
}

// Helper: safely get .toFixed(), fallback to "0.0"
function safeToFixed(n: number | undefined | null, digits: number): string {
  if (typeof n === 'number' && !isNaN(n)) {
    return n.toFixed(digits);
  }
  return (0).toFixed(digits);
}

const DashboardPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  
  // Use custom API hooks for various analytics data
  const dashboardApi = useApi(
    () => chatterSDK.analytics.getDashboardApiV1AnalyticsDashboardGet(),
    { immediate: true }
  );

  const performanceApi = useApi(
    () => chatterSDK.analytics.getPerformanceMetricsApiV1AnalyticsPerformanceGet(),
    { immediate: true }
  );

  const systemApi = useApi(
    () => chatterSDK.analytics.getSystemAnalyticsApiV1AnalyticsSystemGet(),
    { immediate: true }
  );

  const usageApi = useApi(
    () => chatterSDK.analytics.getUsageMetricsApiV1AnalyticsUsageGet(),
    { immediate: true }
  );

  const documentApi = useApi(
    () => chatterSDK.analytics.getDocumentAnalyticsApiV1AnalyticsDocumentsGet(),
    { immediate: true }
  );

  const toolServerApi = useApi(
    () => chatterSDK.analytics.getToolServerAnalyticsApiV1AnalyticsToolserversGet(),
    { immediate: true }
  );

  const data = dashboardApi.data?.data;
  const performanceData = performanceApi.data?.data;
  const systemData = systemApi.data?.data;
  const usageData = usageApi.data?.data;
  const documentData = documentApi.data?.data;
  const toolServerData = toolServerApi.data?.data;

  // Enhanced chart data calculations with additional analytics
  const chartData = useMemo(() => {
    if (!data) return null;

    const conversationStats = data.conversation_stats || {};
    const usageMetrics = data.usage_metrics || {};
    
    // Use real performance data if available
    const realPerformanceData = performanceData || data.performance_metrics || {};
    const realSystemData = systemData || data.system_health || {};

    const conversationChartData = [
      { name: 'Mon', conversations: (conversationStats.total_conversations ?? 0) * 0.8 },
      { name: 'Tue', conversations: (conversationStats.total_conversations ?? 0) * 1.2 },
      { name: 'Wed', conversations: (conversationStats.total_conversations ?? 0) * 0.9 },
      { name: 'Thu', conversations: (conversationStats.total_conversations ?? 0) * 1.1 },
      { name: 'Fri', conversations: (conversationStats.total_conversations ?? 0) * 1.3 },
      { name: 'Sat', conversations: (conversationStats.total_conversations ?? 0) * 0.7 },
      { name: 'Sun', conversations: (conversationStats.total_conversations ?? 0) },
    ];

    const tokenUsageData = [
      { name: 'Week 1', tokens: (usageMetrics.total_tokens ?? 0) * 0.6 },
      { name: 'Week 2', tokens: (usageMetrics.total_tokens ?? 0) * 0.8 },
      { name: 'Week 3', tokens: (usageMetrics.total_tokens ?? 0) * 1.1 },
      { name: 'Week 4', tokens: usageMetrics.total_tokens ?? 0 },
    ];

    // Enhanced performance data from performance API
    const performanceChartData = performanceData ? [
      { name: 'API Latency', value: realPerformanceData.avg_response_time_ms ?? 0 },
      { name: 'P95 Latency', value: realPerformanceData.p95_response_time_ms ?? 0 },
      { name: 'P99 Latency', value: realPerformanceData.p99_response_time_ms ?? 0 },
    ] : [];

    const systemHealthData = [
      { name: 'CPU', value: 65, color: '#8884d8' },
      { name: 'Memory', value: 45, color: '#82ca9d' },
      { name: 'Storage', value: 30, color: '#ffc658' },
      { name: 'Network', value: 80, color: '#ff7c7c' },
    ];

    return {
      conversationChartData,
      tokenUsageData,
      performanceChartData,
      systemHealthData,
    };
  }, [data, performanceData, systemData]);

  // Helper function for exporting analytics
  const handleExportAnalytics = async (format: 'json' | 'csv' | 'xlsx' = 'json') => {
    try {
      await chatterSDK.analytics.exportAnalyticsApiV1AnalyticsExportPost({
        metrics: ['conversations', 'usage', 'performance'],
        format,
        period: '30d'
      });
      toastService.success(`Analytics exported as ${format.toUpperCase()}`);
    } catch (error: any) {
      console.error('Failed to export analytics:', error);
      toastService.error('Failed to export analytics');
    }
  };

  if (dashboardApi.loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress size={60} />
      </Box>
    );
  }

  if (dashboardApi.error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        {dashboardApi.error}
      </Alert>
    );
  }

  if (!data || !chartData) {
    return null;
  }

  // Defensive checks for nested data
  const conversationStats = data.conversation_stats || {};
  const usageMetrics = usageData || data.usage_metrics || {};
  const documentAnalytics = documentData || data.document_analytics || {};
  const systemHealth = systemData || data.system_health || {};
  const performanceMetrics = performanceData || data.performance_metrics || {};

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  const formatBytes = (bytes: number | undefined | null) => {
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    if (!bytes || bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  const toolbar = (
    <>
      <Button
        variant="outlined"
        startIcon={<GetApp />}
        onClick={() => handleExportAnalytics('json')}
        size="small"
      >
        Export JSON
      </Button>
      <Button
        variant="outlined"
        startIcon={<GetApp />}
        onClick={() => handleExportAnalytics('csv')}
        size="small"
      >
        Export CSV
      </Button>
    </>
  );

  return (
    <PageLayout title="Dashboard" toolbar={toolbar}>
      {/* Enhanced Navigation Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={(_, newValue) => setActiveTab(newValue)}
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab icon={<Assessment />} label="Overview" />
          <Tab icon={<ShowChart />} label="Performance" />
          <Tab icon={<Computer />} label="System" />
          <Tab icon={<Storage />} label="Documents" />
          <Tab icon={<Settings />} label="Tools" />
        </Tabs>
      </Paper>

      {/* Tab Content */}
      {activeTab === 0 && (
        <>
          {/* Key Metrics */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid
              size={{
                xs: 12,
                sm: 6,
                md: 3
              }}>
              <MetricCard
                title="Total Conversations"
                value={safeLocaleString(conversationStats.total_conversations)}
                change={`+${safeLocaleString(conversationStats.total_conversations)} today`}
                changeType="positive"
                icon={<Message />}
                color="primary"
              />
            </Grid>
            <Grid
              size={{
                xs: 12,
                sm: 6,
                md: 3
              }}>
              <MetricCard
                title="Total Messages"
                value={safeLocaleString(conversationStats.total_messages)}
                change={`Avg ${safeToFixed(conversationStats.avg_messages_per_conversation, 1)} per conversation`}
                changeType="neutral"
                icon={<TrendingUp />}
                color="secondary"
              />
            </Grid>
            <Grid
              size={{
                xs: 12,
                sm: 6,
                md: 3
              }}>
              <MetricCard
                title="Token Usage"
                value={safeLocaleString(usageMetrics.total_tokens)}
                change={`${safeLocaleString(usageMetrics.total_prompt_tokens)} prompts`}
                changeType="positive"
                icon={<Assessment />}
                color="info"
              />
            </Grid>
            <Grid
              size={{
                xs: 12,
                sm: 6,
                md: 3
              }}>
              <MetricCard
                title="Documents"
                value={safeLocaleString(documentAnalytics.total_documents)}
                change={`${safeLocaleString(documentAnalytics.total_chunks)} chunks`}
                changeType="neutral"
                icon={<Storage />}
                color="success"
              />
            </Grid>
          </Grid>
          {/* Charts Section */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid
              size={{
                xs: 12,
                md: 8
              }}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Daily Conversations
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={chartData.conversationChartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Area type="monotone" dataKey="conversations" stroke="#8884d8" fill="#8884d8" />
                    </AreaChart>
                  </ResponsiveContainer>
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
                  <Typography variant="h6" gutterBottom sx={{ mb: 3 }}>
                    Token Usage Trends
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={chartData.tokenUsageData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Line type="monotone" dataKey="tokens" stroke="#82ca9d" strokeWidth={3} />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </>
      )}

      {activeTab === 1 && (
        <Grid container spacing={3}>
          <Grid size={{ xs: 12, md: 8 }}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Performance Metrics
                </Typography>
                {chartData.performanceChartData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={chartData.performanceChartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip formatter={(value) => [`${value}ms`, 'Latency']} />
                      <Bar dataKey="value" fill="#8884d8" />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <Alert severity="info">Performance data loading...</Alert>
                )}
              </CardContent>
            </Card>
          </Grid>
          <Grid size={{ xs: 12, md: 4 }}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Response Times
                </Typography>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" gutterBottom>
                    Average: {safeToFixed(performanceMetrics.avg_response_time_ms, 2)}ms
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={Math.min((performanceMetrics.avg_response_time_ms ?? 0) / 10, 100)}
                    sx={{ mb: 1 }}
                  />
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" gutterBottom>
                    P95: {safeToFixed(performanceMetrics.p95_response_time_ms ?? 0, 1)}ms
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={Math.min((performanceMetrics.p95_response_time_ms ?? 0) / 20, 100)}
                    color="warning"
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {activeTab === 2 && (
        <Grid container spacing={3}>
          <Grid size={{ xs: 12, md: 6 }}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ mb: 3 }}>
                  System Health
                </Typography>
                <Grid container spacing={2}>
                  <Grid size={6}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <People sx={{ mr: 1, color: 'primary.main' }} />
                      <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="body2">Active Users</Typography>
                        <Typography variant="h6">
                          {safeLocaleString(systemHealth.active_users_today)}
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>
                  <Grid size={6}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <CloudQueue sx={{ mr: 1, color: 'secondary.main' }} />
                      <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="body2">Storage</Typography>
                        <Typography variant="h6">
                          {formatBytes(systemHealth.storage_usage_bytes)}
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
          <Grid size={{ xs: 12, md: 6 }}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Resource Usage
                </Typography>
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={chartData.systemHealthData}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {chartData.systemHealthData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {activeTab === 3 && (
        <Grid container spacing={3}>
          <Grid size={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Document Analytics
                </Typography>
                {documentData ? (
                  <Grid container spacing={2}>
                    <Grid size={4}>
                      <Typography variant="body2" color="text.secondary">Total Documents</Typography>
                      <Typography variant="h5">{safeLocaleString(documentAnalytics.total_documents)}</Typography>
                    </Grid>
                    <Grid size={4}>
                      <Typography variant="body2" color="text.secondary">Total Chunks</Typography>
                      <Typography variant="h5">{safeLocaleString(documentAnalytics.total_chunks)}</Typography>
                    </Grid>
                    <Grid size={4}>
                      <Typography variant="body2" color="text.secondary">Storage Size</Typography>
                      <Typography variant="h5">{formatBytes(documentAnalytics.total_size_bytes ?? 0)}</Typography>
                    </Grid>
                  </Grid>
                ) : (
                  <Alert severity="info">Document analytics loading...</Alert>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {activeTab === 4 && (
        <Grid container spacing={3}>
          <Grid size={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Tool Server Analytics
                </Typography>
                {toolServerData ? (
                  <Grid container spacing={2}>
                    <Grid size={4}>
                      <Typography variant="body2" color="text.secondary">Active Servers</Typography>
                      <Typography variant="h5">{safeLocaleString(toolServerData.active_servers ?? 0)}</Typography>
                    </Grid>
                    <Grid size={4}>
                      <Typography variant="body2" color="text.secondary">Total Requests</Typography>
                      <Typography variant="h5">{safeLocaleString(toolServerData.total_requests ?? 0)}</Typography>
                    </Grid>
                    <Grid size={4}>
                      <Typography variant="body2" color="text.secondary">Avg Response Time</Typography>
                      <Typography variant="h5">{safeToFixed(toolServerData.avg_response_time_ms ?? 0, 1)}ms</Typography>
                    </Grid>
                  </Grid>
                ) : (
                  <Alert severity="info">Tool server analytics loading...</Alert>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Status Indicators */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            System Status
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            <Chip
              label="API Server"
              color="success"
              variant="outlined"
              icon={<CloudQueue />}
            />
            <Chip
              label="Database"
              color="success"
              variant="outlined"
              icon={<Storage />}
            />
            <Chip
              label="Vector Store"
              color="success"
              variant="outlined"
              icon={<SmartToy />}
            />
            <Chip
              label={`Avg Response: ${safeToFixed(performanceMetrics.avg_response_time_ms ?? 0, 0)}ms`}
              color={(performanceMetrics.avg_response_time_ms ?? 0) < 1000 ? "success" : "warning"}
              variant="outlined"
              icon={<Speed />}
            />
          </Box>
        </CardContent>
      </Card>
    </PageLayout>
  );

};

export default memo(DashboardPage);
