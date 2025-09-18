import React, { useState, useCallback, useEffect, useRef } from 'react';
import { Box, Card, CardContent, Typography, Button } from '../utils/mui';
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
import type { ConversationResponse, ChatRequest } from 'chatter-sdk';
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

  // Create a ref to handle circular dependency between handleStreamingResponse and handleRegenerateMessage
  const handleRegenerateMessageRef = useRef<((messageId: string) => Promise<void>) | null>(null);

  // Message handlers
  const handleEditMessage = useCallback(
    (messageId: string, newContent: string) => {
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === messageId ? { ...msg, content: newContent } : msg
        )
      );
    },
    [setMessages]
  );

  const handleDeleteMessage = useCallback(
    (messageId: string) => {
      setMessages((prev) => prev.filter((msg) => msg.id !== messageId));
    },
    [setMessages]
  );

  const handleRateMessage = useCallback(
    (messageId: string, rating: number) => {
      // Implementation for message rating
      const ratingText = rating >= 4 ? 'good' : rating >= 3 ? 'neutral' : 'bad';
      toastService.info(`Message rated as ${ratingText} (${rating} stars)`);
    },
    []
  );

  // Handle streaming response from chat API
  const handleStreamingResponse = useCallback(
    async (chatRequest: ChatRequest, isRegeneration: boolean) => {
      try {
        // Get the streaming response
        const stream =
          await getSDK().chat.streamingChatApiV1ChatStreaming(chatRequest);

        // Create a text decoder to handle the stream
        const decoder = new TextDecoder();
        const reader = stream.getReader();

        let streamedContent = '';
        let assistantMessageId = `assistant-${Date.now()}`;

        // Create initial assistant message with empty content
        const initialAssistantMessage: ChatMessage = {
          id: assistantMessageId,
          role: 'assistant',
          content: '',
          timestamp: new Date(),
          metadata: {
            workflow: {
              stage: 'Streaming',
              currentStep: 0,
              totalSteps: 1,
              stepDescriptions: ['Receiving response...'],
            },
          },
        };

        // Add the initial message to the chat
        if (isRegeneration) {
          setMessages((prev) => {
            const newMessages = [...prev];
            // Find last index by iterating backwards
            let lastAssistantIndex = -1;
            for (let i = newMessages.length - 1; i >= 0; i--) {
              if (newMessages[i].role === 'assistant') {
                lastAssistantIndex = i;
                break;
              }
            }
            if (lastAssistantIndex !== -1) {
              newMessages[lastAssistantIndex] = initialAssistantMessage;
            }
            return newMessages;
          });
        } else {
          setMessages((prev) => [...prev, initialAssistantMessage]);
        }

        let buffer = '';
        let totalTokens: number | undefined;
        let model: string | undefined;
        let processingTime: number | undefined;

        // Process the stream
        while (true) {
          const { done, value } = await reader.read();

          if (done) {
            break;
          }

          // Decode the chunk and add to buffer
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || ''; // Keep the last incomplete line in buffer

          // Process each complete line
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const raw = line.slice(6).trim();

              // Handle special cases
              if (raw === '[DONE]') {
                // End of stream
                continue;
              }

              try {
                const eventData = JSON.parse(raw);

                switch (eventData.type) {
                  case 'start':
                    // Stream started
                    break;

                  case 'token':
                    // Add the token to our streamed content
                    streamedContent += eventData.content || '';

                    // Update the message with the new content
                    setMessages((prev) =>
                      prev.map((msg) =>
                        msg.id === assistantMessageId
                          ? {
                              ...msg,
                              content: streamedContent,
                              metadata: {
                                ...msg.metadata,
                                workflow: {
                                  stage: 'Streaming',
                                  currentStep: 0,
                                  totalSteps: 1,
                                  stepDescriptions: ['Receiving response...'],
                                },
                              },
                            }
                          : msg
                      )
                    );
                    break;

                  case 'complete':
                    // Extract final metadata
                    if (eventData.metadata) {
                      totalTokens = eventData.metadata.total_tokens;
                      model = eventData.metadata.model_used;
                      processingTime = eventData.metadata.response_time_ms;
                    }

                    // Update the message with final metadata
                    setMessages((prev) =>
                      prev.map((msg) =>
                        msg.id === assistantMessageId
                          ? {
                              ...msg,
                              content: streamedContent,
                              metadata: {
                                model,
                                tokens: totalTokens,
                                processingTime,
                                workflow: {
                                  stage: 'Complete',
                                  currentStep: 1,
                                  totalSteps: 1,
                                  stepDescriptions: ['Response completed'],
                                },
                              },
                            }
                          : msg
                      )
                    );
                    break;

                  case 'error':
                    throw new Error(
                      eventData.message || 'Streaming error occurred'
                    );

                  default:
                    // Handle other event types if needed
                    // console.log('Unknown streaming event type:', eventData.type);
                    break;
                }
              } catch (parseError) {
                // Skip malformed data
              }
            }
          }
        }

        // Clean up
        reader.releaseLock();

        // Focus input after streaming is complete
        focusInput();
      } catch (error) {
        // Handle streaming errors by showing an error message
        const errorMessage: ChatMessage = {
          id: `assistant-error-${Date.now()}`,
          role: 'assistant',
          content:
            'Sorry, I encountered an error while processing your request. Please try again.',
          timestamp: new Date(),
          metadata: {
            workflow: {
              stage: 'Error',
              currentStep: 0,
              totalSteps: 1,
              stepDescriptions: ['Error occurred during streaming'],
            },
          },
        };

        if (isRegeneration) {
          setMessages((prev) => {
            const newMessages = [...prev];
            // Find last index by iterating backwards
            let lastAssistantIndex = -1;
            for (let i = newMessages.length - 1; i >= 0; i--) {
              if (newMessages[i].role === 'assistant') {
                lastAssistantIndex = i;
                break;
              }
            }
            if (lastAssistantIndex !== -1) {
              newMessages[lastAssistantIndex] = errorMessage;
            }
            return newMessages;
          });
        } else {
          setMessages((prev) => [...prev, errorMessage]);
        }

        handleError(error, {
          source: 'ChatPage.handleStreamingResponse',
          operation: 'stream chat response',
        });
      }
    },
    [
      setMessages,
      handleEditMessage,
      handleDeleteMessage,
      handleRateMessage,
      focusInput,
    ]
  );

  const handleRegenerateMessage = useCallback(
    async (messageId: string) => {
      try {
        setLoading(true);
        // Find the message and regenerate from the previous user message
        const messageIndex = messages.findIndex((msg) => msg.id === messageId);
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
              document_ids:
                selectedDocuments.length > 0 ? selectedDocuments : undefined,
              temperature,
              max_tokens: maxTokens,
              enable_retrieval: enableRetrieval,
            };

            // Send message to API
            let response;
            if (streamingEnabled) {
              // Use streaming endpoint
              await handleStreamingResponse(chatRequest, true);
              return; // Streaming handling is complete
            } else {
              // Use non-streaming endpoint
              response = await getSDK().chat.chatChat(chatRequest);
            }

            // Validate response structure
            if (
              !response ||
              !response.message ||
              typeof response.message.content !== 'string'
            ) {
              throw new Error('Invalid response from chat API');
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
            };

            // Replace the last assistant message
            setMessages((prev) => {
              const newMessages = [...prev];
              // Find last index by iterating backwards
              let lastAssistantIndex = -1;
              for (let i = newMessages.length - 1; i >= 0; i--) {
                if (newMessages[i].role === 'assistant') {
                  lastAssistantIndex = i;
                  break;
                }
              }
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
    },
    [
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
      handleStreamingResponse,
    ]
  );

  // Update the ref with the current function so it can be called from handleStreamingResponse
  handleRegenerateMessageRef.current = handleRegenerateMessage;

  const handleSelectConversation = useCallback(
    async (conversation: ConversationResponse) => {
      try {
        const conversationWithMessages =
          await getSDK().conversations.getConversationApiV1ConversationsConversationId(
            conversation.id
          );
        setCurrentConversation(conversationWithMessages);
        await loadMessagesForConversation(conversation.id);
        setHistoryDialogOpen(false);
      } catch (error) {
        handleError(error, {
          source: 'ChatPage.handleSelectConversation',
          operation: 'select conversation',
        });
      }
    },
    [setCurrentConversation, loadMessagesForConversation]
  );

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

  const sendMessage = useCallback(
    async (messageText?: string, isRegeneration = false) => {
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
        };

        if (!isRegeneration) {
          setMessages((prev) => [...prev, userMessage]);
        }

        // Prepare chat request
        const chatRequest = {
          message: textToSend,
          profile_id: selectedProfile || undefined,
          prompt_id: selectedPrompt || undefined,
          document_ids:
            selectedDocuments.length > 0 ? selectedDocuments : undefined,
          temperature,
          max_tokens: maxTokens,
          enable_retrieval: enableRetrieval,
        };

        // Send message to API
        let response;
        if (streamingEnabled) {
          // Use streaming endpoint
          await handleStreamingResponse(chatRequest, isRegeneration);
          return; // Streaming handling is complete
        } else {
          // Use non-streaming endpoint
          response = await getSDK().chat.chatChat(chatRequest);
        }

        // Validate response structure
        if (
          !response ||
          !response.message ||
          typeof response.message.content !== 'string'
        ) {
          throw new Error('Invalid response from chat API');
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
        };

        if (isRegeneration) {
          // Replace the last assistant message
          setMessages((prev) => {
            const newMessages = [...prev];
            // Find last index by iterating backwards
            let lastAssistantIndex = -1;
            for (let i = newMessages.length - 1; i >= 0; i--) {
              if (newMessages[i].role === 'assistant') {
                lastAssistantIndex = i;
                break;
              }
            }
            if (lastAssistantIndex !== -1) {
              newMessages[lastAssistantIndex] = assistantMessage;
            }
            return newMessages;
          });
        } else {
          setMessages((prev) => [...prev, assistantMessage]);
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
    },
    [
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
      handleStreamingResponse,
    ]
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLDivElement>) => {
      if (
        e.key === 'Enter' &&
        !e.shiftKey &&
        !(e.nativeEvent as KeyboardEvent & { isComposing?: boolean })
          .isComposing
      ) {
        e.preventDefault();
        sendMessage();
      }
    },
    [sendMessage]
  );

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
    <PageLayout title="Chat" toolbar={toolbar} fixedBottom={messageInput}>
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
              onEdit={handleEditMessage}
              onRegenerate={handleRegenerateMessage}
              onDelete={handleDeleteMessage}
              onRate={handleRateMessage}
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
