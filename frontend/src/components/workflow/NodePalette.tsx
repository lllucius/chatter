import React, { useState } from 'react';
import {
  Paper,
  Typography,
  Box,
  Chip,
  IconButton,
  Collapse,
  Tooltip,
  Card,
  CardContent,
  useTheme,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  DragIndicator as DragIcon,
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
  Transform as TransformIcon,
  Api as ApiIcon,
  Webhook as WebhookIcon,
  Code as CodeIcon,
  Hub as HubIcon,
  Psychology as PsychologyIcon,
} from '@mui/icons-material';
import { WorkflowNodeType } from './types';

export interface NodeDefinition {
  type: WorkflowNodeType;
  label: string;
  description: string;
  icon: React.ReactElement;
  category: 'core' | 'advanced' | 'integrations' | 'ai';
  color: string;
  properties: NodePropertyDefinition[];
}

export interface NodePropertyDefinition {
  name: string;
  label: string;
  type: 'string' | 'number' | 'boolean' | 'select' | 'textarea' | 'slider' | 'multiselect';
  required: boolean;
  default?: unknown;
  options?: Array<{ value: string; label: string }>;
  min?: number;
  max?: number;
  step?: number;
  description?: string;
  validation?: (value: unknown) => string | null;
}

interface NodePaletteProps {
  onAddNode: (nodeType: WorkflowNodeType) => void;
  disabled?: boolean;
}

