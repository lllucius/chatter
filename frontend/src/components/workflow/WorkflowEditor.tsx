import React, {
  useState,
  useEffect,
  useMemo,
  useCallback,
  useRef,
} from 'react';
import {
  ReactFlow,
  Node,
  Edge,
  Connection,
  useNodesState,
  useEdgesState,
  addEdge,
  Controls,
  ControlButton,
  Background,
  MiniMap,
  NodeTypes,
  EdgeTypes,
  ConnectionMode,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import './WorkflowEditor.css';
import {
  Box,
  Toolbar,
  Button,
  ButtonGroup,
  Typography,
  Menu,
  MenuItem,
  Alert,
  Snackbar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Grid,
  FormControlLabel,
  Switch,
} from '@mui/material';
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
  Error as ErrorIcon,
  GetApp as ExampleIcon,
  GridOn as GridIcon,
  Undo as UndoIcon,
  Redo as RedoIcon,
  ContentCopy as CopyIcon,
  ContentPaste as PasteIcon,
  LibraryBooks as TemplateIcon,
  Map as MiniMapIcon,
  MapOutlined as MiniMapOutlinedIcon,
} from '@mui/icons-material';

// Import custom node components
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
import CustomEdge from './edges/CustomEdge';
import TemplateManager from './TemplateManager';
import { useWorkflowTemplates, WorkflowTemplate } from './useWorkflowTemplates';
import { exampleWorkflows, WorkflowValidator } from './WorkflowExamples';
import {
  workflowDefaultsService,
  WorkflowDefaults,
} from '../../services/workflow-defaults-service';
import { ThemeContext } from '../../App';
import { toastService } from '../../services/toast-service';
import { getSDK } from '../../services/auth-service';
import { handleError } from '../../utils/error-handler';

// Define node types for the workflow
export type WorkflowNodeType =
  | 'start'
  | 'model'
  | 'tool'
  | 'memory'
  | 'retrieval'
  | 'conditional'
  | 'loop'
  | 'variable'
  | 'errorHandler'
  | 'delay';

export interface WorkflowNodeData extends Record<string, unknown> {
  label: string;
  nodeType: WorkflowNodeType;
  config?: Record<string, unknown>;
}

export interface WorkflowEdgeData extends Record<string, unknown> {
  condition?: string;
  label?: string;
}

export interface WorkflowDefinition {
  id?: string;
  nodes: Node<WorkflowNodeData>[];
  edges: Edge<WorkflowEdgeData>[];
  metadata: {
    name: string;
    description: string;
    version: string;
    createdAt: string;
    updatedAt: string;
  };
}

interface WorkflowEditorProps {
  initialWorkflow?: WorkflowDefinition;
  onWorkflowChange?: (workflow: WorkflowDefinition) => void;
  onNodeClick?: (event: React.MouseEvent, node: Node<WorkflowNodeData>) => void;
  onSave?: (workflow: WorkflowDefinition) => void;
  readOnly?: boolean;
  showToolbar?: boolean;
}

// Grid settings for smart positioning
const GRID_SIZE = 20;
const NODE_SPACING = 200;

// Define custom node types
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
};

// Define custom edge types
const edgeTypes: EdgeTypes = {
  custom: CustomEdge,
};

const WorkflowEditor = React.forwardRef<
  {
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
  },
  WorkflowEditorProps
