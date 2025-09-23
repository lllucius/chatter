import React from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import { Card, CardContent, Typography, Box, Chip } from '@mui/material';
import { Memory as MemoryIcon } from '@mui/icons-material';
import { WorkflowNodeData } from '../types';

const MemoryNode: React.FC<NodeProps> = ({ data, selected }) => {
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
          bgcolor: 'secondary.light',
          color: 'secondary.contrastText',
        }}
      >
        <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
          <>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <MemoryIcon sx={{ mr: 1, fontSize: 20 }} />
              <Typography variant="body1" fontWeight="bold">
                Memory
              </Typography>
            </Box>
            <Typography variant="body2" sx={{ mb: 1 }}>
              Manage context
            </Typography>
            {config.window && (
              <Chip
                label={`Window: ${config.window}`}
                size="small"
                color="secondary"
                variant="outlined"
                sx={{ mr: 0.5 }}
              />
            )}
            <Chip
              label={config.enabled ? 'Enabled' : 'Disabled'}
              size="small"
              color={config.enabled ? 'success' : 'error'}
              variant="outlined"
            />
          </>
        </CardContent>
      </Card>

      {/* Output handle */}
      <Handle
        type="source"
        position={Position.Right}
        style={{ background: '#9c27b0' }}
      />
    </>
  );
};

export default MemoryNode;
