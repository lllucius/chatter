import React, { memo } from 'react';
import { Grid, Paper, Typography, Box, Chip } from '../../utils/mui';
import { ABTestResponse } from 'chatter-sdk';
import { format } from 'date-fns';

interface ABTestOverviewTabProps {
  test: ABTestResponse;
}

const ABTestOverviewTab: React.FC<ABTestOverviewTabProps> = memo(({ test }) => {
  return (
    <Grid container spacing={3}>
      <Grid size={{ xs: 12, md: 6 }}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Test Details
          </Typography>
          <Typography>
            <strong>Type:</strong> {test.test_type}
          </Typography>
          <Typography>
            <strong>Status:</strong> {test.status}
          </Typography>
          <Typography>
            <strong>Duration:</strong> {test.duration_days} days
          </Typography>
          <Typography>
            <strong>Sample Size:</strong>{' '}
            {test.min_sample_size.toLocaleString()}
          </Typography>
          <Typography>
            <strong>Confidence:</strong>{' '}
            {(test.confidence_level * 100).toFixed(1)}%
          </Typography>
          {test.created_at && (
            <Typography>
              <strong>Created:</strong>{' '}
              {format(new Date(test.created_at), 'MMM dd, yyyy HH:mm')}
            </Typography>
          )}
          {test.description && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2">Description</Typography>
              <Typography variant="body2" color="text.secondary">
                {test.description}
              </Typography>
            </Box>
          )}
        </Paper>
      </Grid>

      <Grid size={{ xs: 12, md: 6 }}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Test Configuration
          </Typography>

          {test.variants && test.variants.length > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Variants
              </Typography>
              {test.variants.map((variant, index) => (
                <Box key={index} sx={{ mb: 1 }}>
                  <Chip
                    label={variant.name || `Variant ${index + 1}`}
                    size="small"
                    sx={{ mr: 1 }}
                  />
                  {variant.weight && (
                    <Typography variant="caption" color="text.secondary">
                      {variant.weight}% traffic
                    </Typography>
                  )}
                </Box>
              ))}
            </Box>
          )}

          {test.metrics && test.metrics.length > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Success Metrics
              </Typography>
              {test.metrics.map((metric, index) => (
                <Typography key={index} variant="body2">
                  • {metric}
                </Typography>
              ))}
            </Box>
          )}

          {test.target_audience && (
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Target Audience
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {typeof test.target_audience === 'string'
                  ? test.target_audience
                  : JSON.stringify(test.target_audience)}
              </Typography>
            </Box>
          )}
        </Paper>
      </Grid>

      {test.description && (
        <Grid size={{ xs: 12 }}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Test Description
            </Typography>
            <Typography variant="body1">{test.description}</Typography>
          </Paper>
        </Grid>
      )}
    </Grid>
  );
});

ABTestOverviewTab.displayName = 'ABTestOverviewTab';

export default ABTestOverviewTab;
