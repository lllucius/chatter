import React, { useCallback, useState, useMemo } from 'react';
import {
  ReactFlow,
  Node,
  Edge,
  Connection,
  useNodesState,
  useEdgesState,
  addEdge,
  Controls,
  Background,
  MiniMap,
  NodeTypes,
  EdgeTypes,
  ConnectionMode,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
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
  FormControl,
  InputLabel,
  Select,
} from '@mui/material';
import {
  PlayArrow as StartIcon,
  SmartToy as ModelIcon,
  Build as ToolIcon,
  Memory as MemoryIcon,
  Search as RetrievalIcon,
  CallSplit as ConditionalIcon,
  CheckCircle as ValidIcon,
  Error as ErrorIcon,
  GetApp as ExampleIcon,
} from '@mui/icons-material';

// Import custom node components
import StartNode from './nodes/StartNode';
import ModelNode from './nodes/ModelNode';
import ToolNode from './nodes/ToolNode';
import MemoryNode from './nodes/MemoryNode';
import RetrievalNode from './nodes/RetrievalNode';
import ConditionalNode from './nodes/ConditionalNode';
import CustomEdge from './edges/CustomEdge';
import { exampleWorkflows, WorkflowValidator } from './WorkflowExamples';

// Define node types for the workflow
export type WorkflowNodeType = 
  | 'start'
  | 'model'
  | 'tool'
  | 'memory'
  | 'retrieval'
  | 'conditional';

export interface WorkflowNodeData extends Record<string, unknown> {
  label: string;
  nodeType: WorkflowNodeType;
  config?: Record<string, any>;
}

export interface WorkflowEdgeData extends Record<string, unknown> {
  condition?: string;
  label?: string;
}

export interface WorkflowDefinition {
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
  onSave?: (workflow: WorkflowDefinition) => void;
  readOnly?: boolean;
}

// Define custom node types
const nodeTypes: NodeTypes = {
  start: StartNode,
  model: ModelNode,
  tool: ToolNode,
  memory: MemoryNode,
  retrieval: RetrievalNode,
  conditional: ConditionalNode,
};

// Define custom edge types
const edgeTypes: EdgeTypes = {
  custom: CustomEdge,
};

