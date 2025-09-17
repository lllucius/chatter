import React from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import { Card, CardContent, Typography, Box, Chip } from '@mui/material';
import { Build as ToolIcon } from '@mui/icons-material';
import { WorkflowNodeData } from '../WorkflowEditor';

const ToolNode: React.FC<NodeProps<WorkflowNodeData>> = ({
  data,
  selected,
}) => {
  const config = data.config || {};

  return (
    <>
      {/* Input handle */}
      <Handle
        type="target"
        position={Position.Left}
        style={{ background: '#ff9800' }}
      />

      <Card
        sx={{
          minWidth: 180,
          border: selected ? 2 : 1,
          borderColor: selected ? 'primary.main' : 'divider',
          bgcolor: 'warning.light',
          color: 'warning.contrastText',
        }}
      >
        <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <ToolIcon sx={{ mr: 1, fontSize: 20 }} />
            <Typography variant="body1" fontWeight="bold">
              Tool Execution
            </Typography>
          </Box>
          <Typography variant="body2" sx={{ mb: 1 }}>
            Execute tools
          </Typography>
          {config.parallel && (
            <Chip
              label="Parallel"
              size="small"
              color="warning"
              variant="outlined"
              sx={{ mr: 0.5 }}
            />
          )}
          {config.tools && config.tools.length > 0 && (
            <Chip
              label={`${config.tools.length} tools`}
              size="small"
              color="warning"
              variant="outlined"
            />
          )}
        </CardContent>
      </Card>

      {/* Output handle */}
      <Handle
        type="source"
        position={Position.Right}
        style={{ background: '#ff9800' }}
      />
    </>
  );
};

export default ToolNode;
