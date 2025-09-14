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
import { AgentCreateRequest, AgentUpdateRequest, AgentResponse, AgentType, AgentStatus, AgentCapability } from 'chatter-sdk';
import { CrudFormProps } from './CrudDataTable';

interface AgentFormProps extends CrudFormProps<AgentCreateRequest, AgentUpdateRequest> {}

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
    agent_type: AgentType.conversational,  // Use correct SDK enum
    status: AgentStatus.active,  // Use correct SDK enum  
    primary_llm: 'gpt-4',
    fallback_llm: '',
    system_prompt: '',
    personality_traits: [] as string[],
    knowledge_domains: [] as string[],
    response_style: 'professional',
    max_conversation_length: 50,
    temperature: 0.7,
    max_tokens: 1000,
    response_timeout: 30,
    learning_enabled: true,
    feedback_weight: 0.1,
    adaptation_threshold: 0.8,
    available_tools: [] as string[],
    capabilities: [] as AgentCapability[],  // Use correct SDK enum array
    tags: [] as string[],
    metadata: {} as Record<string, unknown>,
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
    { value: AgentType.conversational, label: 'Conversational', description: 'General-purpose chat agent' },
    { value: AgentType.task_oriented, label: 'Task-Oriented', description: 'Focused on specific tasks' },
    { value: AgentType.analytical, label: 'Analytical', description: 'Data analysis and insights' },
    { value: AgentType.creative, label: 'Creative', description: 'Content creation and ideation' },
    { value: AgentType.research, label: 'Research', description: 'Research and information gathering' },
    { value: AgentType.support, label: 'Support', description: 'Customer support and assistance' },
    { value: AgentType.specialized, label: 'Specialized', description: 'Domain-specific expertise' },
  ];

  const agentStatuses = [
    { value: AgentStatus.active, label: 'Active', color: 'success' },
    { value: AgentStatus.inactive, label: 'Inactive', color: 'default' },
    { value: AgentStatus.training, label: 'Training', color: 'warning' },
    { value: AgentStatus.error, label: 'Error', color: 'error' },
    { value: AgentStatus.maintenance, label: 'Maintenance', color: 'warning' },
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
    { value: AgentCapability.natural_language, description: 'Natural language understanding and generation' },
    { value: AgentCapability.memory, description: 'Remember conversation context and history' },
    { value: AgentCapability.code_generation, description: 'Generate and understand code' },
    { value: AgentCapability.tool_use, description: 'Use external tools and APIs' },
    { value: AgentCapability.analytical, description: 'Analyze data and provide insights' },
    { value: AgentCapability.creative, description: 'Creative content generation' },
    { value: AgentCapability.research, description: 'Research and information gathering' },
    { value: AgentCapability.support, description: 'Customer support and assistance' },
  ];

  useEffect(() => {
    if (open) {
      if (mode === 'edit' && initialData) {
        const agent = initialData as AgentResponse;
        setFormData({
          name: agent.name || '',
          description: agent.description || '',
          agent_type: agent.type || AgentType.conversational,
          status: agent.status || AgentStatus.active,
          primary_llm: agent.primary_llm || 'gpt-4',
          fallback_llm: agent.fallback_llm || '',
          system_prompt: agent.system_message || '',
          personality_traits: agent.personality_traits || [],
          knowledge_domains: agent.knowledge_domains || [],
          response_style: agent.response_style || 'professional',
          max_conversation_length: agent.max_conversation_length || 50,
          temperature: agent.temperature || 0.7,
          max_tokens: agent.max_tokens || 1000,
          response_timeout: agent.response_timeout || 30,
          learning_enabled: agent.learning_enabled ?? true,
          feedback_weight: agent.feedback_weight || 0.1,
          adaptation_threshold: agent.adaptation_threshold || 0.8,
          available_tools: agent.available_tools || [],
          capabilities: agent.capabilities || [],
          tags: agent.tags || [],
          metadata: agent.metadata || {},
        });
      } else {
        // Reset form for create mode
        setFormData({
          name: '',
          description: '',
          agent_type: AgentType.conversational,
          status: AgentStatus.active,
          primary_llm: 'gpt-4',
          fallback_llm: '',
          system_prompt: '',
          personality_traits: [],
          knowledge_domains: [],
          response_style: 'professional',
          max_conversation_length: 50,
          temperature: 0.7,
          max_tokens: 1000,
          response_timeout: 30,
          learning_enabled: true,
          feedback_weight: 0.1,
          adaptation_threshold: 0.8,
          available_tools: [],
          capabilities: [],
          tags: [],
          metadata: {},
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
        agent_type: formData.agent_type,  // Correct field name
        system_prompt: formData.system_prompt,  // Correct field name
        personality_traits: formData.personality_traits,
        knowledge_domains: formData.knowledge_domains,
        response_style: formData.response_style,
        capabilities: formData.capabilities,  // Already correct format - enum array
        available_tools: formData.available_tools,
        primary_llm: formData.primary_llm,
        fallback_llm: formData.fallback_llm || undefined,
        temperature: formData.temperature,
        max_tokens: formData.max_tokens,
        max_conversation_length: formData.max_conversation_length,
        context_window_size: 4000,  // Default value
        response_timeout: formData.response_timeout,
        learning_enabled: formData.learning_enabled,
        feedback_weight: formData.feedback_weight,
        adaptation_threshold: formData.adaptation_threshold,
        tags: formData.tags,
        metadata: formData.metadata,
      };

      await onSubmit(submitData);
    } catch {
      // Error saving agent - handled gracefully by finally block
    } finally {
      setSaving(false);
    }
  };

  const addExpertiseArea = () => {
    if (expertiseInput.trim() && !formData.knowledge_domains.includes(expertiseInput.trim())) {
      setFormData({
        ...formData,
        knowledge_domains: [...formData.knowledge_domains, expertiseInput.trim()]
      });
      setExpertiseInput('');
    }
  };

  const removeExpertiseArea = (area: string) => {
    setFormData({
      ...formData,
      knowledge_domains: formData.knowledge_domains.filter(e => e !== area)
    });
  };

  const toggleCapability = (capability: AgentCapability) => {
    const exists = formData.capabilities.includes(capability);
    if (exists) {
      setFormData({
        ...formData,
        capabilities: formData.capabilities.filter(c => c !== capability)
      });
    } else {
      setFormData({
        ...formData,
        capabilities: [...formData.capabilities, capability]
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
                      value={formData.agent_type}
                      onChange={(e) => setFormData({ ...formData, agent_type: e.target.value as AgentType })}
                      label="Agent Type"
                    >
                      {agentTypes.map((type) => (
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
                      {agentStatuses.map((status) => (
                        <MenuItem key={status.value} value={status.value}>
                          {status.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
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
                    {formData.knowledge_domains.map((area) => (
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
                      {llmModels.map((model) => (
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
                      {llmModels.map((model) => (
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
                    label="Max Conversation Length"
                    value={formData.max_conversation_length}
                    onChange={(e) => setFormData({ ...formData, max_conversation_length: parseInt(e.target.value) })}
                    inputProps={{ min: 1, max: 1000 }}
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
                {defaultCapabilities.map((capability) => (
                  <Grid item xs={12} sm={6} md={4} key={capability.value}>
                    <Box
                      sx={{
                        p: 2,
                        border: '1px solid',
                        borderColor: formData.capabilities.includes(capability.value) 
                          ? 'primary.main' 
                          : 'divider',
                        borderRadius: 1,
                        cursor: 'pointer',
                        bgcolor: formData.capabilities.includes(capability.value) 
                          ? 'primary.50' 
                          : 'transparent',
                      }}
                      onClick={() => toggleCapability(capability.value)}
                    >
                      <Typography variant="subtitle2" gutterBottom>
                        {capability.value.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
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
                  <TextField
                    fullWidth
                    type="number"
                    label="Response Timeout (seconds)"
                    value={formData.response_timeout}
                    onChange={(e) => setFormData({ ...formData, response_timeout: parseInt(e.target.value) })}
                    inputProps={{ min: 1, max: 300 }}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={formData.learning_enabled}
                        onChange={(e) => setFormData({ ...formData, learning_enabled: e.target.checked })}
                      />
                    }
                    label="Learning Enabled"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Feedback Weight"
                    value={formData.feedback_weight}
                    onChange={(e) => setFormData({ ...formData, feedback_weight: parseFloat(e.target.value) })}
                    inputProps={{ min: 0, max: 1, step: 0.1 }}
                    disabled={!formData.learning_enabled}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Adaptation Threshold"
                    value={formData.adaptation_threshold}
                    onChange={(e) => setFormData({ ...formData, adaptation_threshold: parseFloat(e.target.value) })}
                    inputProps={{ min: 0, max: 1, step: 0.1 }}
                    disabled={!formData.learning_enabled}
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