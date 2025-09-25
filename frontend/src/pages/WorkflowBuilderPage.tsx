import React, { useState, useCallback, useEffect, useRef } from 'react';
import { ReactFlowProvider } from '@xyflow/react';
import { 
  Box, 
  Button, 
  Menu, 
  MenuItem, 
  ButtonGroup,
  Divider,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Typography,
} from '../utils/mui';
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
import PageLayout from '../components/PageLayout';
import ModernWorkflowEditor from '../components/workflow/ModernWorkflowEditor';
import WorkflowPropertiesPanel from './WorkflowPropertiesPanel';
import { nodeDefinitions } from '../components/workflow/NodePalette';
import { WorkflowDefinition, WorkflowNodeType } from '../components/workflow/types';
import { useRightSidebar } from '../components/RightSidebarContext';
import { toastService } from '../services/toast-service';
import { exampleWorkflows } from '../components/workflow/WorkflowExamples';

// Template Selection Component
const TemplateSelectionList: React.FC<{
  onSelectTemplate: (templateId: string) => void;
}> = ({ onSelectTemplate }) => {
  const [templates, setTemplates] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadTemplates = async () => {
      try {
        setLoading(true);
        const workflowService = (await import('../services/workflow-service')).default;
        const templateList = await workflowService.listTemplates();
        setTemplates(templateList);
        setError(null);
      } catch (err) {
        setError('Failed to load templates');
        setTemplates([]);
      } finally {
        setLoading(false);
      }
    };

    loadTemplates();
  }, []);

  if (loading) {
    return <Typography>Loading templates...</Typography>;
  }

  if (error) {
    return <Typography color="error">{error}</Typography>;
  }

  if (templates.length === 0) {
    return <Typography>No templates available</Typography>;
  }

  return (
    <List>
      {templates.map((template) => (
        <ListItem key={template.id} disablePadding>
          <ListItemButton onClick={() => onSelectTemplate(template.id)}>
            <ListItemText
              primary={template.name}
              secondary={template.description || 'No description available'}
            />
          </ListItemButton>
        </ListItem>
      ))}
    </List>
  );
};

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

