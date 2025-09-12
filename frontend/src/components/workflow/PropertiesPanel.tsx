import React, { useState, useCallback, useEffect } from 'react';
import {
  Paper,
  Typography,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Slider,
  Box,
  Chip,
  IconButton,
  Divider,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Close as CloseIcon,
  ExpandMore as ExpandMoreIcon,
} from '@mui/icons-material';
import { Node } from '@xyflow/react';
import { WorkflowNodeData, WorkflowNodeType } from './WorkflowEditor';

interface PropertiesPanelProps {
  selectedNode: Node<WorkflowNodeData> | null;
  onNodeUpdate: (nodeId: string, updates: Partial<WorkflowNodeData>) => void;
  onClose: () => void;
}

const PropertiesPanel: React.FC<PropertiesPanelProps> = ({
  selectedNode,
  onNodeUpdate,
  onClose,
}) => {
  const [config, setConfig] = useState<Record<string, unknown>>({});
  const [label, setLabel] = useState('');

  // Sync with selected node
  useEffect(() => {
    if (selectedNode) {
      setConfig(selectedNode.data.config || {});
      setLabel(selectedNode.data.label || '');
    }
  }, [selectedNode]);

  // Update node with current values
  const handleUpdate = useCallback(() => {
    if (selectedNode) {
      onNodeUpdate(selectedNode.id, {
        ...selectedNode.data,
        label,
        config,
      });
    }
  }, [selectedNode, label, config, onNodeUpdate]);

  // Auto-update on changes
  useEffect(() => {
    const timeoutId = setTimeout(handleUpdate, 500);
    return () => clearTimeout(timeoutId);
  }, [handleUpdate]);

  if (!selectedNode) {
    return (
      <Paper 
        sx={{ 
          width: 350, 
          height: '100%', 
          p: 2,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Typography color="textSecondary">
          Select a node to edit its properties
        </Typography>
      </Paper>
    );
  }

  const renderNodeTypeSpecificControls = () => {
    switch (selectedNode.data.nodeType) {
      case 'model':
        return (
          <>
            <TextField
              fullWidth
              label="System Message"
              multiline
              rows={3}
              value={config.systemMessage || ''}
              onChange={(e) => setConfig({ ...config, systemMessage: e.target.value })}
              sx={{ mb: 2 }}
            />
            <Box sx={{ mb: 2 }}>
              <Typography gutterBottom>Temperature: {config.temperature || 0.7}</Typography>
              <Slider
                value={config.temperature || 0.7}
                onChange={(_, value) => setConfig({ ...config, temperature: value })}
                min={0}
                max={2}
                step={0.1}
                marks={[
                  { value: 0, label: '0' },
                  { value: 1, label: '1' },
                  { value: 2, label: '2' },
                ]}
              />
            </Box>
            <TextField
              fullWidth
              label="Max Tokens"
              type="number"
              value={config.maxTokens || 1000}
              onChange={(e) => setConfig({ ...config, maxTokens: parseInt(e.target.value) || 1000 })}
              sx={{ mb: 2 }}
            />
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Model</InputLabel>
              <Select
                value={config.model || 'gpt-4'}
                label="Model"
                onChange={(e) => setConfig({ ...config, model: e.target.value })}
              >
                <MenuItem value="gpt-4">GPT-4</MenuItem>
                <MenuItem value="gpt-4-turbo">GPT-4 Turbo</MenuItem>
                <MenuItem value="gpt-3.5-turbo">GPT-3.5 Turbo</MenuItem>
                <MenuItem value="claude-3-opus">Claude 3 Opus</MenuItem>
                <MenuItem value="claude-3-sonnet">Claude 3 Sonnet</MenuItem>
              </Select>
            </FormControl>
          </>
        );

      case 'tool':
        return (
          <>
            <FormControlLabel
              control={
                <Switch
                  checked={config.parallel || false}
                  onChange={(e) => setConfig({ ...config, parallel: e.target.checked })}
                />
              }
              label="Execute in Parallel"
              sx={{ mb: 2 }}
            />
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>
                Selected Tools:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 1 }}>
                {(config.tools || []).map((tool: string, index: number): void => (
                  <Chip
                    key={index}
                    label={tool}
                    onDelete={() => {
                      const newTools = [...(config.tools || [])];
                      newTools.splice(index, 1);
                      setConfig({ ...config, tools: newTools });
                    }}
                  />
                ))}
              </Box>
              <FormControl fullWidth>
                <InputLabel>Add Tool</InputLabel>
                <Select
                  value=""
                  label="Add Tool"
                  onChange={(e) => {
                    const tool = e.target.value as string;
                    if (tool && !config.tools?.includes(tool)) {
                      setConfig({ 
                        ...config, 
                        tools: [...(config.tools || []), tool] 
                      });
                    }
                  }}
                >
                  <MenuItem value="web_search">Web Search</MenuItem>
                  <MenuItem value="calculator">Calculator</MenuItem>
                  <MenuItem value="code_executor">Code Executor</MenuItem>
                  <MenuItem value="file_reader">File Reader</MenuItem>
                  <MenuItem value="database_query">Database Query</MenuItem>
                </Select>
              </FormControl>
            </Box>
          </>
        );

      case 'memory':
        return (
          <>
            <FormControlLabel
              control={
                <Switch
                  checked={config.enabled !== false}
                  onChange={(e) => setConfig({ ...config, enabled: e.target.checked })}
                />
              }
              label="Enable Memory"
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Memory Window Size"
              type="number"
              value={config.window || 20}
              onChange={(e) => setConfig({ ...config, window: parseInt(e.target.value) || 20 })}
              helperText="Number of messages to remember"
              sx={{ mb: 2 }}
            />
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Memory Type</InputLabel>
              <Select
                value={config.memoryType || 'conversation'}
                label="Memory Type"
                onChange={(e) => setConfig({ ...config, memoryType: e.target.value })}
              >
                <MenuItem value="conversation">Conversation Buffer</MenuItem>
                <MenuItem value="summary">Summary Buffer</MenuItem>
                <MenuItem value="vector">Vector Memory</MenuItem>
                <MenuItem value="entity">Entity Memory</MenuItem>
              </Select>
            </FormControl>
          </>
        );

      case 'retrieval':
        return (
          <>
            <TextField
              fullWidth
              label="Collection Name"
              value={config.collection || ''}
              onChange={(e) => setConfig({ ...config, collection: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Top K Results"
              type="number"
              value={config.topK || 5}
              onChange={(e) => setConfig({ ...config, topK: parseInt(e.target.value) || 5 })}
              sx={{ mb: 2 }}
            />
            <Box sx={{ mb: 2 }}>
              <Typography gutterBottom>Similarity Threshold: {config.threshold || 0.7}</Typography>
              <Slider
                value={config.threshold || 0.7}
                onChange={(_, value) => setConfig({ ...config, threshold: value })}
                min={0}
                max={1}
                step={0.05}
                marks={[
                  { value: 0.5, label: '0.5' },
                  { value: 0.7, label: '0.7' },
                  { value: 0.9, label: '0.9' },
                ]}
              />
            </Box>
          </>
        );

      case 'conditional':
        return (
          <>
            <TextField
              fullWidth
              label="Condition Expression"
              multiline
              rows={2}
              value={config.condition || ''}
              onChange={(e) => setConfig({ ...config, condition: e.target.value })}
              helperText="JavaScript-like expression (e.g., response.includes('yes'))"
              sx={{ mb: 2 }}
            />
            <Alert severity="info" sx={{ mb: 2 }}>
              <Typography variant="caption">
                Use variables like: `response`, `user_input`, `context`, `tools_used`
              </Typography>
            </Alert>
          </>
        );

      case 'loop':
        return (
          <>
            <TextField
              fullWidth
              label="Max Iterations"
              type="number"
              value={config.maxIterations || 10}
              onChange={(e) => setConfig({ ...config, maxIterations: parseInt(e.target.value) || 10 })}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Loop Condition"
              multiline
              rows={2}
              value={config.condition || ''}
              onChange={(e) => setConfig({ ...config, condition: e.target.value })}
              helperText="Continue while this condition is true"
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Break Condition"
              multiline
              rows={2}
              value={config.breakCondition || ''}
              onChange={(e) => setConfig({ ...config, breakCondition: e.target.value })}
              helperText="Break loop when this condition is true"
              sx={{ mb: 2 }}
            />
          </>
        );

      case 'variable':
        return (
          <>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Operation</InputLabel>
              <Select
                value={config.operation || 'set'}
                label="Operation"
                onChange={(e) => setConfig({ ...config, operation: e.target.value })}
              >
                <MenuItem value="set">Set Variable</MenuItem>
                <MenuItem value="get">Get Variable</MenuItem>
                <MenuItem value="append">Append to Variable</MenuItem>
                <MenuItem value="increment">Increment</MenuItem>
                <MenuItem value="decrement">Decrement</MenuItem>
              </Select>
            </FormControl>
            <TextField
              fullWidth
              label="Variable Name"
              value={config.variableName || ''}
              onChange={(e) => setConfig({ ...config, variableName: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Value"
              multiline
              rows={2}
              value={config.value || ''}
              onChange={(e) => setConfig({ ...config, value: e.target.value })}
              helperText="Can use expressions and other variables"
              sx={{ mb: 2 }}
            />
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Scope</InputLabel>
              <Select
                value={config.scope || 'workflow'}
                label="Scope"
                onChange={(e) => setConfig({ ...config, scope: e.target.value })}
              >
                <MenuItem value="workflow">Workflow</MenuItem>
                <MenuItem value="session">Session</MenuItem>
                <MenuItem value="global">Global</MenuItem>
              </Select>
            </FormControl>
          </>
        );

      case 'errorHandler':
        return (
          <>
            <TextField
              fullWidth
              label="Retry Count"
              type="number"
              value={config.retryCount || 3}
              onChange={(e) => setConfig({ ...config, retryCount: parseInt(e.target.value) || 3 })}
              sx={{ mb: 2 }}
            />
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Fallback Action</InputLabel>
              <Select
                value={config.fallbackAction || 'continue'}
                label="Fallback Action"
                onChange={(e) => setConfig({ ...config, fallbackAction: e.target.value })}
              >
                <MenuItem value="continue">Continue Workflow</MenuItem>
                <MenuItem value="stop">Stop Workflow</MenuItem>
                <MenuItem value="skip">Skip to Next</MenuItem>
                <MenuItem value="custom">Custom Handler</MenuItem>
              </Select>
            </FormControl>
            <FormControlLabel
              control={
                <Switch
                  checked={config.logErrors !== false}
                  onChange={(e) => setConfig({ ...config, logErrors: e.target.checked })}
                />
              }
              label="Log Errors"
              sx={{ mb: 2 }}
            />
          </>
        );

      case 'delay':
        return (
          <>
            <TextField
              fullWidth
              label="Duration"
              type="number"
              value={config.duration || 1}
              onChange={(e) => setConfig({ ...config, duration: parseInt(e.target.value) || 1 })}
              sx={{ mb: 2 }}
            />
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Type</InputLabel>
              <Select
                value={config.type || 'fixed'}
                label="Type"
                onChange={(e) => setConfig({ ...config, type: e.target.value })}
              >
                <MenuItem value="fixed">Fixed Delay</MenuItem>
                <MenuItem value="random">Random Delay</MenuItem>
                <MenuItem value="exponential">Exponential Backoff</MenuItem>
                <MenuItem value="dynamic">Dynamic (from variable)</MenuItem>
              </Select>
            </FormControl>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Unit</InputLabel>
              <Select
                value={config.unit || 'seconds'}
                label="Unit"
                onChange={(e) => setConfig({ ...config, unit: e.target.value })}
              >
                <MenuItem value="milliseconds">Milliseconds</MenuItem>
                <MenuItem value="seconds">Seconds</MenuItem>
                <MenuItem value="minutes">Minutes</MenuItem>
                <MenuItem value="hours">Hours</MenuItem>
              </Select>
            </FormControl>
          </>
        );

      default:
        return (
          <Alert severity="info">
            This node type has no configurable properties.
          </Alert>
        );
    }
  };

  const getNodeTypeDescription = (nodeType: WorkflowNodeType): string => {
    switch (nodeType) {
      case 'start': return 'Entry point for the workflow execution';
      case 'model': return 'Large Language Model interaction with configurable parameters';
      case 'tool': return 'Execute external tools and functions';
      case 'memory': return 'Manage conversation context and history';
      case 'retrieval': return 'Search and retrieve relevant documents';
      case 'conditional': return 'Branch execution based on conditions';
      case 'loop': return 'Repeat execution with conditions and limits';
      case 'variable': return 'Store, retrieve, and manipulate workflow variables';
      case 'errorHandler': return 'Handle errors and implement retry logic';
      case 'delay': return 'Add time delays to workflow execution';
      default: return 'Workflow node';
    }
  };

  return (
    <Paper 
      sx={{ 
        width: 350, 
        height: '100%', 
        display: 'flex',
        flexDirection: 'column',
        bgcolor: 'background.paper',
      }}
    >
      {/* Header */}
      <Box 
        sx={{ 
          p: 2, 
          borderBottom: 1, 
          borderColor: 'divider',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}
      >
        <Typography variant="h6" component="h2">
          Node Properties
        </Typography>
        <IconButton size="small" onClick={onClose}>
          <CloseIcon />
        </IconButton>
      </Box>

      {/* Content */}
      <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
        {/* Node Info */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" color="primary" sx={{ mb: 1 }}>
            {selectedNode.data.nodeType.toUpperCase()} NODE
          </Typography>
          <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
            {getNodeTypeDescription(selectedNode.data.nodeType)}
          </Typography>
          <TextField
            fullWidth
            label="Node Label"
            value={label}
            onChange={(e) => setLabel(e.target.value)}
            sx={{ mb: 2 }}
          />
        </Box>

        <Divider sx={{ mb: 2 }} />

        {/* Configuration */}
        <Accordion defaultExpanded>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="subtitle1">Configuration</Typography>
          </AccordionSummary>
          <AccordionDetails>
            {renderNodeTypeSpecificControls()}
          </AccordionDetails>
        </Accordion>

        {/* Advanced Settings */}
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="subtitle1">Advanced Settings</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <FormControlLabel
              control={
                <Switch
                  checked={config.enabled !== false}
                  onChange={(e) => setConfig({ ...config, enabled: e.target.checked })}
                />
              }
              label="Enable Node"
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Timeout (seconds)"
              type="number"
              value={config.timeout || 30}
              onChange={(e) => setConfig({ ...config, timeout: parseInt(e.target.value) || 30 })}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Retry Attempts"
              type="number"
              value={config.retries || 1}
              onChange={(e) => setConfig({ ...config, retries: parseInt(e.target.value) || 1 })}
              sx={{ mb: 2 }}
            />
          </AccordionDetails>
        </Accordion>
      </Box>
    </Paper>
  );
};

export default PropertiesPanel;