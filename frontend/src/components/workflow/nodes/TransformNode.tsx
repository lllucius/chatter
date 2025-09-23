import React from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import { Card, CardContent, Typography, Box, Chip } from '@mui/material';
import { Transform as TransformIcon } from '@mui/icons-material';
import { WorkflowNodeData } from '../types';

const TransformNode: React.FC<NodeProps> = ({ data, selected }) => {
  const nodeData = data as WorkflowNodeData;
  const config = nodeData.config || {};

  return (
    <>
      {/* Input handle */}
      <Handle
        type="target"
        position={Position.Left}
        style={{ background: '#8bc34a' }}
      />

      <Card
        sx={{
          minWidth: 180,
          border: selected ? 2 : 1,
          borderColor: selected ? 'primary.main' : 'divider',
          bgcolor: '#8bc34a20',
          color: '#8bc34a',
        }}
      >
        <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <TransformIcon sx={{ mr: 1, fontSize: 20 }} />
            <Typography variant="body1" fontWeight="bold">
              Transform
            </Typography>
          </Box>
          <Typography variant="body2" sx={{ mb: 1 }}>
            Data transformation
          </Typography>
          {config.transformType && (
            <Chip
              label={config.transformType}
              size="small"
              variant="outlined"
              sx={{ mr: 0.5, mb: 0.5, borderColor: '#8bc34a', color: '#8bc34a' }}
            />
          )}
        </CardContent>
      </Card>

      {/* Output handle */}
      <Handle
        type="source"
        position={Position.Right}
        style={{ background: '#8bc34a' }}
      />
    </>
  );
};

export default TransformNode;