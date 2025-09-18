import React from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import { Card, CardContent, Typography, Box, Chip } from '@mui/material';
import { SmartToy as ModelIcon } from '@mui/icons-material';
import { WorkflowNodeData } from '../WorkflowEditor';

const ModelNode: React.FC<NodeProps> = ({
  data,
  selected,
}) => {
  const nodeData = data as WorkflowNodeData;
  const config = nodeData.config || {};

  return (
    <>
      {/* Input handle */}
      <Handle
        type="target"
        position={Position.Left}
        style={{ background: '#2196f3' }}
      />

      <Card
        sx={{
          minWidth: 180,
          border: selected ? 2 : 1,
          borderColor: selected ? 'primary.main' : 'divider',
          bgcolor: 'primary.light',
          color: 'primary.contrastText',
        }}
      >
        <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <ModelIcon sx={{ mr: 1, fontSize: 20 }} />
            <Typography variant="body1" fontWeight="bold">
              Model Call
            </Typography>
          </Box>
          <Typography variant="body2" sx={{ mb: 1 }}>
            LLM interaction
          </Typography>
          {config.temperature !== undefined && (
            <Chip
              label={`T: ${config.temperature}`}
              size="small"
              color="primary"
              variant="outlined"
              sx={{ mr: 0.5, mb: 0.5 }}
            />
          )}
          {config.maxTokens && (
            <Chip
              label={`Max: ${config.maxTokens}`}
              size="small"
              color="primary"
              variant="outlined"
            />
          )}
        </CardContent>
      </Card>

      {/* Output handle */}
      <Handle
        type="source"
        position={Position.Right}
        style={{ background: '#2196f3' }}
      />
    </>
  );
};

export default ModelNode;
