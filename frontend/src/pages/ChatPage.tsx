import React, { useState, useCallback, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
} from '../utils/mui';
import {
  BotIcon,
  HistoryIcon,
  DownloadIcon,
  RefreshIcon,
} from '../utils/icons';
import PageLayout from '../components/PageLayout';
import ChatConfigPanel from './ChatConfigPanel';
import ConversationHistory from '../components/ConversationHistory';
import ChatExport from '../components/ChatExport';
import ChatMessageList from '../components/chat/ChatMessageList';
import ChatInput from '../components/chat/ChatInput';
import { useChatData, useChatMessages } from '../hooks/useChatData';
import { getSDK } from '../services/auth-service';
import { toastService } from '../services/toast-service';
import { handleError } from '../utils/error-handler';
import { ChatMessage } from '../components/EnhancedMessage';
import { useRightSidebar } from '../components/RightSidebarContext';

const ChatPage: React.FC = () => {
  
  // Use right sidebar context
  const { setPanelContent, setTitle, setOpen } = useRightSidebar();
  
  // Use custom hooks for data and message management
  const {
    profiles,
    prompts,
    documents,
    currentConversation,
    selectedProfile,
    selectedPrompt,
    selectedDocuments,
    streamingEnabled,
    temperature,
    maxTokens,
    enableRetrieval,
    setSelectedProfile,
    setSelectedPrompt,
    setSelectedDocuments,
    setCurrentConversation,
    setStreamingEnabled,
    setTemperature,
    setMaxTokens,
    setEnableRetrieval,
    loadData,
  } = useChatData();

  const {
    message,
    messages,
    loading,
    messagesEndRef,
    inputRef,
    setMessage,
    setMessages,
    setLoading,
    loadMessagesForConversation,
    clearMessages,
    focusInput,
  } = useChatMessages();

  // Dialog state
  const [historyDialogOpen, setHistoryDialogOpen] = useState(false);
  const [exportDialogOpen, setExportDialogOpen] = useState(false);

  // Message handlers
  const handleEditMessage = useCallback((messageId: string, newContent: string) => {
    setMessages(prev => prev.map(msg => 
      msg.id === messageId 
        ? { ...msg, content: newContent }
        : msg
    ));
  }, [setMessages]);

  const handleRegenerateMessage = useCallback(async (messageId: string) => {
    try {
      setLoading(true);
      // Find the message and regenerate from the previous user message
      const messageIndex = messages.findIndex(msg => msg.id === messageId);
      if (messageIndex > 0) {
        const userMessage = messages[messageIndex - 1];
        if (userMessage.role === 'user') {
          // Call sendMessage directly here to avoid circular dependency
          const textToSend = userMessage.content;
          if (!textToSend) return;

          // Prepare chat request
          const chatRequest = {
            message: textToSend,
            profile_id: selectedProfile || undefined,
            prompt_id: selectedPrompt || undefined,
            document_ids: selectedDocuments.length > 0 ? selectedDocuments : undefined,
            temperature,
            max_tokens: maxTokens,
            stream: streamingEnabled,
            enable_retrieval: enableRetrieval,
          };

          // Send message to API
          let response;
          if (streamingEnabled) {
            // Use streaming endpoint
            response = await getSDK().chat.streamingChatApiV1ChatStreaming(chatRequest);
          } else {
            // Use non-streaming endpoint  
            response = await getSDK().chat.chatApiV1Chat(chatRequest);
          }

          // Create assistant message
          const assistantMessage: ChatMessage = {
            id: `assistant-${Date.now()}`,
            role: 'assistant',
            content: response.message.content,
            timestamp: new Date(),
            metadata: {
              model: response.message.model_used || undefined,
              tokens: response.message.total_tokens || undefined,
              processingTime: response.message.response_time_ms || undefined,
              workflow: {
                stage: 'Complete',
                currentStep: 0,
                totalSteps: 1,
                stepDescriptions: ['Message processed'],
              },
            },
            onEdit: handleEditMessage,
            onRegenerate: handleRegenerateMessage,
            onDelete: handleDeleteMessage,
            onRate: handleRateMessage,
          };

          // Replace the last assistant message
          setMessages(prev => {
            const newMessages = [...prev];
            const lastAssistantIndex = newMessages.findLastIndex(msg => msg.role === 'assistant');
            if (lastAssistantIndex !== -1) {
              newMessages[lastAssistantIndex] = assistantMessage;
            }
            return newMessages;
          });
        }
      }
    } catch (error) {
      handleError(error, {
        source: 'ChatPage.handleRegenerateMessage',
        operation: 'regenerate message',
      });
    } finally {
      setLoading(false);
    }
  }, [
    messages, 
    setLoading, 
    selectedProfile,
    selectedPrompt,
    selectedDocuments,
    temperature,
    maxTokens,
    streamingEnabled,
    enableRetrieval,
    setMessages,
    handleEditMessage,
    handleDeleteMessage,
    handleRateMessage,
  ]);

  const handleDeleteMessage = useCallback((messageId: string) => {
    setMessages(prev => prev.filter(msg => msg.id !== messageId));
  }, [setMessages]);

  const handleRateMessage = useCallback((messageId: string, rating: 'good' | 'bad') => {
    // Implementation for message rating
    toastService.info(`Message rated as ${rating}`);
  }, []);

  const handleSelectConversation = useCallback(async (conversationId: string) => {
    try {
      const conversation = await getSDK().conversations.getConversationApiV1ConversationsConversationId(conversationId);
      setCurrentConversation(conversation);
      await loadMessagesForConversation(conversationId);
      setHistoryDialogOpen(false);
    } catch (error) {
      handleError(error, {
        source: 'ChatPage.handleSelectConversation',
        operation: 'select conversation',
      });
    }
  }, [setCurrentConversation, loadMessagesForConversation]);

  // Set up right sidebar content
  useEffect(() => {
    setTitle('Chat Settings');
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
        onSelectConversation={handleSelectConversation}
      />
    );
    setOpen(true);
  }, [
    setPanelContent, 
    setTitle, 
    setOpen,
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
    handleSelectConversation,
  ]);

  const sendMessage = useCallback(async (messageText?: string, isRegeneration = false) => {
    const textToSend = messageText || message.trim();
    if (!textToSend || loading) return;

    try {
      setLoading(true);
      
      if (!isRegeneration) {
        setMessage('');
      }

      // Create user message
      const userMessage: ChatMessage = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: textToSend,
        timestamp: new Date(),
        onEdit: handleEditMessage,
        onRegenerate: handleRegenerateMessage,
        onDelete: handleDeleteMessage,
        onRate: handleRateMessage,
      };

      if (!isRegeneration) {
        setMessages(prev => [...prev, userMessage]);
      }

      // Prepare chat request
      const chatRequest = {
        message: textToSend,
        profile_id: selectedProfile || undefined,
        prompt_id: selectedPrompt || undefined,
        document_ids: selectedDocuments.length > 0 ? selectedDocuments : undefined,
        temperature,
        max_tokens: maxTokens,
        stream: streamingEnabled,
        enable_retrieval: enableRetrieval,
      };

      // Send message to API
      let response;
      if (streamingEnabled) {
        // Use streaming endpoint
        response = await getSDK().chat.streamingChatApiV1ChatStreaming(chatRequest);
      } else {
        // Use non-streaming endpoint  
        response = await getSDK().chat.chatApiV1Chat(chatRequest);
      }

      // Create assistant message
      const assistantMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.message.content,
        timestamp: new Date(),
        metadata: {
          model: response.message.model_used || undefined,
          tokens: response.message.total_tokens || undefined,
          processingTime: response.message.response_time_ms || undefined,
          workflow: {
            stage: 'Complete',
            currentStep: 0,
            totalSteps: 1,
            stepDescriptions: ['Message processed'],
          },
        },
        onEdit: handleEditMessage,
        onRegenerate: handleRegenerateMessage,
        onDelete: handleDeleteMessage,
        onRate: handleRateMessage,
      };

      if (isRegeneration) {
        // Replace the last assistant message
        setMessages(prev => {
          const newMessages = [...prev];
          const lastAssistantIndex = newMessages.findLastIndex(msg => msg.role === 'assistant');
          if (lastAssistantIndex !== -1) {
            newMessages[lastAssistantIndex] = assistantMessage;
          }
          return newMessages;
        });
      } else {
        setMessages(prev => [...prev, assistantMessage]);
      }

      focusInput();
    } catch (error) {
      handleError(error, {
        source: 'ChatPage.sendMessage',
        operation: 'send message',
      });
    } finally {
      setLoading(false);
    }
  }, [
    message,
    loading,
    selectedProfile,
    selectedPrompt,
    selectedDocuments,
    temperature,
    maxTokens,
    streamingEnabled,
    enableRetrieval,
    setMessage,
    setMessages,
    setLoading,
    handleEditMessage,
    handleRegenerateMessage,
    handleDeleteMessage,
    handleRateMessage,
    focusInput,
  ]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLDivElement>) => {
    if (
      e.key === 'Enter' &&
      !e.shiftKey &&
      !(e.nativeEvent as KeyboardEvent & { isComposing?: boolean }).isComposing
    ) {
      e.preventDefault();
      sendMessage();
    }
  }, [sendMessage]);

  const handleClearMessages = useCallback(() => {
    clearMessages();
    setCurrentConversation(null);
  }, [clearMessages, setCurrentConversation]);

  // Toolbar content
  const toolbar = (
    <>
      <Button
        variant="outlined"
        startIcon={<RefreshIcon />}
        onClick={loadData}
        size="small"
      >
        Refresh
      </Button>
      <Button
        variant="outlined"
        startIcon={<HistoryIcon />}
        onClick={() => setHistoryDialogOpen(true)}
        size="small"
      >
        History
      </Button>
      <Button
        variant="outlined"
        startIcon={<DownloadIcon />}
        onClick={() => setExportDialogOpen(true)}
        disabled={messages.length === 0}
        size="small"
      >
        Export
      </Button>
    </>
  );

  // Chat input component
  const messageInput = (
    <ChatInput
      message={message}
      setMessage={setMessage}
      loading={loading}
      streamingEnabled={streamingEnabled}
      setStreamingEnabled={setStreamingEnabled}
      onSendMessage={() => sendMessage()}
      onClearMessages={handleClearMessages}
      onKeyDown={handleKeyDown}
      inputRef={inputRef}
    />
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
          {messages.length === 0 ? (
            <Box
              sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100%',
                color: 'text.secondary',
                p: 4,
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
            <ChatMessageList
              messages={messages}
              messagesEndRef={messagesEndRef}
              loading={loading}
            />
          )}
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
        conversationTitle={
          currentConversation?.title || 'Untitled Conversation'
        }
      />
    </PageLayout>
  );
};

export default ChatPage;