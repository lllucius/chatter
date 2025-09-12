import React from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import { Card, CardContent, Typography, Box, Chip } from '@mui/material';
import { PlayArrow as StartIcon } from '@mui/icons-material';
import { WorkflowNodeData } from '../WorkflowEditor';

const StartNode: React.FC<NodeProps<WorkflowNodeData>> = ({ data: _data, selected }) => {
  return (
    <>
      <Card 
        sx={{ 
          minWidth: 150, 
          border: selected ? 2 : 1, 
          borderColor: selected ? 'primary.main' : 'divider',
          bgcolor: 'success.light',
          color: 'success.contrastText'
        }}
      >
        <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <StartIcon sx={{ mr: 1, fontSize: 20 }} />
            <Typography variant="body1" fontWeight="bold">
              Start
            </Typography>
          </Box>
          <Typography variant="body2" sx={{ mb: 1 }}>
            Entry point
          </Typography>
          <Chip 
            label="Entry" 
            size="small" 
            color="success" 
            variant="outlined"
          />
        </CardContent>
      </Card>
      
      {/* Output handle */}
      <Handle 
        type="source" 
        position={Position.Right} 
        style={{ background: '#4caf50' }}
      />
    </>
  );
};

export default StartNode;