>(
  (
    {
      initialWorkflow,
      onWorkflowChange,
      onNodeClick: onNodeClickProp,
      onSave,
      readOnly = false,
      showToolbar = true,
    },
    ref
  ) => {
    const [nodes, setNodes, onNodesChange] = useNodesState(
      initialWorkflow?.nodes || []
    );
    const [edges, setEdges, onEdgesChange] = useEdgesState(
      initialWorkflow?.edges || []
    );

    const [nodeIdCounter, setNodeIdCounter] = useState(1);
    const [exampleMenuAnchor, setExampleMenuAnchor] =
      useState<null | HTMLElement>(null);
    const [validationResult, setValidationResult] = useState<{
      isValid: boolean;
      errors: string[];
    } | null>(null);
    const [showValidation, setShowValidation] = useState(false);
    const [selectedNode, setSelectedNode] =
      useState<Node<WorkflowNodeData> | null>(null);
    const [snapToGrid, setSnapToGrid] = useState(true);
    const [clipboard, setClipboard] = useState<{
      nodes: Node<WorkflowNodeData>[];
      edges: Edge<WorkflowEdgeData>[];
    } | null>(null);
    const [history, setHistory] = useState<
      { nodes: Node<WorkflowNodeData>[]; edges: Edge<WorkflowEdgeData>[] }[]
    >([]);
    const [historyIndex, setHistoryIndex] = useState(-1);
    const [showTemplateManager, setShowTemplateManager] = useState(false);
    const [workflowDefaults, setWorkflowDefaults] =
      useState<WorkflowDefaults | null>(null);
    const [loadingDefaults, setLoadingDefaults] = useState(false);
    const [showMiniMap, setShowMiniMap] = useState(true);

    // Execution dialog state
    const [showExecutionDialog, setShowExecutionDialog] = useState(false);
    const [executionInputs, setExecutionInputs] = useState<
      Record<string, string>
    >({});
    const [debugMode, setDebugMode] = useState(false);

    // Access theme context for styling
    const { darkMode } = React.useContext(ThemeContext);

    // Load workflow defaults on mount
    useEffect(() => {
      const loadDefaults = async () => {
        setLoadingDefaults(true);
        try {
          const defaults = await workflowDefaultsService.getWorkflowDefaults();
          setWorkflowDefaults(defaults);
        } catch (error) {
          console.error('Failed to load workflow defaults:', error);
        } finally {
          setLoadingDefaults(false);
        }
      };

      loadDefaults();
    }, []);

    // Save current state to history with optional debouncing for property updates
    const saveToHistory = useCallback(
      (immediate = false) => {
        const currentState = { nodes, edges };

        // Don't save duplicate states
        if (
          history[historyIndex] &&
          JSON.stringify(history[historyIndex]) === JSON.stringify(currentState)
        ) {
          return;
        }

        const newHistory = history.slice(0, historyIndex + 1);
        newHistory.push(currentState);

        // Limit history size to prevent memory issues
        if (newHistory.length > 50) {
          newHistory.shift();
        } else {
          setHistoryIndex(newHistory.length - 1);
        }

        setHistory(newHistory);
      },
      [nodes, edges, history, historyIndex]
    );

    // Debounced save for property updates
    const debouncedSaveToHistory = useCallback(() => {
      const timeoutId = setTimeout(() => {
        saveToHistory(false);
      }, 1000); // Save after 1 second of inactivity

      return () => clearTimeout(timeoutId);
    }, [saveToHistory]);

    // Handle node updates from properties panel - use debounced save
    const _handleNodeUpdate = useCallback(
      (nodeId: string, updates: Partial<WorkflowNodeData>) => {
        setNodes((nds) =>
          nds.map((node) =>
            node.id === nodeId
              ? { ...node, data: { ...node.data, ...updates } }
              : node
          )
        );
        // Use debounced save for property changes to avoid creating too many history entries
        debouncedSaveToHistory();
      },
      [setNodes, debouncedSaveToHistory]
    );

    // Handle node selection
    const onNodeClick = useCallback(
      (event: React.MouseEvent, node: Node<WorkflowNodeData>) => {
        setSelectedNode(node);
        // Call external handler if provided
        if (onNodeClickProp) {
          onNodeClickProp(event, node);
        }
      },
      [onNodeClickProp]
    );

    // Smart positioning function
    const getSmartPosition = useCallback(
      (_nodeType: WorkflowNodeType): { x: number; y: number } => {
        const existingNodes = nodes;
        let x = 100;
        let y = 100;

        // Try to place new nodes in a logical flow
        if (existingNodes.length === 0) {
          return { x: 100, y: 200 };
        }

        // Find rightmost node and place new node to its right
        const rightmostNode = existingNodes.reduce((rightmost, node) =>
          node.position.x > rightmost.position.x ? node : rightmost
        );

        x = rightmostNode.position.x + NODE_SPACING;
        y = rightmostNode.position.y;

        // Snap to grid if enabled
        if (snapToGrid) {
          x = Math.round(x / GRID_SIZE) * GRID_SIZE;
          y = Math.round(y / GRID_SIZE) * GRID_SIZE;
        }

        return { x, y };
      },
      [nodes, snapToGrid]
    );
    // Handle new connections
    const onConnect = useCallback(
      (params: Connection) => {
        saveToHistory(true); // Immediate save for structural changes
        const newEdge: Edge<WorkflowEdgeData> = {
          ...params,
          id: `e${edges.length + 1}`,
          type: 'custom',
          animated: true,
        };
        setEdges((eds) => addEdge(newEdge, eds));
      },
      [setEdges, edges.length, saveToHistory]
    );

    // Add new node of specific type
    const addNode = useCallback(
      (nodeType: WorkflowNodeType) => {
        saveToHistory(true); // Immediate save for structural changes
        const position = getSmartPosition(nodeType);
        const newNode: Node<WorkflowNodeData> = {
          id: `${nodeType}-${nodeIdCounter}`,
          type: nodeType,
          position,
          data: {
            label: `${nodeType.charAt(0).toUpperCase() + nodeType.slice(1)} Node`,
            nodeType,
            config: getDefaultNodeConfig(nodeType),
          },
        };

        setNodes((nds) => [...nds, newNode]);
        setNodeIdCounter((counter) => counter + 1);
      },
      [setNodes, nodeIdCounter, saveToHistory, getSmartPosition]
    );

    // Get default configuration for node type
    const getDefaultNodeConfig = useCallback(
      (nodeType: WorkflowNodeType): Record<string, unknown> => {
        // Use dynamic defaults if available
        if (workflowDefaults?.node_types[nodeType]) {
          return workflowDefaults.node_types[nodeType];
        }

        // Fallback to hardcoded defaults
        switch (nodeType) {
          case 'start':
            return { isEntryPoint: true };
          case 'model':
            return {
              systemMessage: '',
              temperature: 0.7,
              maxTokens: 1000,
              model: 'gpt-4',
            };
          case 'tool':
            return { tools: [], parallel: false };
          case 'memory':
            return { enabled: true, window: 20, memoryType: 'conversation' };
          case 'retrieval':
            return { collection: '', topK: 5, threshold: 0.7 };
          case 'conditional':
            return { condition: '', branches: {} };
          case 'loop':
            return { maxIterations: 10, condition: '', breakCondition: '' };
          case 'variable':
            return {
              operation: 'set',
              variableName: '',
              value: '',
              scope: 'workflow',
            };
          case 'errorHandler':
            return {
              retryCount: 3,
              fallbackAction: 'continue',
              logErrors: true,
            };
          case 'delay':
            return { duration: 1, type: 'fixed', unit: 'seconds' };
          default:
            return {};
        }
      },
      [workflowDefaults]
    );

    // Create current workflow definition
    const currentWorkflow = useMemo(
      (): WorkflowDefinition => ({
        nodes,
        edges,
        metadata: {
          name: initialWorkflow?.metadata?.name || 'Untitled Workflow',
          description: initialWorkflow?.metadata?.description || '',
          version: '1.0.0',
          createdAt:
            initialWorkflow?.metadata?.createdAt || new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
      }),
      [nodes, edges, initialWorkflow]
    );

    // Undo functionality
    const handleUndo = useCallback(() => {
      if (historyIndex > 0) {
        const previousState = history[historyIndex - 1];
        setNodes(previousState.nodes);
        setEdges(previousState.edges);
        setHistoryIndex(historyIndex - 1);
      }
    }, [history, historyIndex, setNodes, setEdges]);

    // Redo functionality
    const handleRedo = useCallback(() => {
      if (historyIndex < history.length - 1) {
        const nextState = history[historyIndex + 1];
        setNodes(nextState.nodes);
        setEdges(nextState.edges);
        setHistoryIndex(historyIndex + 1);
      }
    }, [history, historyIndex, setNodes, setEdges]);

    // Copy functionality
    const handleCopy = useCallback(() => {
      if (selectedNode) {
        const selectedEdges = edges.filter(
          (edge) =>
            edge.source === selectedNode.id || edge.target === selectedNode.id
        );
        setClipboard({ nodes: [selectedNode], edges: selectedEdges });
      }
    }, [selectedNode, edges]);

    // Paste functionality
    const handlePaste = useCallback(() => {
      if (clipboard) {
        saveToHistory();
        const nodeIdMap = new Map<string, string>();

        // Create new nodes with new IDs
        const newNodes = clipboard.nodes.map((node) => {
          const newId = `${node.type}-${nodeIdCounter + nodes.length}`;
          nodeIdMap.set(node.id, newId);
          return {
            ...node,
            id: newId,
            position: {
              x: node.position.x + 50,
              y: node.position.y + 50,
            },
          };
        });

        // Create new edges with updated IDs
        const newEdges = clipboard.edges
          .filter(
            (edge) => nodeIdMap.has(edge.source) && nodeIdMap.has(edge.target)
          )
          .map((edge) => ({
            ...edge,
            id: `e${edges.length + newNodes.length}`,
            source: nodeIdMap.get(edge.source)!,
            target: nodeIdMap.get(edge.target)!,
          }));

        setNodes((nds) => [...nds, ...newNodes]);
        setEdges((eds) => [...eds, ...newEdges]);
        setNodeIdCounter((counter) => counter + newNodes.length);
      }
    }, [
      clipboard,
      nodes,
      edges,
      nodeIdCounter,
      setNodes,
      setEdges,
      saveToHistory,
    ]);

    // Delete selected node
    const handleDeleteSelected = useCallback(() => {
      if (selectedNode) {
        saveToHistory(true); // Immediate save for structural changes
        setNodes((nds) => nds.filter((node) => node.id !== selectedNode.id));
        setEdges((eds) =>
          eds.filter(
            (edge) =>
              edge.source !== selectedNode.id && edge.target !== selectedNode.id
          )
        );
        setSelectedNode(null);
      }
    }, [selectedNode, setNodes, setEdges, saveToHistory]);

    // Handle save
    const handleSave = useCallback(() => {
      if (onSave) {
        onSave(currentWorkflow);
      }
    }, [onSave, currentWorkflow]);

    // Keyboard shortcuts
    React.useEffect(() => {
      const handleKeyDown = (event: KeyboardEvent) => {
        if (event.ctrlKey || event.metaKey) {
          switch (event.key) {
            case 'z':
              event.preventDefault();
              if (event.shiftKey) {
                handleRedo();
              } else {
                handleUndo();
              }
              break;
            case 'c':
              event.preventDefault();
              handleCopy();
              break;
            case 'v':
              event.preventDefault();
              handlePaste();
              break;
            case 's':
              event.preventDefault();
              handleSave();
              break;
          }
        }
        if (event.key === 'Delete' && selectedNode) {
          event.preventDefault();
          handleDeleteSelected();
        }
      };

      document.addEventListener('keydown', handleKeyDown);
      return () => document.removeEventListener('keydown', handleKeyDown);
    }, [
      selectedNode,
      handleCopy,
      handleDeleteSelected,
      handlePaste,
      handleRedo,
      handleSave,
      handleUndo,
    ]);

    // Notify parent of changes
    React.useEffect(() => {
      if (onWorkflowChange) {
        onWorkflowChange(currentWorkflow);
      }
    }, [currentWorkflow, onWorkflowChange]);

    // Clear workflow
    const handleClear = useCallback(() => {
      saveToHistory();
      setNodes([]);
      setEdges([]);
      setSelectedNode(null);
    }, [setNodes, setEdges, saveToHistory]);

    // Load example workflow
    const handleLoadExample = useCallback(
      (exampleKey: string) => {
        const example = exampleWorkflows[exampleKey];
        if (example) {
          saveToHistory();
          setNodes(example.nodes);
          setEdges(example.edges);
        }
        setExampleMenuAnchor(null);
      },
      [setNodes, setEdges, saveToHistory]
    );

    // Load template workflow
    const handleLoadTemplate = useCallback(
      (workflow: WorkflowDefinition) => {
        saveToHistory();
        setNodes(workflow.nodes);
        setEdges(workflow.edges);
        setSelectedNode(null);
      },
      [setNodes, setEdges, saveToHistory]
    );

    // Save as template
    const handleSaveAsTemplate = useCallback(
      async (templateData: Omit<WorkflowTemplate, 'id' | 'createdAt'>) => {
        try {
          // First create a workflow definition if we don't have one
          let workflowDefinitionId = currentWorkflow.id;

          if (!workflowDefinitionId) {
            const workflowData = {
              name: templateData.name,
              description: templateData.description || undefined,
              nodes: currentWorkflow.nodes.map((node) => ({
                id: node.id,
                type: node.type || 'unknown', // Ensure type is always a string
                position: node.position,
                data: node.data,
              })),
              edges: currentWorkflow.edges.map((edge) => ({
                id: edge.id,
                source: edge.source,
                target: edge.target,
                type: edge.type || 'default', // Ensure type is always a string
                data: edge.data || {},
                sourceHandle: edge.sourceHandle,
                targetHandle: edge.targetHandle,
              })),
              metadata: {
                ...currentWorkflow.metadata,
                name: templateData.name,
                description: templateData.description || '',
              },
            };

            const workflowResponse =
              await getSDK().workflows.createWorkflowDefinitionApiV1WorkflowsDefinitions(
                workflowData
              );
            workflowDefinitionId = workflowResponse.id;
          }

          // Now create the template
          const templateCreateData = {
            name: templateData.name,
            description: templateData.description,
            category: templateData.category || 'custom',
            tags: templateData.tags || [],
            workflow_definition_id: workflowDefinitionId,
          };

          await getSDK().workflows.createWorkflowTemplateApiV1WorkflowsTemplates(
            templateCreateData
          );

          toastService.success(
            `Template "${templateData.name}" saved successfully`
          );
          setShowTemplateManager(false);
        } catch (error) {
          handleError(error, {
            source: 'WorkflowEditor.handleSaveAsTemplate',
            operation: 'save template',
          });
        }
      },
      [currentWorkflow]
    );

    // Validate workflow
    const handleValidate = useCallback(() => {
      const result = WorkflowValidator.validate(currentWorkflow);
      setValidationResult(result);

      // Use toast notifications instead of snackbar
      if (result.isValid) {
        toastService.success('Workflow is valid!');
      } else {
        toastService.error(
          `Validation failed: ${result.errors.join(', ')}`,
          'Workflow Validation',
          {
            autoClose: 8000, // Longer duration for detailed error messages
          }
        );
      }
    }, [currentWorkflow]);

    // Toggle grid
    const handleToggleGrid = useCallback(() => {
      setSnapToGrid(!snapToGrid);
    }, [snapToGrid]);

    // Toggle MiniMap
    const handleToggleMiniMap = useCallback(() => {
      setShowMiniMap(!showMiniMap);
    }, [showMiniMap]);

    // Execute workflow
    const handleExecute = useCallback(() => {
      // First validate the workflow
      const result = WorkflowValidator.validate(currentWorkflow);
      if (!result.isValid) {
        toastService.error(
          `Cannot execute invalid workflow: ${result.errors.join(', ')}`,
          'Execution Error'
        );
        return;
      }

      // Check if the workflow has input parameters
      const hasInputParams = currentWorkflow.nodes.some(
        (node) => node.type === 'start' && node.data?.config?.requiresInput
      );

      if (hasInputParams || currentWorkflow.nodes.length > 0) {
        // Reset and show execution input dialog
        setExecutionInputs({});
        setShowExecutionDialog(true);
      } else {
        // Execute directly for simple workflows
        executeWorkflow({});
      }
    }, [currentWorkflow]);

    // Execute workflow with inputs
    const executeWorkflow = useCallback(
      async (inputs: Record<string, string>) => {
        try {
          // TODO: Implement actual workflow execution API call
          // For demonstration purposes, include debug mode in the execution
          const inputKeys = Object.keys(inputs);
          const debugStatus = debugMode ? ' (Debug Mode Enabled)' : '';
          const inputSummary =
            inputKeys.length > 0 ? ` with inputs: ${inputKeys.join(', ')}` : '';

          toastService.success(
            `Workflow execution started${inputSummary}${debugStatus}!`
          );
          setShowExecutionDialog(false);

          // Log debug information if debug mode is enabled
          if (debugMode) {
            console.log('Debug Mode Enabled - Execution Details:', {
              workflow: currentWorkflow,
              inputs,
              debugMode,
              timestamp: new Date().toISOString(),
            });
          }
        } catch (error) {
          toastService.error('Failed to execute workflow', 'Execution Error');
          console.error('Workflow execution error:', error);
        }
      },
      [debugMode, currentWorkflow]
    );

    // Debug workflow
    const handleDebug = useCallback(() => {
      // First validate the workflow
      const result = WorkflowValidator.validate(currentWorkflow);
      if (!result.isValid) {
        toastService.error(
          `Cannot debug invalid workflow: ${result.errors.join(', ')}`,
          'Debug Error'
        );
        return;
      }

      // TODO: Implement workflow debugging
      toastService.info('Debug mode activated!');
    }, [currentWorkflow]);

    // Expose methods through ref
    React.useImperativeHandle(
      ref,
      () => ({
        addNode,
        handleUndo,
        handleRedo,
        handleCopy,
        handlePaste,
        handleSave,
        handleClear,
        handleToggleGrid,
        handleToggleMiniMap,
        handleValidate,
        handleExecute,
        handleDebug,
        loadExample: handleLoadExample,
        showTemplateManager: () => setShowTemplateManager(true),
        deleteSelected: handleDeleteSelected,
        updateNode: _handleNodeUpdate,
      }),
      [
        addNode,
        handleUndo,
        handleRedo,
        handleCopy,
        handlePaste,
        handleSave,
        handleClear,
        handleToggleGrid,
        handleToggleMiniMap,
        handleValidate,
        handleExecute,
        handleDebug,
        handleLoadExample,
        handleDeleteSelected,
        _handleNodeUpdate,
      ]
    );

    return (
      <Box sx={{ height: '100%', width: '100%', display: 'flex' }}>
        {/* Main Editor Area */}
        <Box
          sx={{
            flex: 1,
            border: '1px solid #e0e0e0',
            borderRadius: 1,
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          {/* Toolbar */}
          {showToolbar && (
            <Toolbar
              sx={{
                bgcolor: 'background.paper',
                borderBottom: '1px solid #e0e0e0',
                minHeight: '48px !important',
              }}
            >
              <Typography variant="h6" sx={{ flexGrow: 1 }}>
                Workflow Editor
              </Typography>

              {!readOnly && (
                <>
                  {/* Node Type Buttons */}
                  <ButtonGroup size="small" sx={{ mr: 2 }}>
                    <Button
                      startIcon={<StartIcon />}
                      onClick={() => addNode('start')}
                      variant="outlined"
                    >
                      Start
                    </Button>
                    <Button
                      startIcon={<ModelIcon />}
                      onClick={() => addNode('model')}
                      variant="outlined"
                    >
                      Model
                    </Button>
                    <Button
                      startIcon={<ToolIcon />}
                      onClick={() => addNode('tool')}
                      variant="outlined"
                    >
                      Tool
                    </Button>
                    <Button
                      startIcon={<MemoryIcon />}
                      onClick={() => addNode('memory')}
                      variant="outlined"
                    >
                      Memory
                    </Button>
                    <Button
                      startIcon={<RetrievalIcon />}
                      onClick={() => addNode('retrieval')}
                      variant="outlined"
                    >
                      Retrieval
                    </Button>
                    <Button
                      startIcon={<ConditionalIcon />}
                      onClick={() => addNode('conditional')}
                      variant="outlined"
                    >
                      Conditional
                    </Button>
                  </ButtonGroup>

                  {/* Advanced Node Types */}
                  <ButtonGroup size="small" sx={{ mr: 2 }}>
                    <Button
                      startIcon={<LoopIcon />}
                      onClick={() => addNode('loop')}
                      variant="outlined"
                      color="secondary"
                    >
                      Loop
                    </Button>
                    <Button
                      startIcon={<VariableIcon />}
                      onClick={() => addNode('variable')}
                      variant="outlined"
                      color="secondary"
                    >
                      Variable
                    </Button>
                    <Button
                      startIcon={<ErrorHandlerIcon />}
                      onClick={() => addNode('errorHandler')}
                      variant="outlined"
                      color="secondary"
                    >
                      Error
                    </Button>
                    <Button
                      startIcon={<DelayIcon />}
                      onClick={() => addNode('delay')}
                      variant="outlined"
                      color="secondary"
                    >
                      Delay
                    </Button>
                  </ButtonGroup>

                  {/* Edit Controls */}
                  <ButtonGroup size="small" sx={{ mr: 2 }}>
                    <Button
                      onClick={handleUndo}
                      disabled={historyIndex <= 0}
                      variant="outlined"
                      startIcon={<UndoIcon />}
                      title="Undo (Ctrl+Z)"
                    >
                      Undo
                    </Button>
                    <Button
                      onClick={handleRedo}
                      disabled={historyIndex >= history.length - 1}
                      variant="outlined"
                      startIcon={<RedoIcon />}
                      title="Redo (Ctrl+Shift+Z)"
                    >
                      Redo
                    </Button>
                    <Button
                      onClick={handleCopy}
                      disabled={!selectedNode}
                      variant="outlined"
                      startIcon={<CopyIcon />}
                      title="Copy (Ctrl+C)"
                    >
                      Copy
                    </Button>
                    <Button
                      onClick={handlePaste}
                      disabled={!clipboard}
                      variant="outlined"
                      startIcon={<PasteIcon />}
                      title="Paste (Ctrl+V)"
                    >
                      Paste
                    </Button>
                  </ButtonGroup>

                  {/* Utility Controls */}
                  <ButtonGroup size="small" sx={{ mr: 2 }}>
                    <Button
                      onClick={() => setSnapToGrid(!snapToGrid)}
                      variant={snapToGrid ? 'contained' : 'outlined'}
                      startIcon={<GridIcon />}
                      title="Toggle Grid Snap"
                    >
                      Grid
                    </Button>
                    <Button
                      onClick={handleValidate}
                      variant="outlined"
                      startIcon={
                        validationResult?.isValid ? (
                          <ValidIcon />
                        ) : (
                          <ErrorIcon />
                        )
                      }
                      color={
                        validationResult?.isValid === false
                          ? 'error'
                          : 'primary'
                      }
                    >
                      Validate
                    </Button>
                  </ButtonGroup>

                  {/* Workflow Controls */}
                  <ButtonGroup size="small">
                    <Button
                      onClick={() => setShowTemplateManager(true)}
                      variant="outlined"
                      startIcon={<TemplateIcon />}
                    >
                      Templates
                    </Button>
                    <Button
                      onClick={(e) => setExampleMenuAnchor(e.currentTarget)}
                      variant="outlined"
                      startIcon={<ExampleIcon />}
                    >
                      Examples
                    </Button>
                    <Button onClick={handleSave} variant="contained">
                      Save
                    </Button>
                    <Button
                      onClick={handleClear}
                      variant="outlined"
                      color="error"
                    >
                      Clear
                    </Button>
                  </ButtonGroup>
                </>
              )}
            </Toolbar>
          )}

          {/* React Flow Canvas */}
          <Box
            sx={{
              height: showToolbar ? 'calc(100% - 48px)' : '100%',
              width: '100%', // Ensure width is explicitly set
              overflow: 'hidden', // Prevent scrolling on container
            }}
            data-theme={darkMode ? 'dark' : 'light'}
          >
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
              onNodeClick={onNodeClick}
              nodeTypes={nodeTypes}
              edgeTypes={edgeTypes}
              connectionMode={ConnectionMode.Loose}
              fitView
              snapToGrid={snapToGrid}
              snapGrid={[GRID_SIZE, GRID_SIZE]}
              attributionPosition="bottom-left"
              proOptions={{ hideAttribution: true }}
              panOnDrag={true} // Enable infinite panning
              panOnScroll={false} // Disable scroll-to-pan to prevent conflicts
              zoomOnScroll={false} // Disable zoom on scroll for cleaner interaction
            >
              <Controls>
                <ControlButton
                  onClick={handleToggleMiniMap}
                  title={showMiniMap ? 'Hide MiniMap' : 'Show MiniMap'}
                >
                  {showMiniMap ? (
                    <MiniMapIcon sx={{ fontSize: 16 }} />
                  ) : (
                    <MiniMapOutlinedIcon sx={{ fontSize: 16 }} />
                  )}
                </ControlButton>
              </Controls>
              {showMiniMap && <MiniMap />}
              <Background gap={GRID_SIZE} />
            </ReactFlow>
          </Box>
        </Box>

        {/* Dialogs and Menus */}
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
          open={showTemplateManager}
          onClose={() => setShowTemplateManager(false)}
          onSelectTemplate={handleLoadTemplate}
          currentWorkflow={currentWorkflow}
          onSaveAsTemplate={handleSaveAsTemplate}
        />

        {/* Workflow Execution Input Dialog */}
        <Dialog
          open={showExecutionDialog}
          onClose={() => setShowExecutionDialog(false)}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>Workflow Execution - Input Parameters</DialogTitle>
          <DialogContent>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Provide input parameters for workflow execution:
            </Typography>
            <Grid container spacing={2}>
              <Grid size={12}>
                <TextField
                  fullWidth
                  label="User Input"
                  multiline
                  rows={3}
                  value={executionInputs.userInput || ''}
                  onChange={(e) =>
                    setExecutionInputs((prev) => ({
                      ...prev,
                      userInput: e.target.value,
                    }))
                  }
                  placeholder="Enter your input for the workflow..."
                  helperText="This will be passed to the workflow as the initial input"
                />
              </Grid>
              <Grid size={12}>
                <TextField
                  fullWidth
                  label="Additional Parameters (JSON)"
                  multiline
                  rows={3}
                  value={executionInputs.parameters || ''}
                  onChange={(e) =>
                    setExecutionInputs((prev) => ({
                      ...prev,
                      parameters: e.target.value,
                    }))
                  }
                  placeholder='{"key": "value", "setting": "option"}'
                  helperText="Optional: Additional parameters as JSON object"
                />
              </Grid>
              <Grid size={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={debugMode}
                      onChange={(e) => setDebugMode(e.target.checked)}
                      name="debugMode"
                      color="primary"
                    />
                  }
                  label="Enable Debug Mode"
                />
                <Typography
                  variant="caption"
                  display="block"
                  color="text.secondary"
                >
                  Capture detailed execution logs and debugging information
                </Typography>
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setShowExecutionDialog(false)}>
              Cancel
            </Button>
            <Button
              onClick={() => executeWorkflow(executionInputs)}
              variant="contained"
              startIcon={<StartIcon />}
            >
              Execute Workflow
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    );
  }
);

WorkflowEditor.displayName = 'WorkflowEditor';

export default WorkflowEditor;
