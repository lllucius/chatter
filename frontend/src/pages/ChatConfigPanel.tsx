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
  Button,
  Tooltip,
  IconButton,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  TextSnippet as PromptIcon,
  AccountBox as ProfileIcon,
  Description as DocumentIcon,
  Speed as SpeedIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { ProfileResponse, PromptResponse, DocumentResponse, ConversationResponse } from '../sdk';
import { useRightSidebar } from '../components/RightSidebarContext';

interface Props {
  profiles: ProfileResponse[];
  prompts: PromptResponse[];
  documents: DocumentResponse[];
  currentConversation: ConversationResponse | null;
  messagesCount: number;

  selectedProfile: string;
  setSelectedProfile: (id: string) => void;

  selectedPrompt: string;
  setSelectedPrompt: (id: string) => void;

  selectedDocuments: string[];
  setSelectedDocuments: (ids: string[]) => void;

  streamingEnabled: boolean;
  setStreamingEnabled: (v: boolean) => void;

  temperature: number;
  setTemperature: (v: number) => void;

  maxTokens: number;
  setMaxTokens: (v: number) => void;

  enableRetrieval: boolean;
  setEnableRetrieval: (v: boolean) => void;

  startNewConversation: () => void;
}

const ChatConfigPanel: React.FC<Props> = ({
  profiles,
  prompts,
  documents,
  currentConversation,
  messagesCount,
  selectedProfile,
  setSelectedProfile,
  selectedPrompt,
  setSelectedPrompt,
  selectedDocuments,
  setSelectedDocuments,
  streamingEnabled,
  setStreamingEnabled,
  temperature,
  setTemperature,
  maxTokens,
  setMaxTokens,
  enableRetrieval,
  setEnableRetrieval,
  startNewConversation,
}) => {
  const { collapsed, setCollapsed } = useRightSidebar();
  const [expandedPanel, setExpandedPanel] = useState<string>('profile');

  const handlePanelChange =
    (panel: string) => (_: React.SyntheticEvent, isExpanded: boolean) =>
      setExpandedPanel(isExpanded ? panel : '');

  if (collapsed) {
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, mt: 1 }}>
        <Tooltip title="Profile Settings" placement="left">
          <IconButton
            onClick={() => {
              setCollapsed(false);
              setExpandedPanel('profile');
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
            }}
            sx={{ borderRadius: 1 }}
          >
            <DocumentIcon />
          </IconButton>
        </Tooltip>
        <Tooltip title="Advanced Settings" placement="left">
          <IconButton
            onClick={() => {
              setCollapsed(false);
              setExpandedPanel('advanced');
            }}
            sx={{ borderRadius: 1 }}
          >
            <SpeedIcon />
          </IconButton>
        </Tooltip>
      </Box>
    );
  }

  return (
    <Box>
      {/* Optional current chat info */}
      {currentConversation && (
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          {currentConversation.title} ({messagesCount} messages)
        </Typography>
      )}

      {/* Profile */}
      <Accordion expanded={expandedPanel === 'profile'} onChange={handlePanelChange('profile')}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <ProfileIcon sx={{ mr: 1 }} />
          <Typography>Profile Settings</Typography>
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
      <Accordion expanded={expandedPanel === 'prompts'} onChange={handlePanelChange('prompts')}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <PromptIcon sx={{ mr: 1 }} />
          <Typography>Prompt Templates</Typography>
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
                {prompts.find((p) => p.id === selectedPrompt)?.content?.substring(0, 100)}...
              </Typography>
            </Box>
          )}
        </AccordionDetails>
      </Accordion>

      {/* Knowledge */}
      <Accordion expanded={expandedPanel === 'knowledge'} onChange={handlePanelChange('knowledge')}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <DocumentIcon sx={{ mr: 1 }} />
          <Typography>Knowledge Base</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <FormControlLabel
            control={<Switch checked={enableRetrieval} onChange={(e) => setEnableRetrieval(e.target.checked)} />}
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
                    return <Chip key={value} label={doc?.title || value} size="small" variant="outlined" />;
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

      {/* Advanced */}
      <Accordion expanded={expandedPanel === 'advanced'} onChange={handlePanelChange('advanced')}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <SpeedIcon sx={{ mr: 1 }} />
          <Typography>Advanced Settings</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <FormControlLabel
            control={<Switch checked={streamingEnabled} onChange={(e) => setStreamingEnabled(e.target.checked)} />}
            label="Streaming Responses"
            sx={{ mb: 2 }}
          />

          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {streamingEnabled ? 'Responses will be streamed in real-time' : 'Responses will be delivered all at once'}
          </Typography>

          <Button variant="outlined" fullWidth onClick={startNewConversation} startIcon={<RefreshIcon />}>
            Apply Settings & New Chat
          </Button>
        </AccordionDetails>
      </Accordion>
    </Box>
  );
};

export default ChatConfigPanel;
