import React, { memo } from 'react';
import { Box } from '../../utils/mui';
import CustomScrollbar from '../CustomScrollbar';
import EnhancedMessage, { ChatMessage } from '../EnhancedMessage';

interface ChatMessageListProps {
  messages: ChatMessage[];
  messagesEndRef: React.RefObject<HTMLDivElement>;
  loading: boolean;
}

const ChatMessageList: React.FC<ChatMessageListProps> = memo(
  ({ messages, messagesEndRef, loading }) => {
    return (
      <Box sx={{ flexGrow: 1, overflow: 'hidden' }}>
        <CustomScrollbar maxHeight="calc(100vh - 200px)">
          <Box sx={{ p: 2, minHeight: '100%' }}>
            {messages.map((msg) => (
              <EnhancedMessage
                key={msg.id}
                message={msg}
                onEdit={msg.onEdit}
                onRegenerate={msg.onRegenerate}
                onDelete={msg.onDelete}
                onRate={msg.onRate}
              />
            ))}

            {loading && (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
                <EnhancedMessage
                  message={{
                    id: 'loading',
                    role: 'assistant',
                    content: '',
                    timestamp: new Date(),
                    isStreaming: true,
                    streamingContent: '',
                    metadata: {
                      workflow: {
                        stage: 'Processing',
                        currentStep: 1,
                        totalSteps: 3,
                        stepDescriptions: [
                          'Analyzing input',
                          'Generating response',
                          'Finalizing',
                        ],
                      },
                    },
                    onEdit: () => {
                      // Mock function for loading state
                    },
                    onRegenerate: () => {
                      // Mock function for loading state
                    },
                    onDelete: () => {
                      // Mock function for loading state
                    },
                    onRate: () => {
                      // Mock function for loading state
                    },
                  }}
                  onEdit={() => {
                    // Mock function for loading state
                  }}
                  onRegenerate={() => {
                    // Mock function for loading state
                  }}
                  onDelete={() => {
                    // Mock function for loading state
                  }}
                  onRate={() => {
                    // Mock function for loading state
                  }}
                />
              </Box>
            )}

            <div ref={messagesEndRef} />
          </Box>
        </CustomScrollbar>
      </Box>
    );
  }
);

ChatMessageList.displayName = 'ChatMessageList';

export default ChatMessageList;
