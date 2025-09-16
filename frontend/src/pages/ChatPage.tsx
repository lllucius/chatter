import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  IconButton,
  CircularProgress,
  Chip,
  Button,
  Divider,
  FormControlLabel,
  Switch,
  Avatar,
} from '@mui/material';
import CustomScrollbar from '../components/CustomScrollbar';
import PageLayout from '../components/PageLayout';
import {
  Send as SendIcon,
  SmartToy as BotIcon,
  Refresh as RefreshIcon,
  History as HistoryIcon,
  Download as DownloadIcon,
  Clear as ClearIcon,
} from '@mui/icons-material';
import { getSDK } from '../services/auth-service';
import { toastService } from '../services/toast-service';
import { handleError } from '../utils/error-handler';
import { ProfileResponse, PromptResponse, DocumentResponse, ConversationResponse, ConversationCreate, ChatRequest } from 'chatter-sdk';
import { useRightSidebar } from '../components/RightSidebarContext';
import ChatConfigPanel from './ChatConfigPanel';
import ConversationHistory from '../components/ConversationHistory';
import ChatExport from '../components/ChatExport';
import EnhancedMessage, { ChatMessage } from '../components/EnhancedMessage';

// Use ChatMessage directly as it already has the required fields
type ExtendedChatMessage = ChatMessage;

