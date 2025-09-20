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
  Tooltip,
  IconButton,
  TextField,
  Button,
  Card,
  CardContent,
  Grid,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  TextSnippet as PromptIcon,
  AccountBox as ProfileIcon,
  Description as DocumentIcon,
  RestartAlt as ResetIcon,
  Build as ToolIcon,
  Storage as RetrievalIcon,
  Memory as MemoryIcon,
  Settings as AdvancedIcon,
} from '@mui/icons-material';
import {
  ProfileResponse,
  PromptResponse,
  DocumentResponse,
  ConversationResponse,
} from 'chatter-sdk';
import { useRightSidebar } from '../components/RightSidebarContext';
import {
  ChatWorkflowConfig,
  ChatWorkflowTemplate,
} from '../hooks/useWorkflowChat';

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
  workflowTemplates: Record<string, ChatWorkflowTemplate>;
  selectedTemplate: string;
  setSelectedTemplate: (name: string) => void;
  workflowConfig: ChatWorkflowConfig;
  updateWorkflowConfig: (updates: Partial<ChatWorkflowConfig>) => void;
  resetToTemplate: (templateName: string) => void;

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
  workflowTemplates,
  selectedTemplate,
  setSelectedTemplate,
  workflowConfig,
  updateWorkflowConfig,
  resetToTemplate,
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

  const handleTemplateChange = (templateName: string) => {
    if (templateName) {
      resetToTemplate(templateName);
    } else {
      setSelectedTemplate('');
    }
  };

  const renderTemplateCard = (name: string, template: ChatWorkflowTemplate) => (
    <Card
      key={name}
      variant={selectedTemplate === name ? 'outlined' : 'elevation'}
      sx={{
        mb: 1,
        cursor: 'pointer',
        border: selectedTemplate === name ? 2 : 0,
        borderColor: selectedTemplate === name ? 'primary.main' : 'transparent',
      }}
      onClick={() => handleTemplateChange(name)}
    >
      <CardContent sx={{ py: 1 }}>
        <Typography variant="subtitle2" fontWeight="bold">
          {template.name}
        </Typography>
        <Typography variant="caption" color="text.secondary" display="block">
          {template.description}
        </Typography>
        <Box sx={{ mt: 1, display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
          {template.config.enable_retrieval && (
            <Chip size="small" icon={<RetrievalIcon />} label="RAG" />
          )}
          {template.config.enable_tools && (
            <Chip size="small" icon={<ToolIcon />} label="Tools" />
          )}
          {template.config.enable_memory && (
            <Chip size="small" icon={<MemoryIcon />} label="Memory" />
          )}
          <Chip
            size="small"
            label={`Score: ${template.complexity_score ?? 'N/A'}`}
            color={
              (template.complexity_score ?? 5) <= 3
                ? 'success'
                : (template.complexity_score ?? 5) <= 6
                  ? 'warning'
                  : 'error'
            }
          />
        </Box>
      </CardContent>
    </Card>
  );

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
              Choose a pre-built template or configure a custom workflow
            </Typography>

            {/* Template Selection */}
            <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
              Templates
            </Typography>
            <Box sx={{ maxHeight: 200, overflowY: 'auto' }}>
              <Card
                variant={!selectedTemplate ? 'outlined' : 'elevation'}
                sx={{
                  mb: 1,
                  cursor: 'pointer',
                  border: !selectedTemplate ? 2 : 0,
                  borderColor: !selectedTemplate
                    ? 'primary.main'
                    : 'transparent',
                }}
                onClick={() => setSelectedTemplate('')}
              >
                <CardContent sx={{ py: 1 }}>
                  <Typography variant="subtitle2" fontWeight="bold">
                    Custom Configuration
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Build your own workflow configuration
                  </Typography>
                </CardContent>
              </Card>

              {Object.entries(workflowTemplates).map(([name, template]) =>
                renderTemplateCard(name, template)
              )}
            </Box>

            {/* Custom Configuration */}
            {!selectedTemplate && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" sx={{ mb: 1 }}>
                  Custom Configuration
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
                    sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}
                  >
                    <Typography variant="subtitle2" gutterBottom>
                      Model Configuration
                    </Typography>

                    <Typography gutterBottom>
                      Temperature:{' '}
                      {workflowConfig.llm_config?.temperature || 0.7}
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
                      Max Tokens:{' '}
                      {workflowConfig.llm_config?.max_tokens || 1000}
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
                          value={
                            workflowConfig.tool_config?.max_tool_calls || 3
                          }
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
                                workflowConfig.tool_config
                                  ?.parallel_tool_calls || false
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
                  </Box>
                )}
              </Box>
            )}
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
                    <Typography variant="body2">{doc.title}</Typography>
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
