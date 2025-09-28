import React, { useState, useCallback, useRef, useEffect } from 'react';
import { Node } from '@xyflow/react';
import { useLocation } from 'react-router-dom';
import { Box, Menu, MenuItem, Button } from '../utils/mui';
import {
  PlayArrow as StartIcon,
  SmartToy as ModelIcon,
  Build as ToolIcon,
  Memory as MemoryIcon,
  Search as RetrievalIcon,
  CallSplit as ConditionalIcon,
  Loop as LoopIcon,
  Storage as VariableIcon,
  Error as ErrorHandlerIcon,
  Schedule as DelayIcon,
  CheckCircle as ValidIcon,
  GetApp as ExampleIcon,
  GridOn as GridIcon,
  Undo as UndoIcon,
  Redo as RedoIcon,
  ContentCopy as CopyIcon,
  ContentPaste as PasteIcon,
  LibraryBooks as TemplateIcon,
  Save as SaveIcon,
  Clear as ClearIcon,
  MoreVert as MoreIcon,
  Delete as DeleteIcon,
  PlayArrow as ExecuteIcon,
  BugReport as DebugIcon,
} from '@mui/icons-material';
import PageLayout from '../components/PageLayout';
import WorkflowEditor from '../components/workflow/WorkflowEditor';
import WorkflowSectionDrawer from '../components/workflow/WorkflowSectionDrawer';
import { WorkflowDefinition, WorkflowNodeData, WorkflowNodeType } from '../components/workflow/WorkflowEditor';

