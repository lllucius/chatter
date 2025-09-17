import React, { memo } from 'react';
import {
  Box,
  Typography,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  LinearProgress,
} from '../../utils/mui';
import { JobIcon, RefreshIcon } from '../../utils/icons';
import { JobResponse, JobStatsResponse } from 'chatter-sdk';

interface JobsTabProps {
  jobs: JobResponse[];
  jobStats: JobStatsResponse | null;
  loading: boolean;
  onRefresh: () => void;
  onCreateJob: () => void;
}

const JobsTab: React.FC<JobsTabProps> = memo(({
  jobs,
  jobStats,
  loading,
  onRefresh,
  onCreateJob,
}) => {
  const getJobStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      case 'running':
        return 'info';
      case 'pending':
        return 'warning';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      {/* Job Statistics */}
      {jobStats && (
        <Box sx={{ mb: 3, p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
          <Typography variant="h6" gutterBottom>
            Job Statistics
          </Typography>
          <Box sx={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Total Jobs
              </Typography>
              <Typography variant="h6">{jobStats.total_jobs}</Typography>
            </Box>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Completed
              </Typography>
              <Typography variant="h6" color="success.main">
                {jobStats.completed_jobs}
              </Typography>
            </Box>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Failed
              </Typography>
              <Typography variant="h6" color="error.main">
                {jobStats.failed_jobs}
              </Typography>
            </Box>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Running
              </Typography>
              <Typography variant="h6" color="info.main">
                {jobStats.running_jobs}
              </Typography>
            </Box>
          </Box>
        </Box>
      )}

      {/* Actions */}
      <Box sx={{ mb: 2, display: 'flex', gap: 1 }}>
        <Button
          variant="contained"
          startIcon={<JobIcon />}
          onClick={onCreateJob}
          disabled={loading}
        >
          Create Job
        </Button>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={onRefresh}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>

      {/* Jobs List */}
      <List>
        {jobs.map((job) => (
          <ListItem key={job.id}>
            <ListItemIcon>
              <JobIcon />
            </ListItemIcon>
            <ListItemText
              primary={job.name || job.id.substring(0, 8)}
              secondary={
                <Box sx={{ mt: 1 }}>
                  <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                    <Chip
                      size="small"
                      label={job.status}
                      color={getJobStatusColor(job.status)}
                    />
                    <Typography variant="caption" color="text.secondary">
                      Priority: {job.priority}
                    </Typography>
                  </Box>
                  {job.status === 'running' && job.progress && (
                    <Box sx={{ mt: 1 }}>
                      <LinearProgress
                        variant="determinate"
                        value={job.progress}
                        sx={{ mb: 1 }}
                      />
                      <Typography variant="caption">
                        {job.progress}% complete
                      </Typography>
                    </Box>
                  )}
                  <Typography variant="caption" color="text.secondary">
                    Created: {new Date(job.created_at).toLocaleString()}
                  </Typography>
                </Box>
              }
            />
          </ListItem>
        ))}
        {jobs.length === 0 && (
          <ListItem>
            <ListItemText
              primary="No background jobs found"
              secondary="Background jobs will appear here when created"
            />
          </ListItem>
        )}
      </List>
    </Box>
  );
});

JobsTab.displayName = 'JobsTab';

export default JobsTab;