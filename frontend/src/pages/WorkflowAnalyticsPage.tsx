import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  Grid,
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
import { WorkflowDefinitionResponse, WorkflowAnalyticsResponse } from 'chatter-sdk';
import { handleError } from '../utils/error-handler';

const WorkflowAnalyticsPage: React.FC = () => {
  const [workflows, setWorkflows] = useState<WorkflowDefinitionResponse[]>([]);
  const [selectedWorkflowId, setSelectedWorkflowId] = useState<string>('');
  const [analytics, setAnalytics] = useState<WorkflowAnalyticsResponse | null>(null);
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
      const response = await sdk.workflows.listWorkflowDefinitionsApiV1WorkflowsDefinitions();
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
      const analyticsData = await sdk.workflows.getWorkflowAnalyticsApiV1WorkflowsDefinitionsWorkflowIdAnalytics(workflowId);
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
        <Alert severity="info">
          Select a workflow to view its analytics.
        </Alert>
      )}

      {selectedWorkflowId && loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {selectedWorkflowId && !loading && analytics && (
        <Box>
          <Grid container spacing={3}>
            {/* Complexity Score */}
            <Grid item xs={12} md={6} lg={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <AnalyticsIcon color="primary" sx={{ mr: 1 }} />
                    <Typography variant="h6" component="h2">
                      Complexity Score
                    </Typography>
                  </Box>
                  <Typography variant="h3" color="primary">
                    {analytics.complexityScore || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Lower is simpler
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            {/* Node Count */}
            <Grid item xs={12} md={6} lg={3}>
              <Card>
                <CardContent>
                  <Typography variant="h6" component="h2" gutterBottom>
                    Total Nodes
                  </Typography>
                  <Typography variant="h3" color="secondary">
                    {analytics.totalNodes || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Workflow components
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            {/* Execution Paths */}
            <Grid item xs={12} md={6} lg={3}>
              <Card>
                <CardContent>
                  <Typography variant="h6" component="h2" gutterBottom>
                    Execution Paths
                  </Typography>
                  <Typography variant="h3" color="info.main">
                    {analytics.executionPaths?.length || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Possible routes
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            {/* Bottlenecks */}
            <Grid item xs={12} md={6} lg={3}>
              <Card>
                <CardContent>
                  <Typography variant="h6" component="h2" gutterBottom>
                    Bottlenecks
                  </Typography>
                  <Typography variant="h3" color="warning.main">
                    {analytics.potentialBottlenecks?.length || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Performance issues
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            {/* Node Type Distribution */}
            {analytics.nodeTypeDistribution && (
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" component="h2" gutterBottom>
                      Node Type Distribution
                    </Typography>
                    <Box sx={{ mt: 2 }}>
                      {Object.entries(analytics.nodeTypeDistribution).map(([type, count]) => (
                        <Box key={type} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                          <Typography variant="body2">{type}</Typography>
                          <Typography variant="body2" fontWeight="medium">{count}</Typography>
                        </Box>
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            )}

            {/* Recommendations */}
            {analytics.optimizationSuggestions && analytics.optimizationSuggestions.length > 0 && (
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" component="h2" gutterBottom>
                      Optimization Suggestions
                    </Typography>
                    <Box sx={{ mt: 2 }}>
                      {analytics.optimizationSuggestions.map((suggestion, index) => (
                        <Alert key={index} severity="info" sx={{ mb: 1 }}>
                          <Typography variant="body2">
                            <strong>{suggestion.type}:</strong> {suggestion.message}
                          </Typography>
                        </Alert>
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            )}

            {/* Bottleneck Details */}
            {analytics.potentialBottlenecks && analytics.potentialBottlenecks.length > 0 && (
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" component="h2" gutterBottom>
                      Potential Bottlenecks
                    </Typography>
                    <Box sx={{ mt: 2 }}>
                      {analytics.potentialBottlenecks.map((bottleneck, index) => (
                        <Alert key={index} severity="warning" sx={{ mb: 1 }}>
                          <Typography variant="body2">
                            <strong>Node {bottleneck.nodeId}:</strong> {bottleneck.reason}
                            {bottleneck.impactScore && (
                              <> (Impact Score: {bottleneck.impactScore})</>
                            )}
                          </Typography>
                        </Alert>
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            )}
          </Grid>
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