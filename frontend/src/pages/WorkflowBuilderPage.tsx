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
    toastService.info('Load Example functionality not implemented');
  }, []);

  const handleLoadTemplate = useCallback(async () => {
    try {
      const workflowService = (await import('../services/workflow-service')).default;
      const templates = await workflowService.listTemplates();
      
      if (templates.length === 0) {
        toastService.info('No templates available');
        return;
      }
      
      // For now, load the first template. In a real implementation,
      // this should open a template selection dialog
      const template = templates[0];
      const newWorkflow = await workflowService.createFromTemplate(template.id);
      setWorkflow(newWorkflow);
      setSelectedNodeId(undefined);
      setSelectedEdgeId(undefined);
      toastService.success(`Loaded template: ${template.name}`);
    } catch (error) {
      toastService.error('Failed to load template');
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
    </PageLayout>
  );
};

export default WorkflowBuilderPage;