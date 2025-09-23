import React from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import { Card, CardContent, Typography, Box, Chip } from '@mui/material';
import { Loop as LoopIcon } from '@mui/icons-material';
import { WorkflowNodeData } from '../types';

const LoopNode: React.FC<NodeProps> = ({ data, selected }) => {
  const nodeData = data as WorkflowNodeData;
  const config = nodeData.config || {};

  return (
    <>
      {/* Input handle */}
      <Handle
        type="target"
        position={Position.Left}
        style={{ background: '#9c27b0' }}
      />

      <Card
        sx={{
          minWidth: 180,
          border: selected ? 2 : 1,
          borderColor: selected ? 'primary.main' : 'divider',
          bgcolor: '#ba68c8',
          color: 'white',
        }}
      >
        <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
          <>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <LoopIcon sx={{ mr: 1, fontSize: 20 }} />
              <Typography variant="body1" fontWeight="bold">
                Loop
              </Typography>
            </Box>
            <Typography variant="body2" sx={{ mb: 1 }}>
              Repeat execution
            </Typography>
            {config.maxIterations && (
              <Chip
                label={`Max: ${config.maxIterations}`}
                size="small"
                sx={{
                  bgcolor: 'rgba(255,255,255,0.2)',
                  color: 'white',
                  border: '1px solid rgba(255,255,255,0.3)',
                  mr: 0.5,
                }}
              />
            )}
            {config.condition && (
              <Chip
                label="Conditional"
                size="small"
                sx={{
                  bgcolor: 'rgba(255,255,255,0.2)',
                  color: 'white',
                  border: '1px solid rgba(255,255,255,0.3)',
                }}
              />
            )}
          </>
        </CardContent>
      </Card>

      {/* Output handles */}
      <Handle
        type="source"
        position={Position.Right}
        id="continue"
        style={{ background: '#9c27b0', top: '40%' }}
      />
      <Handle
        type="source"
        position={Position.Right}
        id="exit"
        style={{ background: '#e91e63', top: '60%' }}
      />
    </>
  );
};

export default LoopNode;
