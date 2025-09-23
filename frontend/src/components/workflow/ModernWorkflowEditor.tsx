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
  Paper,
} from '@mui/material';

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

  // UI state
  const [showPropertiesPanel, setShowPropertiesPanel] = useState(showProperties);
  const [showAnalyticsPanel, setShowAnalyticsPanel] = useState(false);
  const [showTemplatesDialog, setShowTemplatesDialog] = useState(false);
  const [showNodePalette, setShowNodePalette] = useState(showPalette);
  const [exampleMenuAnchor, setExampleMenuAnchor] = useState<null | HTMLElement>(null);
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
  const [showValidationSnackbar, setShowValidationSnackbar] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

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
          onToggleProperties={() => setShowPropertiesPanel(!showPropertiesPanel)}
          onToggleAnalytics={() => setShowAnalyticsPanel(!showAnalyticsPanel)}
          onToggleTemplates={() => setShowTemplatesDialog(!showTemplatesDialog)}
          onZoomIn={zoomIn}
          onZoomOut={zoomOut}
          onFitView={fitView}
          onLoadExamples={(event: React.MouseEvent<HTMLElement>) => setExampleMenuAnchor(event.currentTarget)}
          snapToGrid={snapToGrid}
          showProperties={showPropertiesPanel}
          showAnalytics={showAnalyticsPanel}
          showTemplates={showTemplatesDialog}
          validationStatus={
            validationResult
              ? validationResult.isValid
                ? 'valid'
                : 'invalid'
              : 'unknown'
          }
        />
      )}

      {/* Main editor area */}
      <Box sx={{ flex: 1, display: 'flex', position: 'relative' }}>
        {/* Node Palette */}
        {showNodePalette && !readOnly && (
          <NodePalette onAddNode={addNode} disabled={readOnly} />
        )}

        {/* React Flow Canvas */}
        <Box
          ref={reactFlowWrapper}
          sx={{ flex: 1, position: 'relative' }}
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

        {/* Properties Panel */}
        {showPropertiesPanel && (
          <EnhancedPropertiesPanel
            selectedNode={selectedNode}
            selectedEdge={selectedEdge}
            onNodeUpdate={updateNode}
            onEdgeUpdate={updateEdge}
            onClose={() => setShowPropertiesPanel(false)}
            width={350}
          />
        )}

        {/* Analytics Panel */}
        {showAnalyticsPanel && (
          <Box sx={{ width: 300, borderLeft: `1px solid ${theme.palette.divider}` }}>
            <WorkflowAnalytics workflow={workflow} />
          </Box>
        )}
      </Box>

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