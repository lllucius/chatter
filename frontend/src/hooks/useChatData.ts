import { useState, useEffect, useRef, useCallback } from 'react';
import { getSDK } from '../services/auth-service';
import { handleError } from '../utils/error-handler';
import {
  ProfileResponse,
  PromptResponse,
  DocumentResponse,
  ConversationResponse,
} from 'chatter-sdk';
import { ChatMessage } from '../components/EnhancedMessage';

// Use ChatMessage directly as it already has the required fields
type ExtendedChatMessage = ChatMessage;

export const useChatData = () => {
  const [profiles, setProfiles] = useState<ProfileResponse[]>([]);
  const [prompts, setPrompts] = useState<PromptResponse[]>([]);
  const [documents, setDocuments] = useState<DocumentResponse[]>([]);
  const [selectedProfile, setSelectedProfile] = useState<string>('');
  const [selectedPrompt, setSelectedPrompt] = useState<string>('');
  const [selectedDocuments, setSelectedDocuments] = useState<string[]>([]);
  const [currentConversation, setCurrentConversation] =
    useState<ConversationResponse | null>(() => {
      // Try to restore the current conversation from localStorage
      const saved = localStorage.getItem('chatter_currentConversation');
      return saved ? JSON.parse(saved) : null;
    });

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
    return saved ? parseInt(saved) : 1000;
  });

  const [enableRetrieval, setEnableRetrieval] = useState(() => {
    const saved = localStorage.getItem('chatter_enableRetrieval');
    return saved ? JSON.parse(saved) : false;
  });

  const [enableTools, setEnableTools] = useState(() => {
    const saved = localStorage.getItem('chatter_enableTools');
    return saved ? JSON.parse(saved) : false;
  });

  const [customPromptText, setCustomPromptText] = useState(() => {
    const saved = localStorage.getItem('chatter_customPromptText');
    return saved ? saved : '';
  });

  // Load initial data
  const loadData = useCallback(async () => {
    let profilesResponse: ProfileResponse[] | null = null;
    try {
      const sdk = getSDK();
      const [
        profilesResp,
        promptsResponse,
        documentsResponse,
        conversationsResp,
      ] = await Promise.all([
        sdk.profiles.listProfilesApiV1Profiles({}),
        sdk.prompts.listPromptsApiV1Prompts({}),
        sdk.documents.listDocumentsGetApiV1Documents({}),
        sdk.conversations.listConversationsApiV1Conversations({
          limit: 1,
          offset: 0,
        }),
      ]);

      profilesResponse = profilesResp.profiles || [];
      setProfiles(profilesResponse);
      setPrompts(promptsResponse.prompts || []);
      setDocuments(documentsResponse?.documents || []);

      // Auto-select first profile if none selected and profiles exist
      if (!selectedProfile && profilesResponse.length > 0) {
        setSelectedProfile(profilesResponse[0].id);
      }

      // Load most recent conversation if any
      const conversations = conversationsResp.conversations || [];
      if (conversations.length > 0) {
        setCurrentConversation(conversations[0]);
      }
    } catch (error) {
      handleError(error, {
        source: 'useChatData.loadData',
        operation: 'load chat data',
      });
    }
  }, [selectedProfile]);

  // Persist settings to localStorage
  useEffect(() => {
    localStorage.setItem(
      'chatter_streamingEnabled',
      JSON.stringify(streamingEnabled)
    );
  }, [streamingEnabled]);

  useEffect(() => {
    localStorage.setItem('chatter_temperature', temperature.toString());
  }, [temperature]);

  useEffect(() => {
    localStorage.setItem('chatter_maxTokens', maxTokens.toString());
  }, [maxTokens]);

  useEffect(() => {
    localStorage.setItem(
      'chatter_enableRetrieval',
      JSON.stringify(enableRetrieval)
    );
  }, [enableRetrieval]);

  useEffect(() => {
    localStorage.setItem('chatter_enableTools', JSON.stringify(enableTools));
  }, [enableTools]);

  useEffect(() => {
    localStorage.setItem('chatter_customPromptText', customPromptText);
  }, [customPromptText]);

  // Persist current conversation
  useEffect(() => {
    if (currentConversation) {
      localStorage.setItem(
        'chatter_currentConversation',
        JSON.stringify(currentConversation)
      );
    } else {
      localStorage.removeItem('chatter_currentConversation');
    }
  }, [currentConversation]);

  // Load data on mount
  useEffect(() => {
    loadData();
  }, [loadData]);

  return {
    // Data
    profiles,
    prompts,
    documents,
    currentConversation,

    // Selected items
    selectedProfile,
    selectedPrompt,
    selectedDocuments,

    // Configuration
    streamingEnabled,
    temperature,
    maxTokens,
    enableRetrieval,
    enableTools,
    customPromptText,

    // Actions
    setSelectedProfile,
    setSelectedPrompt,
    setSelectedDocuments,
    setCurrentConversation,
    setStreamingEnabled,
    setTemperature,
    setMaxTokens,
    setEnableRetrieval,
    setEnableTools,
    setCustomPromptText,
    loadData,
  };
};

export const useChatMessages = () => {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<ExtendedChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement | HTMLTextAreaElement>(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = useCallback(() => {
    const timeoutId = setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
    return () => clearTimeout(timeoutId);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Focus input after sending
  const focusInput = useCallback(() => {
    const timeoutId = setTimeout(() => {
      inputRef.current?.focus();
    }, 100);
    return () => clearTimeout(timeoutId);
  }, []);

  // Load messages for a conversation
  const loadMessagesForConversation = useCallback(
    async (conversationId: string) => {
      try {
        const response =
          await getSDK().conversations.getConversationMessagesApiV1ConversationsConversationIdMessages(
            conversationId
          );

        const chatMessages: ExtendedChatMessage[] =
          response?.map((msg, _index) => ({
            id: msg.id,
            role: msg.role as 'user' | 'assistant',
            content: msg.content,
            timestamp: new Date(msg.created_at),
            metadata: {
              model: msg.model_used || undefined,
              tokens: msg.total_tokens || undefined,
              processingTime: msg.response_time_ms || undefined,
              workflow: {
                stage: 'Complete',
                currentStep: 0,
                totalSteps: 1,
                stepDescriptions: ['Message processed'],
              },
            },
            isStreaming: false,
            streamingContent: '',
            onEdit: () => {
              // Placeholder for edit functionality
            },
            onRegenerate: () => {
              // Placeholder for regenerate functionality
            },
            onDelete: () => {
              // Placeholder for delete functionality
            },
            onRate: (_rating: 'good' | 'bad') => {
              // Placeholder for rating functionality
              // TODO: Implement message rating
            },
          })) || [];

        setMessages(chatMessages);
      } catch (error) {
        handleError(error, {
          source: 'useChatMessages.loadMessagesForConversation',
          operation: 'load conversation messages',
        });
      }
    },
    []
  );

  // Clear all messages
  const clearMessages = useCallback(() => {
    setMessages([]);
    setMessage('');
  }, []);

  return {
    // Message state
    message,
    messages,
    loading,

    // Refs
    messagesEndRef,
    inputRef,

    // Actions
    setMessage,
    setMessages,
    setLoading,
    loadMessagesForConversation,
    clearMessages,
    scrollToBottom,
    focusInput,
  };
};
