import React, { useState, useCallback, useEffect, useRef } from 'react';
import { Box, Card, CardContent, Typography, Button } from '../utils/mui';
import {
  BotIcon,
  HistoryIcon,
  DownloadIcon,
  RefreshIcon,
} from '../utils/icons';
import PageLayout from '../components/PageLayout';
import ChatWorkflowConfigPanel from './ChatWorkflowConfigPanel';
import ConversationHistory from '../components/ConversationHistory';
import ChatExport from '../components/ChatExport';
import ChatMessageList from '../components/chat/ChatMessageList';
import ChatInput from '../components/chat/ChatInput';
import { useChatData, useChatMessages } from '../hooks/useChatData';
import { useWorkflowChat } from '../hooks/useWorkflowChat';
import { getSDK } from '../services/auth-service';
import { toastService } from '../services/toast-service';
import { handleError } from '../utils/error-handler';
import { ChatMessage } from '../components/EnhancedMessage';
import type {
  ConversationResponse,
  ChatResponse,
} from 'chatter-sdk';
import type { ChatWorkflowRequest } from '../hooks/useWorkflowChat';
import { parseSSELine } from '../utils/sse-parser';
import { useRightSidebar } from '../components/RightSidebarContext';

interface EventMetadata {
  model_used?: string;
  total_tokens?: number;
  response_time_ms?: number;
  [key: string]: unknown;
}

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
    temperature: _temperature,
    maxTokens: _maxTokens,
    enableRetrieval: _enableRetrieval,
    enableTools: _enableTools,
    customPromptText,
    setSelectedProfile,
    setSelectedPrompt,
    setSelectedDocuments,
    setCurrentConversation,
    setStreamingEnabled,
    setCustomPromptText,
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

  // Use workflow-based chat hook
  const {
    customWorkflowConfig,
    updateWorkflowConfig,
    buildWorkflowRequest,
    sendWorkflowMessage,
    getEffectiveConfig,
  } = useWorkflowChat();

  // Dialog state
  const [historyDialogOpen, setHistoryDialogOpen] = useState(false);
  const [exportDialogOpen, setExportDialogOpen] = useState(false);

  // Tracing state
  const [enableTracing, setEnableTracing] = useState(false);

  // Load conversation messages if we have a current conversation on mount
  useEffect(() => {
    if (
      currentConversation &&
      currentConversation.id &&
      messages.length === 0
    ) {
      loadMessagesForConversation(currentConversation.id);
    }
  }, [currentConversation, loadMessagesForConversation, messages.length]);

  // Create a ref to handle circular dependency for handleRegenerateMessage
  const handleRegenerateMessageRef = useRef<
    ((messageId: string) => Promise<void>) | null
  >(null);

  // Message handlers
  // Note: State setters (setMessages, setMessage, setLoading) are intentionally NOT included
  // in dependency arrays below. React guarantees state setters are stable references, and
  // including them can cause unnecessary callback re-creations and potential race conditions.
  const handleEditMessage = useCallback(
    (messageId: string, newContent: string) => {
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === messageId ? { ...msg, content: newContent } : msg
        )
      );
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps -- setMessages is a stable state setter
    []
  );

  const handleDeleteMessage = useCallback(
    (messageId: string) => {
      setMessages((prev) => prev.filter((msg) => msg.id !== messageId));
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps -- setMessages is a stable state setter
    []
  );

  const handleRateMessage = useCallback((messageId: string, rating: number) => {
    // Implementation for message rating
    const ratingText = rating >= 4 ? 'good' : rating >= 3 ? 'neutral' : 'bad';
    toastService.info(`Message rated as ${ratingText} (${rating} stars)`);
  }, []);

  // Shared streaming processing logic to avoid duplication
  const processStreamingResponse = useCallback(
    async (
      stream: ReadableStream<Uint8Array>,
      isRegeneration: boolean,
      assistantMessageId: string,
      setStreamedContent: (updater: (prev: string) => string) => void,
      setTotalTokens: (tokens: number | undefined) => void,
      setModel: (model: string | undefined) => void,
      setProcessingTime: (time: number | undefined) => void
    ) => {
      const decoder = new TextDecoder();
      const reader = stream.getReader();

      let buffer = '';
      let accumulatedContent = ''; // Track accumulated content locally

      try {
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
            if (!line.trim()) continue; // Skip empty lines

            const eventData = parseSSELine(line);
            if (!eventData) {
              continue; // Skip invalid or non-data lines
            }

            // Handle special end-of-stream marker
            if (eventData.type === 'done') {
              continue;
            }

            switch (eventData.type) {
              case 'start':
                // Stream started
                break;

              case 'token': {
                // Add the token to our streamed content
                const tokenContent = (eventData.content as string) || '';
                accumulatedContent += tokenContent;
                setStreamedContent((prev) => prev + tokenContent);

                // Update the message with the accumulated content
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === assistantMessageId
                      ? {
                          ...msg,
                          content: accumulatedContent,
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
              }

              case 'complete':
                // Extract final metadata
                if (
                  eventData.metadata &&
                  typeof eventData.metadata === 'object'
                ) {
                  const metadata = eventData.metadata as Record<
                    string,
                    unknown
                  >;
                  setTotalTokens(metadata.total_tokens as number | undefined);
                  setModel(metadata.model_used as string | undefined);
                  setProcessingTime(
                    metadata.response_time_ms as number | undefined
                  );
                }

                // Update the message with final metadata
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === assistantMessageId
                      ? {
                          ...msg,
                          metadata: {
                            model: (eventData.metadata as EventMetadata)
                              ?.model_used,
                            tokens: (eventData.metadata as EventMetadata)
                              ?.total_tokens,
                            processingTime: (
                              eventData.metadata as EventMetadata
                            )?.response_time_ms,
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

              case 'error': {
                // Handle error events gracefully
                // Server sends error in 'error' field, but fallback to 'message' for compatibility
                const errorMessage =
                  (eventData.error as string) ||
                  (eventData.message as string) ||
                  'Workflow streaming error occurred';

                // Log the error for debugging
                console.error('Workflow streaming error:', errorMessage);

                // Throw the error to be caught by handleWorkflowStreamingResponse
                throw new Error(errorMessage);
              }

              default:
                // Handle other event types if needed
                // console.log('Unknown streaming event type:', eventData.type);
                break;
            }
          }
        }

        // Clean up
        reader.releaseLock();
      } catch (error) {
        // Clean up on error
        if (reader) {
          try {
            reader.releaseLock();
          } catch {
            // Ignore release errors
          }
        }
        throw error; // Re-throw for caller to handle
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps -- setMessages is a stable state setter
    []
  );

  const handleWorkflowStreamingResponse = useCallback(
    async (workflowRequest: ChatWorkflowRequest, isRegeneration: boolean) => {
      try {
        // Get the streaming response from workflow API
        const stream = (await sendWorkflowMessage(
          workflowRequest,
          true
        )) as ReadableStream<Uint8Array>;

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
            } else {
              // If no assistant message found to replace, add it instead
              console.warn(
                '[ChatPage] No assistant message found to replace during streaming regeneration, adding new message'
              );
              newMessages.push(initialAssistantMessage);
            }
            return newMessages;
          });
        } else {
          setMessages((prev) => [...prev, initialAssistantMessage]);
        }

        // Local state for the callback functions (though they may not be used in this design)
        let streamedContent = '';
        // let totalTokens: number | undefined;
        // let model: string | undefined;
        // let processingTime: number | undefined;

        // Use the shared streaming processing logic
        await processStreamingResponse(
          stream,
          isRegeneration,
          assistantMessageId,
          (updater) => {
            streamedContent = updater(streamedContent);
          },
          (_tokens) => {
            // totalTokens = tokens;
          },
          (_modelName) => {
            // model = modelName;
          },
          (_time) => {
            // processingTime = time;
          }
        );

        // Focus input after streaming is complete
        focusInput();
      } catch (error) {
        // Handle errors by showing an error message
        console.error(
          'Streaming error in handleWorkflowStreamingResponse:',
          error
        );
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
              stepDescriptions: ['Error occurred during workflow processing'],
            },
          },
        };

        if (isRegeneration) {
          setMessages((prev) => {
            const newMessages = [...prev];
            let lastAssistantIndex = -1;
            for (let i = newMessages.length - 1; i >= 0; i--) {
              if (newMessages[i].role === 'assistant') {
                lastAssistantIndex = i;
                break;
              }
            }
            if (lastAssistantIndex !== -1) {
              newMessages[lastAssistantIndex] = errorMessage;
            } else {
              // If no assistant message found to replace, add the error message instead
              console.warn(
                '[ChatPage] No assistant message found to replace during error handling in streaming, adding error message'
              );
              newMessages.push(errorMessage);
            }
            return newMessages;
          });
        } else {
          setMessages((prev) => [...prev, errorMessage]);
        }

        handleError(error, {
          source: 'ChatPage.handleWorkflowStreamingResponse',
          operation: 'process workflow chat response',
        });
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps -- setMessages is a stable state setter
    [sendWorkflowMessage, focusInput, processStreamingResponse]
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

            // Prepare workflow chat request
            const workflowRequest = buildWorkflowRequest(
              textToSend,
              currentConversation?.id,
              {
                profile_id: selectedProfile || undefined,
                system_prompt_override: customPromptText.trim() || undefined,
                document_ids:
                  selectedDocuments.length > 0 ? selectedDocuments : undefined,
                enable_tracing: enableTracing,
                // Use workflow configuration directly for all settings
                enable_retrieval: customWorkflowConfig.enable_retrieval,
                enable_tools: customWorkflowConfig.enable_tools,
                enable_memory: customWorkflowConfig.enable_memory,
                enable_web_search:
                  customWorkflowConfig.enable_web_search || false,
                // Use the effective workflow configuration
                workflow_config: getEffectiveConfig(),
              }
            );

            // Send message to workflow API
            let response: ChatResponse;
            if (streamingEnabled) {
              // Use streaming workflow endpoint
              await handleWorkflowStreamingResponse(workflowRequest, true);
              return; // Streaming handling is complete
            } else {
              // Use non-streaming workflow endpoint
              response = (await sendWorkflowMessage(
                workflowRequest,
                false
              )) as ChatResponse;
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
              } else {
                // If no assistant message found to replace, add it instead
                console.warn(
                  '[ChatPage] No assistant message found to replace during regeneration, adding new message'
                );
                newMessages.push(assistantMessage);
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
      selectedProfile,
      selectedDocuments,
      currentConversation,
      customPromptText,
      streamingEnabled,
      customWorkflowConfig,
      buildWorkflowRequest,
      getEffectiveConfig,
      sendWorkflowMessage,
      handleWorkflowStreamingResponse,
      enableTracing,
    ]
  );

  // Update the ref with the current function
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
      <ChatWorkflowConfigPanel
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
        customPromptText={customPromptText}
        setCustomPromptText={setCustomPromptText}
        workflowConfig={customWorkflowConfig}
        updateWorkflowConfig={updateWorkflowConfig}
        enableTracing={enableTracing}
        setEnableTracing={setEnableTracing}
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
    customPromptText,
    customWorkflowConfig,
    handleSelectConversation,
    setSelectedProfile,
    setSelectedPrompt,
    setSelectedDocuments,
    setCustomPromptText,
    updateWorkflowConfig,
    enableTracing,
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

        // Prepare workflow chat request
        const workflowRequest = buildWorkflowRequest(
          textToSend,
          currentConversation?.id,
          {
            profile_id: selectedProfile || undefined,
            system_prompt_override: customPromptText.trim() || undefined,
            document_ids:
              selectedDocuments.length > 0 ? selectedDocuments : undefined,
            enable_tracing: enableTracing,
            // Use workflow configuration directly for all settings
            enable_retrieval: customWorkflowConfig.enable_retrieval,
            enable_tools: customWorkflowConfig.enable_tools,
            enable_memory: customWorkflowConfig.enable_memory,
            enable_web_search: customWorkflowConfig.enable_web_search || false,
            // Use the effective workflow configuration
            workflow_config: getEffectiveConfig(),
          }
        );

        // Send message to workflow API
        let response: ChatResponse;
        if (streamingEnabled) {
          // Use streaming workflow endpoint
          await handleWorkflowStreamingResponse(
            workflowRequest,
            isRegeneration
          );
          return; // Streaming handling is complete
        } else {
          // Use non-streaming workflow endpoint
          response = (await sendWorkflowMessage(
            workflowRequest,
            false
          )) as ChatResponse;
          console.log('[ChatPage] Received non-streaming response:', response);
        }

        // Validate response structure
        if (
          !response ||
          !response.message ||
          typeof response.message.content !== 'string'
        ) {
          console.error('[ChatPage] Invalid response structure:', {
            hasResponse: !!response,
            hasMessage: !!response?.message,
            contentType: typeof response?.message?.content,
            contentValue: response?.message?.content,
            fullResponse: response,
          });
          throw new Error('Invalid response from chat API');
        }

        console.log(
          '[ChatPage] Response validation passed, content:',
          response.message.content
        );

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

        console.log('[ChatPage] Created assistant message:', assistantMessage);
        console.log('[ChatPage] isRegeneration:', isRegeneration);

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
            } else {
              // If no assistant message found to replace, add it instead
              console.warn(
                '[ChatPage] No assistant message found to replace during regeneration in sendMessage, adding new message'
              );
              newMessages.push(assistantMessage);
            }
            return newMessages;
          });
        } else {
          console.log(
            '[ChatPage] Adding assistant message to state (not regeneration)'
          );
          setMessages((prev) => {
            console.log(
              '[ChatPage] setMessages updater called, prev.length:',
              prev.length
            );
            const newMessages = [...prev, assistantMessage];
            console.log(
              '[ChatPage] setMessages updater returning, newMessages.length:',
              newMessages.length
            );
            return newMessages;
          });
          console.log('[ChatPage] setMessages call completed');
        }

        console.log('[ChatPage] Message handling complete, focusing input');
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
      selectedDocuments,
      currentConversation,
      customPromptText,
      streamingEnabled,
      customWorkflowConfig,
      buildWorkflowRequest,
      getEffectiveConfig,
      sendWorkflowMessage,
      handleWorkflowStreamingResponse,
      focusInput,
      enableTracing,
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
              streamingEnabled={streamingEnabled}
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
