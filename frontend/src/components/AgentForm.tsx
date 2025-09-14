import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Chip,
  Typography,
  Switch,
  FormControlLabel,
  Grid,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Tooltip,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { AgentCreateRequest, AgentUpdateRequest, AgentResponse, AgentType, AgentStatus } from 'chatter-sdk';
import { CrudFormProps } from './CrudDataTable';

interface AgentFormProps extends CrudFormProps<AgentCreateRequest, AgentUpdateRequest> {}

interface Tool {
  name: string;
  description?: string;
  enabled: boolean;
}

interface AgentCapability {
  name: string;
  enabled: boolean;
  config?: Record<string, unknown>;
}

const AgentForm: React.FC<AgentFormProps> = ({
  open,
  mode,
  initialData,
  onClose,
  onSubmit,
}) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    type: 'conversational' as 'conversational' | 'task_oriented' | 'analytical' | 'creative',
    status: 'active' as 'active' | 'inactive' | 'training',
    primary_llm: 'gpt-4',
    fallback_llm: '',
    system_prompt: '',
    personality: '',
    expertise_areas: [] as string[],
    max_iterations: 10,
    temperature: 0.7,
    max_tokens: 1000,
    timeout_seconds: 30,
    memory_enabled: true,
    memory_window: 20,
    tools: [] as Tool[],
    capabilities: [] as AgentCapability[],
    knowledge_sources: [] as string[],
    safety_filters: true,
    audit_enabled: true,
    is_active: true,
  });

  const [expertiseInput, setExpertiseInput] = useState('');
  const [saving, setSaving] = useState(false);
  const [expandedSections, setExpandedSections] = useState({
    basic: true,
    behavior: false,
    llm: false,
    tools: false,
    capabilities: false,
    knowledge: false,
    advanced: false,
  });

  // Available options
  const agentTypes = [
    { value: 'conversational', label: 'Conversational', description: 'General-purpose chat agent' },
    { value: 'task_oriented', label: 'Task-Oriented', description: 'Focused on specific tasks' },
    { value: 'analytical', label: 'Analytical', description: 'Data analysis and insights' },
    { value: 'creative', label: 'Creative', description: 'Content creation and ideation' },
  ];

  const agentStatuses = [
    { value: 'active', label: 'Active', color: 'success' },
    { value: 'inactive', label: 'Inactive', color: 'default' },
    { value: 'training', label: 'Training', color: 'warning' },
  ];

  const llmModels = [
    'gpt-4',
    'gpt-4-turbo',
    'gpt-3.5-turbo',
    'claude-3-opus',
    'claude-3-sonnet',
    'claude-3-haiku',
    'gemini-pro',
    'llama-3-70b',
    'mistral-large',
  ];

  const defaultCapabilities = [
    { name: 'natural_language', description: 'Natural language understanding and generation' },
    { name: 'memory', description: 'Remember conversation context and history' },
    { name: 'code_generation', description: 'Generate and understand code' },
    { name: 'tool_use', description: 'Use external tools and APIs' },
    { name: 'analytical', description: 'Analyze data and provide insights' },
    { name: 'creative', description: 'Creative content generation' },
    { name: 'research', description: 'Research and information gathering' },
    { name: 'support', description: 'Customer support and assistance' },
  ];

  useEffect(() => {
    if (open) {
      if (mode === 'edit' && initialData) {
        const agent = initialData as AgentResponse;
        setFormData({
          name: agent.name || '',
          description: agent.description || '',
          type: agent.type || 'conversational',
          status: agent.status || 'active',
          primary_llm: agent.primary_llm || 'gpt-4',
          fallback_llm: agent.fallback_llm || '',
          system_prompt: agent.system_prompt || '',
          personality: agent.personality || '',
          expertise_areas: agent.expertise_areas || [],
          max_iterations: agent.max_iterations || 10,
          temperature: agent.temperature || 0.7,
          max_tokens: agent.max_tokens || 1000,
          timeout_seconds: agent.timeout_seconds || 30,
          memory_enabled: agent.memory_enabled ?? true,
          memory_window: agent.memory_window || 20,
          tools: agent.tools?.map(t => ({ 
            name: t.name || '', 
            description: t.description,
            enabled: t.enabled ?? true 
          })) || [],
          capabilities: agent.capabilities?.map(c => ({
            name: c.name || '',
            enabled: c.enabled ?? true,
            config: c.config || {}
          })) || [],
          knowledge_sources: agent.knowledge_sources || [],
          safety_filters: agent.safety_filters ?? true,
          audit_enabled: agent.audit_enabled ?? true,
          is_active: agent.is_active ?? true,
        });
      } else {
        // Reset form for create mode
        setFormData({
          name: '',
          description: '',
          type: 'conversational',
          status: 'active',
          primary_llm: 'gpt-4',
          fallback_llm: '',
          system_prompt: '',
          personality: '',
          expertise_areas: [],
          max_iterations: 10,
          temperature: 0.7,
          max_tokens: 1000,
          timeout_seconds: 30,
          memory_enabled: true,
          memory_window: 20,
          tools: [],
          capabilities: [],
          knowledge_sources: [],
          safety_filters: true,
          audit_enabled: true,
          is_active: true,
        });
      }
    }
  }, [open, mode, initialData]);

  const handleSubmit = async () => {
    setSaving(true);
    try {
      const submitData: AgentCreateRequest = {
        name: formData.name,
        description: formData.description,
        agent_type: formData.type,  // Fix: use agent_type instead of type
        status: formData.status,
        primary_llm: formData.primary_llm,
        fallback_llm: formData.fallback_llm || undefined,
        system_prompt: formData.system_prompt,
        personality: formData.personality || undefined,
        expertise_areas: formData.expertise_areas,
        max_iterations: formData.max_iterations,
        temperature: formData.temperature,
        max_tokens: formData.max_tokens,
        timeout_seconds: formData.timeout_seconds,
        memory_enabled: formData.memory_enabled,
        memory_window: formData.memory_window,
        tools: formData.tools,
        capabilities: formData.capabilities.map(cap => cap.name),  // Fix: send only capability names as strings
        knowledge_sources: formData.knowledge_sources,
        safety_filters: formData.safety_filters,
        audit_enabled: formData.audit_enabled,
        is_active: formData.is_active,
      };

      await onSubmit(submitData);
    } catch {
      // Error saving agent - handled gracefully by finally block
    } finally {
      setSaving(false);
    }
  };

  const addExpertiseArea = () => {
    if (expertiseInput.trim() && !formData.expertise_areas.includes(expertiseInput.trim())) {
      setFormData({
        ...formData,
        expertise_areas: [...formData.expertise_areas, expertiseInput.trim()]
      });
      setExpertiseInput('');
    }
  };

  const removeExpertiseArea = (area: string) => {
    setFormData({
      ...formData,
      expertise_areas: formData.expertise_areas.filter(e => e !== area)
    });
  };

  // TODO: Implement tool management functionality
  // const addTool = () => {
  //   if (toolInput.name.trim()) {
  //     setFormData({
  //       ...formData,
  //       tools: [...formData.tools, { ...toolInput, enabled: true }]
  //     });
  //     setToolInput({ name: '', description: '' });
  //   }
  // };

  // const removeTool = (index: number) => {
  //   setFormData({
  //     ...formData,
  //     tools: formData.tools.filter((_, i) => i !== index)
  //   });
  // };

  const toggleCapability = (capabilityName: string) => {
    const exists = formData.capabilities.find(c => c.name === capabilityName);
    if (exists) {
      setFormData({
        ...formData,
        capabilities: formData.capabilities.filter(c => c.name !== capabilityName)
      });
    } else {
      setFormData({
        ...formData,
        capabilities: [...formData.capabilities, { name: capabilityName, enabled: true }]
      });
    }
  };

  const handleSectionToggle = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section as keyof typeof prev]
    }));
  };

  const isFormValid = formData.name.trim().length > 0 && formData.primary_llm.trim().length > 0;

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="lg" 
      fullWidth
      PaperProps={{
        sx: { height: '90vh', maxHeight: '900px' }
      }}
    >
      <DialogTitle>
        {mode === 'edit' ? 'Edit Agent' : 'Create New Agent'}
      </DialogTitle>
      
      <DialogContent sx={{ overflow: 'auto' }}>
        <Box sx={{ pt: 1 }}>
          {/* Basic Information */}
          <Accordion 
            expanded={expandedSections.basic}
            onChange={() => handleSectionToggle('basic')}
            sx={{ mb: 2 }}
          >
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">Basic Information</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Agent Name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth>
                    <InputLabel>Agent Type</InputLabel>
                    <Select
                      value={formData.type}
                      onChange={(e) => setFormData({ ...formData, type: e.target.value as AgentType })}
                      label="Agent Type"
                    >
                      {agentTypes.map((type): void => (
                        <MenuItem key={type.value} value={type.value}>
                          <Tooltip title={type.description}>
                            <span>{type.label}</span>
                          </Tooltip>
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    multiline
                    rows={3}
                    label="Description"
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    placeholder="Describe what this agent does and its primary purpose..."
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth>
                    <InputLabel>Status</InputLabel>
                    <Select
                      value={formData.status}
                      onChange={(e) => setFormData({ ...formData, status: e.target.value as AgentStatus })}
                      label="Status"
                    >
                      {agentStatuses.map((status): void => (
                        <MenuItem key={status.value} value={status.value}>
                          {status.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={formData.is_active}
                        onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                      />
                    }
                    label="Active"
                  />
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>

          {/* Behavior & Personality */}
          <Accordion 
            expanded={expandedSections.behavior}
            onChange={() => handleSectionToggle('behavior')}
            sx={{ mb: 2 }}
          >
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">Behavior & Personality</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    multiline
                    rows={4}
                    label="System Prompt"
                    value={formData.system_prompt}
                    onChange={(e) => setFormData({ ...formData, system_prompt: e.target.value })}
                    placeholder="Define the agent's role, behavior, and guidelines..."
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    multiline
                    rows={2}
                    label="Personality"
                    value={formData.personality}
                    onChange={(e) => setFormData({ ...formData, personality: e.target.value })}
                    placeholder="Describe the agent's personality traits and communication style..."
                  />
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" gutterBottom>
                    Expertise Areas
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, mb: 1, flexWrap: 'wrap' }}>
                    {formData.expertise_areas.map((area): void => (
                      <Chip
                        key={area}
                        label={area}
                        onDelete={() => removeExpertiseArea(area)}
                        variant="outlined"
                      />
                    ))}
                  </Box>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <TextField
                      size="small"
                      label="Add expertise area"
                      value={expertiseInput}
                      onChange={(e) => setExpertiseInput(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && addExpertiseArea()}
                    />
                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={<AddIcon />}
                      onClick={addExpertiseArea}
                    >
                      Add
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>

          {/* LLM Configuration */}
          <Accordion 
            expanded={expandedSections.llm}
            onChange={() => handleSectionToggle('llm')}
            sx={{ mb: 2 }}
          >
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">LLM Configuration</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth>
                    <InputLabel>Primary LLM</InputLabel>
                    <Select
                      value={formData.primary_llm}
                      onChange={(e) => setFormData({ ...formData, primary_llm: e.target.value })}
                      label="Primary LLM"
                      required
                    >
                      {llmModels.map((model): void => (
                        <MenuItem key={model} value={model}>
                          {model}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth>
                    <InputLabel>Fallback LLM</InputLabel>
                    <Select
                      value={formData.fallback_llm}
                      onChange={(e) => setFormData({ ...formData, fallback_llm: e.target.value })}
                      label="Fallback LLM"
                    >
                      <MenuItem value="">None</MenuItem>
                      {llmModels.map((model): void => (
                        <MenuItem key={model} value={model}>
                          {model}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Temperature"
                    value={formData.temperature}
                    onChange={(e) => setFormData({ ...formData, temperature: parseFloat(e.target.value) })}
                    inputProps={{ min: 0, max: 2, step: 0.1 }}
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Max Tokens"
                    value={formData.max_tokens}
                    onChange={(e) => setFormData({ ...formData, max_tokens: parseInt(e.target.value) })}
                    inputProps={{ min: 1, max: 32000 }}
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Max Iterations"
                    value={formData.max_iterations}
                    onChange={(e) => setFormData({ ...formData, max_iterations: parseInt(e.target.value) })}
                    inputProps={{ min: 1, max: 100 }}
                  />
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>

          {/* Capabilities */}
          <Accordion 
            expanded={expandedSections.capabilities}
            onChange={() => handleSectionToggle('capabilities')}
            sx={{ mb: 2 }}
          >
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">Capabilities</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                {defaultCapabilities.map((capability): void => (
                  <Grid item xs={12} sm={6} md={4} key={capability.name}>
                    <Box
                      sx={{
                        p: 2,
                        border: '1px solid',
                        borderColor: formData.capabilities.find(c => c.name === capability.name) 
                          ? 'primary.main' 
                          : 'divider',
                        borderRadius: 1,
                        cursor: 'pointer',
                        bgcolor: formData.capabilities.find(c => c.name === capability.name) 
                          ? 'primary.50' 
                          : 'transparent',
                      }}
                      onClick={() => toggleCapability(capability.name)}
                    >
                      <Typography variant="subtitle2" gutterBottom>
                        {capability.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {capability.description}
                      </Typography>
                    </Box>
                  </Grid>
                ))}
              </Grid>
            </AccordionDetails>
          </Accordion>

          {/* Advanced Settings */}
          <Accordion 
            expanded={expandedSections.advanced}
            onChange={() => handleSectionToggle('advanced')}
            sx={{ mb: 2 }}
          >
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">Advanced Settings</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={formData.memory_enabled}
                        onChange={(e) => setFormData({ ...formData, memory_enabled: e.target.checked })}
                      />
                    }
                    label="Memory Enabled"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Memory Window"
                    value={formData.memory_window}
                    onChange={(e) => setFormData({ ...formData, memory_window: parseInt(e.target.value) })}
                    inputProps={{ min: 1, max: 100 }}
                    disabled={!formData.memory_enabled}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Timeout (seconds)"
                    value={formData.timeout_seconds}
                    onChange={(e) => setFormData({ ...formData, timeout_seconds: parseInt(e.target.value) })}
                    inputProps={{ min: 1, max: 300 }}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={formData.safety_filters}
                        onChange={(e) => setFormData({ ...formData, safety_filters: e.target.checked })}
                      />
                    }
                    label="Safety Filters"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={formData.audit_enabled}
                        onChange={(e) => setFormData({ ...formData, audit_enabled: e.target.checked })}
                      />
                    }
                    label="Audit Logging"
                  />
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
        </Box>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} disabled={saving}>
          Cancel
        </Button>
        <Button 
          onClick={handleSubmit} 
          variant="contained"
          disabled={!isFormValid || saving}
        >
          {saving ? 'Saving...' : mode === 'edit' ? 'Update Agent' : 'Create Agent'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default AgentForm;