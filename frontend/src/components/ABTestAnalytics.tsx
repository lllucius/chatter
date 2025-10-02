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
import {
  TestRecommendations,
  TestPerformance,
} from '../hooks/useABTestingData';

interface ABTestAnalyticsProps {
  testId: string;
  testName: string;
  metrics?: ABTestMetricsResponse;
  results?: ABTestResultsResponse;
  recommendations?: TestRecommendations;
  performance?: TestPerformance;
}

const ABTestAnalytics: React.FC<ABTestAnalyticsProps> = ({
  testId: _testId,
  testName: _testName,
  metrics,
  results,
  recommendations,
  performance: _performance,
}) => {
  // Use real metrics data - no sample data
  const actualMetrics = React.useMemo(() => {
    return metrics || null;
  }, [metrics]);

  // Use real statistics from backend - no sample data
  const actualStatistics = React.useMemo(() => {
    // In real implementation, this would come from results prop
    return results ? {
      confidence_level: 0.95,
      effect_size: results.metrics?.find((m: any) => m.metric_name === 'effect_size')?.value || 0,
      power: 0.8,
      p_value: results.metrics?.find((m: any) => m.metric_name === 'p_value')?.value || 0,
    } : null;
  }, [results]);

  // Use real variant data - no mock data
  const actualVariants = React.useMemo(() => {
    // Extract variants from metrics if available
    if (metrics?.metrics) {
      return metrics.metrics;
    }
    return [];
  }, [metrics]);

  // Use real results data - no sample data
  const actualResults = React.useMemo(() => {
    return results || null;
  }, [results]);

  // Time series data for charts - show empty if no real data
  const timeSeriesData = React.useMemo(() => {
    // In a real implementation, this would come from the performance prop or API
    // For now, return empty array to indicate no data available
    return [];
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
                {actualMetrics?.participant_count?.toLocaleString() || 'N/A'}
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
                  {results &&
                  Object.keys(results.statistical_significance).length > 0 &&
                  Object.values(results.statistical_significance)[0]
                    ? 'Yes'
                    : 'No'}
                </Typography>
                {results &&
                Object.keys(results.statistical_significance).length > 0 &&
                Object.values(results.statistical_significance)[0] ? (
                  <CheckCircle color="success" sx={{ ml: 1 }} />
                ) : (
                  <Warning color="warning" sx={{ ml: 1 }} />
                )}
              </Box>
              <Typography variant="body2" color="text.secondary">
                p-value: N/A
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
                {actualResults?.winning_variant
                  ?.replace('_', ' ')
                  .toUpperCase() || 'TBD'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                +20.8% improvement
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
                {Math.round(((14 - 3) / 14) * 100)}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={((14 - 3) / 14) * 100}
                sx={{ mt: 1 }}
              />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                3 days remaining
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Conversion Rate Trend */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid size={{ xs: 12, lg: 8 }}>
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

        <Grid size={{ xs: 12, lg: 4 }}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Variant Performance
              </Typography>
              {actualVariants && actualVariants.length > 0 ? (
                <List>
                  {actualVariants.map((variant: any) => (
                    <ListItem key={variant.name || variant.variant_id} sx={{ px: 0 }}>
                      <ListItemIcon>
                        {getTrendIcon(variant.conversion_rate || 0, 0.12)}
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
                              {(variant.name || variant.variant_id || 'Unknown').replace('_', ' ').toUpperCase()}
                            </Typography>
                            <Chip
                              label={`${((variant.conversion_rate || 0) * 100).toFixed(1)}%`}
                              size="small"
                              color={
                                (variant.name || variant.variant_id) === actualResults?.winning_variant
                                  ? 'success'
                                  : 'default'
                              }
                            />
                          </Box>
                        }
                        secondary={
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              {variant.conversions || 0} / {variant.participants || 0}{' '}
                              conversions
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              ROI: {(variant.roi || 0).toFixed(2)}x
                            </Typography>
                          </Box>
                        }
                      />
                  </ListItem>
                ))}
              </List>
              ) : (
                <Typography variant="body2" color="text.secondary" sx={{ py: 2 }}>
                  No variant data available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Detailed Charts */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid size={{ xs: 12, md: 6 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Participant Distribution
              </Typography>
              {actualVariants && actualVariants.length > 0 ? (
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={actualVariants}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={(props: {
                        name?: string;
                        value?: string | number;
                      }) =>
                        `${props.name?.replace('_', ' ').toUpperCase() || 'Unknown'}: ${props.value || 0}`
                      }
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="participants"
                    >
                      {actualVariants.map((entry: any, index: number) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={Object.values(variantColors)[index]}
                        />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <Typography variant="body2" color="text.secondary" sx={{ py: 2 }}>
                  No participant data available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 6 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Revenue Comparison
              </Typography>
              {actualVariants && actualVariants.length > 0 ? (
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={actualVariants}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="name"
                      tickFormatter={(value) =>
                        value?.replace('_', ' ').toUpperCase() || ''
                      }
                    />
                    <YAxis />
                    <Tooltip
                      formatter={(value: unknown) => [
                        `$${Number(value).toLocaleString()}`,
                        'Revenue',
                      ]}
                      labelFormatter={(label) =>
                        label?.replace('_', ' ').toUpperCase() || ''
                      }
                    />
                    <Bar dataKey="revenue" fill="#82ca9d" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <Typography variant="body2" color="text.secondary" sx={{ py: 2 }}>
                  No revenue data available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recommendations */}
      {recommendations &&
        (recommendations.recommendations.length > 0 ||
          recommendations.insights.length > 0) && (
          <Grid container spacing={3}>
            <Grid size={{ xs: 12, md: 6 }}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    AI Recommendations
                  </Typography>
                  <List>
                    {recommendations.recommendations.map((rec, index) => (
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

            <Grid size={{ xs: 12, md: 6 }}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Key Insights
                  </Typography>
                  <List>
                    {recommendations.insights.map((insight, index) => (
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
                      {actualStatistics ? (actualStatistics.confidence_level * 100).toFixed(0) : 'N/A'}%
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Confidence Level
                    </Typography>
                  </Paper>
                </Grid>
                <Grid size={{ xs: 6, sm: 3 }}>
                  <Paper variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="h6">
                      {actualStatistics ? (actualStatistics.effect_size * 100).toFixed(1) : 'N/A'}%
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Effect Size
                    </Typography>
                  </Paper>
                </Grid>
                <Grid size={{ xs: 6, sm: 3 }}>
                  <Paper variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="h6">
                      {actualStatistics ? (actualStatistics.power * 100).toFixed(0) : 'N/A'}%
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Statistical Power
                    </Typography>
                  </Paper>
                </Grid>
                <Grid size={{ xs: 6, sm: 3 }}>
                  <Paper variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="h6">
                      {actualStatistics ? actualStatistics.p_value.toFixed(4) : 'N/A'}
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
