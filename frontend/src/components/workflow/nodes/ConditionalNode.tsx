import React from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import { Card, CardContent, Typography, Box, Chip } from '@mui/material';
import { CallSplit as ConditionalIcon } from '@mui/icons-material';
import { WorkflowNodeData } from '../WorkflowEditor';

const ConditionalNode: React.FC<NodeProps> = ({
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
        style={{ background: '#795548' }}
      />

      <Card
        sx={{
          minWidth: 200,
          border: selected ? 2 : 1,
          borderColor: selected ? 'primary.main' : 'divider',
          bgcolor: '#8d6e63',
          color: 'white',
        }}
      >
        <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <ConditionalIcon sx={{ mr: 1, fontSize: 20 }} />
            <Typography variant="body1" fontWeight="bold">
              Conditional
            </Typography>
          </Box>
          <Typography variant="body2" sx={{ mb: 1 }}>
            Decision point
          </Typography>
          {String(config.condition) && (
            <Chip
              label={
                String(config.condition).slice(0, 20) +
                (String(config.condition).length > 20 ? '...' : '')
              }
              size="small"
              sx={{
                bgcolor: 'rgba(255,255,255,0.2)',
                color: 'white',
                border: '1px solid rgba(255,255,255,0.3)',
              }}
            />
          )}
        </CardContent>
      </Card>

      {/* Multiple output handles for different branches */}
      <Handle
        type="source"
        position={Position.Right}
        id="true"
        style={{ background: '#4caf50', top: '40%' }}
      />
      <Handle
        type="source"
        position={Position.Right}
        id="false"
        style={{ background: '#f44336', top: '60%' }}
      />
    </>
  );
};

export default ConditionalNode;
