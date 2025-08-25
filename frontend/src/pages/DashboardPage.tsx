import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  LinearProgress,
  Alert,
  CircularProgress,
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
} from '@mui/icons-material';
import { chatterSDK } from '../services/chatter-sdk';
import { DashboardResponse } from '../sdk';

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: string;
  changeType?: 'positive' | 'negative' | 'neutral';
  icon: React.ReactElement;
  color: string;
}

const MetricCard: React.FC<MetricCardProps> = ({
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
};

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
  const [data, setData] = useState<DashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const response = await chatterSDK.analytics.getDashboardApiV1AnalyticsDashboardGet();
        setData(response.data);
      } catch (err: any) {
        setError(err?.response?.data?.detail || 'Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress size={60} />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        {error}
      </Alert>
    );
  }

  if (!data) {
    return null;
  }

  // Defensive checks for nested data (for demo, but you may want more robust validation)
  const conversationStats = data.conversation_stats || {};
  const usageMetrics = data.usage_metrics || {};
  const documentAnalytics = data.document_analytics || {};
  const systemHealth = data.system_health || {};
  const performanceMetrics = data.performance_metrics || {};

  // Sample chart data (in a real app, this would come from the API)
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

  const systemHealthData = [
    { name: 'CPU', value: 65, color: '#8884d8' },
    { name: 'Memory', value: 45, color: '#82ca9d' },
    { name: 'Storage', value: 30, color: '#ffc658' },
    { name: 'Network', value: 80, color: '#ff7c7c' },
  ];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  const formatBytes = (bytes: number | undefined | null) => {
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    if (!bytes || bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 3, fontWeight: 'bold' }}>
        Dashboard
      </Typography>
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
                <AreaChart data={conversationChartData}>
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
              <Typography variant="h6" gutterBottom>
                System Resources
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={systemHealthData}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    label
                  >
                    {systemHealthData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      {/* Additional Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid
          size={{
            xs: 12,
            md: 6
          }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Token Usage Trends
              </Typography>
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={tokenUsageData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="tokens" stroke="#82ca9d" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
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
                <Grid size={12}>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" gutterBottom>
                      Response Time: {safeToFixed(performanceMetrics.avg_response_time_ms, 2)}ms
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={Math.min((performanceMetrics.avg_response_time_ms ?? 0) / 10, 100)}
                      sx={{ mb: 1 }}
                    />
                  </Box>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" gutterBottom>
                      P95 Response Time: {safeToFixed(performanceMetrics.p95_response_time_ms ?? 0, 1)}ms
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={Math.min((performanceMetrics.p95_response_time_ms ?? 0) / 20, 100)}
                      color="warning"
                    />
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
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
    </Box>
  );
};

export default DashboardPage;
