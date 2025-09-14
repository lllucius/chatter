import React from 'react';
import {
  Paper,
  Typography,
  Box,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Alert,
  LinearProgress,
} from '@mui/material';
import {
  Assessment as AnalyticsIcon,
  Timeline as PathIcon,
  Warning as WarningIcon,
  CheckCircle as CheckIcon,
} from '@mui/icons-material';
import { WorkflowDefinition, WorkflowNodeType, WorkflowNode } from './WorkflowEditor';
import { getSDK } from '../../services/auth-service';

interface WorkflowAnalyticsProps {
  workflow: WorkflowDefinition;
}

interface WorkflowMetrics {
  totalNodes: number;
  nodeTypeDistribution: Record<WorkflowNodeType, number>;
  complexityScore: number;
  executionPaths: string[][];
  potentialBottlenecks: string[];
  recommendations: string[];
}

const WorkflowAnalytics: React.FC<WorkflowAnalyticsProps> = ({ workflow }) => {
  const [analytics, setAnalytics] = React.useState<WorkflowMetrics | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    const fetchAnalytics = async () => {
      // Only fetch analytics if we have a workflow with an ID
      if (!workflow.id || !workflow.nodes.length) {
        // Fallback to simple client-side calculation for workflows without ID
        setAnalytics(calculateSimpleMetrics());
        return;
      }

      setLoading(true);
      setError(null);
      
      try {
        // Use the new server-side analytics API
        const response = await getSDK().workflows.getWorkflowAnalyticsApiV1WorkflowsDefinitionsWorkflowIdAnalytics(
          workflow.id
        );
        
        // Transform server response to client format
        const serverAnalytics = response.data;
        const clientMetrics: WorkflowMetrics = {
          totalNodes: serverAnalytics.complexity.node_count,
          nodeTypeDistribution: calculateNodeTypeDistribution(workflow.nodes),
          complexityScore: serverAnalytics.complexity.score,
          executionPaths: [], // Server returns count, not paths
          potentialBottlenecks: serverAnalytics.bottlenecks.map(b => b.reason),
          recommendations: serverAnalytics.optimization_suggestions.map(s => s.description),
        };
        
        setAnalytics(clientMetrics);
      } catch {
        // Failed to fetch workflow analytics - using fallback
        setError('Failed to load analytics. Using fallback calculations.');
        // Fallback to client-side calculation
        setAnalytics(calculateSimpleMetrics());
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [workflow.id, workflow.nodes, workflow.edges, calculateSimpleMetrics]);

  const calculateNodeTypeDistribution = (nodes: WorkflowNode[]): Record<WorkflowNodeType, number> => {
    return nodes.reduce((acc, node) => {
      const nodeType = node.data.nodeType;
      acc[nodeType] = (acc[nodeType] || 0) + 1;
      return acc;
    }, {} as Record<WorkflowNodeType, number>);
  };

  const calculateSimpleMetrics = (): WorkflowMetrics => {
    const { nodes, edges } = workflow;
    
    // Simple fallback calculation for workflows without server-side analytics
    const nodeTypeDistribution = calculateNodeTypeDistribution(nodes);
    
    let complexityScore = nodes.length + edges.length;
    
    const potentialBottlenecks: string[] = [];
    const recommendations: string[] = [];
    
    if (nodeTypeDistribution.errorHandler === 0 && nodes.length > 5) {
      recommendations.push('Consider adding error handling nodes for better reliability');
    }
    
    if (complexityScore > 20) {
      recommendations.push('Workflow complexity is moderate - consider optimizing');
    }

    return {
      totalNodes: nodes.length,
      nodeTypeDistribution,
      complexityScore,
      executionPaths: [],
      potentialBottlenecks,
      recommendations,
    };
  };

  if (loading) {
    return (
      <div className="workflow-analytics">
        <h3>Workflow Analytics</h3>
        <div className="loading">Loading analytics...</div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="workflow-analytics">
        <h3>Workflow Analytics</h3>
        <div className="error">Unable to load analytics</div>
      </div>
    );
  }

  // Use the analytics data (either from server or fallback)

  const findPaths = (
    currentNodeId: string,
    currentPath: string[],
    visited: Set<string>,
    allPaths: string[][],
    edges: Array<{ source: string; target: string }>,
    nodes: Array<{ id: string }>
  ) => {
    const outgoingEdges = edges.filter(edge => edge.source === currentNodeId);
    
    if (outgoingEdges.length === 0) {
      // End of path
      allPaths.push([...currentPath]);
      return;
    }
    
    outgoingEdges.forEach(edge => {
      if (!visited.has(edge.target)) {
        const newVisited = new Set(visited);
        newVisited.add(edge.target);
        const newPath = [...currentPath, edge.target];
        findPaths(edge.target, newPath, newVisited, allPaths, edges, nodes);
      }
    });
  };

  const getComplexityColor = (score: number): 'success' | 'warning' | 'error' => {
    if (score < 20) return 'success';
    if (score < 50) return 'warning';
    return 'error';
  };

  const getComplexityLabel = (score: number): string => {
    if (score < 20) return 'Low';
    if (score < 50) return 'Medium';
    return 'High';
  };

  // Use the analytics data (either from server or fallback)
  if (loading) {
    return (
      <Paper sx={{ p: 2, height: '100%', overflow: 'auto' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <AnalyticsIcon sx={{ mr: 1 }} />
          <Typography variant="h6">Workflow Analytics</Typography>
        </Box>
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <LinearProgress sx={{ width: '100%' }} />
        </Box>
      </Paper>
    );
  }

  if (!analytics) {
    return (
      <Paper sx={{ p: 2, height: '100%', overflow: 'auto' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <AnalyticsIcon sx={{ mr: 1 }} />
          <Typography variant="h6">Workflow Analytics</Typography>
        </Box>
        <Alert severity="error">Unable to load analytics</Alert>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 2, height: '100%', overflow: 'auto' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <AnalyticsIcon sx={{ mr: 1 }} />
        <Typography variant="h6">Workflow Analytics</Typography>
        {error && (
          <Alert severity="warning" sx={{ ml: 2, flex: 1 }}>
            {error}
          </Alert>
        )}
      </Box>

      {/* Overview */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle1" sx={{ mb: 1, fontWeight: 'bold' }}>
          Overview
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
          <Chip label={`${analytics.totalNodes} Nodes`} color="primary" />
          <Chip label={`${workflow.edges.length} Connections`} color="primary" />
          <Chip 
            label={`${getComplexityLabel(analytics.complexityScore)} Complexity`} 
            color={getComplexityColor(analytics.complexityScore)}
          />
        </Box>
        
        <Typography variant="body2" sx={{ mb: 1 }}>Complexity Score</Typography>
        <LinearProgress 
          variant="determinate" 
          value={Math.min(analytics.complexityScore, 100)} 
          color={getComplexityColor(analytics.complexityScore)}
          sx={{ mb: 1 }}
        />
        <Typography variant="caption" color="textSecondary">
          {analytics.complexityScore}/100
        </Typography>
      </Box>

      <Divider sx={{ mb: 2 }} />

      {/* Node Distribution */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle1" sx={{ mb: 1, fontWeight: 'bold' }}>
          Node Distribution
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {Object.entries(analytics.nodeTypeDistribution).map(([type, count]) => (
            <Chip
              key={type}
              label={`${type}: ${count}`}
              size="small"
              variant="outlined"
            />
          ))}
        </Box>
      </Box>

      <Divider sx={{ mb: 2 }} />

      {/* Execution Paths */}
      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <PathIcon sx={{ mr: 1, fontSize: 20 }} />
          <Typography variant="subtitle1" fontWeight="bold">
            Execution Paths ({analytics.executionPaths.length})
          </Typography>
        </Box>
        {analytics.executionPaths.slice(0, 3).map((path, index) => (
          <Typography key={index} variant="body2" sx={{ mb: 0.5 }}>
            Path {index + 1}: {path.length} nodes
          </Typography>
        ))}
        {analytics.executionPaths.length > 3 && (
          <Typography variant="body2" color="textSecondary">
            +{analytics.executionPaths.length - 3} more paths...
          </Typography>
        )}
        {analytics.executionPaths.length === 0 && (
          <Typography variant="body2" color="textSecondary">
            No execution paths analyzed
          </Typography>
        )}
      </Box>

      <Divider sx={{ mb: 2 }} />

      {/* Bottlenecks */}
      {analytics.potentialBottlenecks.length > 0 && (
        <>
          <Box sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <WarningIcon sx={{ mr: 1, fontSize: 20, color: 'warning.main' }} />
              <Typography variant="subtitle1" fontWeight="bold">
                Potential Bottlenecks
              </Typography>
            </Box>
            <List dense>
              {analytics.potentialBottlenecks.map((bottleneck, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    <WarningIcon fontSize="small" color="warning" />
                  </ListItemIcon>
                  <ListItemText 
                    primary={bottleneck}
                    primaryTypographyProps={{ variant: 'body2' }}
                  />
                </ListItem>
              ))}
            </List>
          </Box>
          <Divider sx={{ mb: 2 }} />
        </>
      )}

      {/* Recommendations */}
      <Box sx={{ mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <CheckIcon sx={{ mr: 1, fontSize: 20, color: 'success.main' }} />
          <Typography variant="subtitle1" fontWeight="bold">
            Optimization Recommendations
          </Typography>
        </Box>
        <List dense>
          {analytics.recommendations.map((recommendation, index) => (
            <ListItem key={index}>
              <ListItemIcon>
                <CheckIcon fontSize="small" color="success" />
              </ListItemIcon>
              <ListItemText 
                primary={recommendation}
                primaryTypographyProps={{ variant: 'body2' }}
              />
            </ListItem>
          ))}
        </List>
        {analytics.recommendations.length === 0 && (
          <Typography variant="body2" color="textSecondary">
            No specific recommendations available
          </Typography>
        )}
      </Box>
    </Paper>
  );
};

export default WorkflowAnalytics;