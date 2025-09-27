import React, { useState, useCallback } from 'react';
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
} from '@mui/icons-material';
import PageLayout from '../components/PageLayout';
import WorkflowEditor from '../components/workflow/WorkflowEditor';
import { useRightSidebar } from '../components/RightSidebarContext';
import PropertiesPanel from '../components/workflow/PropertiesPanel';
import WorkflowAnalytics from '../components/workflow/WorkflowAnalytics';
import { WorkflowDefinition, WorkflowNodeData } from '../components/workflow/WorkflowEditor';

const WorkflowBuilderPage: React.FC = () => {
  const [_selectedNode, setSelectedNode] = useState<Node<WorkflowNodeData> | null>(null);
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
  
  // Right sidebar state
  const { setPanelContent, setTitle, setOpen } = useRightSidebar();
  
  // Dropdown menu state
  const [nodeMenuAnchor, setNodeMenuAnchor] = useState<null | HTMLElement>(null);
  const [editMenuAnchor, setEditMenuAnchor] = useState<null | HTMLElement>(null);
  const [exampleMenuAnchor, setExampleMenuAnchor] = useState<null | HTMLElement>(null);
  const [actionMenuAnchor, setActionMenuAnchor] = useState<null | HTMLElement>(null);

  // Handle node selection - show properties in right sidebar
  const handleNodeClick = useCallback((event: React.MouseEvent, node: Node<WorkflowNodeData>) => {
    setSelectedNode(node);
    setTitle('Node Properties');
    setPanelContent(
      <PropertiesPanel
        selectedNode={node}
        onNodeUpdate={(nodeId: string, data: Partial<WorkflowNodeData>) => {
          // Update node logic would go here
          // console.log('Update node:', nodeId, data);
        }}
        onClose={() => {
          setSelectedNode(null);
          setPanelContent(null);
        }}
      />
    );
    setOpen(true);
  }, [setPanelContent, setTitle, setOpen]);

  // Show analytics in right sidebar
  const handleShowAnalytics = useCallback(() => {
    setTitle('Workflow Analytics');
    setPanelContent(
      <WorkflowAnalytics workflow={currentWorkflow} />
    );
    setOpen(true);
  }, [currentWorkflow, setPanelContent, setTitle, setOpen]);

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

      {/* Analytics Button */}
      <Button
        variant="outlined"
        onClick={handleShowAnalytics}
        startIcon={<ValidIcon />}
      >
        Analytics
      </Button>
    </>
  );

  return (
    <PageLayout title="Workflow Builder" toolbar={toolbar}>
      <Box sx={{ height: '100%', width: '100%' }}>
        <WorkflowEditor
          onNodeClick={handleNodeClick}
          onWorkflowChange={setCurrentWorkflow}
          showToolbar={false}
        />
      </Box>

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
              // Add node logic would go here
              console.log('Add node:', nodeType.type);
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
        <MenuItem onClick={() => setEditMenuAnchor(null)}>
          <UndoIcon sx={{ mr: 1 }} />
          Undo
        </MenuItem>
        <MenuItem onClick={() => setEditMenuAnchor(null)}>
          <RedoIcon sx={{ mr: 1 }} />
          Redo
        </MenuItem>
        <MenuItem onClick={() => setEditMenuAnchor(null)}>
          <CopyIcon sx={{ mr: 1 }} />
          Copy
        </MenuItem>
        <MenuItem onClick={() => setEditMenuAnchor(null)}>
          <PasteIcon sx={{ mr: 1 }} />
          Paste
        </MenuItem>
      </Menu>

      {/* Examples Menu */}
      <Menu
        anchorEl={exampleMenuAnchor}
        open={Boolean(exampleMenuAnchor)}
        onClose={() => setExampleMenuAnchor(null)}
      >
        <MenuItem onClick={() => setExampleMenuAnchor(null)}>
          Simple Chat
        </MenuItem>
        <MenuItem onClick={() => setExampleMenuAnchor(null)}>
          RAG with Tools
        </MenuItem>
        <MenuItem onClick={() => setExampleMenuAnchor(null)}>
          Multi-step Process
        </MenuItem>
      </Menu>

      {/* Actions Menu */}
      <Menu
        anchorEl={actionMenuAnchor}
        open={Boolean(actionMenuAnchor)}
        onClose={() => setActionMenuAnchor(null)}
      >
        <MenuItem onClick={() => setActionMenuAnchor(null)}>
          <SaveIcon sx={{ mr: 1 }} />
          Save
        </MenuItem>
        <MenuItem onClick={() => setActionMenuAnchor(null)}>
          <TemplateIcon sx={{ mr: 1 }} />
          Save as Template
        </MenuItem>
        <MenuItem onClick={() => setActionMenuAnchor(null)}>
          <ValidIcon sx={{ mr: 1 }} />
          Validate
        </MenuItem>
        <MenuItem onClick={() => setActionMenuAnchor(null)}>
          <GridIcon sx={{ mr: 1 }} />
          Toggle Grid
        </MenuItem>
        <MenuItem onClick={() => setActionMenuAnchor(null)}>
          <ClearIcon sx={{ mr: 1 }} />
          Clear All
        </MenuItem>
      </Menu>
    </PageLayout>
  );
};

export default WorkflowBuilderPage;