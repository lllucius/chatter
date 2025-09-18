import React from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import { Card, CardContent, Typography, Box, Chip } from '@mui/material';
import { Schedule as DelayIcon } from '@mui/icons-material';
import { WorkflowNodeData } from '../WorkflowEditor';

const DelayNode: React.FC<NodeProps> = ({
  data,
  selected,
}) => {
  const nodeData = data as WorkflowNodeData;
  const config = nodeData.config || {};

  const formatDelay = (seconds: number) => {
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
    return `${Math.floor(seconds / 3600)}h`;
  };

  return (
    <>
      {/* Input handle */}
      <Handle
        type="target"
        position={Position.Left}
        style={{ background: '#3f51b5' }}
      />

      <Card
        sx={{
          minWidth: 180,
          border: selected ? 2 : 1,
          borderColor: selected ? 'primary.main' : 'divider',
          bgcolor: '#5c6bc0',
          color: 'white',
        }}
      >
        <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
          <>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <DelayIcon sx={{ mr: 1, fontSize: 20 }} />
              <Typography variant="body1" fontWeight="bold">
                Delay
              </Typography>
            </Box>
            <Typography variant="body2" sx={{ mb: 1 }}>
              Wait before continuing
            </Typography>
            {config.duration && (
              <Chip
                label={formatDelay(Number(config.duration))}
                size="small"
                sx={{
                  bgcolor: 'rgba(255,255,255,0.2)',
                  color: 'white',
                  border: '1px solid rgba(255,255,255,0.3)',
                  mr: 0.5,
                }}
              />
            )}
            {config.type === 'dynamic' && (
            <Chip
              label="Dynamic"
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

      {/* Output handle */}
      <Handle
        type="source"
        position={Position.Right}
        style={{ background: '#3f51b5' }}
      />
    </>
  );
};

export default DelayNode;
