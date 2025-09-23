import { useState, useCallback, useRef, useEffect } from 'react';
import { Node, Edge, useNodesState, useEdgesState, addEdge, Connection } from '@xyflow/react';
import { 
  WorkflowDefinition, 
  WorkflowNodeData, 
  WorkflowEdgeData, 
  WorkflowNodeType, 
  UseWorkflowEditor,
  ValidationResult,
  EditorState,
  ClipboardData,
} from '../types';
import { nodeDefinitions } from '../NodePalette';

const GRID_SIZE = 20;
const NODE_SPACING = 200;
const MAX_HISTORY = 50;

interface WorkflowHistory {
  nodes: Node<WorkflowNodeData>[];
  edges: Edge<WorkflowEdgeData>[];
  timestamp: number;
}

export const useWorkflowEditor = (
  initialWorkflow?: WorkflowDefinition,
  onWorkflowChange?: (workflow: WorkflowDefinition) => void
): UseWorkflowEditor => {
  // Core React Flow state
  const [nodes, setNodes, onNodesChange] = useNodesState(
    initialWorkflow?.nodes || []
  );
  const [edges, setEdges, onEdgesChange] = useEdgesState(
    initialWorkflow?.edges || []
  );

  // Editor state
  const [nodeIdCounter, setNodeIdCounter] = useState(1);
  const [selectedNodeId, setSelectedNodeId] = useState<string | undefined>();
  const [selectedEdgeId, setSelectedEdgeId] = useState<string | undefined>();
  const [clipboardData, setClipboardData] = useState<ClipboardData | null>(null);
  const [snapToGrid, setSnapToGrid] = useState(true);

  // History management
  const [history, setHistory] = useState<WorkflowHistory[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const historyRef = useRef<WorkflowHistory[]>([]);
  const historyIndexRef = useRef(-1);

  // Update refs when state changes
  useEffect(() => {
    historyRef.current = history;
    historyIndexRef.current = historyIndex;
  }, [history, historyIndex]);

  // Save current state to history
  const saveToHistory = useCallback(() => {
    const currentState: WorkflowHistory = {
      nodes: [...nodes],
      edges: [...edges],
      timestamp: Date.now(),
    };

    setHistory(prev => {
      // Remove any history items after current index
      const newHistory = prev.slice(0, historyIndexRef.current + 1);
      
      // Add new state
      newHistory.push(currentState);
      
      // Limit history size
      if (newHistory.length > MAX_HISTORY) {
        newHistory.shift();
        return newHistory;
      }
      
      return newHistory;
    });

    setHistoryIndex(prev => Math.min(prev + 1, MAX_HISTORY - 1));
  }, [nodes, edges]);

  // Initialize history with initial state
  useEffect(() => {
    if (history.length === 0) {
      saveToHistory();
    }
  }, []); // Only run once on mount

  // Create current workflow object
  const workflow: WorkflowDefinition = {
    id: initialWorkflow?.id,
    nodes,
    edges,
    metadata: initialWorkflow?.metadata || {
      name: 'Untitled Workflow',
      description: '',
      version: '1.0.0',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
    version: initialWorkflow?.version || '1.0.0',
    variables: initialWorkflow?.variables || {},
    settings: initialWorkflow?.settings || {
      autoSave: true,
      autoSaveInterval: 30000,
      enableValidation: true,
      enableAnalytics: true,
    },
  };

  // Notify parent of changes
  useEffect(() => {
    if (onWorkflowChange) {
      onWorkflowChange(workflow);
    }
  }, [nodes, edges, onWorkflowChange]);

  // Smart positioning for new nodes
  const getSmartPosition = useCallback(
    (nodeType: WorkflowNodeType): { x: number; y: number } => {
      if (nodes.length === 0) {
        return { x: 100, y: 200 };
      }

      // Find rightmost node and place new node to its right
      const rightmostNode = nodes.reduce((rightmost, node) =>
        node.position.x > rightmost.position.x ? node : rightmost
      );

      let x = rightmostNode.position.x + NODE_SPACING;
      let y = rightmostNode.position.y;

      // Check for overlapping nodes and adjust position
      const hasOverlap = (testX: number, testY: number) =>
        nodes.some(node => 
          Math.abs(node.position.x - testX) < 150 && 
          Math.abs(node.position.y - testY) < 100
        );

      while (hasOverlap(x, y)) {
        y += 120;
        if (y > 800) {
          y = 100;
          x += NODE_SPACING;
        }
      }

      // Snap to grid if enabled
      if (snapToGrid) {
        x = Math.round(x / GRID_SIZE) * GRID_SIZE;
        y = Math.round(y / GRID_SIZE) * GRID_SIZE;
      }

      return { x, y };
    },
    [nodes, snapToGrid]
  );

  // Get default configuration for node type
  const getDefaultNodeConfig = useCallback((nodeType: WorkflowNodeType) => {
    const definition = nodeDefinitions.find(def => def.type === nodeType);
    if (!definition) return {};

    const config: Record<string, unknown> = {};
    definition.properties.forEach(prop => {
      if (prop.default !== undefined) {
        config[prop.name] = prop.default;
      }
    });

    return config;
  }, []);

  // Update workflow metadata
  const updateWorkflow = useCallback((updates: Partial<WorkflowDefinition>) => {
    if (updates.nodes) {
      setNodes(updates.nodes);
    }
    if (updates.edges) {
      setEdges(updates.edges);
    }
    // Metadata and other properties would be handled by parent component
  }, [setNodes, setEdges]);

  // Add new node
  const addNode = useCallback(
    (nodeType: WorkflowNodeType, position?: { x: number; y: number }) => {
      saveToHistory();
      
      const nodePosition = position || getSmartPosition(nodeType);
      const definition = nodeDefinitions.find(def => def.type === nodeType);
      
      const newNode: Node<WorkflowNodeData> = {
        id: `${nodeType}-${nodeIdCounter}`,
        type: nodeType,
        position: nodePosition,
        data: {
          label: definition?.label || `${nodeType.charAt(0).toUpperCase() + nodeType.slice(1)} Node`,
          nodeType,
          config: getDefaultNodeConfig(nodeType),
          description: definition?.description || '',
        },
      };

      setNodes(nds => [...nds, newNode]);
      setNodeIdCounter(counter => counter + 1);
      setSelectedNodeId(newNode.id);
    },
    [saveToHistory, getSmartPosition, getDefaultNodeConfig, nodeIdCounter, setNodes]
  );

  // Update node
  const updateNode = useCallback(
    (nodeId: string, updates: Partial<WorkflowNodeData>) => {
      setNodes(nds =>
        nds.map(node =>
          node.id === nodeId
            ? { ...node, data: { ...node.data, ...updates } }
            : node
        )
      );
    },
    [setNodes]
  );

  // Delete node
  const deleteNode = useCallback(
    (nodeId: string) => {
      saveToHistory();
      setNodes(nds => nds.filter(node => node.id !== nodeId));
      setEdges(eds =>
        eds.filter(edge => edge.source !== nodeId && edge.target !== nodeId)
      );
      if (selectedNodeId === nodeId) {
        setSelectedNodeId(undefined);
      }
    },
    [saveToHistory, setNodes, setEdges, selectedNodeId]
  );

  // Add edge
  const addWorkflowEdge = useCallback(
    (edge: Partial<Edge<WorkflowEdgeData>>) => {
      saveToHistory();
      
      const newEdge: Edge<WorkflowEdgeData> = {
        id: `edge-${Date.now()}`,
        source: '',
        target: '',
        type: 'default',
        animated: false,
        ...edge,
        data: {
          label: '',
          ...edge.data,
        },
      };

      setEdges(eds => [...eds, newEdge]);
    },
    [saveToHistory, setEdges]
  );

  // Update edge
  const updateEdge = useCallback(
    (edgeId: string, updates: Partial<WorkflowEdgeData>) => {
      setEdges(eds =>
        eds.map(edge =>
          edge.id === edgeId
            ? { ...edge, data: { ...edge.data, ...updates } }
            : edge
        )
      );
    },
    [setEdges]
  );

  // Delete edge
  const deleteEdge = useCallback(
    (edgeId: string) => {
      saveToHistory();
      setEdges(eds => eds.filter(edge => edge.id !== edgeId));
      if (selectedEdgeId === edgeId) {
        setSelectedEdgeId(undefined);
      }
    },
    [saveToHistory, setEdges, selectedEdgeId]
  );

  // Handle new connections
  const onConnect = useCallback(
    (params: Connection) => {
      saveToHistory();
      const newEdge: Edge<WorkflowEdgeData> = {
        ...params,
        id: `edge-${Date.now()}`,
        type: 'smoothstep',
        animated: true,
        data: {
          label: '',
        },
      };
      setEdges(eds => addEdge(newEdge, eds));
    },
    [saveToHistory, setEdges]
  );

  // Validation
  const validate = useCallback((): ValidationResult => {
    const errors: any[] = [];
    const warnings: any[] = [];
    const suggestions: any[] = [];

    // Check for isolated nodes (except start nodes)
    const connectedNodes = new Set<string>();
    edges.forEach(edge => {
      connectedNodes.add(edge.source);
      connectedNodes.add(edge.target);
    });

    const isolatedNodes = nodes.filter(
      node => node.data.nodeType !== 'start' && !connectedNodes.has(node.id)
    );

    if (isolatedNodes.length > 0) {
      errors.push({
        type: 'error',
        message: `Found ${isolatedNodes.length} isolated node(s)`,
        code: 'ISOLATED_NODES',
        severity: 'medium' as const,
        nodeId: isolatedNodes[0].id,
      });
    }

    // Check for start nodes
    const startNodes = nodes.filter(node => node.data.nodeType === 'start');
    if (startNodes.length === 0) {
      errors.push({
        type: 'error',
        message: 'Workflow must have at least one start node',
        code: 'NO_START_NODE',
        severity: 'high' as const,
      });
    } else if (startNodes.length > 1) {
      warnings.push({
        type: 'warning',
        message: 'Multiple start nodes detected',
        code: 'MULTIPLE_START_NODES',
        suggestion: 'Consider using only one start node for clarity',
      });
    }

    // Check node configurations
    nodes.forEach(node => {
      const definition = nodeDefinitions.find(def => def.type === node.data.nodeType);
      if (definition) {
        definition.properties.forEach(prop => {
          if (prop.required && !node.data.config?.[prop.name]) {
            errors.push({
              type: 'error',
              message: `Missing required property: ${prop.label}`,
              code: 'MISSING_REQUIRED_PROPERTY',
              severity: 'high' as const,
              nodeId: node.id,
            });
          }

          // Run custom validation if available
          if (prop.validation && node.data.config?.[prop.name] !== undefined) {
            const validationError = prop.validation(node.data.config[prop.name]);
            if (validationError) {
              errors.push({
                type: 'error',
                message: validationError,
                code: 'PROPERTY_VALIDATION_FAILED',
                severity: 'medium' as const,
                nodeId: node.id,
              });
            }
          }
        });
      }
    });

    // Performance suggestions
    if (nodes.length > 20) {
      suggestions.push({
        type: 'suggestion',
        message: 'Large workflow detected. Consider breaking into smaller sub-workflows.',
        action: 'optimize_workflow',
      });
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
      suggestions,
    };
  }, [nodes, edges]);

  // History operations
  const undo = useCallback((): boolean => {
    if (historyIndexRef.current > 0) {
      const newIndex = historyIndexRef.current - 1;
      const previousState = historyRef.current[newIndex];
      
      if (previousState) {
        setNodes(previousState.nodes);
        setEdges(previousState.edges);
        setHistoryIndex(newIndex);
        return true;
      }
    }
    return false;
  }, [setNodes, setEdges]);

  const redo = useCallback((): boolean => {
    if (historyIndexRef.current < historyRef.current.length - 1) {
      const newIndex = historyIndexRef.current + 1;
      const nextState = historyRef.current[newIndex];
      
      if (nextState) {
        setNodes(nextState.nodes);
        setEdges(nextState.edges);
        setHistoryIndex(newIndex);
        return true;
      }
    }
    return false;
  }, [setNodes, setEdges]);

  // Clipboard operations
  const copySelection = useCallback(() => {
    const selectedNodes = nodes.filter(node => node.selected);
    const selectedEdges = edges.filter(edge => edge.selected);
    
    if (selectedNodes.length > 0 || selectedEdges.length > 0) {
      setClipboardData({
        type: 'nodes',
        data: { nodes: selectedNodes, edges: selectedEdges },
        timestamp: new Date().toISOString(),
      });
    }
  }, [nodes, edges]);

  const pasteFromClipboard = useCallback(() => {
    if (!clipboardData || clipboardData.type !== 'nodes') return;
    
    const { nodes: clipboardNodes, edges: clipboardEdges } = clipboardData.data as {
      nodes: Node<WorkflowNodeData>[];
      edges: Edge<WorkflowEdgeData>[];
    };
    
    if (clipboardNodes.length === 0) return;
    
    saveToHistory();
    
    // Create new IDs and adjust positions
    const idMap = new Map<string, string>();
    const newNodes = clipboardNodes.map((node, index) => {
      const newId = `${node.data.nodeType}-${nodeIdCounter + index}`;
      idMap.set(node.id, newId);
      
      return {
        ...node,
        id: newId,
        position: {
          x: node.position.x + 50,
          y: node.position.y + 50,
        },
        selected: false,
      };
    });
    
    const newEdges = clipboardEdges
      .filter(edge => idMap.has(edge.source) && idMap.has(edge.target))
      .map(edge => ({
        ...edge,
        id: `edge-${Date.now()}-${Math.random()}`,
        source: idMap.get(edge.source)!,
        target: idMap.get(edge.target)!,
        selected: false,
      }));
    
    setNodes(nds => [...nds, ...newNodes]);
    setEdges(eds => [...eds, ...newEdges]);
    setNodeIdCounter(counter => counter + newNodes.length);
  }, [clipboardData, saveToHistory, setNodes, setEdges, nodeIdCounter]);

  // Select all
  const selectAll = useCallback(() => {
    setNodes(nds => nds.map(node => ({ ...node, selected: true })));
    setEdges(eds => eds.map(edge => ({ ...edge, selected: true })));
  }, [setNodes, setEdges]);

  // Delete selection
  const deleteSelection = useCallback(() => {
    const selectedNodes = nodes.filter(node => node.selected);
    const selectedEdges = edges.filter(edge => edge.selected);
    
    if (selectedNodes.length > 0 || selectedEdges.length > 0) {
      saveToHistory();
      
      const selectedNodeIds = new Set(selectedNodes.map(node => node.id));
      
      setNodes(nds => nds.filter(node => !node.selected));
      setEdges(eds => eds.filter(edge => 
        !edge.selected && 
        !selectedNodeIds.has(edge.source) && 
        !selectedNodeIds.has(edge.target)
      ));
    }
  }, [nodes, edges, saveToHistory, setNodes, setEdges]);

  return {
    workflow,
    updateWorkflow,
    addNode,
    updateNode,
    deleteNode,
    addEdge: addWorkflowEdge,
    updateEdge,
    deleteEdge,
    validate,
    undo,
    redo,
    canUndo: historyIndex > 0,
    canRedo: historyIndex < history.length - 1,
    copySelection,
    pasteFromClipboard,
    selectAll,
    deleteSelection,
    // Additional React Flow state
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
  };
};