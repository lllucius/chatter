import type { Node, Edge } from '@xyflow/react';

// Extended node types including new ones
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
  | 'delay'
  | 'transform'
  | 'api';

// Enhanced node data interface with better typing
export interface WorkflowNodeData extends Record<string, unknown> {
  label: string;
  nodeType: WorkflowNodeType;
  config: NodeConfig;
  description?: string;
  tags?: string[];
  metadata?: {
    created?: string;
    updated?: string;
    version?: string;
    author?: string;
  };
}

// Enhanced edge data interface
export interface WorkflowEdgeData extends Record<string, unknown> {
  condition?: string;
  label?: string;
  priority?: number;
  metadata?: {
    created?: string;
    type?: 'success' | 'error' | 'conditional' | 'default';
  };
}

// Comprehensive node configuration types
export interface NodeConfig {
  // Common properties
  name?: string;
  description?: string;
  enabled?: boolean;
  timeout?: number;
  retryCount?: number;
  
  // Model node specific
  model?: string;
  systemMessage?: string;
  temperature?: number;
  maxTokens?: number;
  topP?: number;
  frequencyPenalty?: number;
  presencePenalty?: number;
  stopSequences?: string[];
  responseFormat?: 'text' | 'json' | 'markdown';
  
  // Tool node specific
  tools?: string[];
  parallel?: boolean;
  errorHandling?: 'stop' | 'continue' | 'retry' | 'fallback';
  
  // Memory node specific
  memoryType?: 'conversation' | 'summary' | 'vector' | 'entity' | 'knowledge_graph';
  window?: number;
  maxMemoryTokens?: number;
  summarizationThreshold?: number;
  persistenceEnabled?: boolean;
  
  // Retrieval node specific
  collection?: string;
  retrievalType?: 'similarity' | 'keyword' | 'hybrid' | 'mmr';
  topK?: number;
  threshold?: number;
  diversityLambda?: number;
  filters?: string;
  reranking?: boolean;
  
  // Conditional node specific
  condition?: string;
  conditionType?: 'expression' | 'contains' | 'equals' | 'regex' | 'sentiment' | 'classification';
  branches?: Record<string, unknown>;
  defaultBranch?: string;
  
  // Loop node specific
  loopType?: 'for_each' | 'while' | 'count' | 'until';
  maxIterations?: number;
  iterationVar?: string;
  breakCondition?: string;
  batchSize?: number;
  
  // Variable node specific
  operation?: 'set' | 'get' | 'append' | 'increment' | 'decrement' | 'merge' | 'transform';
  variableName?: string;
  value?: unknown;
  dataType?: 'auto' | 'string' | 'number' | 'boolean' | 'array' | 'object';
  scope?: 'workflow' | 'global' | 'session' | 'temporary';
  
  // Error handler specific
  errorTypes?: string[];
  retryDelay?: number;
  backoffStrategy?: 'fixed' | 'linear' | 'exponential' | 'jitter';
  fallbackAction?: 'continue' | 'stop' | 'branch' | 'return_default';
  defaultValue?: unknown;
  logErrors?: boolean;
  
  // Delay node specific
  delayType?: 'fixed' | 'random' | 'exponential' | 'rate_limit';
  duration?: number;
  maxDuration?: number;
  jitter?: boolean;
  rateLimit?: number;
  
  // Transform node specific
  transformType?: 'json' | 'text' | 'array' | 'custom';
  expression?: string;
  
  // API node specific
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  url?: string;
  headers?: Record<string, string>;
  body?: string;
  
  // Additional common properties
  [key: string]: unknown;
}

// Enhanced workflow definition
export interface WorkflowDefinition {
  id?: string;
  nodes: Node<WorkflowNodeData>[];
  edges: Edge<WorkflowEdgeData>[];
  metadata: WorkflowMetadata;
  version?: string;
  variables?: Record<string, unknown>;
  settings?: WorkflowSettings;
}

export interface WorkflowMetadata {
  name: string;
  description: string;
  version: string;
  createdAt: string;
  updatedAt: string;
  author?: string;
  tags?: string[];
  category?: string;
  complexity?: 'low' | 'medium' | 'high';
  estimatedRuntime?: number;
}

export interface WorkflowSettings {
  autoSave?: boolean;
  autoSaveInterval?: number;
  enableValidation?: boolean;
  enableAnalytics?: boolean;
  maxExecutionTime?: number;
  errorHandling?: 'stop' | 'continue' | 'retry';
  logLevel?: 'error' | 'warn' | 'info' | 'debug';
  concurrency?: number;
  rateLimit?: {
    enabled: boolean;
    requestsPerMinute: number;
  };
}

