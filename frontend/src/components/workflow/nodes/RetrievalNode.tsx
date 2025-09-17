import React from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import { Card, CardContent, Typography, Box, Chip } from '@mui/material';
import { Search as RetrievalIcon } from '@mui/icons-material';
import { WorkflowNodeData } from '../WorkflowEditor';

const RetrievalNode: React.FC<NodeProps<WorkflowNodeData>> = ({
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
        style={{ background: '#607d8b' }}
      />

      <Card
        sx={{
          minWidth: 180,
          border: selected ? 2 : 1,
          borderColor: selected ? 'primary.main' : 'divider',
          bgcolor: 'info.light',
          color: 'info.contrastText',
        }}
      >
        <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <RetrievalIcon sx={{ mr: 1, fontSize: 20 }} />
            <Typography variant="body1" fontWeight="bold">
              Retrieval
            </Typography>
          </Box>
          <Typography variant="body2" sx={{ mb: 1 }}>
            Fetch context
          </Typography>
          {config.topK && (
            <Chip
              label={`Top K: ${config.topK}`}
              size="small"
              color="info"
              variant="outlined"
              sx={{ mr: 0.5 }}
            />
          )}
          {config.collection && (
            <Chip
              label={config.collection}
              size="small"
              color="info"
              variant="outlined"
            />
          )}
        </CardContent>
      </Card>

      {/* Output handle */}
      <Handle
        type="source"
        position={Position.Right}
        style={{ background: '#607d8b' }}
      />
    </>
  );
};

export default RetrievalNode;
