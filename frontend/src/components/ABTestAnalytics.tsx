import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  TrendingFlat,
  CheckCircle,
  Warning,
  Error as ErrorIcon,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { ABTestMetricsResponse, ABTestResultsResponse } from 'chatter-sdk';

interface ABTestAnalyticsProps {
  _testId: string;
  _testName: string;
  metrics?: ABTestMetricsResponse;
  results?: ABTestResultsResponse;
  recommendations?: {
    recommendations: string[];
    insights: string[];
    winner?: string;
    confidence?: number;
  };
  _performance?: {
    response_times: Array<{
      timestamp: string;
      variant: string;
      response_time: number;
    }>;
    error_rates: Array<{
      timestamp: string;
      variant: string;
      error_rate: number;
    }>;
    throughput: Array<{
      timestamp: string;
      variant: string;
      requests_per_second: number;
    }>;
  };
}

const ABTestAnalytics: React.FC<ABTestAnalyticsProps> = ({
  _testId,
  _testName,
  metrics,
  results,
  recommendations,
  _performance,
}) => {
  // Generate sample data if real data isn't available
  const sampleMetrics = React.useMemo(() => {
    if (metrics) return metrics;

    return {
      total_participants: 5420,
      conversion_rate: {
        control: 0.12,
        variant_a: 0.145,
        variant_b: 0.138,
      },
      confidence_level: 0.95,
      statistical_significance: true,
      p_value: 0.032,
      effect_size: 0.025,
      power: 0.84,
      duration_days: 14,
      remaining_days: 3,
    };
  }, [metrics]);

  const sampleResults = React.useMemo(() => {
    if (results) return results;

    return {
      winner: 'variant_a',
      improvement: 0.208,
      confidence: 0.95,
      significance: true,
      variants: [
        {
          name: 'control',
          participants: 1807,
          conversions: 217,
          conversion_rate: 0.12,
          revenue: 43400,
          cost: 12100,
          roi: 2.59,
        },
        {
          name: 'variant_a',
          participants: 1806,
          conversions: 262,
          conversion_rate: 0.145,
          revenue: 52400,
          cost: 12000,
          roi: 3.37,
        },
        {
          name: 'variant_b',
          participants: 1807,
          conversions: 249,
          conversion_rate: 0.138,
          revenue: 49800,
          cost: 11900,
          roi: 3.18,
        },
      ],
    };
  }, [results]);

  // Time series data for charts
  const timeSeriesData = React.useMemo(() => {
    const days = 14;
    const data = [];

    for (let i = 0; i < days; i++) {
      data.push({
        day: i + 1,
        control: 0.1 + Math.random() * 0.04 + i * 0.001,
        variant_a: 0.12 + Math.random() * 0.05 + i * 0.002,
        variant_b: 0.115 + Math.random() * 0.045 + i * 0.0015,
        control_participants: 120 + Math.floor(Math.random() * 20),
        variant_a_participants: 118 + Math.floor(Math.random() * 22),
        variant_b_participants: 122 + Math.floor(Math.random() * 18),
      });
    }

    return data;
  }, []);

  // Variant colors for charts
  const variantColors = {
    control: '#8884d8',
    variant_a: '#82ca9d',
    variant_b: '#ffc658',
  };

  const getRecommendationIcon = (type: string) => {
    switch (type) {
      case 'winner':
        return <CheckCircle color="success" />;
      case 'warning':
        return <Warning color="warning" />;
      case 'error':
        return <ErrorIcon color="error" />;
      default:
        return <TrendingUp color="info" />;
    }
  };

  const getTrendIcon = (current: number, previous: number) => {
    if (current > previous) return <TrendingUp color="success" />;
    if (current < previous) return <TrendingDown color="error" />;
    return <TrendingFlat color="action" />;
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Total Participants
              </Typography>
              <Typography variant="h4">
                {sampleMetrics.total_participants?.toLocaleString() || 'N/A'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Across all variants
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Statistical Significance
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Typography variant="h4">
                  {sampleMetrics.statistical_significance ? 'Yes' : 'No'}
                </Typography>
                {sampleMetrics.statistical_significance ? (
                  <CheckCircle color="success" sx={{ ml: 1 }} />
                ) : (
                  <Warning color="warning" sx={{ ml: 1 }} />
                )}
              </Box>
              <Typography variant="body2" color="text.secondary">
                p-value: {sampleMetrics.p_value?.toFixed(4) || 'N/A'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Best Performer
              </Typography>
              <Typography variant="h5">
                {sampleResults.winner?.replace('_', ' ').toUpperCase() || 'TBD'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                +{((sampleResults.improvement || 0) * 100).toFixed(1)}%
                improvement
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Test Progress
              </Typography>
              <Typography variant="h5">
                {Math.round(
                  (((sampleMetrics.duration_days || 14) -
                    (sampleMetrics.remaining_days || 0)) /
                    (sampleMetrics.duration_days || 14)) *
                    100
                )}
                %
              </Typography>
              <LinearProgress
                variant="determinate"
                value={
                  (((sampleMetrics.duration_days || 14) -
                    (sampleMetrics.remaining_days || 0)) /
                    (sampleMetrics.duration_days || 14)) *
                  100
                }
                sx={{ mt: 1 }}
              />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                {sampleMetrics.remaining_days || 0} days remaining
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Conversion Rate Trend */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid size={{ xs: 12 }} lg={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Conversion Rate Over Time
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={timeSeriesData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="day"
                    label={{
                      value: 'Days',
                      position: 'insideBottom',
                      offset: -5,
                    }}
                  />
                  <YAxis
                    label={{
                      value: 'Conversion Rate',
                      angle: -90,
                      position: 'insideLeft',
                    }}
                  />
                  <Tooltip
                    formatter={(value: unknown, name: string) => [
                      `${(Number(value) * 100).toFixed(2)}%`,
                      name.replace('_', ' ').toUpperCase(),
                    ]}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="control"
                    stroke={variantColors.control}
                    strokeWidth={2}
                    name="Control"
                  />
                  <Line
                    type="monotone"
                    dataKey="variant_a"
                    stroke={variantColors.variant_a}
                    strokeWidth={2}
                    name="Variant A"
                  />
                  <Line
                    type="monotone"
                    dataKey="variant_b"
                    stroke={variantColors.variant_b}
                    strokeWidth={2}
                    name="Variant B"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12 }} lg={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Variant Performance
              </Typography>
              <List>
                {sampleResults.variants?.map((variant): void => (
                  <ListItem key={variant.name} sx={{ px: 0 }}>
                    <ListItemIcon>
                      {getTrendIcon(variant.conversion_rate, 0.12)}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box
                          sx={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                          }}
                        >
                          <Typography variant="subtitle2">
                            {variant.name.replace('_', ' ').toUpperCase()}
                          </Typography>
                          <Chip
                            label={`${(variant.conversion_rate * 100).toFixed(1)}%`}
                            size="small"
                            color={
                              variant.name === sampleResults.winner
                                ? 'success'
                                : 'default'
                            }
                          />
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            {variant.conversions} / {variant.participants}{' '}
                            conversions
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            ROI: {variant.roi.toFixed(2)}x
                          </Typography>
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Detailed Charts */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid size={{ xs: 12 }} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Participant Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={sampleResults.variants}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, participants }) =>
                      `${name.replace('_', ' ').toUpperCase()}: ${participants}`
                    }
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="participants"
                  >
                    {sampleResults.variants?.map((entry, index): void => (
                      <Cell
                        key={`cell-${index}`}
                        fill={Object.values(variantColors)[index]}
                      />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12 }} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Revenue Comparison
              </Typography>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={sampleResults.variants}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="name"
                    tickFormatter={(value) =>
                      value.replace('_', ' ').toUpperCase()
                    }
                  />
                  <YAxis />
                  <Tooltip
                    formatter={(value: unknown) => [
                      `$${Number(value).toLocaleString()}`,
                      'Revenue',
                    ]}
                    labelFormatter={(label) =>
                      label.replace('_', ' ').toUpperCase()
                    }
                  />
                  <Bar dataKey="revenue" fill="#82ca9d" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recommendations */}
      {recommendations &&
        (recommendations.recommendations.length > 0 ||
          recommendations.insights.length > 0) && (
          <Grid container spacing={3}>
            <Grid size={{ xs: 12 }} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    AI Recommendations
                  </Typography>
                  <List>
                    {recommendations.recommendations.map((rec, index): void => (
                      <ListItem key={index} sx={{ px: 0 }}>
                        <ListItemIcon>
                          {getRecommendationIcon('winner')}
                        </ListItemIcon>
                        <ListItemText primary={rec} />
                      </ListItem>
                    ))}
                  </List>
                </CardContent>
              </Card>
            </Grid>

            <Grid size={{ xs: 12 }} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Key Insights
                  </Typography>
                  <List>
                    {recommendations.insights.map((insight, index): void => (
                      <ListItem key={index} sx={{ px: 0 }}>
                        <ListItemIcon>
                          {getRecommendationIcon('info')}
                        </ListItemIcon>
                        <ListItemText primary={insight} />
                      </ListItem>
                    ))}
                  </List>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

      {/* Statistical Details */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid size={{ xs: 12 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Statistical Analysis
              </Typography>
              <Grid container spacing={2}>
                <Grid size={{ xs: 6, sm: 3 }}>
                  <Paper variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="h6">
                      {((sampleMetrics.confidence_level || 0) * 100).toFixed(0)}
                      %
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Confidence Level
                    </Typography>
                  </Paper>
                </Grid>
                <Grid size={{ xs: 6, sm: 3 }}>
                  <Paper variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="h6">
                      {((sampleMetrics.effect_size || 0) * 100).toFixed(1)}%
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Effect Size
                    </Typography>
                  </Paper>
                </Grid>
                <Grid size={{ xs: 6, sm: 3 }}>
                  <Paper variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="h6">
                      {((sampleMetrics.power || 0) * 100).toFixed(0)}%
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Statistical Power
                    </Typography>
                  </Paper>
                </Grid>
                <Grid size={{ xs: 6, sm: 3 }}>
                  <Paper variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="h6">
                      {sampleMetrics.p_value?.toFixed(4) || 'N/A'}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      P-Value
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ABTestAnalytics;
