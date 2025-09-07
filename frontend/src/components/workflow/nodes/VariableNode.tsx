import React from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import { Card, CardContent, Typography, Box, Chip } from '@mui/material';
import { Storage as VariableIcon } from '@mui/icons-material';
import { WorkflowNodeData } from '../WorkflowEditor';

const VariableNode: React.FC<NodeProps<WorkflowNodeData>> = ({ data, selected }) => {
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
          bgcolor: '#78909c',
          color: 'white'
        }}
      >
        <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <VariableIcon sx={{ mr: 1, fontSize: 20 }} />
            <Typography variant="body1" fontWeight="bold">
              Variable
            </Typography>
          </Box>
          <Typography variant="body2" sx={{ mb: 1 }}>
            Store & retrieve data
          </Typography>
          {config.operation && (
            <Chip 
              label={config.operation} 
              size="small" 
              sx={{ 
                bgcolor: 'rgba(255,255,255,0.2)', 
                color: 'white',
                border: '1px solid rgba(255,255,255,0.3)',
                mr: 0.5
              }}
            />
          )}
          {config.variableName && (
            <Chip 
              label={config.variableName.slice(0, 8) + (config.variableName.length > 8 ? '...' : '')} 
              size="small" 
              sx={{ 
                bgcolor: 'rgba(255,255,255,0.2)', 
                color: 'white',
                border: '1px solid rgba(255,255,255,0.3)'
              }}
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

export default VariableNode;