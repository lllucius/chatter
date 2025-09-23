import React from 'react';
import { ReactFlowProvider } from '@xyflow/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box } from '@mui/material';
import ModernWorkflowEditor from '../components/workflow/ModernWorkflowEditor';
import { WorkflowDefinition } from '../components/workflow/types';

const theme = createTheme({
  palette: {
    mode: 'light',
  },
});

// Demo workflow for testing
const demoWorkflow: WorkflowDefinition = {
  id: 'demo-workflow',
  nodes: [
    {
      id: 'start-1',
      type: 'start',
      position: { x: 100, y: 200 },
      data: {
        label: 'Start',
        nodeType: 'start',
        config: { name: 'Start' },
        description: 'Entry point for the workflow',
      },
    },
    {
      id: 'model-1',
      type: 'model',
      position: { x: 350, y: 200 },
      data: {
        label: 'AI Model',
        nodeType: 'model',
        config: {
          name: 'AI Model',
          model: 'gpt-4',
          temperature: 0.7,
          maxTokens: 1000,
          systemMessage: 'You are a helpful AI assistant.',
        },
        description: 'Language model interaction',
      },
    },
  ],
  edges: [
    {
      id: 'e1',
      source: 'start-1',
      target: 'model-1',
      type: 'smoothstep',
      animated: true,
    },
  ],
  metadata: {
    name: 'Demo Workflow',
    description: 'A simple demonstration workflow',
    version: '1.0.0',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  version: '1.0.0',
  variables: {},
  settings: {
    autoSave: false,
    enableValidation: true,
    enableAnalytics: true,
  },
};

const WorkflowBuilderDemo: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ height: '100vh', width: '100vw' }}>
        <ReactFlowProvider>
          <ModernWorkflowEditor
            initialWorkflow={demoWorkflow}
            onWorkflowChange={(workflow) => console.log('Workflow changed:', workflow)}
            onSave={async (workflow) => {
              console.log('Saving workflow:', workflow);
              // Simulate save delay
              await new Promise(resolve => setTimeout(resolve, 1000));
            }}
            readOnly={false}
            showToolbar={true}
            showPalette={true}
            showProperties={true}
            showMinimap={true}
            height="100vh"
            width="100vw"
          />
        </ReactFlowProvider>
      </Box>
    </ThemeProvider>
  );
};

export default WorkflowBuilderDemo;