import React, { useState, useCallback, useEffect } from 'react';
import { ReactFlowProvider } from '@xyflow/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box, Button, Menu, MenuItem, ButtonGroup, Divider, Tooltip } from '@mui/material';
import {
  UndoIcon,
  RedoIcon,
  CopyIcon,
  PasteIcon,
  SaveIcon,
  ClearIcon,
  GridIcon,
  ZoomInIcon,
  ZoomOutIcon,
  FitViewIcon,
  ValidIcon,
  ErrorIcon,
  TemplateIcon,
  ExampleIcon,
  AddIcon,
  DropdownIcon,
} from '../utils/icons';
import ModernWorkflowEditor from '../components/workflow/ModernWorkflowEditor';
import { nodeDefinitions } from '../components/workflow/NodePalette';
import { WorkflowDefinition, WorkflowNodeType } from '../components/workflow/types';

const theme = createTheme({
  palette: {
    mode: 'light',
  },
});

// Demo workflow for initial state
const defaultWorkflow: WorkflowDefinition = {
  id: 'new-workflow',
  nodes: [],
  edges: [],
  metadata: {
    name: 'New Workflow',
    description: 'A new workflow',
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

const NewWorkflowBuilderDemo: React.FC = () => {
  const [workflow, setWorkflow] = useState<WorkflowDefinition>(defaultWorkflow);
  const [selectedNodeId, setSelectedNodeId] = useState<string | undefined>();
  const [selectedEdgeId, setSelectedEdgeId] = useState<string | undefined>();
  const [isSaving, setIsSaving] = useState(false);
  const [validationStatus, setValidationStatus] = useState<'valid' | 'invalid' | undefined>();

  // Menu anchors for dropdowns
  const [editMenuAnchor, setEditMenuAnchor] = useState<null | HTMLElement>(null);
  const [viewMenuAnchor, setViewMenuAnchor] = useState<null | HTMLElement>(null);
  const [toolsMenuAnchor, setToolsMenuAnchor] = useState<null | HTMLElement>(null);
  const [nodeMenuAnchor, setNodeMenuAnchor] = useState<null | HTMLElement>(null);

  // Mock handlers for demo
  const handleUndo = useCallback(() => console.log('Undo clicked'), []);
  const handleRedo = useCallback(() => console.log('Redo clicked'), []);
  const handleCopy = useCallback(() => console.log('Copy clicked'), []);
  const handlePaste = useCallback(() => console.log('Paste clicked'), []);
  const handleZoomIn = useCallback(() => console.log('Zoom In clicked'), []);
  const handleZoomOut = useCallback(() => console.log('Zoom Out clicked'), []);
  const handleFitView = useCallback(() => console.log('Fit View clicked'), []);
  const handleToggleGrid = useCallback(() => console.log('Toggle Grid clicked'), []);
  const handleValidate = useCallback(() => {
    setValidationStatus(workflow.nodes.length === 0 ? 'invalid' : 'valid');
  }, [workflow]);
  const handleSave = useCallback(async () => {
    setIsSaving(true);
    setTimeout(() => setIsSaving(false), 1000);
  }, []);
  const handleClear = useCallback(() => {
    if (window.confirm('Clear workflow?')) {
      setWorkflow(defaultWorkflow);
    }
  }, []);
  const handleLoadExample = useCallback(() => console.log('Load Example clicked'), []);
  const handleLoadTemplate = useCallback(() => console.log('Load Template clicked'), []);
  const handleAddNode = useCallback((nodeType: WorkflowNodeType) => {
    console.log(`Add ${nodeType} node`);
    setNodeMenuAnchor(null);
  }, []);

  // Group node definitions by category
  const nodesByCategory = nodeDefinitions.reduce((acc, node) => {
    if (!acc[node.category]) {
      acc[node.category] = [];
    }
    acc[node.category].push(node);
    return acc;
  }, {} as Record<string, typeof nodeDefinitions>);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ height: '100vh', width: '100vw', display: 'flex', flexDirection: 'column' }}>
        {/* Header with Title and Toolbar */}
        <Box sx={{ 
          bgcolor: 'background.paper', 
          borderBottom: 1, 
          borderColor: 'divider',
          p: 2,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <Box sx={{ fontSize: '1.5rem', fontWeight: 600 }}>
            Workflow Builder (New Design)
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {/* Node Palette Dropdown */}
            <Button
              variant="outlined"
              startIcon={<AddIcon />}
              endIcon={<DropdownIcon />}
              onClick={(event) => setNodeMenuAnchor(event.currentTarget)}
              size="small"
            >
              Add Node
            </Button>
            <Menu
              anchorEl={nodeMenuAnchor}
              open={Boolean(nodeMenuAnchor)}
              onClose={() => setNodeMenuAnchor(null)}
            >
              {Object.entries(nodesByCategory).map(([category, nodes]) => [
                <MenuItem key={`${category}-header`} disabled>
                  <Box sx={{ fontWeight: 'bold', textTransform: 'capitalize' }}>
                    {category.replace('_', ' ')}
                  </Box>
                </MenuItem>,
                ...nodes.map(node => (
                  <MenuItem 
                    key={node.type}
                    onClick={() => handleAddNode(node.type)}
                    sx={{ pl: 3 }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Box sx={{ fontSize: 20 }}>{node.icon}</Box>
                      <Box>
                        <Box sx={{ fontWeight: 500 }}>{node.label}</Box>
                        <Box sx={{ fontSize: 12, color: 'text.secondary' }}>
                          {node.description}
                        </Box>
                      </Box>
                    </Box>
                  </MenuItem>
                )),
                <Divider key={`${category}-divider`} />
              ]).flat()}
            </Menu>

            <Divider orientation="vertical" flexItem />

            {/* Edit Menu */}
            <Button
              variant="outlined"
              endIcon={<DropdownIcon />}
              onClick={(event) => setEditMenuAnchor(event.currentTarget)}
              size="small"
            >
              Edit
            </Button>
            <Menu
              anchorEl={editMenuAnchor}
              open={Boolean(editMenuAnchor)}
              onClose={() => setEditMenuAnchor(null)}
            >
              <MenuItem onClick={() => { handleUndo(); setEditMenuAnchor(null); }}>
                <UndoIcon sx={{ mr: 1 }} />
                Undo
              </MenuItem>
              <MenuItem onClick={() => { handleRedo(); setEditMenuAnchor(null); }}>
                <RedoIcon sx={{ mr: 1 }} />
                Redo
              </MenuItem>
              <Divider />
              <MenuItem onClick={() => { handleCopy(); setEditMenuAnchor(null); }}>
                <CopyIcon sx={{ mr: 1 }} />
                Copy Selection
              </MenuItem>
              <MenuItem onClick={() => { handlePaste(); setEditMenuAnchor(null); }}>
                <PasteIcon sx={{ mr: 1 }} />
                Paste
              </MenuItem>
            </Menu>

            {/* View Menu */}
            <Button
              variant="outlined"
              endIcon={<DropdownIcon />}
              onClick={(event) => setViewMenuAnchor(event.currentTarget)}
              size="small"
            >
              View
            </Button>
            <Menu
              anchorEl={viewMenuAnchor}
              open={Boolean(viewMenuAnchor)}
              onClose={() => setViewMenuAnchor(null)}
            >
              <MenuItem onClick={() => { handleZoomIn(); setViewMenuAnchor(null); }}>
                <ZoomInIcon sx={{ mr: 1 }} />
                Zoom In
              </MenuItem>
              <MenuItem onClick={() => { handleZoomOut(); setViewMenuAnchor(null); }}>
                <ZoomOutIcon sx={{ mr: 1 }} />
                Zoom Out
              </MenuItem>
              <MenuItem onClick={() => { handleFitView(); setViewMenuAnchor(null); }}>
                <FitViewIcon sx={{ mr: 1 }} />
                Fit to View
              </MenuItem>
              <Divider />
              <MenuItem onClick={() => { handleToggleGrid(); setViewMenuAnchor(null); }}>
                <GridIcon sx={{ mr: 1 }} />
                Toggle Grid
              </MenuItem>
            </Menu>

            {/* Tools Menu */}
            <Button
              variant="outlined"
              endIcon={<DropdownIcon />}
              onClick={(event) => setToolsMenuAnchor(event.currentTarget)}
              size="small"
            >
              Tools
            </Button>
            <Menu
              anchorEl={toolsMenuAnchor}
              open={Boolean(toolsMenuAnchor)}
              onClose={() => setToolsMenuAnchor(null)}
            >
              <MenuItem onClick={() => { handleValidate(); setToolsMenuAnchor(null); }}>
                {validationStatus === 'valid' ? (
                  <ValidIcon sx={{ mr: 1, color: 'success.main' }} />
                ) : validationStatus === 'invalid' ? (
                  <ErrorIcon sx={{ mr: 1, color: 'error.main' }} />
                ) : (
                  <ValidIcon sx={{ mr: 1 }} />
                )}
                Validate Workflow
              </MenuItem>
              <Divider />
              <MenuItem onClick={() => { handleLoadTemplate(); setToolsMenuAnchor(null); }}>
                <TemplateIcon sx={{ mr: 1 }} />
                Load Template
              </MenuItem>
              <MenuItem onClick={() => { handleLoadExample(); setToolsMenuAnchor(null); }}>
                <ExampleIcon sx={{ mr: 1 }} />
                Load Example
              </MenuItem>
            </Menu>

            <Divider orientation="vertical" flexItem />

            {/* Action Buttons */}
            <ButtonGroup size="small">
              <Tooltip title="Save Workflow (Ctrl+S)">
                <Button
                  variant="contained"
                  startIcon={<SaveIcon />}
                  onClick={handleSave}
                  disabled={isSaving}
                >
                  {isSaving ? 'Saving...' : 'Save'}
                </Button>
              </Tooltip>
              <Tooltip title="Clear Workflow">
                <Button
                  variant="outlined"
                  color="error"
                  startIcon={<ClearIcon />}
                  onClick={handleClear}
                >
                  Clear
                </Button>
              </Tooltip>
            </ButtonGroup>
          </Box>
        </Box>

        {/* Main Content Area */}
        <Box sx={{ flex: 1, display: 'flex' }}>
          {/* Left: Workflow Editor */}
          <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            <ReactFlowProvider>
              <ModernWorkflowEditor
                initialWorkflow={workflow}
                onWorkflowChange={setWorkflow}
                onSave={handleSave}
                readOnly={false}
                showToolbar={false} // We're using our custom toolbar
                showPalette={false} // We're using dropdown instead
                showProperties={false} // Using right sidebar instead
                showMinimap={true}
                height="100%"
                width="100%"
              />
            </ReactFlowProvider>
          </Box>

          {/* Right: Properties Panel */}
          <Box sx={{ 
            width: 320, 
            bgcolor: 'background.paper',
            borderLeft: 1,
            borderColor: 'divider',
            display: 'flex',
            flexDirection: 'column'
          }}>
            <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
              <Box sx={{ fontWeight: 600, fontSize: '1.1rem' }}>Properties & Analysis</Box>
            </Box>
            
            <Box sx={{ flex: 1, p: 2 }}>
              {selectedNodeId ? (
                <Box>
                  <Box sx={{ fontWeight: 500, mb: 1 }}>Node Properties</Box>
                  <Box sx={{ color: 'text.secondary' }}>
                    Edit properties for selected node: {selectedNodeId}
                  </Box>
                </Box>
              ) : (
                <Box sx={{ color: 'text.secondary', textAlign: 'center', mt: 4 }}>
                  <Box sx={{ fontSize: '2rem', mb: 1 }}>⚙️</Box>
                  <Box sx={{ fontWeight: 500, mb: 1 }}>No Selection</Box>
                  <Box>Select a node or edge to edit its properties</Box>
                </Box>
              )}
              
              <Divider sx={{ my: 2 }} />
              
              <Box>
                <Box sx={{ fontWeight: 500, mb: 1 }}>Workflow Analytics</Box>
                <Box sx={{ color: 'text.secondary', fontSize: '0.875rem' }}>
                  <Box>Nodes: {workflow.nodes.length}</Box>
                  <Box>Edges: {workflow.edges.length}</Box>
                  <Box>Status: {validationStatus || 'Not validated'}</Box>
                </Box>
              </Box>
            </Box>
          </Box>
        </Box>
      </Box>
    </ThemeProvider>
  );
};

export default NewWorkflowBuilderDemo;