const ChatPage: React.FC = () => {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<ExtendedChatMessage[]>([]);
  const [profiles, setProfiles] = useState<ProfileResponse[]>([]);
  const [prompts, setPrompts] = useState<PromptResponse[]>([]);
  const [documents, setDocuments] = useState<DocumentResponse[]>([]);
  const [selectedProfile, setSelectedProfile] = useState<string>('');
  const [selectedPrompt, setSelectedPrompt] = useState<string>('');
  const [selectedDocuments, setSelectedDocuments] = useState<string[]>([]);
  const [currentConversation, setCurrentConversation] = useState<ConversationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // New state for advanced features
  const [historyDialogOpen, setHistoryDialogOpen] = useState(false);
  const [exportDialogOpen, setExportDialogOpen] = useState(false);

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
    let profilesResponse: any = null;
    try {
      const sdk = getSDK();
      const [profilesResp, promptsResponse, documentsResponse] = await Promise.all([
        sdk.profiles.listProfilesApiV1Profiles({}),
        sdk.prompts.listPromptsApiV1Prompts({}),
        sdk.documents.listDocumentsApiV1Documents({}),
      ]);
      profilesResponse = profilesResp;
      setProfiles(profilesResponse.profiles);
      setPrompts(promptsResponse.prompts);
      setDocuments(documentsResponse.documents);

      if (profilesResponse.profiles.length > 0) {
        setSelectedProfile(profilesResponse.profiles[0].id);
      }
    } catch (err: unknown) {
      handleError(err, {
        source: 'ChatPage.loadInitialData',
        operation: 'load profiles, prompts and documents',
        additionalData: { hasProfiles: profilesResponse?.profiles?.length }
      });
    }
  };

  // Return the created conversation so callers can use its id immediately
  const startNewConversation = useCallback(async (): Promise<ConversationResponse | null> => {
    const selectedPromptData = prompts.find((p) => p.id === selectedPrompt);
    try {
      await loadData();
      
      const systemPrompt = selectedPromptData?.content || undefined;
      
      const createRequest: ConversationCreate = {
        title: `Chat ${new Date().toLocaleString()}`,
        profile_id: selectedProfile || undefined,
        enable_retrieval: enableRetrieval,
        system_prompt: systemPrompt,
      };
      const response = await getSDK().conversations.createConversationApiV1Conversations(createRequest);
      setCurrentConversation(response);
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
      return response;
    } catch (err: unknown) {
      handleError(err, {
        source: 'ChatPage.startNewConversation',
        operation: 'create new conversation',
        additionalData: { 
          selectedProfile, 
          selectedPrompt, 
          enableRetrieval,
          promptName: selectedPromptData?.name 
        }
      });
      return null;
    }
  }, [selectedProfile, selectedPrompt, prompts, enableRetrieval]);

  const onSelectConversation = useCallback(async (conversation: ConversationResponse) => {
    try {
      // Set current conversation
      setCurrentConversation(conversation);
      
      // Load messages for this conversation
      const response = await getSDK().conversations.getConversationApiV1ConversationsConversationId(
        conversation.id,
        { includeMessages: true }
      );
      
      // Convert messages to ExtendedChatMessage format
      const chatMessages: ExtendedChatMessage[] = (response.messages || []).map(msg => ({
        id: msg.id,
        role: msg.role as 'user' | 'assistant' | 'system',
        content: msg.content,
        timestamp: new Date(msg.created_at),
        metadata: {
          model: msg.model_used || undefined,
          tokens: msg.total_tokens || undefined,
          processingTime: msg.response_time_ms || undefined,
        },
      }));
      
      setMessages(chatMessages);
      
      // Scroll to bottom after messages are set
      setTimeout(() => scrollToBottom(), 100);
    } catch (err: unknown) {
      handleError(err, {
        source: 'ChatPage.onSelectConversation',
        operation: 'load conversation messages',
        additionalData: { 
          conversationId: conversation.id,
          messageCount: conversation.message_count 
        }
      });
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
    setTitle('Configuration');
    
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
        selectedProfile={selectedProfile}
        setSelectedProfile={setSelectedProfile}
        selectedPrompt={selectedPrompt}
        setSelectedPrompt={setSelectedPrompt}
        selectedDocuments={selectedDocuments}
        setSelectedDocuments={setSelectedDocuments}
        temperature={temperature}
        setTemperature={setTemperature}
        maxTokens={maxTokens}
        setMaxTokens={setMaxTokens}
        enableRetrieval={enableRetrieval}
        setEnableRetrieval={setEnableRetrieval}
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
    selectedProfile,
    selectedPrompt,
    selectedDocuments,
    temperature,
    maxTokens,
    enableRetrieval,
    onSelectConversation,
  ]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleStreamingResponse = async (chatRequest: ChatRequest, assistantMessageId?: string) => {
    try {
      let currentMessageId = assistantMessageId || `stream-${Date.now()}`;
      
      // If no assistantMessageId provided, create a placeholder message
      if (!assistantMessageId) {
        const assistantMessage: ExtendedChatMessage = {
          id: currentMessageId,
          role: 'assistant',
          content: '',
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, assistantMessage]);
      }

      // Use SDK streaming method instead of direct fetch
      const sdk = getSDK();
      const stream = await sdk.chat.streamingChatApiV1ChatStreaming(chatRequest);

      if (!stream) {
        throw new Error('No response stream received');
      }

      const reader = stream.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      try {
        while (true) {
          const { done, value } = await reader.read();
          
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || ''; // Keep incomplete line in buffer

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const dataStr = line.slice(6).trim(); // Remove 'data: ' prefix
              
              if (dataStr === '[DONE]') {
                return; // End of stream
              }
              
              if (dataStr) {
                try {
                  const chunk = JSON.parse(dataStr);
                  
                  // Handle start chunk first to get the real message ID
                  if (chunk.type === 'start') {
                    // Update conversation if provided
                    if (chunk.conversation_id && !currentConversation) {
                      setCurrentConversation(prev => prev || { id: chunk.conversation_id } as ConversationResponse);
                    }
                    
                    // Update to real message ID from backend if provided
                    if (chunk.message_id && chunk.message_id !== currentMessageId) {
                      const oldMessageId = currentMessageId;
                      currentMessageId = chunk.message_id;
                      
                      setMessages((prev) =>
                        prev.map((msg) =>
                          msg.id === oldMessageId
                            ? { ...msg, id: currentMessageId }
                            : msg
                        )
                      );
                    }
                  } else if (chunk.type === 'token' && chunk.content) {
                    // Append token content to the message
                    setMessages((prev) =>
                      prev.map((msg) =>
                        msg.id === currentMessageId
                          ? { ...msg, content: msg.content + chunk.content }
                          : msg
                      )
                    );
                  } else if (chunk.type === 'complete' || chunk.type === 'end') {
                    // Stream ended - update final message with metadata if available
                    if (chunk.metadata) {
                      setMessages((prev) =>
                        prev.map((msg) =>
                          msg.id === currentMessageId
                            ? { 
                                ...msg, 
                                metadata: {
                                  model: chunk.metadata.model_used,
                                  tokens: chunk.metadata.total_tokens,
                                  processingTime: chunk.metadata.response_time_ms,
                                }
                              }
                            : msg
                        )
                      );
                    }
                    return; // End the streaming loop
                  } else if (chunk.type === 'error') {
                    throw new Error(chunk.content || chunk.error || 'Streaming error');
                  }
                } catch (parseError) {
                  // Failed to parse streaming chunk - log and skip invalid data
                  console.warn('Failed to parse streaming chunk:', dataStr, parseError);
                }
              }
            }
          }
        }
      } finally {
        reader.releaseLock();
      }

    } catch (err: unknown) {
      handleError(err, {
        source: 'ChatPage.handleStreamingResponse',
        operation: 'process streaming chat response',
        additionalData: { 
          conversationId: currentConversation?.id,
          messageLength: message.length 
        }
      });
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

      const userMessage: ExtendedChatMessage = {
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
        profile_id: selectedProfile && selectedProfile !== currentConversation?.profile_id ? selectedProfile : undefined,
        temperature,
        max_tokens: maxTokens,
        enable_retrieval: enableRetrieval,
        document_ids: selectedDocuments.length > 0 ? selectedDocuments : undefined,
        prompt_id: selectedPrompt || undefined,
        system_prompt_override: selectedPrompt ? prompts.find(p => p.id === selectedPrompt)?.content : undefined,
      };

      if (streamingEnabled) {
        await handleStreamingResponse(sendRequest);
      } else {
        // Use regular API
        const response = await getSDK().chat.chatChat(sendRequest);

        // Update conversation with the response data
        if (response.conversation) {
          setCurrentConversation(response.conversation);
        }

        // Use real message data from the API response
        const assistantMessage: ExtendedChatMessage = {
          id: String(response.message.id),
          role: 'assistant',
          content: response.message.content,
          timestamp: new Date(response.message.created_at),
          metadata: {
            model: response.message.model_used || undefined,
            tokens: response.message.total_tokens || undefined,
            processingTime: response.message.response_time_ms || undefined,
          },
        };
        setMessages((prev) => [...prev, assistantMessage]);

        // Remove the separate token message creation since we're including it in metadata
      }
    } catch (err: unknown) {
      handleError(err, {
        source: 'ChatPage.sendMessage',
        operation: 'send chat message',
        additionalData: { 
          conversationId: currentConversation?.id,
          messageLength: message.length,
          streamingEnabled,
          selectedProfile,
          temperature,
          maxTokens 
        }
      });

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

  // Enhanced message handlers
  const handleEditMessage = useCallback((messageId: string, newContent: string) => {
    setMessages(prev => prev.map(msg => 
      msg.id === messageId 
        ? { ...msg, content: newContent, edited: true, editedAt: new Date() }
        : msg
    ));
  }, []);

  const handleRegenerateMessage = useCallback(async (messageId: string) => {
    const messageIndex = messages.findIndex(msg => msg.id === messageId);
    if (messageIndex === -1) return;

    // Find the last user message before this assistant message
    let userMessageContent = '';
    for (let i = messageIndex - 1; i >= 0; i--) {
      if (messages[i].role === 'user') {
        userMessageContent = messages[i].content;
        break;
      }
    }

    if (!userMessageContent) return;

    // Remove the message to be regenerated and all messages after it
    setMessages(prev => prev.slice(0, messageIndex));

    // Regenerate the response
    try {
      setLoading(true);
      const sendRequest: ChatRequest = {
        message: userMessageContent,
        conversation_id: currentConversation?.id,
        profile_id: selectedProfile,
        temperature,
        max_tokens: maxTokens,
        enable_retrieval: enableRetrieval,
        document_ids: selectedDocuments.length > 0 ? selectedDocuments : undefined,
        prompt_id: selectedPrompt || undefined,
        system_prompt_override: selectedPrompt ? prompts.find(p => p.id === selectedPrompt)?.content : undefined,
      };

      if (streamingEnabled) {
        const assistantMessageId = Date.now().toString();
        const assistantMessage: ExtendedChatMessage = {
          id: assistantMessageId,
          role: 'assistant',
          content: '',
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, assistantMessage]);
        await handleStreamingResponse(sendRequest, assistantMessageId);
      } else {
        const response = await getSDK().chat.chatChat(sendRequest);
        const assistantMessage: ExtendedChatMessage = {
          id: Date.now().toString(),
          role: 'assistant',
          content: response.message.content,
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, assistantMessage]);
      }
    } catch (err: unknown) {
      handleError(err, {
        source: 'ChatPage.regenerateLastMessage',
        operation: 'regenerate assistant message',
        additionalData: { 
          conversationId: currentConversation?.id,
          messageId: messageId,
          selectedProfile,
          temperature,
          maxTokens 
        }
      });
    } finally {
      setLoading(false);
    }
  }, [messages, currentConversation, selectedProfile, streamingEnabled, temperature, maxTokens, enableRetrieval, selectedDocuments, selectedPrompt, prompts]);

  const handleDeleteMessage = useCallback((messageId: string) => {
    setMessages(prev => prev.filter(msg => msg.id !== messageId));
  }, []);

  const handleRateMessage = useCallback(async (messageId: string, rating: number) => {
    if (!currentConversation?.id) {
      toastService.error('No conversation selected for rating');
      return;
    }

    try {
      // Optimistically update the UI
      setMessages(prev => prev.map(msg => 
        msg.id === messageId 
          ? { ...msg, rating }
          : msg
      ));

      // Call the backend API to persist the rating using SDK
      const sdk = getSDK();
      const result = await sdk.conversations.updateMessageRatingApiV1ConversationsConversationIdMessagesMessageIdRating(
        currentConversation.id,
        messageId,
        { rating }
      );
      
      // Update the message with the actual server response (average rating)
      setMessages(prev => prev.map(msg => 
        msg.id === messageId 
          ? { ...msg, rating: result.rating }
          : msg
      ));

      toastService.success('Message rated successfully');
    } catch (error) {
      // Revert the optimistic update on error
      const previousRating = messages.find(msg => msg.id === messageId)?.rating;
      setMessages(prev => prev.map(msg => 
        msg.id === messageId 
          ? { ...msg, rating: previousRating }
          : msg
      ));
      
      handleError(error, {
        source: 'ChatPage.handleRateMessage',
        operation: 'rate message',
        additionalData: { 
          conversationId: currentConversation?.id,
          messageId 
        }
      });
    }
  }, [currentConversation?.id, messages]);

  const handleSelectConversation = useCallback((conversation: ConversationResponse) => {
    setCurrentConversation(conversation);
    // In a real implementation, you would load the conversation messages here
    // For now, we'll just clear the current messages
    setMessages([]);
  }, []);

  const handleClearConversation = useCallback(() => {
    if (window.confirm('Are you sure you want to clear this conversation?')) {
      setMessages([]);
      setCurrentConversation(null);
    }
  }, []);

  // Create the toolbar content
  const toolbar = (
    <>
      <FormControlLabel
        control={
          <Switch
            checked={streamingEnabled}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setStreamingEnabled(e.target.checked)}
          />
        }
        label={streamingEnabled ? 'Streaming' : 'Standard'}
      />
      <Divider orientation="vertical" flexItem />
      <Button variant="outlined" size="small" onClick={startNewConversation} startIcon={<RefreshIcon />}>
        New Chat
      </Button>
      <Button 
        variant="outlined" 
        size="small" 
        onClick={() => setHistoryDialogOpen(true)} 
        startIcon={<HistoryIcon />}
      >
        History
      </Button>
      <Button 
        variant="outlined" 
        size="small" 
        onClick={() => setExportDialogOpen(true)} 
        startIcon={<DownloadIcon />}
        disabled={messages.length === 0}
      >
        Export
      </Button>
      <Button 
        variant="outlined" 
        size="small" 
        onClick={handleClearConversation} 
        startIcon={<ClearIcon />}
        disabled={messages.length === 0}
        color="warning"
      >
        Clear
      </Button>
      {currentConversation && (
        <Chip
          label={`${currentConversation.title} (${messages.length} messages)`}
          size="small"
          variant="outlined"
        />
      )}
    </>
  );

  // Create the fixed bottom input area
  const messageInput = (
    <Box sx={{ p: 1.5 }}>
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
    </Box>
  );

  return (
    <PageLayout 
      title="Chat" 
      toolbar={toolbar}
      fixedBottom={messageInput}
    >
      {/* Messages Area */}
      <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
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
              p: 2,
              display: 'flex',
              flexDirection: 'column',
            }}
          >
            <CustomScrollbar style={{ flex: 1 }}>
              <Box sx={{ display: 'flex', flexDirection: 'column' }}>
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
                <EnhancedMessage
                  key={msg.id}
                  message={msg}
                  onEdit={handleEditMessage}
                  onRegenerate={handleRegenerateMessage}
                  onDelete={handleDeleteMessage}
                  onRate={handleRateMessage}
                  canEdit={msg.role === 'user'}
                  canRegenerate={msg.role === 'assistant'}
                  canDelete={true}
                />
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
            </CustomScrollbar>
          </Box>
        </CardContent>
      </Card>

      {/* Dialogs */}
      <ConversationHistory
        open={historyDialogOpen}
        onClose={() => setHistoryDialogOpen(false)}
        onSelectConversation={handleSelectConversation}
        currentConversationId={currentConversation?.id}
      />
      <ChatExport
        open={exportDialogOpen}
        onClose={() => setExportDialogOpen(false)}
        messages={messages}
        conversationTitle={currentConversation?.title || 'Untitled Conversation'}
      />
    </PageLayout>
  );
};

export default ChatPage;
