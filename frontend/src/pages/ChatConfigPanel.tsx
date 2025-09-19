import React, { useState } from 'react';
import {
  Box,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  FormControlLabel,
  Switch,
  Chip,
  Tooltip,
  IconButton,
  TextField,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  TextSnippet as PromptIcon,
  AccountBox as ProfileIcon,
  Description as DocumentIcon,
  RestartAlt as ResetIcon,
  Build as ToolIcon,
} from '@mui/icons-material';
import {
  ProfileResponse,
  PromptResponse,
  DocumentResponse,
  ConversationResponse,
} from 'chatter-sdk';
import { useRightSidebar } from '../components/RightSidebarContext';

interface Props {
  profiles: ProfileResponse[];
  prompts: PromptResponse[];
  documents: DocumentResponse[];
  currentConversation: ConversationResponse | null;

  selectedProfile: string;
  setSelectedProfile: (id: string) => void;

  selectedPrompt: string;
  setSelectedPrompt: (id: string) => void;

  selectedDocuments: string[];
  setSelectedDocuments: (ids: string[]) => void;

  temperature: number;
  setTemperature: (v: number) => void;

  maxTokens: number;
  setMaxTokens: (v: number) => void;

  enableRetrieval: boolean;
  setEnableRetrieval: (v: boolean) => void;

  enableTools: boolean;
  setEnableTools: (v: boolean) => void;

  customPromptText: string;
  setCustomPromptText: (text: string) => void;

  onSelectConversation: (conversation: ConversationResponse) => void;
}

