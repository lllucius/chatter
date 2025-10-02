import React, { memo, useState } from 'react';
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
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '../../utils/mui';
import { ExpandMore, BugReport } from '@mui/icons-material';

interface LogEntry {
  timestamp: string;
  level: string;
  node_id?: string;
  message: string;
  data?: Record<string, unknown>;
  [key: string]: unknown;
}

interface WorkflowExecution {
  id: string;
  workflow_name: string;
  status: string;
  started_at: string;
  completed_at?: string;
  input: Record<string, unknown>;
  output?: Record<string, unknown>;
  error?: string;
  execution_log?: Array<Record<string, unknown>>;
  debug_info?: Record<string, unknown>;
  execution_time_ms?: number;
}

interface WorkflowExecutionsTabProps {
  executions: WorkflowExecution[];
  loading: boolean;
}

const WorkflowExecutionsTab: React.FC<WorkflowExecutionsTabProps> = memo(
  ({ executions, loading }) => {
    const [debugDialogOpen, setDebugDialogOpen] = useState(false);
    const [selectedExecution, setSelectedExecution] =
      useState<WorkflowExecution | null>(null);

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
      <>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Workflow</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Started</TableCell>
                <TableCell>Completed</TableCell>
                <TableCell>Duration</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {executions.map((execution) => {
                const startTime = new Date(execution.started_at);
                const endTime = execution.completed_at
                  ? new Date(execution.completed_at)
                  : null;
                const duration = endTime
                  ? `${Math.round((endTime.getTime() - startTime.getTime()) / 1000)}s`
                  : '-';

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
                    <TableCell>{startTime.toLocaleString()}</TableCell>
                    <TableCell>
                      {endTime ? endTime.toLocaleString() : '-'}
                    </TableCell>
                    <TableCell>{duration}</TableCell>
                    <TableCell>
                      <IconButton
                        size="small"
                        onClick={() => {
                          setSelectedExecution(execution);
                          setDebugDialogOpen(true);
                        }}
                        title="View Debug Info"
                      >
                        <BugReport />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Debug Information Dialog */}
        <Dialog
          open={debugDialogOpen}
          onClose={() => setDebugDialogOpen(false)}
          maxWidth="lg"
          fullWidth
        >
          <DialogTitle>
            <Box display="flex" alignItems="center" gap={1}>
              <BugReport />
              <Typography variant="h6">Execution Debug Information</Typography>
              {selectedExecution && (
                <Chip
                  label={selectedExecution.status}
                  size="small"
                  color={getStatusColor(selectedExecution.status)}
                />
              )}
            </Box>
          </DialogTitle>
          <DialogContent dividers>
            {selectedExecution && (
              <Box>
                {/* Basic Information */}
                <Accordion defaultExpanded>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography variant="subtitle1">
                      Basic Information
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Box display="flex" flexDirection="column" gap={1}>
                      <Typography>
                        <strong>Execution ID:</strong> {selectedExecution.id}
                      </Typography>
                      <Typography>
                        <strong>Workflow:</strong>{' '}
                        {selectedExecution.workflow_name}
                      </Typography>
                      <Typography>
                        <strong>Status:</strong> {selectedExecution.status}
                      </Typography>
                      <Typography>
                        <strong>Duration:</strong>{' '}
                        {selectedExecution.execution_time_ms
                          ? `${selectedExecution.execution_time_ms}ms`
                          : 'N/A'}
                      </Typography>
                      {selectedExecution.error && (
                        <Alert severity="error">
                          <Typography>
                            <strong>Error:</strong> {selectedExecution.error}
                          </Typography>
                        </Alert>
                      )}
                    </Box>
                  </AccordionDetails>
                </Accordion>

                {/* Execution Logs */}
                {selectedExecution.execution_log &&
                  selectedExecution.execution_log.length > 0 && (
                    <Accordion>
                      <AccordionSummary expandIcon={<ExpandMore />}>
                        <Typography variant="subtitle1">
                          Execution Logs (
                          {selectedExecution.execution_log.length} entries)
                        </Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Box
                          display="flex"
                          flexDirection="column"
                          gap={1}
                          maxHeight={400}
                          overflow="auto"
                        >
                          {selectedExecution.execution_log.map(
                            (logEntry, index) => (
                              <Paper
                                key={index}
                                variant="outlined"
                                sx={{ p: 1 }}
                              >
                                <Typography
                                  variant="caption"
                                  color="text.secondary"
                                >
                                  {(logEntry as LogEntry).timestamp} -{' '}
                                  {(logEntry as LogEntry).level}
                                  {(logEntry as LogEntry).node_id &&
                                    ` - Node: ${(logEntry as LogEntry).node_id}`}
                                </Typography>
                                <Typography variant="body2">
                                  {(logEntry as LogEntry).message}
                                </Typography>
                                {(logEntry as LogEntry).data &&
                                  Object.keys((logEntry as LogEntry).data || {}).length > 0 && (
                                    <pre
                                      style={{
                                        fontSize: '0.75rem',
                                        margin: '4px 0',
                                        overflow: 'auto',
                                      }}
                                    >
                                      {JSON.stringify(
                                        (logEntry as LogEntry).data,
                                        null,
                                        2
                                      )}
                                    </pre>
                                  )}
                              </Paper>
                            )
                          )}
                        </Box>
                      </AccordionDetails>
                    </Accordion>
                  )}

                {/* Debug Info */}
                {selectedExecution.debug_info && (
                  <Accordion>
                    <AccordionSummary expandIcon={<ExpandMore />}>
                      <Typography variant="subtitle1">
                        Debug Information
                      </Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <pre
                        style={{
                          fontSize: '0.75rem',
                          overflow: 'auto',
                          maxHeight: 400,
                        }}
                      >
                        {JSON.stringify(selectedExecution.debug_info, null, 2)}
                      </pre>
                    </AccordionDetails>
                  </Accordion>
                )}

                {/* Input/Output Data */}
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography variant="subtitle1">
                      Input & Output Data
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Box display="flex" flexDirection="column" gap={2}>
                      <Box>
                        <Typography variant="subtitle2">Input:</Typography>
                        <pre
                          style={{
                            fontSize: '0.75rem',
                            overflow: 'auto',
                            maxHeight: 200,
                          }}
                        >
                          {JSON.stringify(selectedExecution.input, null, 2)}
                        </pre>
                      </Box>
                      {selectedExecution.output && (
                        <Box>
                          <Typography variant="subtitle2">Output:</Typography>
                          <pre
                            style={{
                              fontSize: '0.75rem',
                              overflow: 'auto',
                              maxHeight: 200,
                            }}
                          >
                            {JSON.stringify(selectedExecution.output, null, 2)}
                          </pre>
                        </Box>
                      )}
                    </Box>
                  </AccordionDetails>
                </Accordion>
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDebugDialogOpen(false)}>Close</Button>
          </DialogActions>
        </Dialog>
      </>
    );
  }
);

WorkflowExecutionsTab.displayName = 'WorkflowExecutionsTab';

export default WorkflowExecutionsTab;