// Validation types
export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
  suggestions?: ValidationSuggestion[];
}

export interface ValidationError {
  type: 'error';
  nodeId?: string;
  edgeId?: string;
  message: string;
  code: string;
  severity: 'high' | 'medium' | 'low';
  fixable?: boolean;
  fix?: () => void;
}

export interface ValidationWarning {
  type: 'warning';
  nodeId?: string;
  edgeId?: string;
  message: string;
  code: string;
  suggestion?: string;
}

export interface ValidationSuggestion {
  type: 'suggestion';
  message: string;
  action?: string;
  apply?: () => void;
}

// Analytics types
export interface WorkflowAnalytics {
  nodeCount: number;
  edgeCount: number;
  complexityScore: number;
  estimatedRuntime: number;
  bottlenecks: BottleneckInfo[];
  optimizations: OptimizationSuggestion[];
  executionPaths: ExecutionPath[];
  dependencies: NodeDependency[];
}

export interface BottleneckInfo {
  nodeId: string;
  type: 'performance' | 'memory' | 'rate_limit' | 'dependency';
  severity: 'high' | 'medium' | 'low';
  description: string;
  impact: string;
  suggestion: string;
}

export interface OptimizationSuggestion {
  type: 'parallel' | 'caching' | 'batching' | 'removal' | 'replacement';
  title: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  effort: 'low' | 'medium' | 'high';
  savings: string;
  apply?: () => void;
}

export interface ExecutionPath {
  id: string;
  name: string;
  nodeIds: string[];
  probability?: number;
  estimatedTime?: number;
  complexity: 'low' | 'medium' | 'high';
}

export interface NodeDependency {
  nodeId: string;
  dependsOn: string[];
  dependents: string[];
  critical: boolean;
}

// Template types
export interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  category: 'basic' | 'advanced' | 'integration' | 'ai' | 'custom';
  workflow: WorkflowDefinition;
  tags: string[];
  createdAt: string;
  updatedAt?: string;
  author?: string;
  version: string;
  popularity?: number;
  rating?: number;
  downloads?: number;
  featured?: boolean;
  thumbnail?: string;
  documentation?: string;
  examples?: TemplateExample[];
}

export interface TemplateExample {
  name: string;
  description: string;
  input: unknown;
  expectedOutput: unknown;
  notes?: string;
}

// Execution types
export interface WorkflowExecution {
  id: string;
  workflowId: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  startTime: string;
  endTime?: string;
  duration?: number;
  input: unknown;
  output?: unknown;
  error?: ExecutionError;
  logs: ExecutionLog[];
  metrics: ExecutionMetrics;
}

export interface ExecutionError {
  nodeId?: string;
  type: string;
  message: string;
  stack?: string;
  timestamp: string;
  recoverable: boolean;
}

export interface ExecutionLog {
  timestamp: string;
  level: 'debug' | 'info' | 'warn' | 'error';
  nodeId?: string;
  message: string;
  data?: unknown;
}

export interface ExecutionMetrics {
  totalNodes: number;
  completedNodes: number;
  failedNodes: number;
  tokensUsed?: number;
  apiCalls?: number;
  memoryUsage?: number;
  cost?: number;
}

// Editor state types
export interface EditorState {
  selectedNodeId?: string;
  selectedEdgeId?: string;
  clipboardData?: ClipboardData;
  viewportPosition: { x: number; y: number; zoom: number };
  showGrid: boolean;
  snapToGrid: boolean;
  showMinimap: boolean;
  panelMode: 'properties' | 'analytics' | 'templates' | 'logs' | 'none';
  theme: 'light' | 'dark' | 'auto';
}

export interface ClipboardData {
  type: 'nodes' | 'edges' | 'workflow';
  data: unknown;
  timestamp: string;
}

// Event types for workflow builder
export interface WorkflowEvent {
  type: string;
  timestamp: string;
  data: unknown;
}

export interface NodeEvent extends WorkflowEvent {
  type: 'node:add' | 'node:delete' | 'node:update' | 'node:select';
  nodeId: string;
}

export interface EdgeEvent extends WorkflowEvent {
  type: 'edge:add' | 'edge:delete' | 'edge:update' | 'edge:select';
  edgeId: string;
}

export interface WorkflowChangeEvent extends WorkflowEvent {
  type: 'workflow:save' | 'workflow:load' | 'workflow:validate' | 'workflow:execute';
  workflowId?: string;
}

