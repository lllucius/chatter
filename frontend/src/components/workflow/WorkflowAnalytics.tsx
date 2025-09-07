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
import { WorkflowDefinition, WorkflowNodeType } from './WorkflowEditor';

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
  const calculateMetrics = (): WorkflowMetrics => {
    const { nodes, edges } = workflow;
    
    // Node type distribution
    const nodeTypeDistribution = nodes.reduce((acc, node) => {
      const nodeType = node.data.nodeType;
      acc[nodeType] = (acc[nodeType] || 0) + 1;
      return acc;
    }, {} as Record<WorkflowNodeType, number>);

    // Complexity calculation
    let complexityScore = 0;
    complexityScore += nodes.length * 2; // Base complexity per node
    complexityScore += edges.length * 1; // Edge complexity
    
    // Add complexity for specific node types
    nodes.forEach(node => {
      switch (node.data.nodeType) {
        case 'conditional':
          complexityScore += 5;
          break;
        case 'loop':
          complexityScore += 8;
          break;
        case 'errorHandler':
          complexityScore += 3;
          break;
        case 'tool': {
          const toolCount = node.data.config?.tools?.length || 1;
          complexityScore += toolCount * 2;
          break;
        }
      }
    });

    // Find execution paths (simplified)
    const executionPaths: string[][] = [];
    const startNodes = nodes.filter(node => node.data.nodeType === 'start');
    
    startNodes.forEach(startNode => {
      const path = [startNode.id];
      const visited = new Set([startNode.id]);
      findPaths(startNode.id, path, visited, executionPaths, edges, nodes);
    });

    // Identify potential bottlenecks
    const potentialBottlenecks: string[] = [];
    
    // High-degree nodes (many connections)
    const nodeDegrees = new Map<string, number>();
    edges.forEach(edge => {
      nodeDegrees.set(edge.source, (nodeDegrees.get(edge.source) || 0) + 1);
      nodeDegrees.set(edge.target, (nodeDegrees.get(edge.target) || 0) + 1);
    });
    
    nodeDegrees.forEach((degree, nodeId) => {
      if (degree > 4) {
        const node = nodes.find(n => n.id === nodeId);
        if (node) {
          potentialBottlenecks.push(`High-degree node: ${node.data.label}`);
        }
      }
    });

    // Sequential tool nodes (could be parallelized)
    for (let i = 0; i < nodes.length - 1; i++) {
      const current = nodes[i];
      const next = nodes[i + 1];
      if (current.data.nodeType === 'tool' && next.data.nodeType === 'tool') {
        const hasDirectConnection = edges.some(edge => 
          edge.source === current.id && edge.target === next.id
        );
        if (hasDirectConnection) {
          potentialBottlenecks.push(`Sequential tools: ${current.data.label} → ${next.data.label}`);
        }
      }
    }

    // Generate recommendations
    const recommendations: string[] = [];
    
    if (nodeTypeDistribution.errorHandler === 0) {
      recommendations.push('Consider adding error handling nodes for better reliability');
    }
    
    if (nodeTypeDistribution.memory === 0 && nodeTypeDistribution.model > 0) {
      recommendations.push('Add memory nodes to maintain context across model calls');
    }
    
    if (complexityScore > 50) {
      recommendations.push('Workflow complexity is high - consider breaking into smaller sub-workflows');
    }
    
    if (nodeTypeDistribution.tool > 3) {
      recommendations.push('Consider grouping tools or using parallel execution');
    }

    const toolNodes = nodes.filter(n => n.data.nodeType === 'tool');
    const parallelTools = toolNodes.filter(n => n.data.config?.parallel);
    if (toolNodes.length > parallelTools.length) {
      recommendations.push('Some tool nodes could benefit from parallel execution');
    }

    return {
      totalNodes: nodes.length,
      nodeTypeDistribution,
      complexityScore,
      executionPaths,
      potentialBottlenecks,
      recommendations,
    };
  };

  const findPaths = (
    currentNodeId: string,
    currentPath: string[],
    visited: Set<string>,
    allPaths: string[][],
    edges: any[],
    nodes: any[]
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

  const metrics = calculateMetrics();

  return (
    <Paper sx={{ p: 2, height: '100%', overflow: 'auto' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <AnalyticsIcon sx={{ mr: 1 }} />
        <Typography variant="h6">Workflow Analytics</Typography>
      </Box>

      {/* Overview */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle1" sx={{ mb: 1, fontWeight: 'bold' }}>
          Overview
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
          <Chip label={`${metrics.totalNodes} Nodes`} color="primary" />
          <Chip label={`${workflow.edges.length} Connections`} color="primary" />
          <Chip 
            label={`${getComplexityLabel(metrics.complexityScore)} Complexity`} 
            color={getComplexityColor(metrics.complexityScore)}
          />
        </Box>
        
        <Typography variant="body2" sx={{ mb: 1 }}>Complexity Score</Typography>
        <LinearProgress 
          variant="determinate" 
          value={Math.min(metrics.complexityScore, 100)} 
          color={getComplexityColor(metrics.complexityScore)}
          sx={{ mb: 1 }}
        />
        <Typography variant="caption" color="textSecondary">
          {metrics.complexityScore}/100
        </Typography>
      </Box>

      <Divider sx={{ mb: 2 }} />

      {/* Node Distribution */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle1" sx={{ mb: 1, fontWeight: 'bold' }}>
          Node Distribution
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {Object.entries(metrics.nodeTypeDistribution).map(([type, count]) => (
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
            Execution Paths ({metrics.executionPaths.length})
          </Typography>
        </Box>
        {metrics.executionPaths.slice(0, 3).map((path, index) => (
          <Typography key={index} variant="body2" sx={{ mb: 0.5 }}>
            Path {index + 1}: {path.length} nodes
          </Typography>
        ))}
        {metrics.executionPaths.length > 3 && (
          <Typography variant="body2" color="textSecondary">
            +{metrics.executionPaths.length - 3} more paths...
          </Typography>
        )}
      </Box>

      <Divider sx={{ mb: 2 }} />

      {/* Bottlenecks */}
      {metrics.potentialBottlenecks.length > 0 && (
        <>
          <Box sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <WarningIcon sx={{ mr: 1, fontSize: 20, color: 'warning.main' }} />
              <Typography variant="subtitle1" fontWeight="bold">
                Potential Bottlenecks
              </Typography>
            </Box>
            <List dense>
              {metrics.potentialBottlenecks.map((bottleneck, index) => (
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
            Recommendations
          </Typography>
        </Box>
        {metrics.recommendations.length > 0 ? (
          <List dense>
            {metrics.recommendations.map((recommendation, index) => (
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
        ) : (
          <Alert severity="success">
            <Typography variant="body2">
              Your workflow looks well-optimized! No specific recommendations at this time.
            </Typography>
          </Alert>
        )}
      </Box>
    </Paper>
  );
};

export default WorkflowAnalytics;