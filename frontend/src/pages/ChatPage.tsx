import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  IconButton,
  Tooltip,
  Alert,
  CircularProgress,
  Paper,
  Chip,
  Button,
  Divider,
  FormControlLabel,
  Switch,
  Avatar,
} from '@mui/material';
import {
  Send as SendIcon,
  Person as PersonIcon,
  SmartToy as BotIcon,
  Refresh as RefreshIcon,
  Tune as TuneIcon,
  Stream as StreamIcon,
  Speed as SpeedIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { chatterSDK } from '../services/chatter-sdk';
import { ProfileResponse, PromptResponse, DocumentResponse, ConversationResponse, ConversationCreate, ChatRequest } from '../sdk';
import { useRightSidebar } from '../components/RightSidebarContext';
import ChatConfigPanel from './ChatConfigPanel';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}

const ChatPage: React.FC = () => {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [profiles, setProfiles] = useState<ProfileResponse[]>([]);
  const [prompts, setPrompts] = useState<PromptResponse[]>([]);
  const [documents, setDocuments] = useState<DocumentResponse[]>([]);
  const [selectedProfile, setSelectedProfile] = useState<string>('');
  const [selectedPrompt, setSelectedPrompt] = useState<string>('');
  const [selectedDocuments, setSelectedDocuments] = useState<string[]>([]);
  const [currentConversation, setCurrentConversation] = useState<ConversationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Input focus ref (works for textarea in multiline mode)
  const inputRef = useRef<HTMLInputElement | HTMLTextAreaElement>(null);

  // Chat configuration state with localStorage persistence
  const [streamingEnabled, setStreamingEnabled] = useState(() => {
    const saved = localStorage.getItem('chatter_streamingEnabled');
    return saved ? JSON.parse(saved) : false;
  });
  const [temperature, setTemperature] = useState(() => {
    const saved = localStorage.getItem('chatter_temperature');
    return saved ? parseFloat(saved) : 0.7;
  });
  const [maxTokens, setMaxTokens] = useState(() => {
    const saved = localStorage.getItem('chatter_maxTokens');
    return saved ? parseInt(saved) : 2048;
  });
  const [enableRetrieval, setEnableRetrieval] = useState(() => {
    const saved = localStorage.getItem('chatter_enableRetrieval');
    return saved ? JSON.parse(saved) : true;
  });

  // Save config to localStorage when values change
  useEffect(() => {
    localStorage.setItem('chatter_streamingEnabled', JSON.stringify(streamingEnabled));
  }, [streamingEnabled]);
  
  useEffect(() => {
    localStorage.setItem('chatter_temperature', temperature.toString());
  }, [temperature]);
  
  useEffect(() => {
    localStorage.setItem('chatter_maxTokens', maxTokens.toString());
  }, [maxTokens]);
  
  useEffect(() => {
    localStorage.setItem('chatter_enableRetrieval', JSON.stringify(enableRetrieval));
  }, [enableRetrieval]);

  // Right drawer context
  const { setPanelContent, clearPanelContent, setTitle, open, setOpen } = useRightSidebar();
  
  // Save right drawer state when it changes
  useEffect(() => {
    localStorage.setItem('chatter_rightDrawerOpen', JSON.stringify(open));
  }, [open]);

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

      if (profilesResponse.data.profiles.length > 0) {
        setSelectedProfile(profilesResponse.data.profiles[0].id);
      }
    } catch (err: any) {
      setError('Failed to load chat data');
      console.error(err);
    }
  };

  // Return the created conversation so callers can use its id immediately
  const startNewConversation = useCallback(async (): Promise<ConversationResponse | null> => {
    try {
      setError('');
      await loadData();
      
      const selectedPromptData = prompts.find((p) => p.id === selectedPrompt);
      const systemPrompt = selectedPromptData?.content || undefined;
      
      const createRequest: ConversationCreate = {
        title: `Chat ${new Date().toLocaleString()}`,
        profile_id: selectedProfile || undefined,
        enable_retrieval: enableRetrieval,
        system_prompt: systemPrompt,
      };
      const response = await chatterSDK.conversations.createConversationApiV1ChatConversationsPost({
        conversationCreate: createRequest,
      });
      setCurrentConversation(response.data);
      setMessages([]);

      if (selectedPrompt && selectedPromptData) {
        setMessages([
          {
            id: 'system',
            role: 'system',
            content: `Using prompt: "${selectedPromptData.name}" - ${selectedPromptData.content}`,
            timestamp: new Date(),
          },
        ]);
      }
      return response.data;
    } catch (err: any) {
      setError('Failed to start new conversation');
      console.error(err);
      return null;
    }
  }, [selectedProfile, selectedPrompt, prompts, enableRetrieval]);

  const onSelectConversation = useCallback(async (conversation: ConversationResponse) => {
    try {
      setError('');
      
      // Set current conversation
      setCurrentConversation(conversation);
      
      // Load messages for this conversation
      const response = await chatterSDK.conversations.getConversationMessagesApiV1ChatConversationsConversationIdMessagesGet({
        conversationId: conversation.id
      });
      
      // Convert messages to ChatMessage format
      const chatMessages: ChatMessage[] = response.data.map(msg => ({
        id: msg.id,
        role: msg.role as 'user' | 'assistant' | 'system',
        content: msg.content,
        timestamp: new Date(msg.created_at)
      }));
      
      setMessages(chatMessages);
      
      // Scroll to bottom after messages are set
      setTimeout(() => scrollToBottom(), 100);
    } catch (err: any) {
      setError('Failed to load conversation');
      console.error(err);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Focus the input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // Inject configuration panel into the right drawer
  useEffect(() => {
    setTitle('Chat Configuration');
    
    // Restore right drawer state
    const savedDrawerState = localStorage.getItem('chatter_rightDrawerOpen');
    const shouldOpen = savedDrawerState ? JSON.parse(savedDrawerState) : true;
    setOpen(shouldOpen);
    setPanelContent(
      <ChatConfigPanel
        profiles={profiles}
        prompts={prompts}
        documents={documents}
        currentConversation={currentConversation}
        messagesCount={messages.length}
        selectedProfile={selectedProfile}
        setSelectedProfile={setSelectedProfile}
        selectedPrompt={selectedPrompt}
        setSelectedPrompt={setSelectedPrompt}
        selectedDocuments={selectedDocuments}
        setSelectedDocuments={setSelectedDocuments}
        streamingEnabled={streamingEnabled}
        setStreamingEnabled={setStreamingEnabled}
        temperature={temperature}
        setTemperature={setTemperature}
        maxTokens={maxTokens}
        setMaxTokens={setMaxTokens}
        enableRetrieval={enableRetrieval}
        setEnableRetrieval={setEnableRetrieval}
        startNewConversation={startNewConversation}
        onSelectConversation={onSelectConversation}
      />
    );

    return () => {
      clearPanelContent();
    };
    // ESLint disabled: setPanelContent, clearPanelContent, setTitle, setOpen are stable setter functions
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
  }, [
    profiles,
    prompts,
    documents,
    currentConversation,
    messages.length,
    selectedProfile,
    selectedPrompt,
    selectedDocuments,
    streamingEnabled,
    temperature,
    maxTokens,
    enableRetrieval,
    startNewConversation,
    onSelectConversation,
  ]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleStreamingResponse = async (chatRequest: ChatRequest) => {
    try {
      // Create a placeholder assistant message for streaming content
      const messageId = `stream-${Date.now()}`;
      const assistantMessage: ChatMessage = {
        id: messageId,
        role: 'assistant',
        content: '',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);

      // Use the SDK's streaming method
      const reader = await chatterSDK.chatStream(chatRequest);
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // SSE frames are typically separated by \n\n; we split by \n and keep remainder in buffer
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (let rawLine of lines) {
          const line = rawLine.trim();
          if (!line || line.startsWith(':')) continue; // skip comments/empty

          // support both "data: ..." and raw JSON per line
          let payload = line.startsWith('data:') ? line.slice(5).trim() :
                        line.startsWith('data ') ? line.slice(4).trim() :
                        line;

          if (!payload) continue;
          if (payload === '[DONE]') {
            buffer = '';
            return;
          }

          try {
            const chunk = JSON.parse(payload);

            // Accept multiple possible shapes
            if (chunk.type === 'token' || chunk.type === 'delta') {
              const textDelta =
                chunk.content ??
                chunk.delta ??
                chunk.choices?.[0]?.delta?.content ??
                '';

              if (textDelta) {
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === messageId ? { ...msg, content: msg.content + textDelta } : msg
                  )
                );
              }
            } else if (chunk.type === 'message' && chunk.message?.content) {
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.id === messageId ? { ...msg, content: msg.content + chunk.message.content } : msg
                )
              );
            } else if (chunk.type === 'usage' || chunk.usage) {
              const usage = chunk.usage || {};
              const parts: string[] = [];
              if (typeof usage.total_tokens === 'number') parts.push(`Tokens: ${usage.total_tokens}`);
              if (typeof usage.response_time_ms === 'number') parts.push(`Response time: ${usage.response_time_ms}ms`);
              if (parts.length) {
                const tokenMessage: ChatMessage = {
                  id: `token-${chunk.message_id || messageId}`,
                  role: 'system',
                  content: `📊 ${parts.join(' | ')}`,
                  timestamp: new Date(),
                };
                setMessages((prev) => [...prev, tokenMessage]);
              }
            } else if (chunk.type === 'error' || chunk.error) {
              throw new Error(chunk.error || 'Streaming error');
            } else if (chunk.event === 'done' || chunk.type === 'end') {
              return;
            }
          } catch (parseError) {
            // Not JSON or partial line; ignore until buffer completes
            // console.warn('Failed to parse streaming chunk:', parseError, payload);
          }
        }
      }
    } catch (error) {
      console.error('Streaming error:', error);
      throw error;
    }
  };

  const sendMessage = async () => {
    if (!message.trim() || loading) return;

    const text = message.trim();
    setMessage('');
    setLoading(true);

    try {
      // Ensure we have a conversation id we can include immediately
      let conversationId = currentConversation?.id;
      if (!conversationId) {
        const conv = await startNewConversation();
        conversationId = conv?.id;
      }

      const userMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'user',
        content: text,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);

      // Build the chat request with config panel values
      const sendRequest: ChatRequest = {
        message: text,
        conversation_id: conversationId,
        stream: streamingEnabled,
        profile_id: selectedProfile && selectedProfile !== currentConversation?.profile_id ? selectedProfile : undefined,
        temperature: temperature !== 0.7 ? temperature : undefined,
        max_tokens: maxTokens !== 2048 ? maxTokens : undefined,
        enable_retrieval: enableRetrieval,
        document_ids: selectedDocuments.length > 0 ? selectedDocuments : undefined,
        system_prompt_override: selectedPrompt ? prompts.find(p => p.id === selectedPrompt)?.content : undefined,
      };

      if (streamingEnabled) {
        await handleStreamingResponse(sendRequest);
      } else {
        // Use regular API
        const response = await chatterSDK.conversations.chatApiV1ChatChatPost({ chatRequest: sendRequest });

        // Narrow the SDK's loosely-typed response
        type ApiChatMessage = {
          id: string | number;
          content: string;
          created_at: string | number | Date;
          total_tokens?: number;
          response_time_ms?: number;
        };
        const apiMessage = (response.data as { message: ApiChatMessage }).message;

        const assistantMessage: ChatMessage = {
          id: String(apiMessage.id),
          role: 'assistant',
          content: apiMessage.content,
          timestamp: new Date(apiMessage.created_at),
        };
        setMessages((prev) => [...prev, assistantMessage]);

        const hasTokens = typeof apiMessage.total_tokens === 'number';
        const hasTime = typeof apiMessage.response_time_ms === 'number';
        if (hasTokens || hasTime) {
          const parts: string[] = [];
          if (hasTokens) parts.push(`Tokens: ${apiMessage.total_tokens}`);
          if (hasTime) parts.push(`Response time: ${apiMessage.response_time_ms}ms`);
          const tokenMessage: ChatMessage = {
            id: `token-${String(apiMessage.id)}`,
            role: 'system',
            content: `📊 ${parts.join(' | ')}`,
            timestamp: new Date(),
          };
          setMessages((prev) => [...prev, tokenMessage]);
        }
      }
    } catch (err: any) {
      setError('Failed to send message');
      console.error(err);

      const errorMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your message. Please try again.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  // Fix typing to match TextField's onKeyDown (root div)
  const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (e.key === 'Enter' && !e.shiftKey && !(e.nativeEvent as any).isComposing) {
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
        return <SpeedIcon />;
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
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        flex: 1,
        minHeight: 0,
      }}
    >
      {error && (
        <Alert severity="error" sx={{ mb: 1 }}>
          {error}
        </Alert>
      )}

      {/* Quick Actions Bar */}
      <Card sx={{ flexShrink: 0, mb: 1, position: 'relative', zIndex: 1 }}>
        <CardContent sx={{ py: 1, px: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={streamingEnabled}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setStreamingEnabled(e.target.checked)}
                    icon={<SpeedIcon />}
                    checkedIcon={<StreamIcon />}
                  />
                }
                label={streamingEnabled ? 'Streaming' : 'Standard'}
              />
              <Divider orientation="vertical" flexItem />
              <Button variant="outlined" size="small" onClick={startNewConversation} startIcon={<RefreshIcon />}>
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

            {/* Toggle right drawer */}
            <Tooltip title={open ? 'Hide Settings' : 'Show Settings'}>
              <IconButton onClick={() => setOpen(!open)} size="small">
                <TuneIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </CardContent>
      </Card>

      {/* Messages Area */}
      <Card sx={{ flex: 1, minHeight: 0, display: 'flex', flexDirection: 'column', mb: 1 }}>
        <CardContent
          sx={{
            flex: 1,
            minHeight: 0,
            overflow: 'hidden',
            p: 0,
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          <Box
            sx={{
              flex: 1,
              minHeight: 0,
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
                  <Avatar sx={{ bgcolor: getMessageColor(msg.role), ...(msg.role === 'user' ? { ml: 1 } : { mr: 1 }) }}>
                    {getMessageAvatar(msg.role)}
                  </Avatar>
                  <Paper
                    sx={{
                      p: 2,
                      maxWidth: '70%',
                      bgcolor:
                        msg.role === 'user'
                          ? 'primary.light'
                          : (theme) => (theme.palette.mode === 'dark' ? 'grey.800' : 'grey.100'),
                      color: msg.role === 'user' ? 'primary.contrastText' : 'text.primary',
                    }}
                  >
                    <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                      {msg.content}
                    </Typography>
                    <Typography variant="caption" sx={{ display: 'block', mt: 1, opacity: 0.7 }}>
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
      <Paper sx={{ p: 1.5, flexShrink: 0 }}>
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
          <TextField
            fullWidth
            multiline
            maxRows={4}
            placeholder="Type your message here... (Shift+Enter for new line)"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
            variant="outlined"
            size="small"
            inputRef={inputRef}
            autoFocus
            autoComplete="off"
          />
          <IconButton color="primary" onClick={sendMessage} disabled={!message.trim() || loading} sx={{ p: 1.5 }}>
            <SendIcon />
          </IconButton>
        </Box>
      </Paper>
    </Box>
  );
};

export default ChatPage;
