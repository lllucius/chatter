import React from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import { Card, CardContent, Typography, Box, Chip } from '@mui/material';
import { Error as ErrorIcon } from '@mui/icons-material';
import { WorkflowNodeData } from '../WorkflowEditor';

const ErrorHandlerNode: React.FC<NodeProps> = ({ data, selected }) => {
  const nodeData = data as WorkflowNodeData;
  const config = nodeData.config || {};

  return (
    <>
      {/* Input handle */}
      <Handle
        type="target"
        position={Position.Left}
        style={{ background: '#f44336' }}
      />

      <Card
        sx={{
          minWidth: 180,
          border: selected ? 2 : 1,
          borderColor: selected ? 'primary.main' : 'divider',
          bgcolor: '#ef5350',
          color: 'white',
        }}
      >
        <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
          <>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <ErrorIcon sx={{ mr: 1, fontSize: 20 }} />
              <Typography variant="body1" fontWeight="bold">
                Error Handler
              </Typography>
            </Box>
            <Typography variant="body2" sx={{ mb: 1 }}>
              Catch & handle errors
            </Typography>
            {config.retryCount && (
              <Chip
                label={`Retry: ${config.retryCount}`}
                size="small"
                sx={{
                  bgcolor: 'rgba(255,255,255,0.2)',
                  color: 'white',
                  border: '1px solid rgba(255,255,255,0.3)',
                  mr: 0.5,
                }}
              />
            )}
            {config.fallbackAction && (
              <Chip
                label={String(config.fallbackAction)}
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

      {/* Multiple output handles */}
      <Handle
        type="source"
        position={Position.Right}
        id="success"
        style={{ background: '#4caf50', top: '30%' }}
      />
      <Handle
        type="source"
        position={Position.Right}
        id="retry"
        style={{ background: '#ff9800', top: '50%' }}
      />
      <Handle
        type="source"
        position={Position.Right}
        id="fallback"
        style={{ background: '#f44336', top: '70%' }}
      />
    </>
  );
};

export default ErrorHandlerNode;