const WorkflowBuilderPage: React.FC = () => {
  const { setPanelContent, setTitle, setOpen } = useRightSidebar();
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

  // Dialog states
  const [showExampleDialog, setShowExampleDialog] = useState(false);
  const [showTemplateDialog, setShowTemplateDialog] = useState(false);

  // Workflow editor function refs
  const addNodeFunctionRef = useRef<((nodeType: WorkflowNodeType, position?: { x: number; y: number }) => void) | null>(null);
  const viewControlsRef = useRef<{
    zoomIn: () => void;
    zoomOut: () => void;
    fitView: () => void;
    toggleGrid: () => void;
    snapToGrid: boolean;
  } | null>(null);
  const editControlsRef = useRef<{
    undo: () => void;
    redo: () => void;
    copy: () => void;
    paste: () => void;
    canUndo: boolean;
    canRedo: boolean;
    canPaste: boolean;
  } | null>(null);

  const handleUndo = useCallback(() => {
    if (editControlsRef.current) {
      editControlsRef.current.undo();
    }
  }, []);

  const handleRedo = useCallback(() => {
    if (editControlsRef.current) {
      editControlsRef.current.redo();
    }
  }, []);

  const handleCopy = useCallback(() => {
    if (editControlsRef.current) {
      editControlsRef.current.copy();
    }
  }, []);

  const handlePaste = useCallback(() => {
    if (editControlsRef.current) {
      editControlsRef.current.paste();
    }
  }, []);

  const handleZoomIn = useCallback(() => {
    if (viewControlsRef.current) {
      viewControlsRef.current.zoomIn();
    }
  }, []);

  const handleZoomOut = useCallback(() => {
    if (viewControlsRef.current) {
      viewControlsRef.current.zoomOut();
    }
  }, []);

  const handleFitView = useCallback(() => {
    if (viewControlsRef.current) {
      viewControlsRef.current.fitView();
    }
  }, []);

  const handleToggleGrid = useCallback(() => {
    if (viewControlsRef.current) {
      viewControlsRef.current.toggleGrid();
    }
  }, []);

  const handleValidate = useCallback(async () => {
    try {
      const workflowService = (await import('../services/workflow-service')).default;
      const result = await workflowService.validateWorkflow(workflow);
      
      if (result.isValid) {
        setValidationStatus('valid');
        toastService.success('Workflow is valid');
      } else {
        setValidationStatus('invalid');
        const errorCount = result.errors.length;
        const warningCount = result.warnings.length;
        toastService.error(
          `Found ${errorCount} error${errorCount !== 1 ? 's' : ''}${
            warningCount > 0 ? ` and ${warningCount} warning${warningCount !== 1 ? 's' : ''}` : ''
          }`
        );
      }
    } catch (error) {
      setValidationStatus('invalid');
      toastService.error('Failed to validate workflow');
    }
  }, [workflow]);

  const handleSave = useCallback(async () => {
    setIsSaving(true);
    try {
      const workflowService = (await import('../services/workflow-service')).default;
      
      if (workflow.id) {
        // Update existing workflow
        await workflowService.updateWorkflow({
          id: workflow.id,
          name: workflow.metadata.name,
          description: workflow.metadata.description,
          nodes: workflow.nodes,
          edges: workflow.edges,
          metadata: workflow.metadata,
        });
      } else {
        // Create new workflow
        const newWorkflow = await workflowService.createWorkflow({
          name: workflow.metadata.name,
          description: workflow.metadata.description,
          nodes: workflow.nodes,
          edges: workflow.edges,
          metadata: workflow.metadata,
        });
        // Update the workflow with the new ID
        setWorkflow(prev => ({ ...prev, id: newWorkflow.id }));
      }
      
      toastService.success('Workflow saved successfully');
    } catch (error) {
      console.error('Save error:', error);
      toastService.error('Failed to save workflow');
    } finally {
      setIsSaving(false);
    }
  }, [workflow, setWorkflow]);

  const handleClear = useCallback(() => {
    if (window.confirm('Are you sure you want to clear the workflow?')) {
      setWorkflow(defaultWorkflow);
      setSelectedNodeId(undefined);
      setSelectedEdgeId(undefined);
      toastService.info('Workflow cleared');
    }
  }, []);

  const handleLoadExample = useCallback(() => {
    setShowExampleDialog(true);
  }, []);

  const handleSelectExample = useCallback((exampleKey: string) => {
    const example = exampleWorkflows[exampleKey];
    
    if (example) {
      setWorkflow({
        ...example,
        metadata: {
          ...example.metadata,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        }
      });
      setSelectedNodeId(undefined);
      setSelectedEdgeId(undefined);
      toastService.success(`Loaded example: ${example.metadata.name}`);
      setShowExampleDialog(false);
    } else {
      toastService.error('Failed to load example workflow');
    }
  }, [setWorkflow, setSelectedNodeId, setSelectedEdgeId]);

  const handleLoadTemplate = useCallback(() => {
    setShowTemplateDialog(true);
  }, []);

  const handleSelectTemplate = useCallback(async (templateId?: string) => {
    try {
      const workflowService = (await import('../services/workflow-service')).default;
      const templates = await workflowService.listTemplates();
      
      if (templates.length === 0) {
        toastService.info('No templates available');
        setShowTemplateDialog(false);
        return;
      }
      
      // Use provided templateId or first template
      const template = templateId ? templates.find(t => t.id === templateId) || templates[0] : templates[0];
      const newWorkflow = await workflowService.createFromTemplate(template.id);
      setWorkflow(newWorkflow);
      setSelectedNodeId(undefined);
      setSelectedEdgeId(undefined);
      toastService.success(`Loaded template: ${template.name}`);
      setShowTemplateDialog(false);
    } catch (error) {
      toastService.error('Failed to load template');
      setShowTemplateDialog(false);
    }
  }, [setWorkflow, setSelectedNodeId, setSelectedEdgeId]);

  const handleAddNode = useCallback((nodeType: WorkflowNodeType) => {
    // Use the addNode function from the editor if available
    if (addNodeFunctionRef.current) {
      addNodeFunctionRef.current(nodeType);
    }
    setNodeMenuAnchor(null);
  }, []);

  // Set up right sidebar content
  useEffect(() => {
    setTitle('Workflow Properties');
    setPanelContent(
      <WorkflowPropertiesPanel
        workflow={workflow}
        selectedNodeId={selectedNodeId}
        selectedEdgeId={selectedEdgeId}
        onNodeUpdate={(nodeId, updates) => {
          // Update node in workflow
          setWorkflow(prev => ({
            ...prev,
            nodes: prev.nodes.map(node => 
              node.id === nodeId 
                ? { ...node, data: { ...node.data, ...updates } }
                : node
            )
          }));
        }}
        onEdgeUpdate={(edgeId, updates) => {
          // Update edge in workflow
          setWorkflow(prev => ({
            ...prev,
            edges: prev.edges.map(edge => 
              edge.id === edgeId 
                ? { ...edge, data: { ...edge.data, ...updates } }
                : edge
            )
          }));
        }}
      />
    );
    setOpen(true);
  }, [setPanelContent, setTitle, setOpen, workflow, selectedNodeId, selectedEdgeId]);

  // Group node definitions by category
  const nodesByCategory = nodeDefinitions.reduce((acc, node) => {
    if (!acc[node.category]) {
      acc[node.category] = [];
    }
    acc[node.category].push(node);
    return acc;
  }, {} as Record<string, typeof nodeDefinitions>);

  // Toolbar content
  const toolbar = (
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
  );

  return (
    <PageLayout title="Workflow Builder" toolbar={toolbar}>
      <Box sx={{ height: '100%', width: '100%' }}>
        <ReactFlowProvider>
          <ModernWorkflowEditor
            initialWorkflow={workflow}
            onWorkflowChange={setWorkflow}
            onSave={handleSave}
            onAddNodeRef={(fn) => { addNodeFunctionRef.current = fn; }}
            onViewControlsRef={(controls) => { viewControlsRef.current = controls; }}
            onEditControlsRef={(controls) => { editControlsRef.current = controls; }}
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

      {/* Example Selection Dialog */}
      <Dialog
        open={showExampleDialog}
        onClose={() => setShowExampleDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Load Example Workflow</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Choose an example workflow to load:
          </Typography>
          <List>
            {Object.entries(exampleWorkflows).map(([key, example]) => (
              <ListItem key={key} disablePadding>
                <ListItemButton onClick={() => handleSelectExample(key)}>
                  <ListItemText
                    primary={example.metadata.name}
                    secondary={example.metadata.description}
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowExampleDialog(false)}>Cancel</Button>
        </DialogActions>
      </Dialog>

      {/* Template Selection Dialog */}
      <Dialog
        open={showTemplateDialog}
        onClose={() => setShowTemplateDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Load Template</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Loading templates...
          </Typography>
          <TemplateSelectionList onSelectTemplate={handleSelectTemplate} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowTemplateDialog(false)}>Cancel</Button>
        </DialogActions>
      </Dialog>
    </PageLayout>
  );
};

export default WorkflowBuilderPage;