const WorkflowBuilderPage: React.FC = () => {
  const location = useLocation();
  const [selectedNode, setSelectedNode] = useState<Node<WorkflowNodeData> | null>(null);
  const [currentWorkflow, setCurrentWorkflow] = useState<WorkflowDefinition>({
    nodes: [],
    edges: [],
    metadata: {
      name: 'New Workflow',
      description: '',
      version: '1.0.0',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
  });
  
  // Sectioned drawer state
  const [drawerOpen, setDrawerOpen] = useState(true);
  const [drawerCollapsed, setDrawerCollapsed] = useState(false);
  
  // Create a ref to access WorkflowEditor methods
  const workflowEditorRef = useRef<{
    addNode: (nodeType: WorkflowNodeType) => void;
    handleUndo: () => void;
    handleRedo: () => void;
    handleCopy: () => void;
    handlePaste: () => void;
    handleSave: () => void;
    handleClear: () => void;
    handleToggleGrid: () => void;
    handleToggleMiniMap: () => void;
    handleValidate: () => void;
    handleExecute: () => void;
    handleDebug: () => void;
    loadExample: (exampleName: string) => void;
    showTemplateManager: () => void;
    deleteSelected: () => void;
    updateNode: (nodeId: string, updates: Partial<WorkflowNodeData>) => void;
  }>(null);
  
  // Dropdown menu state
  const [nodeMenuAnchor, setNodeMenuAnchor] = useState<null | HTMLElement>(null);
  const [editMenuAnchor, setEditMenuAnchor] = useState<null | HTMLElement>(null);
  const [exampleMenuAnchor, setExampleMenuAnchor] = useState<null | HTMLElement>(null);
  const [actionMenuAnchor, setActionMenuAnchor] = useState<null | HTMLElement>(null);

  // Handle node selection
  const handleNodeClick = useCallback((event: React.MouseEvent, node: Node<WorkflowNodeData>) => {
    setSelectedNode(node);
    if (!drawerOpen) {
      setDrawerOpen(true);
    }
  }, [drawerOpen]);

  // Handle node updates
  const handleNodeUpdate = useCallback((nodeId: string, data: Partial<WorkflowNodeData>) => {
    // Forward the update to WorkflowEditor via ref
    if (workflowEditorRef.current) {
      workflowEditorRef.current.updateNode(nodeId, data);
    }
  }, []);

  // Handle template data from navigation state
  useEffect(() => {
    const state = location.state as any;
    if (state?.editTemplate) {
      const template = state.editTemplate;
      // If template has workflow data, load it
      if (template.workflow) {
        setCurrentWorkflow({
          nodes: template.workflow.nodes || [],
          edges: template.workflow.edges || [],
          metadata: {
            name: template.name || 'Template Workflow',
            description: template.description || '',
            version: '1.0.0',
            createdAt: template.created_at || new Date().toISOString(),
            updatedAt: template.updated_at || new Date().toISOString(),
          },
        });
      }
    }
  }, [location.state]);

  // Node types for dropdown menu
  const nodeTypes = [
    { type: 'start', label: 'Start', icon: <StartIcon /> },
    { type: 'model', label: 'Model', icon: <ModelIcon /> },
    { type: 'tool', label: 'Tool', icon: <ToolIcon /> },
    { type: 'memory', label: 'Memory', icon: <MemoryIcon /> },
    { type: 'retrieval', label: 'Retrieval', icon: <RetrievalIcon /> },
    { type: 'conditional', label: 'Conditional', icon: <ConditionalIcon /> },
    { type: 'loop', label: 'Loop', icon: <LoopIcon /> },
    { type: 'variable', label: 'Variable', icon: <VariableIcon /> },
    { type: 'errorHandler', label: 'Error Handler', icon: <ErrorHandlerIcon /> },
    { type: 'delay', label: 'Delay', icon: <DelayIcon /> },
  ];

  const toolbar = (
    <>
      {/* Add Nodes Dropdown */}
      <Button
        variant="outlined"
        onClick={(e) => setNodeMenuAnchor(e.currentTarget)}
        startIcon={<StartIcon />}
        endIcon={<MoreIcon />}
      >
        Add Node
      </Button>
      
      {/* Edit Actions Dropdown */}
      <Button
        variant="outlined"
        onClick={(e) => setEditMenuAnchor(e.currentTarget)}
        startIcon={<UndoIcon />}
        endIcon={<MoreIcon />}
      >
        Edit
      </Button>
      
      {/* Templates Button */}
      <Button
        variant="outlined"
        onClick={() => {
          if (workflowEditorRef.current) {
            workflowEditorRef.current.showTemplateManager();
          }
        }}
        startIcon={<TemplateIcon />}
      >
        Templates
      </Button>

      {/* Examples Dropdown */}
      <Button
        variant="outlined"
        onClick={(e) => setExampleMenuAnchor(e.currentTarget)}
        startIcon={<ExampleIcon />}
        endIcon={<MoreIcon />}
      >
        Examples
      </Button>
      
      {/* More Actions Dropdown */}
      <Button
        variant="outlined"
        onClick={(e) => setActionMenuAnchor(e.currentTarget)}
        startIcon={<SaveIcon />}
        endIcon={<MoreIcon />}
      >
        Actions
      </Button>
    </>
  );

  const drawerWidth = 350;
  const collapsedDrawerWidth = 64;
  const currentDrawerWidth = drawerCollapsed ? collapsedDrawerWidth : drawerWidth;

  return (
    <Box sx={{ display: 'flex', height: '100%' }}>
      <Box
        sx={{
          flexGrow: 1,
          width: drawerOpen ? `calc(100% - ${currentDrawerWidth}px)` : '100%',
          transition: (theme) =>
            theme.transitions.create('width', {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.leavingScreen,
            }),
        }}
      >
        <PageLayout title="Workflow Builder" toolbar={toolbar} fullHeight={true}>
          <Box sx={{ height: '100%', width: '100%' }}>
            <WorkflowEditor
              ref={workflowEditorRef}
              onNodeClick={handleNodeClick}
              onWorkflowChange={setCurrentWorkflow}
              showToolbar={false}
            />
          </Box>
        </PageLayout>
      </Box>

      {/* Sectioned Right Drawer - only show when open */}
      {drawerOpen && (
        <WorkflowSectionDrawer
          open={drawerOpen}
          collapsed={drawerCollapsed}
          onToggleCollapsed={() => setDrawerCollapsed(!drawerCollapsed)}
          selectedNode={selectedNode}
          currentWorkflow={currentWorkflow}
          onNodeUpdate={handleNodeUpdate}
          width={drawerWidth}
          collapsedWidth={collapsedDrawerWidth}
        />
      )}

      {/* Menu components remain the same */}

      {/* Add Nodes Menu */}
      <Menu
        anchorEl={nodeMenuAnchor}
        open={Boolean(nodeMenuAnchor)}
        onClose={() => setNodeMenuAnchor(null)}
      >
        {nodeTypes.map((nodeType) => (
          <MenuItem 
            key={nodeType.type}
            onClick={() => {
              if (workflowEditorRef.current) {
                workflowEditorRef.current.addNode(nodeType.type as WorkflowNodeType);
              }
              setNodeMenuAnchor(null);
            }}
          >
            {nodeType.icon}
            <Box sx={{ ml: 1 }}>{nodeType.label}</Box>
          </MenuItem>
        ))}
      </Menu>

      {/* Edit Actions Menu */}
      <Menu
        anchorEl={editMenuAnchor}
        open={Boolean(editMenuAnchor)}
        onClose={() => setEditMenuAnchor(null)}
      >
        <MenuItem onClick={() => {
          if (workflowEditorRef.current) {
            workflowEditorRef.current.handleUndo();
          }
          setEditMenuAnchor(null);
        }}>
          <UndoIcon sx={{ mr: 1 }} />
          Undo
        </MenuItem>
        <MenuItem onClick={() => {
          if (workflowEditorRef.current) {
            workflowEditorRef.current.handleRedo();
          }
          setEditMenuAnchor(null);
        }}>
          <RedoIcon sx={{ mr: 1 }} />
          Redo
        </MenuItem>
        <MenuItem onClick={() => {
          if (workflowEditorRef.current) {
            workflowEditorRef.current.handleCopy();
          }
          setEditMenuAnchor(null);
        }}>
          <CopyIcon sx={{ mr: 1 }} />
          Copy
        </MenuItem>
        <MenuItem onClick={() => {
          if (workflowEditorRef.current) {
            workflowEditorRef.current.handlePaste();
          }
          setEditMenuAnchor(null);
        }}>
          <PasteIcon sx={{ mr: 1 }} />
          Paste
        </MenuItem>
        <MenuItem onClick={() => {
          if (workflowEditorRef.current) {
            workflowEditorRef.current.deleteSelected();
          }
          setEditMenuAnchor(null);
        }}>
          <DeleteIcon sx={{ mr: 1 }} />
          Delete
        </MenuItem>
      </Menu>

      {/* Examples Menu */}
      <Menu
        anchorEl={exampleMenuAnchor}
        open={Boolean(exampleMenuAnchor)}
        onClose={() => setExampleMenuAnchor(null)}
      >
        <MenuItem onClick={() => {
          if (workflowEditorRef.current) {
            workflowEditorRef.current.loadExample('simple');
          }
          setExampleMenuAnchor(null);
        }}>
          Simple Chat
        </MenuItem>
        <MenuItem onClick={() => {
          if (workflowEditorRef.current) {
            workflowEditorRef.current.loadExample('ragWithTools');
          }
          setExampleMenuAnchor(null);
        }}>
          RAG with Tools
        </MenuItem>
        <MenuItem onClick={() => {
          if (workflowEditorRef.current) {
            workflowEditorRef.current.loadExample('parallelProcessing');
          }
          setExampleMenuAnchor(null);
        }}>
          Multi-step Process
        </MenuItem>
      </Menu>

      {/* Actions Menu */}
      <Menu
        anchorEl={actionMenuAnchor}
        open={Boolean(actionMenuAnchor)}
        onClose={() => setActionMenuAnchor(null)}
      >
        <MenuItem onClick={() => {
          if (workflowEditorRef.current) {
            workflowEditorRef.current.handleSave();
          }
          setActionMenuAnchor(null);
        }}>
          <SaveIcon sx={{ mr: 1 }} />
          Save
        </MenuItem>
        <MenuItem onClick={() => {
          if (workflowEditorRef.current) {
            workflowEditorRef.current.handleExecute();
          }
          setActionMenuAnchor(null);
        }}>
          <ExecuteIcon sx={{ mr: 1 }} />
          Execute
        </MenuItem>
        <MenuItem onClick={() => {
          if (workflowEditorRef.current) {
            workflowEditorRef.current.handleDebug();
          }
          setActionMenuAnchor(null);
        }}>
          <DebugIcon sx={{ mr: 1 }} />
          Debug
        </MenuItem>
        <MenuItem onClick={() => setActionMenuAnchor(null)}>
          <TemplateIcon sx={{ mr: 1 }} />
          Save as Template
        </MenuItem>
        <MenuItem onClick={() => {
          if (workflowEditorRef.current) {
            workflowEditorRef.current.handleValidate();
          }
          setActionMenuAnchor(null);
        }}>
          <ValidIcon sx={{ mr: 1 }} />
          Validate
        </MenuItem>
        <MenuItem onClick={() => {
          if (workflowEditorRef.current) {
            workflowEditorRef.current.handleToggleGrid();
          }
          setActionMenuAnchor(null);
        }}>
          <GridIcon sx={{ mr: 1 }} />
          Toggle Grid
        </MenuItem>
        <MenuItem onClick={() => {
          if (workflowEditorRef.current) {
            workflowEditorRef.current.handleClear();
          }
          setActionMenuAnchor(null);
        }}>
          <ClearIcon sx={{ mr: 1 }} />
          Clear All
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default WorkflowBuilderPage;