import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Paper,
  Avatar,
  Chip,
  IconButton,
  Tooltip,
  Alert,
  CircularProgress,
  Drawer,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Slider,
  FormControlLabel,
  Switch,
  Divider,
} from '@mui/material';
import {
  Send as SendIcon,
  Person as PersonIcon,
  SmartToy as BotIcon,
  Refresh as RefreshIcon,
  Settings as SettingsIcon,
  ExpandMore as ExpandMoreIcon,
  Tune as TuneIcon,
  Speed as SpeedIcon,
  Description as DocumentIcon,
  TextSnippet as PromptIcon,
  AccountBox as ProfileIcon,
  Stream as StreamIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { chatterSDK } from '../services/chatter-sdk';
import { Profile, Prompt, Document, Conversation, CreateConversationRequest, SendMessageRequest } from '../sdk';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}

const rightSidebarWidth = 320;

const ChatPage: React.FC = () => {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedProfile, setSelectedProfile] = useState<string>('');
  const [selectedPrompt, setSelectedPrompt] = useState<string>('');
  const [selectedDocuments, setSelectedDocuments] = useState<string[]>([]);
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Right sidebar state
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [expandedPanel, setExpandedPanel] = useState<string>('profile');
  
  // Chat configuration state
  const [streamingEnabled, setStreamingEnabled] = useState(false);
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(2048);
  const [enableRetrieval, setEnableRetrieval] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadData = async () => {
    try {
      const [profilesResponse, promptsResponse, documentsResponse] = await Promise.all([
        chatterSDK.profiles.listProfilesApiV1ProfilesGet({}),
        chatterSDK.prompts.listPromptsApiV1PromptsGet({}),
        chatterSDK.documents.listDocumentsApiV1DocumentsGet({}),
      ]);
      setProfiles(profilesResponse.data.profiles);
      setPrompts(promptsResponse.data.prompts);
      setDocuments(documentsResponse.data.documents);
      
      // Set default selections
      if (profilesResponse.data.profiles.length > 0) {
        setSelectedProfile(profilesResponse.data.profiles[0].id);
      }
    } catch (err: any) {
      setError('Failed to load chat data');
      console.error(err);
    }
  };

  const startNewConversation = async () => {
    try {
      setError('');
      const createRequest: CreateConversationRequest = {
        title: `Chat ${new Date().toLocaleString()}`,
        profile_id: selectedProfile || undefined,
      };
      const response = await chatterSDK.conversations.createConversationApiV1ChatConversationsPost({ conversationCreate: createRequest });
      setCurrentConversation(response.data);
      setMessages([]);
      
      // Add system message if prompt is selected
      if (selectedPrompt) {
        const selectedPromptData = prompts.find(p => p.id === selectedPrompt);
        if (selectedPromptData) {
          setMessages([{
            id: 'system',
            role: 'system',
            content: `Using prompt: "${selectedPromptData.name}" - ${selectedPromptData.content}`,
            timestamp: new Date(),
          }]);
        }
      }
    } catch (err: any) {
      setError('Failed to start new conversation');
      console.error(err);
    }
  };

  const sendMessage = async () => {
    if (!message.trim() || loading) return;

    if (!currentConversation) {
      await startNewConversation();
      return;
    }

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: message.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setMessage('');
    setLoading(true);

    try {
      // Send message to the API
      const sendRequest: SendMessageRequest = {
        message: userMessage.content,
      };
      const response = await chatterSDK.conversations.chatApiV1ChatChatPost({ chatRequest: sendRequest });
      
      const assistantMessage: ChatMessage = {
        id: response.data.message.id,
        role: 'assistant',
        content: response.data.message.content,
        timestamp: new Date(response.data.message.created_at),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err: any) {
      setError('Failed to send message');
      console.error(err);
      
      // Add error message to chat
      const errorMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your message. Please try again.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const getMessageAvatar = (role: string) => {
    switch (role) {
      case 'user':
        return <PersonIcon />;
      case 'assistant':
        return <BotIcon />;
      case 'system':
        return <SettingsIcon />;
      default:
        return <BotIcon />;
    }
  };

  const getMessageColor = (role: string) => {
    switch (role) {
      case 'user':
        return 'primary.main';
      case 'assistant':
        return 'secondary.main';
      case 'system':
        return 'info.main';
      default:
        return 'grey.500';
    }
  };

  const handlePanelChange = (panel: string) => (event: React.SyntheticEvent, isExpanded: boolean) => {
    setExpandedPanel(isExpanded ? panel : '');
  };

  return (
    <Box sx={{ display: 'flex', height: 'calc(100vh - 80px)' }}>
      {/* Main Chat Area */}
      <Box sx={{ 
        flexGrow: 1, 
        display: 'flex', 
        flexDirection: 'column',
        width: sidebarOpen ? `calc(100% - ${rightSidebarWidth}px)` : '100%',
        transition: (theme) => theme.transitions.create('width', {
          easing: theme.transitions.easing.sharp,
          duration: theme.transitions.duration.leavingScreen,
        }),
        overflow: 'hidden',
      }}>
        {error && (
          <Alert severity="error" sx={{ mb: 1 }}>
            {error}
          </Alert>
        )}

        {/* Quick Actions Bar */}
        <Card sx={{ mb: 1 }}>
          <CardContent sx={{ py: 1, px: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, justifyContent: 'space-between' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <FormControlLabel
                  control={
                    <Switch 
                      checked={streamingEnabled} 
                      onChange={(e) => setStreamingEnabled(e.target.checked)}
                      icon={<SpeedIcon />}
                      checkedIcon={<StreamIcon />}
                    />
                  }
                  label={streamingEnabled ? 'Streaming' : 'Standard'}
                />
                <Divider orientation="vertical" flexItem />
                <Button
                  variant="outlined"
                  size="small"
                  onClick={startNewConversation}
                  startIcon={<RefreshIcon />}
                >
                  New Chat
                </Button>
                {currentConversation && (
                  <Chip 
                    label={`${currentConversation.title} (${messages.length} messages)`}
                    size="small"
                    variant="outlined"
                  />
                )}
              </Box>
              <Tooltip title={sidebarOpen ? 'Hide Settings' : 'Show Settings'}>
                <IconButton onClick={() => setSidebarOpen(!sidebarOpen)} size="small">
                  <TuneIcon />
                </IconButton>
              </Tooltip>
            </Box>
          </CardContent>
        </Card>

        {/* Messages Area */}
        <Card sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', mb: 1 }}>
          <CardContent sx={{ flexGrow: 1, overflow: 'hidden', p: 0 }}>
            <Box
              sx={{
                height: '100%',
                overflowY: 'auto',
                p: 2,
                display: 'flex',
                flexDirection: 'column',
              }}
            >
              {messages.length === 0 ? (
                <Box
                  sx={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    height: '100%',
                    color: 'text.secondary',
                  }}
                >
                  <BotIcon sx={{ fontSize: 64, mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Welcome to Chatter!
                  </Typography>
                  <Typography variant="body2" textAlign="center">
                    Configure your settings in the right panel and start chatting.
                    Use the streaming toggle for real-time responses.
                  </Typography>
                </Box>
              ) : (
                messages.map((msg) => (
                  <Box
                    key={msg.id}
                    sx={{
                      display: 'flex',
                      mb: 2,
                      alignItems: 'flex-start',
                      ...(msg.role === 'user' && {
                        flexDirection: 'row-reverse',
                      }),
                    }}
                  >
                    <Avatar
                      sx={{
                        bgcolor: getMessageColor(msg.role),
                        ...(msg.role === 'user' ? { ml: 1 } : { mr: 1 }),
                      }}
                    >
                      {getMessageAvatar(msg.role)}
                    </Avatar>
                    <Paper
                      sx={{
                        p: 2,
                        maxWidth: '70%',
                        bgcolor: msg.role === 'user' 
                          ? 'primary.light' 
                          : (theme) => theme.palette.mode === 'dark' ? 'grey.800' : 'grey.100',
                        color: msg.role === 'user' 
                          ? 'primary.contrastText' 
                          : 'text.primary',
                      }}
                    >
                      <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                        {msg.content}
                      </Typography>
                      <Typography
                        variant="caption"
                        sx={{
                          display: 'block',
                          mt: 1,
                          opacity: 0.7,
                        }}
                      >
                        {format(msg.timestamp, 'HH:mm:ss')}
                      </Typography>
                    </Paper>
                  </Box>
                ))
              )}
              {loading && (
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Avatar sx={{ bgcolor: 'secondary.main', mr: 1 }}>
                    <BotIcon />
                  </Avatar>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <CircularProgress size={20} sx={{ mr: 1 }} />
                    <Typography variant="body2" color="text.secondary">
                      {streamingEnabled ? 'Streaming...' : 'Thinking...'}
                    </Typography>
                  </Box>
                </Box>
              )}
              <div ref={messagesEndRef} />
            </Box>
          </CardContent>
        </Card>

        {/* Message Input */}
        <Paper sx={{ p: 1.5 }}>
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
            <TextField
              fullWidth
              multiline
              maxRows={4}
              placeholder="Type your message here... (Shift+Enter for new line)"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={loading}
              variant="outlined"
              size="small"
            />
            <IconButton
              color="primary"
              onClick={sendMessage}
              disabled={!message.trim() || loading}
              sx={{ p: 1.5 }}
            >
              <SendIcon />
            </IconButton>
          </Box>
        </Paper>
      </Box>

      {/* Right Sidebar - Configuration Panel */}
      <Drawer
        variant="persistent"
        anchor="right"
        open={sidebarOpen}
        sx={{
          width: rightSidebarWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: rightSidebarWidth,
            boxSizing: 'border-box',
            position: 'relative',
            border: 'none',
            borderLeft: '1px solid',
            borderColor: 'divider',
          },
        }}
      >
        <Box sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
            <SettingsIcon sx={{ mr: 1 }} />
            Chat Configuration
          </Typography>
          
          {/* Profile Configuration */}
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

          {/* Prompt Configuration */}
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
                    {prompts.find(p => p.id === selectedPrompt)?.content?.substring(0, 100)}...
                  </Typography>
                </Box>
              )}
            </AccordionDetails>
          </Accordion>

          {/* Knowledge Base Configuration */}
          <Accordion expanded={expandedPanel === 'knowledge'} onChange={handlePanelChange('knowledge')}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <DocumentIcon sx={{ mr: 1 }} />
              <Typography>Knowledge Base</Typography>
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
                        const doc = documents.find(d => d.id === value);
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

          {/* Advanced Settings */}
          <Accordion expanded={expandedPanel === 'advanced'} onChange={handlePanelChange('advanced')}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <SpeedIcon sx={{ mr: 1 }} />
              <Typography>Advanced Settings</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <FormControlLabel
                control={
                  <Switch 
                    checked={streamingEnabled} 
                    onChange={(e) => setStreamingEnabled(e.target.checked)}
                  />
                }
                label="Streaming Responses"
                sx={{ mb: 2 }}
              />
              
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                {streamingEnabled 
                  ? 'Responses will be streamed in real-time' 
                  : 'Responses will be delivered all at once'
                }
              </Typography>
              
              <Button
                variant="outlined"
                fullWidth
                onClick={startNewConversation}
                startIcon={<RefreshIcon />}
              >
                Apply Settings & New Chat
              </Button>
            </AccordionDetails>
          </Accordion>
        </Box>
      </Drawer>
    </Box>
  );
};

export default ChatPage;
