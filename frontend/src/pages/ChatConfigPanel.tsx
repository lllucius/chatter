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
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  TextSnippet as PromptIcon,
  AccountBox as ProfileIcon,
  Description as DocumentIcon,
  RestartAlt as ResetIcon,
} from '@mui/icons-material';
import { ProfileResponse, PromptResponse, DocumentResponse } from 'chatter-sdk';
import { useRightSidebar } from '../components/RightSidebarContext';

interface Props {
  profiles: ProfileResponse[];
  prompts: PromptResponse[];
  documents: DocumentResponse[];
  currentConversation: any;

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

  onSelectConversation: (conversation: any) => void;
}

const ChatConfigPanel: React.FC<Props> = ({
  profiles,
  prompts,
  documents,
  currentConversation,
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
  onSelectConversation,
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
      </Box>
    );
  }

  return (
    <Box>
      {/* Profile */}
      <Accordion
        expanded={expandedPanel === 'profile'}
        onChange={handlePanelChange('profile')}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <ProfileIcon sx={{ mr: 1 }} />
          <Typography sx={{ flexGrow: 1 }}>Profile Settings</Typography>
          <Tooltip title="Reset to defaults">
            <span>
              <IconButton
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  resetProfileSettings();
                }}
                sx={{ ml: 1 }}
              >
                <ResetIcon fontSize="small" />
              </IconButton>
            </span>
          </Tooltip>
        </AccordionSummary>
        <AccordionDetails>
          <FormControl fullWidth size="small" sx={{ mb: 2 }}>
            <InputLabel>AI Profile</InputLabel>
            <Select
              value={selectedProfile}
              label="AI Profile"
              onChange={(e) => setSelectedProfile(e.target.value)}
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
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <PromptIcon sx={{ mr: 1 }} />
          <Typography sx={{ flexGrow: 1 }}>Prompt Templates</Typography>
          <Tooltip title="Reset to defaults">
            <span>
              <IconButton
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  resetPromptSettings();
                }}
                sx={{ ml: 1 }}
              >
                <ResetIcon fontSize="small" />
              </IconButton>
            </span>
          </Tooltip>
        </AccordionSummary>
        <AccordionDetails>
          <FormControl fullWidth size="small" sx={{ mb: 2 }}>
            <InputLabel>Prompt Template</InputLabel>
            <Select
              value={selectedPrompt}
              label="Prompt Template"
              onChange={(e) => setSelectedPrompt(e.target.value)}
            >
              <MenuItem value="">None</MenuItem>
              {prompts.map((prompt) => (
                <MenuItem key={prompt.id} value={prompt.id}>
                  {prompt.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
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
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <DocumentIcon sx={{ mr: 1 }} />
          <Typography sx={{ flexGrow: 1 }}>Knowledge Base</Typography>
          <Tooltip title="Reset to defaults">
            <span>
              <IconButton
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  resetKnowledgeSettings();
                }}
                sx={{ ml: 1 }}
              >
                <ResetIcon fontSize="small" />
              </IconButton>
            </span>
          </Tooltip>
        </AccordionSummary>
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
    </Box>
  );
};

export default ChatConfigPanel;
