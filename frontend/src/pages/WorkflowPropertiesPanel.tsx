import React from 'react';
import { Box, Typography, Divider } from '../utils/mui';
import EnhancedPropertiesPanel from '../components/workflow/EnhancedPropertiesPanel';
import WorkflowAnalytics from '../components/workflow/WorkflowAnalytics';
import { WorkflowDefinition } from '../components/workflow/types';

interface WorkflowPropertiesPanelProps {
  workflow?: WorkflowDefinition;
  selectedNodeId?: string;
  selectedEdgeId?: string;
  onNodeUpdate?: (nodeId: string, updates: any) => void;
  onEdgeUpdate?: (edgeId: string, updates: any) => void;
}

const WorkflowPropertiesPanel: React.FC<WorkflowPropertiesPanelProps> = ({
  workflow,
  selectedNodeId,
  selectedEdgeId,
  onNodeUpdate,
  onEdgeUpdate,
}) => {
  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Properties Section */}
      <Box sx={{ flex: 1, minHeight: 0 }}>
        <Typography variant="h6" sx={{ p: 2, pb: 1 }}>
          Properties
        </Typography>
        <Divider />
        <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
          <EnhancedPropertiesPanel
            selectedNode={
              selectedNodeId && workflow?.nodes
                ? workflow.nodes.find(n => n.id === selectedNodeId) || null
                : null
            }
            selectedEdge={
              selectedEdgeId && workflow?.edges
                ? workflow.edges.find(e => e.id === selectedEdgeId) || null
                : null
            }
            workflow={workflow}
            onNodeUpdate={(nodeId, updates) => {
              if (onNodeUpdate) {
                onNodeUpdate(nodeId, updates);
              }
            }}
            onEdgeUpdate={(edgeId, updates) => {
              if (onEdgeUpdate) {
                onEdgeUpdate(edgeId, updates);
              }
            }}
          />
        </Box>
      </Box>

      {/* Analytics Section */}
      <Divider />
      <Box sx={{ maxHeight: '40%', minHeight: 200, display: 'flex', flexDirection: 'column' }}>
        <Typography variant="h6" sx={{ p: 2, pb: 1 }}>
          Analytics
        </Typography>
        <Divider />
        <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
          {workflow && <WorkflowAnalytics workflow={workflow} />}
        </Box>
      </Box>
    </Box>
  );
};

export default WorkflowPropertiesPanel;