// Hook types
export interface UseWorkflowEditor {
  workflow: WorkflowDefinition;
  updateWorkflow: (updates: Partial<WorkflowDefinition>) => void;
  addNode: (nodeType: WorkflowNodeType, position?: { x: number; y: number }) => void;
  updateNode: (nodeId: string, updates: Partial<WorkflowNodeData>) => void;
  deleteNode: (nodeId: string) => void;
  addEdge: (edge: Partial<Edge<WorkflowEdgeData>>) => void;
  updateEdge: (edgeId: string, updates: Partial<WorkflowEdgeData>) => void;
  deleteEdge: (edgeId: string) => void;
  validate: () => ValidationResult;
  undo: () => boolean;
  redo: () => boolean;
  canUndo: boolean;
  canRedo: boolean;
  copySelection: () => void;
  pasteFromClipboard: () => void;
  selectAll: () => void;
  deleteSelection: () => void;
  // Additional React Flow state
  nodes: Node<WorkflowNodeData>[];
  edges: Edge<WorkflowEdgeData>[];
  setNodes: React.Dispatch<React.SetStateAction<Node<WorkflowNodeData>[]>>;
  setEdges: React.Dispatch<React.SetStateAction<Edge<WorkflowEdgeData>[]>>;
  onNodesChange: (changes: any[]) => void;
  onEdgesChange: (changes: any[]) => void;
  onConnect: (connection: any) => void;
  selectedNodeId?: string;
  setSelectedNodeId: (id: string | undefined) => void;
  selectedEdgeId?: string;
  setSelectedEdgeId: (id: string | undefined) => void;
  clipboardData: ClipboardData | null;
  snapToGrid: boolean;
  setSnapToGrid: (snap: boolean) => void;
}

export interface UseWorkflowAnalytics {
  analytics: WorkflowAnalytics | null;
  loading: boolean;
  error: string | null;
  refreshAnalytics: () => Promise<void>;
  optimizeWorkflow: (suggestion: OptimizationSuggestion) => void;
}

export interface UseWorkflowTemplates {
  templates: WorkflowTemplate[];
  loading: boolean;
  error: string | null;
  loadTemplates: () => Promise<void>;
  createTemplate: (template: Omit<WorkflowTemplate, 'id' | 'createdAt'>) => Promise<void>;
  updateTemplate: (id: string, updates: Partial<WorkflowTemplate>) => Promise<void>;
  deleteTemplate: (id: string) => Promise<void>;
  searchTemplates: (query: string) => WorkflowTemplate[];
  filterTemplates: (filters: Partial<WorkflowTemplate>) => WorkflowTemplate[];
}

// Component prop types
export interface WorkflowEditorProps {
  initialWorkflow?: WorkflowDefinition;
  onWorkflowChange?: (workflow: WorkflowDefinition) => void;
  onSave?: (workflow: WorkflowDefinition) => Promise<void>;
  readOnly?: boolean;
  showToolbar?: boolean;
  showPalette?: boolean;
  showProperties?: boolean;
  showMinimap?: boolean;
  theme?: 'light' | 'dark' | 'auto';
  height?: string | number;
  width?: string | number;
  className?: string;
}

export interface NodePaletteProps {
  onAddNode: (nodeType: WorkflowNodeType) => void;
  disabled?: boolean;
  categories?: string[];
  searchQuery?: string;
  onSearch?: (query: string) => void;
}

export interface PropertiesPanelProps {
  selectedNode: Node<WorkflowNodeData> | null;
  selectedEdge?: Edge<WorkflowEdgeData> | null;
  onNodeUpdate: (nodeId: string, updates: Partial<WorkflowNodeData>) => void;
  onEdgeUpdate?: (edgeId: string, updates: Partial<WorkflowEdgeData>) => void;
  onClose: () => void;
  width?: number;
}

export interface WorkflowToolbarProps {
  onUndo: () => void;
  onRedo: () => void;
  onCopy: () => void;
  onPaste: () => void;
  onValidate: () => void;
  onSave: () => void;
  onClear: () => void;
  canUndo: boolean;
  canRedo: boolean;
  canPaste: boolean;
  isValid?: boolean;
  isSaving?: boolean;
  readOnly?: boolean;
  onToggleGrid?: () => void;
  onToggleProperties?: () => void;
  onToggleAnalytics?: () => void;
  onToggleTemplates?: () => void;
  onZoomIn?: () => void;
  onZoomOut?: () => void;
  onFitView?: () => void;
  onLoadExamples?: (event: React.MouseEvent<HTMLElement>) => void;
  snapToGrid?: boolean;
  showProperties?: boolean;
  showAnalytics?: boolean;
  showTemplates?: boolean;
  validationStatus?: 'valid' | 'invalid' | 'unknown';
}