const ChatConfigPanel: React.FC<Props> = ({
  profiles,
  prompts,
  documents,
  currentConversation: _currentConversation,
  selectedProfile,
  setSelectedProfile,
  selectedPrompt,
  setSelectedPrompt,
  selectedDocuments,
  setSelectedDocuments,
  temperature,
  setTemperature,
  maxTokens,
  setMaxTokens,
  enableRetrieval,
  setEnableRetrieval,
  enableTools,
  setEnableTools,
  customPromptText,
  setCustomPromptText,
  onSelectConversation: _onSelectConversation,
}) => {
  const { collapsed, setCollapsed } = useRightSidebar();
  const [expandedPanel, setExpandedPanel] = useState<string>(() => {
    const saved = localStorage.getItem('chatter_expandedPanel');
    return saved ? saved : 'profile';
  });

  // Default values for reset functionality
  const defaultValues = {
    temperature: 0.7,
    maxTokens: 2048,
    enableRetrieval: true,
  };

  const handlePanelChange =
    (panel: string) => (_: React.SyntheticEvent, isExpanded: boolean) => {
      const newPanel = isExpanded ? panel : '';
      setExpandedPanel(newPanel);
      localStorage.setItem('chatter_expandedPanel', newPanel);
    };

  // Reset functions for each panel
  const resetProfileSettings = () => {
    setTemperature(defaultValues.temperature);
    setMaxTokens(defaultValues.maxTokens);
    if (profiles.length > 0) {
      setSelectedProfile(profiles[0].id);
    }
  };

  const resetPromptSettings = () => {
    setSelectedPrompt('');
    setCustomPromptText('');
  };

  const resetToolSettings = () => {
    setEnableTools(false);
  };

  // Handle profile selection and populate settings from profile
  const handleProfileChange = (profileId: string) => {
    setSelectedProfile(profileId);
    
    // Find the selected profile and populate settings
    const profile = profiles.find(p => p.id === profileId);
    if (profile) {
      setTemperature(profile.temperature || 0.7);
      setMaxTokens(profile.max_tokens || 1000);
      setEnableRetrieval(profile.enable_retrieval || false);
      setEnableTools(profile.enable_tools || false);
    }
  };

  // Handle prompt selection and populate custom prompt text
  const handlePromptChange = (promptId: string) => {
    setSelectedPrompt(promptId);
    
    // Find the selected prompt and populate custom text
    const prompt = prompts.find(p => p.id === promptId);
    if (prompt && prompt.content) {
      setCustomPromptText(prompt.content);
    } else if (!promptId) {
      // Clear custom text when no prompt is selected
      setCustomPromptText('');
    }
  };

  const resetKnowledgeSettings = () => {
    setEnableRetrieval(defaultValues.enableRetrieval);
    setSelectedDocuments([]);
  };

  if (collapsed) {
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, mt: 1 }}>
        <Tooltip title="Profile Settings" placement="left">
          <IconButton
            onClick={() => {
              setCollapsed(false);
              setExpandedPanel('profile');
              localStorage.setItem('chatter_expandedPanel', 'profile');
            }}
            sx={{ borderRadius: 1 }}
          >
            <ProfileIcon />
          </IconButton>
        </Tooltip>
        <Tooltip title="Prompt Templates" placement="left">
          <IconButton
            onClick={() => {
              setCollapsed(false);
              setExpandedPanel('prompts');
              localStorage.setItem('chatter_expandedPanel', 'prompts');
            }}
            sx={{ borderRadius: 1 }}
          >
            <PromptIcon />
          </IconButton>
        </Tooltip>
        <Tooltip title="Knowledge Base" placement="left">
          <IconButton
            onClick={() => {
              setCollapsed(false);
              setExpandedPanel('knowledge');
              localStorage.setItem('chatter_expandedPanel', 'knowledge');
            }}
            sx={{ borderRadius: 1 }}
          >
            <DocumentIcon />
          </IconButton>
        </Tooltip>
        <Tooltip title="Tool Settings" placement="left">
          <IconButton
            onClick={() => {
              setCollapsed(false);
              setExpandedPanel('tools');
              localStorage.setItem('chatter_expandedPanel', 'tools');
            }}
            sx={{ borderRadius: 1 }}
          >
            <ToolIcon />
          </IconButton>
        </Tooltip>
      </Box>
    );
  }

  return (
    <Box>
      {/* Profile */}
      <Accordion
        expanded={expandedPanel === 'profile'}
        onChange={handlePanelChange('profile')}
        sx={{ position: 'relative' }}
      >
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
          sx={{
            '& .MuiAccordionSummary-content': {
              alignItems: 'center',
            },
          }}
        >
          <ProfileIcon sx={{ mr: 1 }} />
          <Typography sx={{ flexGrow: 1 }}>Profile Settings</Typography>
        </AccordionSummary>
        <Box
          sx={{
            position: 'absolute',
            top: 8,
            right: 48, // Position to the left of the expand icon
            zIndex: 1,
          }}
        >
          <Tooltip title="Reset to defaults">
            <IconButton
              size="small"
              onClick={(e) => {
                e.stopPropagation();
                resetProfileSettings();
              }}
            >
              <ResetIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
        <AccordionDetails>
          <FormControl fullWidth size="small" sx={{ mb: 2 }}>
            <InputLabel>AI Profile</InputLabel>
            <Select
              value={selectedProfile}
              label="AI Profile"
              onChange={(e) => handleProfileChange(e.target.value)}
            >
              {profiles.map((profile) => (
                <MenuItem key={profile.id} value={profile.id}>
                  {profile.name} ({profile.llm_model})
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Typography gutterBottom>Temperature: {temperature}</Typography>
          <Slider
            value={temperature}
            onChange={(_, value) => setTemperature(value as number)}
            min={0}
            max={2}
            step={0.1}
            marks={[
              { value: 0, label: 'Precise' },
              { value: 1, label: 'Balanced' },
              { value: 2, label: 'Creative' },
            ]}
            sx={{ mb: 2 }}
          />

          <Typography gutterBottom>Max Tokens: {maxTokens}</Typography>
          <Slider
            value={maxTokens}
            onChange={(_, value) => setMaxTokens(value as number)}
            min={256}
            max={4096}
            step={256}
            marks={[
              { value: 256, label: '256' },
              { value: 2048, label: '2K' },
              { value: 4096, label: '4K' },
            ]}
          />
        </AccordionDetails>
      </Accordion>

      {/* Prompts */}
      <Accordion
        expanded={expandedPanel === 'prompts'}
        onChange={handlePanelChange('prompts')}
        sx={{ position: 'relative' }}
      >
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
          sx={{
            '& .MuiAccordionSummary-content': {
              alignItems: 'center',
            },
          }}
        >
          <PromptIcon sx={{ mr: 1 }} />
          <Typography sx={{ flexGrow: 1 }}>Prompt Templates</Typography>
        </AccordionSummary>
        <Box
          sx={{
            position: 'absolute',
            top: 8,
            right: 48, // Position to the left of the expand icon
            zIndex: 1,
          }}
        >
          <Tooltip title="Reset to defaults">
            <IconButton
              size="small"
              onClick={(e) => {
                e.stopPropagation();
                resetPromptSettings();
              }}
            >
              <ResetIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
        <AccordionDetails>
          <FormControl fullWidth size="small" sx={{ mb: 2 }}>
            <InputLabel>Prompt Template</InputLabel>
            <Select
              value={selectedPrompt}
              label="Prompt Template"
              onChange={(e) => handlePromptChange(e.target.value)}
            >
              <MenuItem value="">None</MenuItem>
              {prompts.map((prompt) => (
                <MenuItem key={prompt.id} value={prompt.id}>
                  {prompt.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          
          {/* Custom Prompt Text Editor */}
          <TextField
            label="Custom Prompt Text"
            value={customPromptText}
            onChange={(e) => setCustomPromptText(e.target.value)}
            fullWidth
            multiline
            rows={4}
            placeholder="Enter custom prompt text or select a template above..."
            sx={{ mb: 2 }}
            helperText="Edit the prompt text or select a predefined template above"
          />
          
          {selectedPrompt && (
            <Box>
              <Typography variant="body2" color="text.secondary">
                {prompts
                  .find((p) => p.id === selectedPrompt)
                  ?.content?.substring(0, 100)}
                ...
              </Typography>
            </Box>
          )}
        </AccordionDetails>
      </Accordion>

      {/* Knowledge */}
      <Accordion
        expanded={expandedPanel === 'knowledge'}
        onChange={handlePanelChange('knowledge')}
        sx={{ position: 'relative' }}
      >
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
          sx={{
            '& .MuiAccordionSummary-content': {
              alignItems: 'center',
            },
          }}
        >
          <DocumentIcon sx={{ mr: 1 }} />
          <Typography sx={{ flexGrow: 1 }}>Knowledge Base</Typography>
        </AccordionSummary>
        <Box
          sx={{
            position: 'absolute',
            top: 8,
            right: 48, // Position to the left of the expand icon
            zIndex: 1,
          }}
        >
          <Tooltip title="Reset to defaults">
            <IconButton
              size="small"
              onClick={(e) => {
                e.stopPropagation();
                resetKnowledgeSettings();
              }}
            >
              <ResetIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
        <AccordionDetails>
          <FormControlLabel
            control={
              <Switch
                checked={enableRetrieval}
                onChange={(e) => setEnableRetrieval(e.target.checked)}
              />
            }
            label="Enable Document Retrieval"
            sx={{ mb: 2 }}
          />

          <FormControl fullWidth size="small" sx={{ mb: 2 }}>
            <InputLabel>Selected Documents</InputLabel>
            <Select
              multiple
              value={selectedDocuments}
              label="Selected Documents"
              onChange={(e) => setSelectedDocuments(e.target.value as string[])}
              renderValue={(selected) => (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {(selected as string[]).map((value) => {
                    const doc = documents.find((d) => d.id === value);
                    return (
                      <Chip
                        key={value}
                        label={doc?.title || value}
                        size="small"
                        variant="outlined"
                      />
                    );
                  })}
                </Box>
              )}
            >
              {documents.map((document) => (
                <MenuItem key={document.id} value={document.id}>
                  {document.title}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Typography variant="body2" color="text.secondary">
            {selectedDocuments.length} document(s) selected for context
          </Typography>
        </AccordionDetails>
      </Accordion>

      {/* Tools */}
      <Accordion
        expanded={expandedPanel === 'tools'}
        onChange={handlePanelChange('tools')}
        sx={{ position: 'relative' }}
      >
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
          sx={{
            '& .MuiAccordionSummary-content': {
              alignItems: 'center',
            },
          }}
        >
          <ToolIcon sx={{ mr: 1 }} />
          <Typography sx={{ flexGrow: 1 }}>Tool Execution</Typography>
        </AccordionSummary>
        <Box
          sx={{
            position: 'absolute',
            top: 8,
            right: 48, // Position to the left of the expand icon
            zIndex: 1,
          }}
        >
          <Tooltip title="Reset to defaults">
            <IconButton
              size="small"
              onClick={(e) => {
                e.stopPropagation();
                resetToolSettings();
              }}
            >
              <ResetIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
        <AccordionDetails>
          <FormControlLabel
            control={
              <Switch
                checked={enableTools}
                onChange={(e) => setEnableTools(e.target.checked)}
              />
            }
            label="Enable Tool Execution"
            sx={{ mb: 2 }}
          />

          <Typography variant="body2" color="text.secondary">
            Enable AI assistant to execute tools and functions during conversation
          </Typography>
        </AccordionDetails>
      </Accordion>
    </Box>
  );
};

export default ChatConfigPanel;