const WorkflowEditor: React.FC<WorkflowEditorProps> = ({
  initialWorkflow,
  onWorkflowChange,
  onSave,
  readOnly = false,
}) => {
  const [nodes, setNodes, onNodesChange] = useNodesState(
    initialWorkflow?.nodes || []
  );
  const [edges, setEdges, onEdgesChange] = useEdgesState(
    initialWorkflow?.edges || []
  );

  const [nodeIdCounter, setNodeIdCounter] = useState(1);
  const [exampleMenuAnchor, setExampleMenuAnchor] = useState<null | HTMLElement>(null);
  const [validationResult, setValidationResult] = useState<{ isValid: boolean; errors: string[] } | null>(null);
  const [showValidation, setShowValidation] = useState(false);

  // Handle new connections
  const onConnect = useCallback(
    (params: Connection) => {
      const newEdge = {
        ...params,
        id: `e${edges.length + 1}`,
        type: 'custom',
        animated: true,
      };
      setEdges((eds) => addEdge(newEdge, eds));
    },
    [setEdges, edges.length]
  );

  // Add new node of specific type
  const addNode = useCallback(
    (nodeType: WorkflowNodeType) => {
      const newNode: Node<WorkflowNodeData> = {
        id: `${nodeType}-${nodeIdCounter}`,
        type: nodeType,
        position: { x: Math.random() * 400, y: Math.random() * 400 },
        data: {
          label: `${nodeType.charAt(0).toUpperCase() + nodeType.slice(1)} Node`,
          nodeType,
          config: getDefaultNodeConfig(nodeType),
        },
      };
      
      setNodes((nds) => [...nds, newNode]);
      setNodeIdCounter((counter) => counter + 1);
    },
    [setNodes, nodeIdCounter]
  );

  // Get default configuration for node type
  const getDefaultNodeConfig = (nodeType: WorkflowNodeType): Record<string, any> => {
    switch (nodeType) {
      case 'start':
        return { isEntryPoint: true };
      case 'model':
        return { systemMessage: '', temperature: 0.7, maxTokens: 1000 };
      case 'tool':
        return { tools: [], parallel: false };
      case 'memory':
        return { enabled: true, window: 20 };
      case 'retrieval':
        return { collection: '', topK: 5 };
      case 'conditional':
        return { condition: '', branches: {} };
      default:
        return {};
    }
  };

  // Create current workflow definition
  const currentWorkflow = useMemo((): WorkflowDefinition => ({
    nodes,
    edges,
    metadata: {
      name: initialWorkflow?.metadata?.name || 'Untitled Workflow',
      description: initialWorkflow?.metadata?.description || '',
      version: '1.0.0',
      createdAt: initialWorkflow?.metadata?.createdAt || new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
  }), [nodes, edges, initialWorkflow]);

  // Notify parent of changes
  React.useEffect(() => {
    if (onWorkflowChange) {
      onWorkflowChange(currentWorkflow);
    }
  }, [currentWorkflow, onWorkflowChange]);

  // Handle save
  const handleSave = useCallback(() => {
    if (onSave) {
      onSave(currentWorkflow);
    }
  }, [onSave, currentWorkflow]);

  // Clear workflow
  const handleClear = useCallback(() => {
    setNodes([]);
    setEdges([]);
  }, [setNodes, setEdges]);

  // Load example workflow
  const handleLoadExample = useCallback((exampleKey: string) => {
    const example = exampleWorkflows[exampleKey];
    if (example) {
      setNodes(example.nodes);
      setEdges(example.edges);
    }
    setExampleMenuAnchor(null);
  }, [setNodes, setEdges]);

  // Validate workflow
  const handleValidate = useCallback(() => {
    const result = WorkflowValidator.validate(currentWorkflow);
    setValidationResult(result);
    setShowValidation(true);
  }, [currentWorkflow]);

  return (
    <Box sx={{ height: '600px', width: '100%', border: '1px solid #e0e0e0', borderRadius: 1 }}>
      {/* Toolbar */}
      <Toolbar sx={{ bgcolor: 'background.paper', borderBottom: '1px solid #e0e0e0' }}>
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          Workflow Editor
        </Typography>
        
        {!readOnly && (
          <>
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

            <ButtonGroup size="small">
              <Button 
                onClick={handleValidate}
                variant="outlined"
                startIcon={validationResult?.isValid ? <ValidIcon /> : <ErrorIcon />}
                color={validationResult?.isValid === false ? 'error' : 'primary'}
              >
                Validate
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
              <Button onClick={handleClear} variant="outlined" color="error">
                Clear
              </Button>
            </ButtonGroup>
          </>
        )}
      </Toolbar>

      {/* React Flow Canvas */}
      <Box sx={{ height: 'calc(100% - 64px)' }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          nodeTypes={nodeTypes}
          edgeTypes={edgeTypes}
          connectionMode={ConnectionMode.Loose}
          fitView
          attributionPosition="bottom-left"
          proOptions={{ hideAttribution: true }}
        >
          <Controls />
          <MiniMap />
          <Background />
        </ReactFlow>
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

      {/* Validation feedback */}
      <Snackbar 
        open={showValidation} 
        autoHideDuration={6000} 
        onClose={() => setShowValidation(false)}
      >
        <Alert 
          onClose={() => setShowValidation(false)} 
          severity={validationResult?.isValid ? 'success' : 'error'}
        >
          {validationResult?.isValid 
            ? 'Workflow is valid!' 
            : `Validation errors: ${validationResult?.errors.join(', ')}`
          }
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default WorkflowEditor;