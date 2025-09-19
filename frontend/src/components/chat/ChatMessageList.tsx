import React, { memo } from 'react';
import { Box } from '../../utils/mui';
import EnhancedMessage, { ChatMessage } from '../EnhancedMessage';

interface ChatMessageListProps {
  messages: ChatMessage[];
  messagesEndRef: React.RefObject<HTMLDivElement | null>;
  loading: boolean;
  streamingEnabled?: boolean;
  onEdit?: (messageId: string, newContent: string) => void;
  onRegenerate?: (messageId: string) => void;
  onDelete?: (messageId: string) => void;
  onRate?: (messageId: string, rating: number) => Promise<void> | void;
}

const ChatMessageList: React.FC<ChatMessageListProps> = memo(
  ({
    messages,
    messagesEndRef,
    loading,
    streamingEnabled = false,
    onEdit,
    onRegenerate,
    onDelete,
    onRate,
  }) => {
    return (
      <Box sx={{ flexGrow: 1, minHeight: '100%', p: 2 }}>
        {messages.map((msg) => (
          <EnhancedMessage
            key={msg.id}
            message={msg}
            onEdit={onEdit}
            onRegenerate={onRegenerate}
            onDelete={onDelete}
            onRate={onRate}
          />
        ))}

        {loading && !streamingEnabled && (
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
    );
  }
);

ChatMessageList.displayName = 'ChatMessageList';

export default ChatMessageList;
