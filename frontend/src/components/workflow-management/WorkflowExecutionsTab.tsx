import React, { memo } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Typography,
  Box,
  Alert,
} from '../../utils/mui';

interface WorkflowExecution {
  id: string;
  workflow_name: string;
  status: string;
  started_at: string;
  completed_at?: string;
  input: any;
  output?: any;
  error?: string;
}

interface WorkflowExecutionsTabProps {
  executions: WorkflowExecution[];
  loading: boolean;
}

const WorkflowExecutionsTab: React.FC<WorkflowExecutionsTabProps> = memo(({
  executions,
  loading,
}) => {
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'success';
      case 'running':
        return 'info';
      case 'failed':
        return 'error';
      case 'pending':
        return 'warning';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <Typography>Loading executions...</Typography>
      </Box>
    );
  }

  if (executions.length === 0) {
    return (
      <Alert severity="info">
        No workflow executions found. Execute a workflow to see results here.
      </Alert>
    );
  }

  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Workflow</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Started</TableCell>
            <TableCell>Completed</TableCell>
            <TableCell>Duration</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {executions.map((execution) => {
            const startTime = new Date(execution.started_at);
            const endTime = execution.completed_at ? new Date(execution.completed_at) : null;
            const duration = endTime ? 
              `${Math.round((endTime.getTime() - startTime.getTime()) / 1000)}s` : 
              '-';

            return (
              <TableRow key={execution.id} hover>
                <TableCell>
                  <Typography variant="subtitle2">
                    {execution.workflow_name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    ID: {execution.id.substring(0, 8)}...
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip
                    label={execution.status}
                    size="small"
                    color={getStatusColor(execution.status)}
                  />
                </TableCell>
                <TableCell>
                  {startTime.toLocaleString()}
                </TableCell>
                <TableCell>
                  {endTime ? endTime.toLocaleString() : '-'}
                </TableCell>
                <TableCell>
                  {duration}
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </TableContainer>
  );
});

WorkflowExecutionsTab.displayName = 'WorkflowExecutionsTab';

export default WorkflowExecutionsTab;