import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  CircularProgress,
} from '../utils/mui';
import { RefreshIcon, AnalyticsIcon } from '../utils/icons';
import PageLayout from '../components/PageLayout';
import { getSDK } from '../services/auth-service';
import {
  WorkflowDefinitionResponse,
  WorkflowAnalyticsResponse,
} from 'chatter-sdk';

const WorkflowAnalyticsPage: React.FC = () => {
  const [workflows, setWorkflows] = useState<WorkflowDefinitionResponse[]>([]);
  const [selectedWorkflowId, setSelectedWorkflowId] = useState<string>('');
  const [analytics, setAnalytics] = useState<WorkflowAnalyticsResponse | null>(
    null
  );
  const [loading, setLoading] = useState(false);
  const [workflowsLoading, setWorkflowsLoading] = useState(true);

  // Load available workflows
  useEffect(() => {
    loadWorkflows();
  }, []);

  // Load analytics when workflow is selected
  useEffect(() => {
    if (selectedWorkflowId) {
      loadAnalytics(selectedWorkflowId);
    }
  }, [selectedWorkflowId]);

  const loadWorkflows = async () => {
    try {
      setWorkflowsLoading(true);
      const sdk = await getSDK();
      const response =
        await sdk.workflows.listWorkflowDefinitionsApiV1WorkflowsDefinitions();
      setWorkflows(response.definitions || []);

      // Auto-select first workflow if available
      if (response.definitions && response.definitions.length > 0) {
        setSelectedWorkflowId(response.definitions[0].id);
      }
    } catch (error) {
      console.error('Failed to load workflows:', error);
    } finally {
      setWorkflowsLoading(false);
    }
  };

  const loadAnalytics = async (workflowId: string) => {
    try {
      setLoading(true);
      const sdk = await getSDK();
      const analyticsData =
        await sdk.workflows.getWorkflowAnalyticsApiV1WorkflowsDefinitionsWorkflowIdAnalytics(
          workflowId
        );
      setAnalytics(analyticsData);
    } catch (error) {
      console.error('Failed to load analytics:', error);
      setAnalytics(null);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    loadWorkflows();
    if (selectedWorkflowId) {
      loadAnalytics(selectedWorkflowId);
    }
  };

  // Toolbar content
  const toolbar = (
    <>
      <Button
        variant="outlined"
        startIcon={<RefreshIcon />}
        onClick={handleRefresh}
        disabled={loading}
      >
        Refresh
      </Button>
    </>
  );

  return (
    <PageLayout title="Workflow Analytics" toolbar={toolbar}>
      <Box sx={{ mb: 3 }}>
        <FormControl fullWidth variant="outlined" sx={{ maxWidth: 400 }}>
          <InputLabel>Select Workflow</InputLabel>
          <Select
            value={selectedWorkflowId}
            onChange={(e) => setSelectedWorkflowId(e.target.value)}
            label="Select Workflow"
            disabled={workflowsLoading}
          >
            {workflows.map((workflow) => (
              <MenuItem key={workflow.id} value={workflow.id}>
                {workflow.name || `Workflow ${workflow.id.substring(0, 8)}`}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      {workflowsLoading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {!workflowsLoading && workflows.length === 0 && (
        <Alert severity="info">
          No workflows found. Create a workflow to view analytics.
        </Alert>
      )}

      {!workflowsLoading && workflows.length > 0 && !selectedWorkflowId && (
        <Alert severity="info">Select a workflow to view its analytics.</Alert>
      )}

      {selectedWorkflowId && loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {selectedWorkflowId && !loading && analytics && (
        <Box>
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
              gap: 3,
              mb: 3,
            }}
          >
            {/* Complexity Score */}
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <AnalyticsIcon color="primary" sx={{ mr: 1 }} />
                  <Typography variant="h6" component="h2">
                    Complexity Score
                  </Typography>
                </Box>
                <Typography variant="h3" color="primary">
                  {analytics.complexity?.score || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Lower is simpler
                </Typography>
              </CardContent>
            </Card>

            {/* Node Count */}
            <Card>
              <CardContent>
                <Typography variant="h6" component="h2" gutterBottom>
                  Total Nodes
                </Typography>
                <Typography variant="h3" color="secondary">
                  {analytics.complexity?.node_count || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Workflow components
                </Typography>
              </CardContent>
            </Card>

            {/* Execution Paths */}
            <Card>
              <CardContent>
                <Typography variant="h6" component="h2" gutterBottom>
                  Execution Paths
                </Typography>
                <Typography variant="h3" color="info.main">
                  {analytics.execution_paths || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Possible routes
                </Typography>
              </CardContent>
            </Card>

            {/* Bottlenecks */}
            <Card>
              <CardContent>
                <Typography variant="h6" component="h2" gutterBottom>
                  Bottlenecks
                </Typography>
                <Typography variant="h3" color="warning.main">
                  {analytics.bottlenecks?.length || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Performance issues
                </Typography>
              </CardContent>
            </Card>
          </Box>

          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
              gap: 3,
            }}
          >
            {/* Optimization Suggestions */}
            {analytics.optimization_suggestions &&
              analytics.optimization_suggestions.length > 0 && (
                <Card>
                  <CardContent>
                    <Typography variant="h6" component="h2" gutterBottom>
                      Optimization Suggestions
                    </Typography>
                    <Box sx={{ mt: 2 }}>
                      {analytics.optimization_suggestions.map(
                        (suggestion, index) => (
                          <Alert key={index} severity="info" sx={{ mb: 1 }}>
                            <Typography variant="body2">
                              <strong>{suggestion.type}:</strong>{' '}
                              {suggestion.description}
                            </Typography>
                          </Alert>
                        )
                      )}
                    </Box>
                  </CardContent>
                </Card>
              )}

            {/* Bottleneck Details */}
            {analytics.bottlenecks && analytics.bottlenecks.length > 0 && (
              <Card>
                <CardContent>
                  <Typography variant="h6" component="h2" gutterBottom>
                    Potential Bottlenecks
                  </Typography>
                  <Box sx={{ mt: 2 }}>
                    {analytics.bottlenecks.map((bottleneck, index) => (
                      <Alert key={index} severity="warning" sx={{ mb: 1 }}>
                        <Typography variant="body2">
                          <strong>Node {bottleneck.node_id}:</strong>{' '}
                          {bottleneck.reason}
                          {bottleneck.severity && (
                            <> (Severity: {bottleneck.severity})</>
                          )}
                        </Typography>
                      </Alert>
                    ))}
                  </Box>
                </CardContent>
              </Card>
            )}
          </Box>
        </Box>
      )}

      {selectedWorkflowId && !loading && !analytics && (
        <Alert severity="error">
          Failed to load analytics for the selected workflow.
        </Alert>
      )}
    </PageLayout>
  );
};

export default WorkflowAnalyticsPage;
