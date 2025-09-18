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
        <CustomScrollbar style={{ maxHeight: 'calc(100vh - 200px)' }}>
          <Box sx={{ p: 2, minHeight: '100%' }}>
            {messages.map((msg) => (
              <EnhancedMessage
                key={msg.id}
                message={msg}
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
                    metadata: {
                      workflow: {
                        stage: 'Processing',
                        progress: 33,
                        isStreaming: true,
                        status: 'processing',
                      },
                    },
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
