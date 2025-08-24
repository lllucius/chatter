import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  LinearProgress,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  BarChart,
  Bar,
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
import { api, DashboardData } from '../services/api';

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

const DashboardPage: React.FC = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const dashboardData = await api.getDashboardData();
        setData(dashboardData);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load dashboard data');
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

  // Sample chart data (in a real app, this would come from the API)
  const conversationChartData = [
    { name: 'Mon', conversations: data.conversation_stats.conversations_today * 0.8 },
    { name: 'Tue', conversations: data.conversation_stats.conversations_today * 1.2 },
    { name: 'Wed', conversations: data.conversation_stats.conversations_today * 0.9 },
    { name: 'Thu', conversations: data.conversation_stats.conversations_today * 1.1 },
    { name: 'Fri', conversations: data.conversation_stats.conversations_today * 1.3 },
    { name: 'Sat', conversations: data.conversation_stats.conversations_today * 0.7 },
    { name: 'Sun', conversations: data.conversation_stats.conversations_today },
  ];

  const tokenUsageData = [
    { name: 'Week 1', tokens: data.usage_metrics.tokens_week * 0.6 },
    { name: 'Week 2', tokens: data.usage_metrics.tokens_week * 0.8 },
    { name: 'Week 3', tokens: data.usage_metrics.tokens_week * 1.1 },
    { name: 'Week 4', tokens: data.usage_metrics.tokens_week },
  ];

  const systemHealthData = [
    { name: 'CPU', value: 65, color: '#8884d8' },
    { name: 'Memory', value: 45, color: '#82ca9d' },
    { name: 'Storage', value: 30, color: '#ffc658' },
    { name: 'Network', value: 80, color: '#ff7c7c' },
  ];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  const formatBytes = (bytes: number) => {
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    if (bytes === 0) return '0 Bytes';
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
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Conversations"
            value={data.conversation_stats.total_conversations.toLocaleString()}
            change={`+${data.conversation_stats.conversations_today} today`}
            changeType="positive"
            icon={<Message />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Messages"
            value={data.conversation_stats.total_messages.toLocaleString()}
            change={`Avg ${data.conversation_stats.avg_messages_per_conversation.toFixed(1)} per conversation`}
            changeType="neutral"
            icon={<TrendingUp />}
            color="secondary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Token Usage"
            value={data.usage_metrics.total_tokens.toLocaleString()}
            change={`${data.usage_metrics.tokens_today.toLocaleString()} today`}
            changeType="positive"
            icon={<Assessment />}
            color="info"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Documents"
            value={data.document_analytics.total_documents.toLocaleString()}
            change={`${data.document_analytics.total_chunks.toLocaleString()} chunks`}
            changeType="neutral"
            icon={<Storage />}
            color="success"
          />
        </Grid>
      </Grid>

      {/* Charts Section */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={8}>
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
        <Grid item xs={12} md={4}>
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
        <Grid item xs={12} md={6}>
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
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ mb: 3 }}>
                System Health
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <People sx={{ mr: 1, color: 'primary.main' }} />
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography variant="body2">Active Users</Typography>
                      <Typography variant="h6">
                        {data.system_health.active_users_today}
                      </Typography>
                    </Box>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <CloudQueue sx={{ mr: 1, color: 'secondary.main' }} />
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography variant="body2">Storage</Typography>
                      <Typography variant="h6">
                        {formatBytes(data.system_health.storage_usage_bytes)}
                      </Typography>
                    </Box>
                  </Box>
                </Grid>
                <Grid item xs={12}>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" gutterBottom>
                      Response Time: {data.performance_metrics.avg_response_time.toFixed(2)}ms
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={Math.min(data.performance_metrics.avg_response_time / 10, 100)}
                      sx={{ mb: 1 }}
                    />
                  </Box>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" gutterBottom>
                      Success Rate: {(data.performance_metrics.success_rate * 100).toFixed(1)}%
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={data.performance_metrics.success_rate * 100}
                      color="success"
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
              label={`Performance: ${(data.performance_metrics.success_rate * 100).toFixed(0)}%`}
              color={data.performance_metrics.success_rate > 0.9 ? "success" : "warning"}
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