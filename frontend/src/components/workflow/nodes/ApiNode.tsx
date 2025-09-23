import React from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import { Card, CardContent, Typography, Box, Chip } from '@mui/material';
import { Api as ApiIcon } from '@mui/icons-material';
import { WorkflowNodeData } from '../types';

const ApiNode: React.FC<NodeProps> = ({ data, selected }) => {
  const nodeData = data as WorkflowNodeData;
  const config = nodeData.config || {};

  return (
    <>
      {/* Input handle */}
      <Handle
        type="target"
        position={Position.Left}
        style={{ background: '#00e676' }}
      />

      <Card
        sx={{
          minWidth: 180,
          border: selected ? 2 : 1,
          borderColor: selected ? 'primary.main' : 'divider',
          bgcolor: '#00e67620',
          color: '#00e676',
        }}
      >
        <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <ApiIcon sx={{ mr: 1, fontSize: 20 }} />
            <Typography variant="body1" fontWeight="bold">
              API Call
            </Typography>
          </Box>
          <Typography variant="body2" sx={{ mb: 1 }}>
            HTTP request
          </Typography>
          {config.method && (
            <Chip
              label={config.method}
              size="small"
              variant="outlined"
              sx={{ mr: 0.5, mb: 0.5, borderColor: '#00e676', color: '#00e676' }}
            />
          )}
          {config.url && (
            <Typography variant="caption" display="block" noWrap>
              {config.url}
            </Typography>
          )}
        </CardContent>
      </Card>

      {/* Output handle */}
      <Handle
        type="source"
        position={Position.Right}
        style={{ background: '#00e676' }}
      />
    </>
  );
};

export default ApiNode;