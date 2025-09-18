import React, { memo } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  IconButton,
  Button,
  FormControlLabel,
  Switch,
} from '../../utils/mui';
import { SendIcon, ClearIcon } from '../../utils/icons';

interface ChatInputProps {
  message: string;
  setMessage: (message: string) => void;
  loading: boolean;
  streamingEnabled: boolean;
  setStreamingEnabled: (enabled: boolean) => void;
  onSendMessage: () => void;
  onClearMessages: () => void;
  onKeyDown: (e: React.KeyboardEvent<HTMLDivElement>) => void;
  inputRef: React.RefObject<HTMLInputElement | HTMLTextAreaElement | null>;
}

const ChatInput: React.FC<ChatInputProps> = memo(
  ({
    message,
    setMessage,
    loading,
    streamingEnabled,
    setStreamingEnabled,
    onSendMessage,
    onClearMessages,
    onKeyDown,
    inputRef,
  }) => {
    return (
      <Card>
        <CardContent sx={{ p: 2 }}>
          <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
            <TextField
              fullWidth
              multiline
              minRows={1}
              maxRows={4}
              placeholder="Type your message..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={onKeyDown}
              disabled={loading}
              inputRef={inputRef}
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                },
              }}
            />
            <IconButton
              color="primary"
              onClick={onSendMessage}
              disabled={loading || !message.trim()}
              sx={{
                alignSelf: 'flex-end',
                mb: 0.5,
              }}
            >
              <SendIcon />
            </IconButton>
          </Box>

          <Box
            sx={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <FormControlLabel
              control={
                <Switch
                  checked={streamingEnabled}
                  onChange={(e) => setStreamingEnabled(e.target.checked)}
                  size="small"
                />
              }
              label="Streaming"
            />

            <Button
              variant="outlined"
              startIcon={<ClearIcon />}
              onClick={onClearMessages}
              size="small"
              disabled={loading}
            >
              Clear Chat
            </Button>
          </Box>
        </CardContent>
      </Card>
    );
  }
);

ChatInput.displayName = 'ChatInput';

export default ChatInput;
