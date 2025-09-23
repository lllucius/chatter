import React, { useCallback, useState, useMemo, useRef, useEffect } from 'react';
import {
  ReactFlow,
  Node,
  Edge,
  Controls,
  Background,
  MiniMap,
  NodeTypes,
  EdgeTypes,
  useReactFlow,
  Panel,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import {
  Box,
  Menu,
  MenuItem,
  Alert,
  Snackbar,
  useTheme,
  useMediaQuery,
  Paper,
  Drawer,
  IconButton,
  Fab,
  Typography,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Close as CloseIcon,
} from '@mui/icons-material';

// Import components
import NodePalette from './NodePalette';
import WorkflowToolbar from './WorkflowToolbar';
import EnhancedPropertiesPanel from './EnhancedPropertiesPanel';
import WorkflowAnalytics from './WorkflowAnalytics';
import TemplateManager from './TemplateManager';
import { exampleWorkflows } from './WorkflowExamples';

// Import types
import {
  WorkflowEditorProps,
  WorkflowNodeType,
  WorkflowNodeData,
  WorkflowEdgeData,
  ValidationResult,
} from './types';

// Import hooks
import { useWorkflowEditor } from './hooks/useWorkflowEditor';

// Import node components
import StartNode from './nodes/StartNode';
import ModelNode from './nodes/ModelNode';
import ToolNode from './nodes/ToolNode';
import MemoryNode from './nodes/MemoryNode';
import RetrievalNode from './nodes/RetrievalNode';
import ConditionalNode from './nodes/ConditionalNode';
import LoopNode from './nodes/LoopNode';
import VariableNode from './nodes/VariableNode';
import ErrorHandlerNode from './nodes/ErrorHandlerNode';
import DelayNode from './nodes/DelayNode';
import TransformNode from './nodes/TransformNode';
import ApiNode from './nodes/ApiNode';

// Import edge components
import CustomEdge from './edges/CustomEdge';

const GRID_SIZE = 20;

// Define node types for React Flow
const nodeTypes: NodeTypes = {
  start: StartNode,
  model: ModelNode,
  tool: ToolNode,
  memory: MemoryNode,
  retrieval: RetrievalNode,
  conditional: ConditionalNode,
  loop: LoopNode,
  variable: VariableNode,
  errorHandler: ErrorHandlerNode,
  delay: DelayNode,
  transform: TransformNode,
  api: ApiNode,
};

// Define edge types for React Flow
const edgeTypes: EdgeTypes = {
  custom: CustomEdge,
};

const ModernWorkflowEditor: React.FC<WorkflowEditorProps> = ({
  initialWorkflow,
  onWorkflowChange,
  onSave,
  readOnly = false,
  showToolbar = true,
  showPalette = true,
  showProperties = true,
  showMinimap = true,
  theme: editorTheme = 'auto',
  height = '100vh',
  width = '100%',
  className,
}) => {
  const theme = useTheme();
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const { screenToFlowPosition } = useReactFlow();

  // Responsive breakpoints
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const isTablet = useMediaQuery(theme.breakpoints.down('lg'));

  // Use the workflow editor hook
  const {
    workflow,
    addNode,
    updateNode,
    deleteNode,
    updateEdge,
    validate,
    undo,
    redo,
    canUndo,
    canRedo,
    copySelection,
    pasteFromClipboard,
    selectAll,
    deleteSelection,
    nodes,
    edges,
    setNodes,
    setEdges,
    onNodesChange,
    onEdgesChange,
    onConnect,
    selectedNodeId,
    setSelectedNodeId,
    selectedEdgeId,
    setSelectedEdgeId,
    clipboardData,
    snapToGrid,
    setSnapToGrid,
  } = useWorkflowEditor(initialWorkflow, onWorkflowChange);

  // UI state - responsive panel management
  const [showPropertiesPanel, setShowPropertiesPanel] = useState(!isMobile && showProperties);
  const [showAnalyticsPanel, setShowAnalyticsPanel] = useState(false);
  const [showTemplatesDialog, setShowTemplatesDialog] = useState(false);
  const [showNodePalette, setShowNodePalette] = useState(!isMobile && showPalette);
  
  // Mobile drawer states
  const [mobileNodePaletteOpen, setMobileNodePaletteOpen] = useState(false);
  const [mobilePropertiesOpen, setMobilePropertiesOpen] = useState(false);
  const [mobileAnalyticsOpen, setMobileAnalyticsOpen] = useState(false);
  
  // Other UI state
  const [exampleMenuAnchor, setExampleMenuAnchor] = useState<null | HTMLElement>(null);
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
  const [showValidationSnackbar, setShowValidationSnackbar] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // Responsive panel widths
  const nodePaletteWidth = isMobile ? 0 : isTablet ? 200 : 280;
  const propertiesPanelWidth = isMobile ? 0 : isTablet ? 300 : 350;
  const analyticsPanelWidth = isMobile ? 0 : isTablet ? 280 : 300;

  // Get selected nodes/edges
  const selectedNode = useMemo(
    () => nodes.find((node: Node<WorkflowNodeData>) => node.id === selectedNodeId) || null,
    [nodes, selectedNodeId]
  );

  const selectedEdge = useMemo(
    () => edges.find((edge: Edge<WorkflowEdgeData>) => edge.id === selectedEdgeId) || null,
    [edges, selectedEdgeId]
  );

  // Handle node drag from palette
  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();

      const nodeType = event.dataTransfer.getData('application/reactflow') as WorkflowNodeType;

      if (typeof nodeType === 'undefined' || !nodeType) {
        return;
      }

      if (reactFlowWrapper.current) {
        const position = screenToFlowPosition({
          x: event.clientX,
          y: event.clientY,
        });

        addNode(nodeType, position);
      }
    },
    [addNode, screenToFlowPosition]
  );

  // Handle node selection
  const onNodeClick = useCallback((event: React.MouseEvent, node: Node<WorkflowNodeData>) => {
    setSelectedNodeId(node.id);
    setSelectedEdgeId(undefined);
  }, [setSelectedNodeId, setSelectedEdgeId]);

  // Handle edge selection
  const onEdgeClick = useCallback((event: React.MouseEvent, edge: Edge<WorkflowEdgeData>) => {
    setSelectedEdgeId(edge.id);
    setSelectedNodeId(undefined);
  }, [setSelectedEdgeId, setSelectedNodeId]);

  // Handle pane click (deselect)
  const onPaneClick = useCallback(() => {
    setSelectedNodeId(undefined);
    setSelectedEdgeId(undefined);
  }, [setSelectedNodeId, setSelectedEdgeId]);

  // Validation handler
  const handleValidate = useCallback(() => {
    const result = validate();
    setValidationResult(result);
    setShowValidationSnackbar(true);
  }, [validate]);

  // Save handler
  const handleSave = useCallback(async () => {
    if (onSave && !readOnly) {
      setIsSaving(true);
      try {
        await onSave(workflow);
      } catch (error) {
        console.error('Failed to save workflow:', error);
      } finally {
        setIsSaving(false);
      }
    }
  }, [onSave, readOnly, workflow]);

  // Clear workflow
  const handleClear = useCallback(() => {
    setNodes([]);
    setEdges([]);
    setSelectedNodeId(undefined);
    setSelectedEdgeId(undefined);
  }, [setNodes, setEdges, setSelectedNodeId, setSelectedEdgeId]);

  // Load example workflow
  const handleLoadExample = useCallback(
    (exampleKey: string) => {
      const example = exampleWorkflows[exampleKey];
      if (example) {
        setNodes(example.nodes);
        setEdges(example.edges);
        setSelectedNodeId(undefined);
        setSelectedEdgeId(undefined);
      }
      setExampleMenuAnchor(null);
    },
    [setNodes, setEdges, setSelectedNodeId, setSelectedEdgeId]
  );

  // Zoom controls
  const { zoomIn, zoomOut, fitView } = useReactFlow();

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.ctrlKey || event.metaKey) {
        switch (event.key) {
          case 'z':
            event.preventDefault();
            if (event.shiftKey) {
              redo();
            } else {
              undo();
            }
            break;
          case 'c':
            event.preventDefault();
            copySelection();
            break;
          case 'v':
            event.preventDefault();
            pasteFromClipboard();
            break;
          case 'a':
            event.preventDefault();
            selectAll();
            break;
          case 's':
            event.preventDefault();
            handleSave();
            break;
        }
      }
      if (event.key === 'Delete' && (selectedNodeId || selectedEdgeId)) {
        event.preventDefault();
        deleteSelection();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [
    undo,
    redo,
    copySelection,
    pasteFromClipboard,
    selectAll,
    deleteSelection,
    handleSave,
    selectedNodeId,
    selectedEdgeId,
  ]);

  // Auto-save functionality
  useEffect(() => {
    if (workflow.settings?.autoSave && onSave && !readOnly) {
      const interval = setInterval(() => {
        handleSave();
      }, workflow.settings.autoSaveInterval || 30000);

      return () => clearInterval(interval);
    }
  }, [workflow.settings, onSave, readOnly, handleSave]);

  // Handle responsive panel visibility changes
  useEffect(() => {
    if (isMobile) {
      // On mobile, hide all panels and use drawers instead
      setShowNodePalette(false);
      setShowPropertiesPanel(false);
      setShowAnalyticsPanel(false);
    } else {
      // On desktop/tablet, show panels based on original props
      setShowNodePalette(showPalette);
      setShowPropertiesPanel(showProperties);
    }
  }, [isMobile, showPalette, showProperties]);

  // Mobile panel toggle handlers
  const toggleMobileNodePalette = useCallback(() => {
    setMobileNodePaletteOpen(!mobileNodePaletteOpen);
  }, [mobileNodePaletteOpen]);

  const toggleMobileProperties = useCallback(() => {
    setMobilePropertiesOpen(!mobilePropertiesOpen);
  }, [mobilePropertiesOpen]);

  const toggleMobileAnalytics = useCallback(() => {
    setMobileAnalyticsOpen(!mobileAnalyticsOpen);
  }, [mobileAnalyticsOpen]);

  // Enhanced toggle handlers for responsive behavior
  const handleToggleProperties = useCallback(() => {
    if (isMobile) {
      toggleMobileProperties();
    } else {
      setShowPropertiesPanel(!showPropertiesPanel);
    }
  }, [isMobile, showPropertiesPanel, toggleMobileProperties]);

  const handleToggleAnalytics = useCallback(() => {
    if (isMobile) {
      toggleMobileAnalytics();
    } else {
      setShowAnalyticsPanel(!showAnalyticsPanel);
    }
  }, [isMobile, showAnalyticsPanel, toggleMobileAnalytics]);

  const handleToggleNodePalette = useCallback(() => {
    if (isMobile) {
      toggleMobileNodePalette();
    } else {
      setShowNodePalette(!showNodePalette);
    }
  }, [isMobile, showNodePalette, toggleMobileNodePalette]);

  return (
    <Box
      sx={{
        height,
        width,
        display: 'flex',
        flexDirection: 'column',
        bgcolor: 'background.default',
        position: 'relative',
      }}
      className={className}
    >
      {/* Toolbar */}
      {showToolbar && (
        <WorkflowToolbar
          onUndo={undo}
          onRedo={redo}
          onCopy={copySelection}
          onPaste={pasteFromClipboard}
          onValidate={handleValidate}
          onSave={handleSave}
          onClear={handleClear}
          canUndo={canUndo}
          canRedo={canRedo}
          canPaste={!!clipboardData}
          isSaving={isSaving}
          readOnly={readOnly}
          onToggleGrid={() => setSnapToGrid(!snapToGrid)}
          onToggleProperties={handleToggleProperties}
          onToggleAnalytics={handleToggleAnalytics}
          onToggleTemplates={() => setShowTemplatesDialog(!showTemplatesDialog)}
          onZoomIn={zoomIn}
          onZoomOut={zoomOut}
          onFitView={fitView}
          onLoadExamples={(event: React.MouseEvent<HTMLElement>) => setExampleMenuAnchor(event.currentTarget)}
          snapToGrid={snapToGrid}
          showProperties={showPropertiesPanel || mobilePropertiesOpen}
          showAnalytics={showAnalyticsPanel || mobileAnalyticsOpen}
          showTemplates={showTemplatesDialog}
          validationStatus={
            validationResult
              ? validationResult.isValid
                ? 'valid'
                : 'invalid'
              : 'unknown'
          }
          isMobile={isMobile}
          onToggleNodePalette={handleToggleNodePalette}
        />
      )}

      {/* Main editor area */}
      <Box sx={{ flex: 1, display: 'flex', position: 'relative' }}>
        {/* Desktop/Tablet Node Palette */}
        {showNodePalette && !readOnly && !isMobile && (
          <NodePalette 
            onAddNode={addNode} 
            disabled={readOnly}
            width={nodePaletteWidth}
            isCollapsed={isTablet}
          />
        )}

        {/* React Flow Canvas */}
        <Box
          ref={reactFlowWrapper}
          sx={{ 
            flex: 1, 
            position: 'relative',
            marginLeft: showNodePalette && !isMobile ? 0 : 0,
          }}
          onDrop={onDrop}
          onDragOver={onDragOver}
        >
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            onEdgeClick={onEdgeClick}
            onPaneClick={onPaneClick}
            nodeTypes={nodeTypes}
            edgeTypes={edgeTypes}
            snapToGrid={snapToGrid}
            snapGrid={[GRID_SIZE, GRID_SIZE]}
            attributionPosition="bottom-left"
            proOptions={{ hideAttribution: true }}
            fitView
            fitViewOptions={{
              padding: 0.1,
              includeHiddenNodes: false,
            }}
          >
            <Controls />
            {showMinimap && (
              <MiniMap
                style={{
                  backgroundColor: theme.palette.background.paper,
                  border: `1px solid ${theme.palette.divider}`,
                }}
                nodeColor={(node) => {
                  // Color nodes based on type
                  switch (node.type) {
                    case 'start':
                      return '#4caf50';
                    case 'model':
                      return '#2196f3';
                    case 'tool':
                      return '#ff9800';
                    case 'memory':
                      return '#9c27b0';
                    case 'retrieval':
                      return '#00bcd4';
                    case 'conditional':
                      return '#607d8b';
                    case 'loop':
                      return '#795548';
                    case 'variable':
                      return '#3f51b5';
                    case 'errorHandler':
                      return '#f44336';
                    case 'delay':
                      return '#ff5722';
                    case 'transform':
                      return '#8bc34a';
                    case 'api':
                      return '#00e676';
                    default:
                      return '#757575';
                  }
                }}
              />
            )}
            <Background gap={GRID_SIZE} />

            {/* Validation status panel */}
            {validationResult && (
              <Panel position="top-right">
                <Paper
                  sx={{
                    p: 1,
                    minWidth: 200,
                    bgcolor: validationResult.isValid ? 'success.light' : 'error.light',
                    color: validationResult.isValid ? 'success.contrastText' : 'error.contrastText',
                  }}
                >
                  {validationResult.isValid ? (
                    'Workflow is valid ✓'
                  ) : (
                    `${validationResult.errors.length} error(s) found`
                  )}
                </Paper>
              </Panel>
            )}
          </ReactFlow>
        </Box>

        {/* Desktop/Tablet Properties Panel */}
        {showPropertiesPanel && !isMobile && (
          <EnhancedPropertiesPanel
            selectedNode={selectedNode}
            selectedEdge={selectedEdge}
            onNodeUpdate={updateNode}
            onEdgeUpdate={updateEdge}
            onClose={() => setShowPropertiesPanel(false)}
            width={propertiesPanelWidth}
          />
        )}

        {/* Desktop/Tablet Analytics Panel */}
        {showAnalyticsPanel && !isMobile && (
          <Box sx={{ width: analyticsPanelWidth, borderLeft: `1px solid ${theme.palette.divider}` }}>
            <WorkflowAnalytics workflow={workflow} />
          </Box>
        )}
      </Box>

      {/* Mobile Floating Action Button for Node Palette */}
      {isMobile && !readOnly && (
        <Fab
          sx={{
            position: 'fixed',
            bottom: 16,
            left: 16,
            zIndex: 1000,
          }}
          color="primary"
          onClick={toggleMobileNodePalette}
        >
          <MenuIcon />
        </Fab>
      )}

      {/* Mobile Node Palette Drawer */}
      {isMobile && (
        <Drawer
          anchor="left"
          open={mobileNodePaletteOpen}
          onClose={() => setMobileNodePaletteOpen(false)}
          ModalProps={{
            keepMounted: true, // Better mobile performance
          }}
          sx={{
            '& .MuiDrawer-paper': {
              width: Math.min(320, window.innerWidth * 0.85),
              maxWidth: '85vw',
            },
          }}
        >
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              p: 2,
              borderBottom: `1px solid ${theme.palette.divider}`,
            }}
          >
            <Typography variant="h6">Node Palette</Typography>
            <IconButton onClick={() => setMobileNodePaletteOpen(false)}>
              <CloseIcon />
            </IconButton>
          </Box>
          <NodePalette 
            onAddNode={(nodeType, position) => {
              addNode(nodeType, position);
              setMobileNodePaletteOpen(false);
            }} 
            disabled={readOnly}
            width={Math.min(320, window.innerWidth * 0.85)}
            isMobile
          />
        </Drawer>
      )}

      {/* Mobile Properties Drawer */}
      {isMobile && (
        <Drawer
          anchor="right"
          open={mobilePropertiesOpen}
          onClose={() => setMobilePropertiesOpen(false)}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            '& .MuiDrawer-paper': {
              width: Math.min(350, window.innerWidth * 0.9),
              maxWidth: '90vw',
            },
          }}
        >
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              p: 2,
              borderBottom: `1px solid ${theme.palette.divider}`,
            }}
          >
            <Typography variant="h6">Properties</Typography>
            <IconButton onClick={() => setMobilePropertiesOpen(false)}>
              <CloseIcon />
            </IconButton>
          </Box>
          <EnhancedPropertiesPanel
            selectedNode={selectedNode}
            selectedEdge={selectedEdge}
            onNodeUpdate={updateNode}
            onEdgeUpdate={updateEdge}
            onClose={() => setMobilePropertiesOpen(false)}
            width={Math.min(350, window.innerWidth * 0.9)}
            isMobile
          />
        </Drawer>
      )}

      {/* Mobile Analytics Drawer */}
      {isMobile && (
        <Drawer
          anchor="right"
          open={mobileAnalyticsOpen}
          onClose={() => setMobileAnalyticsOpen(false)}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            '& .MuiDrawer-paper': {
              width: Math.min(350, window.innerWidth * 0.9),
              maxWidth: '90vw',
            },
          }}
        >
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              p: 2,
              borderBottom: `1px solid ${theme.palette.divider}`,
            }}
          >
            <Typography variant="h6">Analytics</Typography>
            <IconButton onClick={() => setMobileAnalyticsOpen(false)}>
              <CloseIcon />
            </IconButton>
          </Box>
          <Box sx={{ height: '100%', overflow: 'auto' }}>
            <WorkflowAnalytics workflow={workflow} />
          </Box>
        </Drawer>
      )}

      {/* Example workflows menu */}
      <Menu
        anchorEl={exampleMenuAnchor}
        open={Boolean(exampleMenuAnchor)}
        onClose={() => setExampleMenuAnchor(null)}
      >
        <MenuItem onClick={() => handleLoadExample('simple')}>
          Simple Chat
        </MenuItem>
        <MenuItem onClick={() => handleLoadExample('ragWithTools')}>
          RAG with Tools
        </MenuItem>
        <MenuItem onClick={() => handleLoadExample('parallelProcessing')}>
          Parallel Processing
        </MenuItem>
      </Menu>

      {/* Template Manager Dialog */}
      <TemplateManager
        open={showTemplatesDialog}
        onClose={() => setShowTemplatesDialog(false)}
        onSelectTemplate={(template) => {
          setNodes(template.nodes);
          setEdges(template.edges);
          setSelectedNodeId(undefined);
          setSelectedEdgeId(undefined);
        }}
        currentWorkflow={workflow}
      />

      {/* Validation feedback snackbar */}
      <Snackbar
        open={showValidationSnackbar}
        autoHideDuration={6000}
        onClose={() => setShowValidationSnackbar(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={() => setShowValidationSnackbar(false)}
          severity={validationResult?.isValid ? 'success' : 'error'}
          variant="filled"
        >
          {validationResult?.isValid
            ? 'Workflow is valid!'
            : `Found ${validationResult?.errors.length || 0} error(s) and ${validationResult?.warnings.length || 0} warning(s)`}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default ModernWorkflowEditor;