const nodeDefinitions: NodeDefinition[] = [
  // Core Nodes
  {
    type: 'start',
    label: 'Start',
    description: 'Entry point for workflow execution',
    icon: <StartIcon />,
    category: 'core',
    color: '#4caf50',
    properties: [
      {
        name: 'name',
        label: 'Node Name',
        type: 'string',
        required: true,
        default: 'Start',
        description: 'Display name for this node',
      },
      {
        name: 'description',
        label: 'Description',
        type: 'textarea',
        required: false,
        description: 'Optional description of what this workflow does',
      },
    ],
  },
  {
    type: 'model',
    label: 'AI Model',
    description: 'Language model interaction with advanced configuration',
    icon: <ModelIcon />,
    category: 'ai',
    color: '#2196f3',
    properties: [
      {
        name: 'name',
        label: 'Node Name',
        type: 'string',
        required: true,
        default: 'AI Model',
      },
      {
        name: 'model',
        label: 'Model',
        type: 'select',
        required: true,
        default: 'gpt-4',
        options: [
          { value: 'gpt-4', label: 'GPT-4' },
          { value: 'gpt-4-turbo', label: 'GPT-4 Turbo' },
          { value: 'gpt-4o', label: 'GPT-4o' },
          { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' },
          { value: 'claude-3-opus', label: 'Claude 3 Opus' },
          { value: 'claude-3-sonnet', label: 'Claude 3 Sonnet' },
          { value: 'claude-3-haiku', label: 'Claude 3 Haiku' },
          { value: 'gemini-pro', label: 'Gemini Pro' },
          { value: 'llama-2-70b', label: 'Llama 2 70B' },
        ],
      },
      {
        name: 'systemMessage',
        label: 'System Message',
        type: 'textarea',
        required: false,
        description: 'System prompt to guide the model behavior',
      },
      {
        name: 'temperature',
        label: 'Temperature',
        type: 'slider',
        required: false,
        default: 0.7,
        min: 0,
        max: 2,
        step: 0.1,
        description: 'Controls randomness in responses (0 = deterministic, 2 = very creative)',
      },
      {
        name: 'maxTokens',
        label: 'Max Tokens',
        type: 'number',
        required: false,
        default: 1000,
        min: 1,
        max: 32000,
        description: 'Maximum number of tokens to generate',
      },
      {
        name: 'topP',
        label: 'Top P',
        type: 'slider',
        required: false,
        default: 1.0,
        min: 0,
        max: 1,
        step: 0.05,
        description: 'Nucleus sampling parameter',
      },
      {
        name: 'frequencyPenalty',
        label: 'Frequency Penalty',
        type: 'slider',
        required: false,
        default: 0,
        min: -2,
        max: 2,
        step: 0.1,
        description: 'Penalty for repeating tokens',
      },
      {
        name: 'presencePenalty',
        label: 'Presence Penalty',
        type: 'slider',
        required: false,
        default: 0,
        min: -2,
        max: 2,
        step: 0.1,
        description: 'Penalty for using tokens that have appeared',
      },
      {
        name: 'stopSequences',
        label: 'Stop Sequences',
        type: 'multiselect',
        required: false,
        description: 'Text sequences that will stop generation',
      },
      {
        name: 'responseFormat',
        label: 'Response Format',
        type: 'select',
        required: false,
        default: 'text',
        options: [
          { value: 'text', label: 'Text' },
          { value: 'json', label: 'JSON' },
          { value: 'markdown', label: 'Markdown' },
        ],
      },
    ],
  },
  {
    type: 'tool',
    label: 'Tool Call',
    description: 'Execute external tools and functions',
    icon: <ToolIcon />,
    category: 'core',
    color: '#ff9800',
    properties: [
      {
        name: 'name',
        label: 'Node Name',
        type: 'string',
        required: true,
        default: 'Tool Call',
      },
      {
        name: 'tools',
        label: 'Available Tools',
        type: 'multiselect',
        required: true,
        options: [
          { value: 'web_search', label: 'Web Search' },
          { value: 'calculator', label: 'Calculator' },
          { value: 'code_executor', label: 'Code Executor' },
          { value: 'file_reader', label: 'File Reader' },
          { value: 'database_query', label: 'Database Query' },
          { value: 'email_sender', label: 'Email Sender' },
          { value: 'calendar', label: 'Calendar' },
          { value: 'weather', label: 'Weather API' },
          { value: 'translation', label: 'Translation' },
          { value: 'image_generator', label: 'Image Generator' },
        ],
      },
      {
        name: 'parallel',
        label: 'Parallel Execution',
        type: 'boolean',
        required: false,
        default: false,
        description: 'Execute multiple tools simultaneously',
      },
      {
        name: 'timeout',
        label: 'Timeout (seconds)',
        type: 'number',
        required: false,
        default: 30,
        min: 1,
        max: 300,
        description: 'Maximum time to wait for tool execution',
      },
      {
        name: 'retryCount',
        label: 'Retry Count',
        type: 'number',
        required: false,
        default: 1,
        min: 1,
        max: 5,
        description: 'Number of retry attempts on failure',
      },
      {
        name: 'errorHandling',
        label: 'Error Handling',
        type: 'select',
        required: false,
        default: 'continue',
        options: [
          { value: 'stop', label: 'Stop on Error' },
          { value: 'continue', label: 'Continue on Error' },
          { value: 'retry', label: 'Retry on Error' },
          { value: 'fallback', label: 'Use Fallback' },
        ],
      },
    ],
  },
  {
    type: 'memory',
    label: 'Memory',
    description: 'Manage conversation history and context',
    icon: <MemoryIcon />,
    category: 'ai',
    color: '#9c27b0',
    properties: [
      {
        name: 'name',
        label: 'Node Name',
        type: 'string',
        required: true,
        default: 'Memory',
      },
      {
        name: 'enabled',
        label: 'Enable Memory',
        type: 'boolean',
        required: false,
        default: true,
      },
      {
        name: 'memoryType',
        label: 'Memory Type',
        type: 'select',
        required: true,
        default: 'conversation',
        options: [
          { value: 'conversation', label: 'Conversation Buffer' },
          { value: 'summary', label: 'Summary Buffer' },
          { value: 'vector', label: 'Vector Memory' },
          { value: 'entity', label: 'Entity Memory' },
          { value: 'knowledge_graph', label: 'Knowledge Graph' },
        ],
      },
      {
        name: 'window',
        label: 'Memory Window',
        type: 'number',
        required: false,
        default: 20,
        min: 1,
        max: 1000,
        description: 'Number of messages/chunks to remember',
      },
      {
        name: 'maxTokens',
        label: 'Max Memory Tokens',
        type: 'number',
        required: false,
        default: 4000,
        min: 100,
        max: 32000,
        description: 'Maximum tokens to store in memory',
      },
      {
        name: 'summarizationThreshold',
        label: 'Summarization Threshold',
        type: 'number',
        required: false,
        default: 0.8,
        min: 0.1,
        max: 1.0,
        step: 0.1,
        description: 'When to trigger summarization (0.8 = 80% of max tokens)',
      },
      {
        name: 'persistenceEnabled',
        label: 'Persistent Storage',
        type: 'boolean',
        required: false,
        default: false,
        description: 'Save memory across workflow sessions',
      },
    ],
  },
  {
    type: 'retrieval',
    label: 'Retrieval',
    description: 'Search and retrieve relevant information',
    icon: <RetrievalIcon />,
    category: 'ai',
    color: '#00bcd4',
    properties: [
      {
        name: 'name',
        label: 'Node Name',
        type: 'string',
        required: true,
        default: 'Retrieval',
      },
      {
        name: 'collection',
        label: 'Collection Name',
        type: 'string',
        required: true,
        description: 'Name of the knowledge base collection',
      },
      {
        name: 'retrievalType',
        label: 'Retrieval Type',
        type: 'select',
        required: true,
        default: 'similarity',
        options: [
          { value: 'similarity', label: 'Semantic Similarity' },
          { value: 'keyword', label: 'Keyword Search' },
          { value: 'hybrid', label: 'Hybrid Search' },
          { value: 'mmr', label: 'Maximal Marginal Relevance' },
        ],
      },
      {
        name: 'topK',
        label: 'Top K Results',
        type: 'number',
        required: false,
        default: 5,
        min: 1,
        max: 100,
        description: 'Number of documents to retrieve',
      },
      {
        name: 'threshold',
        label: 'Similarity Threshold',
        type: 'slider',
        required: false,
        default: 0.7,
        min: 0,
        max: 1,
        step: 0.05,
        description: 'Minimum similarity score for results',
      },
      {
        name: 'diversityLambda',
        label: 'Diversity Lambda (MMR)',
        type: 'slider',
        required: false,
        default: 0.5,
        min: 0,
        max: 1,
        step: 0.1,
        description: 'Balance between relevance and diversity',
      },
      {
        name: 'filters',
        label: 'Metadata Filters',
        type: 'textarea',
        required: false,
        description: 'JSON object for filtering documents by metadata',
      },
      {
        name: 'reranking',
        label: 'Enable Reranking',
        type: 'boolean',
        required: false,
        default: false,
        description: 'Apply additional reranking for better results',
      },
    ],
  },
  {
    type: 'conditional',
    label: 'Conditional',
    description: 'Route workflow based on conditions',
    icon: <ConditionalIcon />,
    category: 'core',
    color: '#607d8b',
    properties: [
      {
        name: 'name',
        label: 'Node Name',
        type: 'string',
        required: true,
        default: 'Conditional',
      },
      {
        name: 'condition',
        label: 'Condition Expression',
        type: 'textarea',
        required: true,
        description: 'JavaScript expression that evaluates to true/false',
      },
      {
        name: 'conditionType',
        label: 'Condition Type',
        type: 'select',
        required: false,
        default: 'expression',
        options: [
          { value: 'expression', label: 'JavaScript Expression' },
          { value: 'contains', label: 'Text Contains' },
          { value: 'equals', label: 'Equals' },
          { value: 'regex', label: 'Regular Expression' },
          { value: 'sentiment', label: 'Sentiment Analysis' },
          { value: 'classification', label: 'Text Classification' },
        ],
      },
      {
        name: 'branches',
        label: 'Branch Configuration',
        type: 'textarea',
        required: false,
        description: 'JSON configuration for multiple branches',
      },
      {
        name: 'defaultBranch',
        label: 'Default Branch',
        type: 'string',
        required: false,
        default: 'false',
        description: 'Branch to take when condition is false',
      },
    ],
  },
  // Advanced Nodes
  {
    type: 'loop',
    label: 'Loop',
    description: 'Iterate over data or repeat operations',
    icon: <LoopIcon />,
    category: 'advanced',
    color: '#795548',
    properties: [
      {
        name: 'name',
        label: 'Node Name',
        type: 'string',
        required: true,
        default: 'Loop',
      },
      {
        name: 'loopType',
        label: 'Loop Type',
        type: 'select',
        required: true,
        default: 'for_each',
        options: [
          { value: 'for_each', label: 'For Each Item' },
          { value: 'while', label: 'While Condition' },
          { value: 'count', label: 'Fixed Count' },
          { value: 'until', label: 'Until Condition' },
        ],
      },
      {
        name: 'maxIterations',
        label: 'Max Iterations',
        type: 'number',
        required: false,
        default: 100,
        min: 1,
        max: 10000,
        description: 'Safety limit to prevent infinite loops',
      },
      {
        name: 'iterationVar',
        label: 'Iteration Variable',
        type: 'string',
        required: false,
        default: 'item',
        description: 'Variable name for current iteration value',
      },
      {
        name: 'breakCondition',
        label: 'Break Condition',
        type: 'textarea',
        required: false,
        description: 'Condition to break out of loop early',
      },
      {
        name: 'parallel',
        label: 'Parallel Execution',
        type: 'boolean',
        required: false,
        default: false,
        description: 'Execute iterations in parallel',
      },
      {
        name: 'batchSize',
        label: 'Batch Size',
        type: 'number',
        required: false,
        default: 10,
        min: 1,
        max: 1000,
        description: 'Number of items to process in each batch',
      },
    ],
  },
  {
    type: 'variable',
    label: 'Variable',
    description: 'Store and manipulate data',
    icon: <VariableIcon />,
    category: 'advanced',
    color: '#3f51b5',
    properties: [
      {
        name: 'name',
        label: 'Node Name',
        type: 'string',
        required: true,
        default: 'Variable',
      },
      {
        name: 'operation',
        label: 'Operation',
        type: 'select',
        required: true,
        default: 'set',
        options: [
          { value: 'set', label: 'Set Value' },
          { value: 'get', label: 'Get Value' },
          { value: 'append', label: 'Append to Array' },
          { value: 'increment', label: 'Increment Number' },
          { value: 'decrement', label: 'Decrement Number' },
          { value: 'merge', label: 'Merge Objects' },
          { value: 'transform', label: 'Transform Data' },
        ],
      },
      {
        name: 'variableName',
        label: 'Variable Name',
        type: 'string',
        required: true,
        description: 'Name of the variable to operate on',
      },
      {
        name: 'value',
        label: 'Value',
        type: 'textarea',
        required: false,
        description: 'Value to set (can be JSON, expression, or literal)',
      },
      {
        name: 'dataType',
        label: 'Data Type',
        type: 'select',
        required: false,
        default: 'auto',
        options: [
          { value: 'auto', label: 'Auto-detect' },
          { value: 'string', label: 'String' },
          { value: 'number', label: 'Number' },
          { value: 'boolean', label: 'Boolean' },
          { value: 'array', label: 'Array' },
          { value: 'object', label: 'Object' },
        ],
      },
      {
        name: 'scope',
        label: 'Variable Scope',
        type: 'select',
        required: false,
        default: 'workflow',
        options: [
          { value: 'workflow', label: 'Workflow Scope' },
          { value: 'global', label: 'Global Scope' },
          { value: 'session', label: 'Session Scope' },
          { value: 'temporary', label: 'Temporary' },
        ],
      },
    ],
  },
  {
    type: 'errorHandler',
    label: 'Error Handler',
    description: 'Handle errors and implement fallback logic',
    icon: <ErrorHandlerIcon />,
    category: 'advanced',
    color: '#f44336',
    properties: [
      {
        name: 'name',
        label: 'Node Name',
        type: 'string',
        required: true,
        default: 'Error Handler',
      },
      {
        name: 'errorTypes',
        label: 'Handle Error Types',
        type: 'multiselect',
        required: false,
        options: [
          { value: 'all', label: 'All Errors' },
          { value: 'timeout', label: 'Timeout Errors' },
          { value: 'network', label: 'Network Errors' },
          { value: 'validation', label: 'Validation Errors' },
          { value: 'rate_limit', label: 'Rate Limit Errors' },
          { value: 'auth', label: 'Authentication Errors' },
          { value: 'quota', label: 'Quota Exceeded' },
        ],
      },
      {
        name: 'retryCount',
        label: 'Retry Count',
        type: 'number',
        required: false,
        default: 3,
        min: 0,
        max: 10,
        description: 'Number of times to retry failed operation',
      },
      {
        name: 'retryDelay',
        label: 'Retry Delay (ms)',
        type: 'number',
        required: false,
        default: 1000,
        min: 0,
        max: 60000,
        description: 'Delay between retry attempts',
      },
      {
        name: 'backoffStrategy',
        label: 'Backoff Strategy',
        type: 'select',
        required: false,
        default: 'exponential',
        options: [
          { value: 'fixed', label: 'Fixed Delay' },
          { value: 'linear', label: 'Linear Backoff' },
          { value: 'exponential', label: 'Exponential Backoff' },
          { value: 'jitter', label: 'Jittered Backoff' },
        ],
      },
      {
        name: 'fallbackAction',
        label: 'Fallback Action',
        type: 'select',
        required: false,
        default: 'continue',
        options: [
          { value: 'continue', label: 'Continue Workflow' },
          { value: 'stop', label: 'Stop Workflow' },
          { value: 'branch', label: 'Go to Error Branch' },
          { value: 'return_default', label: 'Return Default Value' },
        ],
      },
      {
        name: 'defaultValue',
        label: 'Default Value',
        type: 'textarea',
        required: false,
        description: 'Value to return when using return_default action',
      },
      {
        name: 'logErrors',
        label: 'Log Errors',
        type: 'boolean',
        required: false,
        default: true,
        description: 'Whether to log errors for debugging',
      },
    ],
  },
  {
    type: 'delay',
    label: 'Delay',
    description: 'Add timing controls and rate limiting',
    icon: <DelayIcon />,
    category: 'advanced',
    color: '#ff5722',
    properties: [
      {
        name: 'name',
        label: 'Node Name',
        type: 'string',
        required: true,
        default: 'Delay',
      },
      {
        name: 'delayType',
        label: 'Delay Type',
        type: 'select',
        required: true,
        default: 'fixed',
        options: [
          { value: 'fixed', label: 'Fixed Delay' },
          { value: 'random', label: 'Random Delay' },
          { value: 'exponential', label: 'Exponential Backoff' },
          { value: 'rate_limit', label: 'Rate Limiting' },
        ],
      },
      {
        name: 'duration',
        label: 'Delay Duration (ms)',
        type: 'number',
        required: true,
        default: 1000,
        min: 0,
        max: 3600000,
        description: 'Delay duration in milliseconds',
      },
      {
        name: 'maxDuration',
        label: 'Max Duration (ms)',
        type: 'number',
        required: false,
        default: 5000,
        min: 0,
        max: 3600000,
        description: 'Maximum delay for random/exponential types',
      },
      {
        name: 'jitter',
        label: 'Add Jitter',
        type: 'boolean',
        required: false,
        default: false,
        description: 'Add randomness to prevent thundering herd',
      },
      {
        name: 'rateLimit',
        label: 'Rate Limit (requests/minute)',
        type: 'number',
        required: false,
        default: 60,
        min: 1,
        max: 10000,
        description: 'Maximum requests per minute',
      },
    ],
  },
  // New Node Types
  {
    type: 'transform' as WorkflowNodeType,
    label: 'Transform',
    description: 'Transform and manipulate data',
    icon: <TransformIcon />,
    category: 'advanced',
    color: '#8bc34a',
    properties: [
      {
        name: 'name',
        label: 'Node Name',
        type: 'string',
        required: true,
        default: 'Transform',
      },
      {
        name: 'transformType',
        label: 'Transform Type',
        type: 'select',
        required: true,
        default: 'json',
        options: [
          { value: 'json', label: 'JSON Transform' },
          { value: 'text', label: 'Text Processing' },
          { value: 'array', label: 'Array Operations' },
          { value: 'custom', label: 'Custom Function' },
        ],
      },
      {
        name: 'expression',
        label: 'Transform Expression',
        type: 'textarea',
        required: true,
        description: 'JavaScript expression or JSONPath for transformation',
      },
    ],
  },
  {
    type: 'api' as WorkflowNodeType,
    label: 'API Call',
    description: 'Make HTTP requests to external APIs',
    icon: <ApiIcon />,
    category: 'integrations',
    color: '#00e676',
    properties: [
      {
        name: 'name',
        label: 'Node Name',
        type: 'string',
        required: true,
        default: 'API Call',
      },
      {
        name: 'method',
        label: 'HTTP Method',
        type: 'select',
        required: true,
        default: 'GET',
        options: [
          { value: 'GET', label: 'GET' },
          { value: 'POST', label: 'POST' },
          { value: 'PUT', label: 'PUT' },
          { value: 'PATCH', label: 'PATCH' },
          { value: 'DELETE', label: 'DELETE' },
        ],
      },
      {
        name: 'url',
        label: 'URL',
        type: 'string',
        required: true,
        description: 'API endpoint URL',
      },
      {
        name: 'headers',
        label: 'Headers',
        type: 'textarea',
        required: false,
        description: 'JSON object with request headers',
      },
      {
        name: 'body',
        label: 'Request Body',
        type: 'textarea',
        required: false,
        description: 'Request body (for POST, PUT, PATCH)',
      },
      {
        name: 'timeout',
        label: 'Timeout (seconds)',
        type: 'number',
        required: false,
        default: 30,
        min: 1,
        max: 300,
      },
    ],
  },
];

const categoryColors = {
  core: '#2196f3',
  advanced: '#ff9800',
  integrations: '#4caf50',
  ai: '#9c27b0',
};

const NodePalette: React.FC<NodePaletteProps> = ({ onAddNode, disabled = false }) => {
  const theme = useTheme();
  const [expandedCategories, setExpandedCategories] = useState<Record<string, boolean>>({
    core: true,
    ai: true,
    advanced: false,
    integrations: false,
  });

  const categorizedNodes = nodeDefinitions.reduce((acc, node) => {
    if (!acc[node.category]) {
      acc[node.category] = [];
    }
    acc[node.category].push(node);
    return acc;
  }, {} as Record<string, NodeDefinition[]>);

  const toggleCategory = (category: string) => {
    setExpandedCategories(prev => ({
      ...prev,
      [category]: !prev[category],
    }));
  };

  const handleDragStart = (event: React.DragEvent, nodeType: WorkflowNodeType) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.effectAllowed = 'move';
  };

  return (
    <Paper
      sx={{
        width: 280,
        height: '100%',
        overflow: 'auto',
        borderRadius: 0,
        borderRight: `1px solid ${theme.palette.divider}`,
      }}
    >
      <Box sx={{ p: 2, borderBottom: `1px solid ${theme.palette.divider}` }}>
        <Typography variant="h6" component="h2">
          Node Palette
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Drag nodes to the canvas or click to add
        </Typography>
      </Box>

      {Object.entries(categorizedNodes).map(([category, nodes]) => (
        <Box key={category}>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              p: 1,
              cursor: 'pointer',
              bgcolor: categoryColors[category as keyof typeof categoryColors] + '10',
              '&:hover': {
                bgcolor: categoryColors[category as keyof typeof categoryColors] + '20',
              },
            }}
            onClick={() => toggleCategory(category)}
          >
            <Chip
              label={category.charAt(0).toUpperCase() + category.slice(1)}
              size="small"
              sx={{
                bgcolor: categoryColors[category as keyof typeof categoryColors],
                color: 'white',
                mr: 1,
              }}
            />
            <Typography variant="body2" sx={{ flex: 1 }}>
              {nodes.length} nodes
            </Typography>
            <IconButton size="small">
              {expandedCategories[category] ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          </Box>

          <Collapse in={expandedCategories[category]}>
            <Box sx={{ p: 1 }}>
              {nodes.map((node) => (
                <Tooltip
                  key={node.type}
                  title={node.description}
                  placement="right"
                  arrow
                >
                  <Card
                    sx={{
                      mb: 1,
                      cursor: disabled ? 'not-allowed' : 'grab',
                      opacity: disabled ? 0.5 : 1,
                      '&:hover': disabled ? {} : {
                        boxShadow: theme.shadows[4],
                        transform: 'translateY(-1px)',
                      },
                      transition: 'all 0.2s ease-in-out',
                    }}
                    draggable={!disabled}
                    onDragStart={(e) => handleDragStart(e, node.type)}
                    onClick={() => !disabled && onAddNode(node.type)}
                  >
                    <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Box
                          sx={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            width: 32,
                            height: 32,
                            borderRadius: 1,
                            bgcolor: node.color + '20',
                            color: node.color,
                            mr: 1,
                          }}
                        >
                          {node.icon}
                        </Box>
                        <Box sx={{ flex: 1, minWidth: 0 }}>
                          <Typography variant="body2" fontWeight="medium" noWrap>
                            {node.label}
                          </Typography>
                          <Typography
                            variant="caption"
                            color="textSecondary"
                            sx={{
                              display: '-webkit-box',
                              WebkitLineClamp: 2,
                              WebkitBoxOrient: 'vertical',
                              overflow: 'hidden',
                            }}
                          >
                            {node.description}
                          </Typography>
                        </Box>
                        <DragIcon sx={{ color: 'text.secondary', fontSize: 16 }} />
                      </Box>
                    </CardContent>
                  </Card>
                </Tooltip>
              ))}
            </Box>
          </Collapse>
        </Box>
      ))}
    </Paper>
  );
};

export default NodePalette;
export { nodeDefinitions };