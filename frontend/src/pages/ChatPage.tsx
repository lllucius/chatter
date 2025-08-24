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
} from '@mui/material';
import Grid from '@mui/material/GridLegacy';
import {
  Send as SendIcon,
  Person as PersonIcon,
  SmartToy as BotIcon,
  Refresh as RefreshIcon,
  Settings as SettingsIcon,
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

  return (
    <Box sx={{ height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column' }}>
      <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 3, fontWeight: 'bold' }}>
        Chat Interface
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Configuration Panel */}
      <Card sx={{ mb: 2 }}>
        <CardContent sx={{ pb: 2 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Profile</InputLabel>
                <Select
                  value={selectedProfile}
                  label="Profile"
                  onChange={(e) => setSelectedProfile(e.target.value)}
                >
                  {profiles.map((profile) => (
                    <MenuItem key={profile.id} value={profile.id}>
                      {profile.name} ({profile.llm_model})
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
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
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Knowledge Base</InputLabel>
                <Select
                  multiple
                  value={selectedDocuments}
                  label="Knowledge Base"
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
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <Tooltip title="Start New Conversation">
                <Button
                  variant="outlined"
                  fullWidth
                  onClick={startNewConversation}
                  startIcon={<RefreshIcon />}
                  size="small"
                >
                  New Chat
                </Button>
              </Tooltip>
            </Grid>
          </Grid>
          
          {currentConversation && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Current conversation: {currentConversation.title}
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Messages Area */}
      <Card sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', mb: 2 }}>
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
                  Configure your profile and prompt template above, then start chatting.
                  Select documents from your knowledge base to enhance responses.
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
                      bgcolor: msg.role === 'user' ? 'primary.light' : 'grey.100',
                      color: msg.role === 'user' ? 'primary.contrastText' : 'text.primary',
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
                    Thinking...
                  </Typography>
                </Box>
              </Box>
            )}
            <div ref={messagesEndRef} />
          </Box>
        </CardContent>
      </Card>

      {/* Message Input */}
      <Paper sx={{ p: 2 }}>
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
  );
};

export default ChatPage;
