import React, { useState, useEffect } from 'react';
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
  TextField,
  Button,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  TextSnippet as PromptIcon,
  AccountBox as ProfileIcon,
  Description as DocumentIcon,
  Settings as AdvancedIcon,
} from '@mui/icons-material';
import {
  ProfileResponse,
  PromptResponse,
  DocumentResponse,
  ConversationResponse,
} from 'chatter-sdk';
import { useRightSidebar } from '../components/RightSidebarContext';
import { ChatWorkflowConfig } from '../hooks/useWorkflowChat';

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

  customPromptText: string;
  setCustomPromptText: (text: string) => void;

  // New workflow-based configuration
  workflowConfig: ChatWorkflowConfig;
  updateWorkflowConfig: (updates: Partial<ChatWorkflowConfig>) => void;

  // Tracing configuration
  enableTracing: boolean;
  setEnableTracing: (enabled: boolean) => void;

  onSelectConversation: (conversation: ConversationResponse) => void;
}

const ChatWorkflowConfigPanel: React.FC<Props> = ({
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
  customPromptText,
  setCustomPromptText,
  workflowConfig,
  updateWorkflowConfig,
  enableTracing,
  setEnableTracing,
  onSelectConversation: _onSelectConversation,
}) => {
  const { collapsed, setCollapsed } = useRightSidebar();
  const [expandedPanel, setExpandedPanel] = useState<string>(() => {
    const saved = localStorage.getItem('chatter_expandedPanel');
    return saved ? saved : 'workflow';
  });

  const [showAdvancedConfig, setShowAdvancedConfig] = useState(false);

  useEffect(() => {
    localStorage.setItem('chatter_expandedPanel', expandedPanel);
  }, [expandedPanel]);

  const handlePanelChange = (panel: string) => {
    setExpandedPanel(expandedPanel === panel ? '' : panel);
  };

  // Collapsed view with icon buttons
  if (collapsed) {
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, mt: 1 }}>
        <Tooltip title="Workflow Configuration" placement="left">
          <IconButton
            onClick={() => {
              setCollapsed(false);
              setExpandedPanel('workflow');
            }}
            sx={{ borderRadius: 1 }}
          >
            <AdvancedIcon />
          </IconButton>
        </Tooltip>
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
              setExpandedPanel('prompt');
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
              setExpandedPanel('documents');
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
    <Box sx={{ width: '100%', p: collapsed ? 0 : 1 }}>
      {/* Workflow Configuration */}
      <Accordion
        expanded={expandedPanel === 'workflow'}
        onChange={() => handlePanelChange('workflow')}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <AdvancedIcon />
            <Typography>Workflow Configuration</Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Configure your custom workflow settings
            </Typography>

            {/* Workflow Configuration */}
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>
                Workflow Configuration
              </Typography>

              <FormControlLabel
                control={
                  <Switch
                    checked={workflowConfig.enable_retrieval}
                    onChange={(e) =>
                      updateWorkflowConfig({
                        enable_retrieval: e.target.checked,
                      })
                    }
                  />
                }
                label="Document Retrieval (RAG)"
              />

              <FormControlLabel
                control={
                  <Switch
                    checked={workflowConfig.enable_tools}
                    onChange={(e) =>
                      updateWorkflowConfig({ enable_tools: e.target.checked })
                    }
                  />
                }
                label="Function Calling (Tools)"
              />

              <FormControlLabel
                control={
                  <Switch
                    checked={workflowConfig.enable_memory}
                    onChange={(e) =>
                      updateWorkflowConfig({
                        enable_memory: e.target.checked,
                      })
                    }
                  />
                }
                label="Conversation Memory"
              />

              <Button
                variant="outlined"
                size="small"
                startIcon={<AdvancedIcon />}
                onClick={() => setShowAdvancedConfig(!showAdvancedConfig)}
                sx={{ mt: 1 }}
              >
                {showAdvancedConfig ? 'Hide' : 'Show'} Advanced
              </Button>

              {showAdvancedConfig && (
                <Box
                  sx={{
                    mt: 2,
                    p: 2,
                    bgcolor: (theme) =>
                      theme.palette.mode === 'dark' ? 'grey.900' : 'grey.50',
                    borderRadius: 1,
                  }}
                >
                  <Typography variant="subtitle2" gutterBottom>
                    Model Configuration
                  </Typography>

                  <Typography gutterBottom>
                    Temperature: {workflowConfig.llm_config?.temperature || 0.7}
                  </Typography>
                  <Slider
                    value={workflowConfig.llm_config?.temperature || 0.7}
                    onChange={(_, value) =>
                      updateWorkflowConfig({
                        llm_config: {
                          ...workflowConfig.llm_config,
                          temperature: value as number,
                        },
                      })
                    }
                    min={0}
                    max={2}
                    step={0.1}
                    valueLabelDisplay="auto"
                  />

                  <Typography gutterBottom>
                    Max Tokens: {workflowConfig.llm_config?.max_tokens || 1000}
                  </Typography>
                  <Slider
                    value={workflowConfig.llm_config?.max_tokens || 1000}
                    onChange={(_, value) =>
                      updateWorkflowConfig({
                        llm_config: {
                          ...workflowConfig.llm_config,
                          max_tokens: value as number,
                        },
                      })
                    }
                    min={100}
                    max={4000}
                    step={100}
                    valueLabelDisplay="auto"
                  />

                  {workflowConfig.enable_retrieval && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Retrieval Configuration
                      </Typography>

                      <Typography gutterBottom>
                        Max Documents:{' '}
                        {workflowConfig.retrieval_config?.max_documents || 5}
                      </Typography>
                      <Slider
                        value={
                          workflowConfig.retrieval_config?.max_documents || 5
                        }
                        onChange={(_, value) =>
                          updateWorkflowConfig({
                            retrieval_config: {
                              ...workflowConfig.retrieval_config,
                              enabled: true,
                              max_documents: value as number,
                            },
                          })
                        }
                        min={1}
                        max={20}
                        step={1}
                        valueLabelDisplay="auto"
                      />

                      <FormControlLabel
                        control={
                          <Switch
                            checked={
                              workflowConfig.retrieval_config?.rerank || false
                            }
                            onChange={(e) =>
                              updateWorkflowConfig({
                                retrieval_config: {
                                  ...workflowConfig.retrieval_config,
                                  enabled: true,
                                  rerank: e.target.checked,
                                },
                              })
                            }
                          />
                        }
                        label="Enable Reranking"
                      />
                    </Box>
                  )}

                  {workflowConfig.enable_tools && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Tool Configuration
                      </Typography>

                      <Typography gutterBottom>
                        Max Tool Calls:{' '}
                        {workflowConfig.tool_config?.max_tool_calls || 3}
                      </Typography>
                      <Slider
                        value={workflowConfig.tool_config?.max_tool_calls || 3}
                        onChange={(_, value) =>
                          updateWorkflowConfig({
                            tool_config: {
                              ...workflowConfig.tool_config,
                              enabled: true,
                              max_tool_calls: value as number,
                            },
                          })
                        }
                        min={1}
                        max={10}
                        step={1}
                        valueLabelDisplay="auto"
                      />

                      <FormControlLabel
                        control={
                          <Switch
                            checked={
                              workflowConfig.tool_config?.parallel_tool_calls ||
                              false
                            }
                            onChange={(e) =>
                              updateWorkflowConfig({
                                tool_config: {
                                  ...workflowConfig.tool_config,
                                  enabled: true,
                                  parallel_tool_calls: e.target.checked,
                                },
                              })
                            }
                          />
                        }
                        label="Parallel Tool Calls"
                      />
                    </Box>
                  )}

                  {/* Tracing Configuration */}
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Debug Configuration
                    </Typography>

                    <FormControlLabel
                      control={
                        <Switch
                          checked={enableTracing}
                          onChange={(e) => setEnableTracing(e.target.checked)}
                        />
                      }
                      label="Enable Backend Workflow Tracing"
                    />
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{ mt: 0.5 }}
                    >
                      Shows detailed workflow execution steps in the response
                    </Typography>
                  </Box>
                </Box>
              )}
            </Box>
          </Box>
        </AccordionDetails>
      </Accordion>

      {/* Profile Selection */}
      <Accordion
        expanded={expandedPanel === 'profile'}
        onChange={() => handlePanelChange('profile')}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <ProfileIcon />
            <Typography>Profile</Typography>
            {selectedProfile && (
              <Chip size="small" label="Active" color="primary" />
            )}
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <FormControl fullWidth size="small">
            <InputLabel>Select Profile</InputLabel>
            <Select
              value={selectedProfile}
              onChange={(e) => setSelectedProfile(e.target.value)}
              label="Select Profile"
            >
              <MenuItem value="">
                <em>No Profile</em>
              </MenuItem>
              {profiles.map((profile) => (
                <MenuItem key={profile.id} value={profile.id}>
                  {profile.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </AccordionDetails>
      </Accordion>

      {/* System Prompt */}
      <Accordion
        expanded={expandedPanel === 'prompt'}
        onChange={() => handlePanelChange('prompt')}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <PromptIcon />
            <Typography>System Prompt</Typography>
            {(selectedPrompt || customPromptText) && (
              <Chip size="small" label="Active" color="primary" />
            )}
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <FormControl fullWidth size="small" sx={{ mb: 2 }}>
            <InputLabel>Select Prompt Template</InputLabel>
            <Select
              value={selectedPrompt}
              onChange={(e) => setSelectedPrompt(e.target.value)}
              label="Select Prompt Template"
            >
              <MenuItem value="">
                <em>No Template</em>
              </MenuItem>
              {prompts.map((prompt) => (
                <MenuItem key={prompt.id} value={prompt.id}>
                  {prompt.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <TextField
            label="Custom System Prompt"
            multiline
            rows={3}
            fullWidth
            value={customPromptText}
            onChange={(e) => setCustomPromptText(e.target.value)}
            placeholder="Enter a custom system prompt..."
            size="small"
          />
        </AccordionDetails>
      </Accordion>

      {/* Documents */}
      <Accordion
        expanded={expandedPanel === 'documents'}
        onChange={() => handlePanelChange('documents')}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <DocumentIcon />
            <Typography>Documents</Typography>
            {selectedDocuments.length > 0 && (
              <Chip
                size="small"
                label={selectedDocuments.length}
                color="primary"
              />
            )}
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Box sx={{ maxHeight: 200, overflowY: 'auto' }}>
            {documents.map((doc) => (
              <FormControlLabel
                key={doc.id}
                control={
                  <Switch
                    checked={selectedDocuments.includes(doc.id)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedDocuments([...selectedDocuments, doc.id]);
                      } else {
                        setSelectedDocuments(
                          selectedDocuments.filter((id) => id !== doc.id)
                        );
                      }
                    }}
                  />
                }
                label={
                  <Box>
                    <Typography variant="body2">
                      {doc.title || doc.filename}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {doc.document_type}
                    </Typography>
                  </Box>
                }
                sx={{ display: 'block', mb: 1 }}
              />
            ))}
          </Box>
        </AccordionDetails>
      </Accordion>
    </Box>
  );
};

export default ChatWorkflowConfigPanel;
