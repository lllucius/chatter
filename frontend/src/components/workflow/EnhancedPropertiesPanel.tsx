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
  Button,
  Tooltip,
  Stack,
  Autocomplete,
  Card,
  CardContent,
  CardHeader,
  useTheme,
} from '@mui/material';
import {
  Close as CloseIcon,
  ExpandMore as ExpandMoreIcon,
  Help as HelpIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Settings as SettingsIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { Node, Edge } from '@xyflow/react';
import { 
  WorkflowNodeData, 
  WorkflowEdgeData, 
  PropertiesPanelProps,
  NodeConfig,
  WorkflowNodeType
} from './types';
import { nodeDefinitions, NodePropertyDefinition } from './NodePalette';

const EnhancedPropertiesPanel: React.FC<PropertiesPanelProps> = ({
  selectedNode,
  selectedEdge,
  onNodeUpdate,
  onEdgeUpdate,
  onClose,
  width = 350,
  isMobile = false,
}) => {
  const theme = useTheme();
  const [config, setConfig] = useState<NodeConfig>({});
  const [label, setLabel] = useState('');
  const [description, setDescription] = useState('');
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    basic: true,
    advanced: false,
    validation: false,
    metadata: false,
  });

  // Get node definition for the selected node
  const nodeDefinition = selectedNode 
    ? nodeDefinitions.find(def => def.type === selectedNode.data.nodeType)
    : null;

  // Sync with selected node/edge
  useEffect(() => {
    if (selectedNode) {
      setConfig(selectedNode.data.config || {});
      setLabel(selectedNode.data.label || '');
      setDescription(selectedNode.data.description || '');
    } else if (selectedEdge) {
      setLabel(selectedEdge.data?.label || '');
      setDescription((selectedEdge.data?.description as string) || '');
    }
  }, [selectedNode, selectedEdge]);

  // Update node with current values
  const handleUpdate = useCallback(() => {
    if (selectedNode && onNodeUpdate) {
      onNodeUpdate(selectedNode.id, {
        ...selectedNode.data,
        label,
        description,
        config,
      });
    } else if (selectedEdge && onEdgeUpdate) {
      onEdgeUpdate(selectedEdge.id, {
        ...selectedEdge.data,
        label,
        description,
      });
    }
  }, [selectedNode, selectedEdge, label, description, config, onNodeUpdate, onEdgeUpdate]);

  // Auto-update with debounce
  useEffect(() => {
    const timeoutId = setTimeout(handleUpdate, 300);
    return () => clearTimeout(timeoutId);
  }, [handleUpdate]);

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  const renderPropertyField = (property: NodePropertyDefinition) => {
    const value = config[property.name];

    switch (property.type) {
      case 'string':
        return (
          <TextField
            fullWidth
            label={property.label}
            value={value || property.default || ''}
            onChange={(e) => setConfig(prev => ({ ...prev, [property.name]: e.target.value }))}
            required={property.required}
            helperText={property.description}
            size="small"
          />
        );

      case 'textarea':
        return (
          <TextField
            fullWidth
            label={property.label}
            value={value || property.default || ''}
            onChange={(e) => setConfig(prev => ({ ...prev, [property.name]: e.target.value }))}
            required={property.required}
            helperText={property.description}
            multiline
            rows={3}
            size="small"
          />
        );

      case 'number':
        return (
          <TextField
            fullWidth
            label={property.label}
            type="number"
            value={value ?? property.default ?? ''}
            onChange={(e) => setConfig(prev => ({ 
              ...prev, 
              [property.name]: e.target.value ? Number(e.target.value) : undefined 
            }))}
            required={property.required}
            helperText={property.description}
            inputProps={{ 
              min: property.min, 
              max: property.max,
              step: property.step,
            }}
            size="small"
          />
        );

      case 'boolean':
        return (
          <FormControlLabel
            control={
              <Switch
                checked={Boolean(value ?? property.default ?? false)}
                onChange={(e) => setConfig(prev => ({ 
                  ...prev, 
                  [property.name]: e.target.checked 
                }))}
              />
            }
            label={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="body2">{property.label}</Typography>
                {property.description && (
                  <Tooltip title={property.description} arrow>
                    <HelpIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                  </Tooltip>
                )}
              </Box>
            }
          />
        );

      case 'select':
        return (
          <FormControl fullWidth size="small">
            <InputLabel>{property.label}</InputLabel>
            <Select
              value={value || property.default || ''}
              label={property.label}
              onChange={(e) => setConfig(prev => ({ 
                ...prev, 
                [property.name]: e.target.value 
              }))}
              required={property.required}
            >
              {property.options?.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </Select>
            {property.description && (
              <Typography variant="caption" color="textSecondary" sx={{ mt: 0.5 }}>
                {property.description}
              </Typography>
            )}
          </FormControl>
        );

      case 'multiselect':
        return (
          <Autocomplete
            multiple
            options={property.options || []}
            getOptionLabel={(option) => option.label}
            value={property.options?.filter(opt => 
              Array.isArray(value) && value.includes(opt.value)
            ) || []}
            onChange={(_, newValue) => setConfig(prev => ({ 
              ...prev, 
              [property.name]: newValue.map(v => v.value)
            }))}
            renderTags={(tagValue, getTagProps) =>
              tagValue.map((option, index) => (
                <Chip
                  variant="outlined"
                  label={option.label}
                  {...getTagProps({ index })}
                  key={option.value}
                  size="small"
                />
              ))
            }
            renderInput={(params) => (
              <TextField
                {...params}
                label={property.label}
                helperText={property.description}
                size="small"
              />
            )}
            size="small"
          />
        );

      case 'slider':
        const sliderValue = Number(value ?? property.default ?? 0);
        return (
          <Box>
            <Typography gutterBottom variant="body2" color="textSecondary">
              {property.label}: {sliderValue}
            </Typography>
            <Slider
              value={sliderValue}
              onChange={(_, newValue) => setConfig(prev => ({
                ...prev,
                [property.name]: Array.isArray(newValue) ? newValue[0] : newValue,
              }))}
              min={property.min || 0}
              max={property.max || 100}
              step={property.step || 1}
              marks={property.min !== undefined && property.max !== undefined ? [
                { value: property.min, label: String(property.min) },
                { value: property.max, label: String(property.max) },
              ] : undefined}
              sx={{ mx: 1 }}
            />
            {property.description && (
              <Typography variant="caption" color="textSecondary">
                {property.description}
              </Typography>
            )}
          </Box>
        );

      default:
        return null;
    }
  };

  const renderBasicProperties = () => {
    if (!selectedNode && !selectedEdge) return null;

    return (
      <Stack spacing={2}>
        <TextField
          fullWidth
          label="Name"
          value={label}
          onChange={(e) => setLabel(e.target.value)}
          size="small"
          required
        />
        <TextField
          fullWidth
          label="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          multiline
          rows={2}
          size="small"
          helperText="Optional description for documentation"
        />
      </Stack>
    );
  };

  const renderNodeSpecificProperties = () => {
    if (!selectedNode || !nodeDefinition) return null;

    // Group properties by category
    const basicProps = nodeDefinition.properties.filter(p => 
      ['name', 'description'].includes(p.name) || p.required
    );
    const advancedProps = nodeDefinition.properties.filter(p => 
      !['name', 'description'].includes(p.name) && !p.required
    );

    return (
      <>
        {basicProps.length > 0 && (
          <Accordion 
            expanded={expandedSections.basic} 
            onChange={() => toggleSection('basic')}
          >
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle2">Basic Configuration</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Stack spacing={2}>
                {basicProps.map((property) => (
                  <Box key={property.name}>
                    {renderPropertyField(property)}
                  </Box>
                ))}
              </Stack>
            </AccordionDetails>
          </Accordion>
        )}

        {advancedProps.length > 0 && (
          <Accordion 
            expanded={expandedSections.advanced} 
            onChange={() => toggleSection('advanced')}
          >
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle2">Advanced Configuration</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Stack spacing={2}>
                {advancedProps.map((property) => (
                  <Box key={property.name}>
                    {renderPropertyField(property)}
                  </Box>
                ))}
              </Stack>
            </AccordionDetails>
          </Accordion>
        )}
      </>
    );
  };

  const renderValidationInfo = () => {
    if (!selectedNode) return null;

    // Basic validation rules based on node type
    const validationRules = [];
    
    if (selectedNode.data.nodeType === 'model') {
      if (!config.model) validationRules.push('Model selection is required');
      if (config.temperature && (config.temperature < 0 || config.temperature > 2)) {
        validationRules.push('Temperature must be between 0 and 2');
      }
    }
    
    if (selectedNode.data.nodeType === 'conditional' && !config.condition) {
      validationRules.push('Condition expression is required');
    }

    return (
      <Accordion 
        expanded={expandedSections.validation} 
        onChange={() => toggleSection('validation')}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="subtitle2">
            Validation {validationRules.length > 0 && (
              <Chip 
                label={validationRules.length} 
                size="small" 
                color="error" 
                sx={{ ml: 1 }}
              />
            )}
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          {validationRules.length > 0 ? (
            <Alert severity="error" sx={{ mb: 2 }}>
              <Typography variant="body2" component="div">
                Issues found:
                <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
                  {validationRules.map((rule, index) => (
                    <li key={index}>{rule}</li>
                  ))}
                </ul>
              </Typography>
            </Alert>
          ) : (
            <Alert severity="success">
              <Typography variant="body2">
                No validation issues found
              </Typography>
            </Alert>
          )}
        </AccordionDetails>
      </Accordion>
    );
  };

  const renderMetadataInfo = () => {
    if (!selectedNode) return null;

    return (
      <Accordion 
        expanded={expandedSections.metadata} 
        onChange={() => toggleSection('metadata')}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="subtitle2">Metadata & Info</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Stack spacing={1}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="body2" color="textSecondary">Node Type:</Typography>
              <Chip label={selectedNode.data.nodeType} size="small" />
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="body2" color="textSecondary">Node ID:</Typography>
              <Typography variant="body2" fontFamily="monospace">
                {selectedNode.id}
              </Typography>
            </Box>
            {selectedNode.position && (
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2" color="textSecondary">Position:</Typography>
                <Typography variant="body2" fontFamily="monospace">
                  ({Math.round(selectedNode.position.x)}, {Math.round(selectedNode.position.y)})
                </Typography>
              </Box>
            )}
            {nodeDefinition && (
              <>
                <Divider sx={{ my: 1 }} />
                <Typography variant="body2" color="textSecondary">
                  {nodeDefinition.description}
                </Typography>
                <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mt: 1 }}>
                  <Chip 
                    label={nodeDefinition.category} 
                    size="small" 
                    variant="outlined"
                    sx={{ 
                      borderColor: nodeDefinition.color,
                      color: nodeDefinition.color,
                    }}
                  />
                </Box>
              </>
            )}
          </Stack>
        </AccordionDetails>
      </Accordion>
    );
  };

  if (!selectedNode && !selectedEdge) {
    return (
      <Paper
        sx={{
          width,
          height: '100%',
          p: 3,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          borderRadius: 0,
          borderLeft: `1px solid ${theme.palette.divider}`,
        }}
      >
        <InfoIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h6" color="textSecondary" align="center">
          No Selection
        </Typography>
        <Typography variant="body2" color="textSecondary" align="center" sx={{ mt: 1 }}>
          Select a node or edge to edit its properties
        </Typography>
      </Paper>
    );
  }

  return (
    <Paper
      sx={{
        width,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        borderRadius: 0,
        borderLeft: `1px solid ${theme.palette.divider}`,
      }}
    >
      {/* Header */}
      <Box sx={{ 
        p: 2, 
        borderBottom: `1px solid ${theme.palette.divider}`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <SettingsIcon color="primary" />
          <Typography variant="h6">
            {selectedNode ? 'Node Properties' : 'Edge Properties'}
          </Typography>
        </Box>
        <IconButton onClick={onClose} size="small">
          <CloseIcon />
        </IconButton>
      </Box>

      {/* Content */}
      <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
        <Stack spacing={2}>
          {/* Basic properties for all items */}
          <Card variant="outlined">
            <CardHeader 
              title="Basic Properties" 
              titleTypographyProps={{ variant: 'subtitle2' }}
              sx={{ pb: 1 }}
            />
            <CardContent sx={{ pt: 0 }}>
              {renderBasicProperties()}
            </CardContent>
          </Card>

          {/* Node-specific properties */}
          {selectedNode && (
            <>
              {renderNodeSpecificProperties()}
              {renderValidationInfo()}
              {renderMetadataInfo()}
            </>
          )}

          {/* Edge-specific properties */}
          {selectedEdge && (
            <Card variant="outlined">
              <CardHeader 
                title="Edge Configuration" 
                titleTypographyProps={{ variant: 'subtitle2' }}
                sx={{ pb: 1 }}
              />
              <CardContent sx={{ pt: 0 }}>
                <Stack spacing={2}>
                  <TextField
                    fullWidth
                    label="Condition"
                    value={selectedEdge.data?.condition || ''}
                    onChange={(e) => onEdgeUpdate?.(selectedEdge.id, {
                      ...selectedEdge.data,
                      condition: e.target.value,
                    })}
                    multiline
                    rows={2}
                    size="small"
                    helperText="Optional condition for this connection"
                  />
                  <FormControl fullWidth size="small">
                    <InputLabel>Edge Type</InputLabel>
                    <Select
                      value={selectedEdge.data?.metadata?.type || 'default'}
                      label="Edge Type"
                      onChange={(e) => onEdgeUpdate?.(selectedEdge.id, {
                        ...selectedEdge.data,
                        metadata: {
                          ...selectedEdge.data?.metadata,
                          type: e.target.value,
                        },
                      })}
                    >
                      <MenuItem value="default">Default</MenuItem>
                      <MenuItem value="success">Success</MenuItem>
                      <MenuItem value="error">Error</MenuItem>
                      <MenuItem value="conditional">Conditional</MenuItem>
                    </Select>
                  </FormControl>
                </Stack>
              </CardContent>
            </Card>
          )}
        </Stack>
      </Box>
    </Paper>
  );
};

export default EnhancedPropertiesPanel;