import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Divider,
} from '@mui/material';
import EnhancedMessage, { ChatMessage } from './EnhancedMessage';

/**
 * Demonstration component showing the merged chat bubbles with workflow progress
 */
const ChatBubbleDemo: React.FC = () => {
  const [demoMessages, setDemoMessages] = useState<ChatMessage[]>([]);
  const [demoStep, setDemoStep] = useState(0);

  // Demo messages showing the progression
  const demoSteps: ChatMessage[] = [
    {
      id: 'user-1',
      role: 'user',
      content: 'Explain how machine learning works',
      timestamp: new Date(),
    },
    {
      id: 'assistant-1',
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      metadata: {
        workflow: {
          stage: 'Thinking',
          status: 'thinking',
          isStreaming: true,
        },
      },
    },
    {
      id: 'assistant-1',
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      metadata: {
        workflow: {
          stage: 'Processing',
          status: 'processing',
          isStreaming: true,
          progress: 25,
        },
      },
    },
    {
      id: 'assistant-1',
      role: 'assistant',
      content: 'Machine learning is a subset of artificial intelligence...',
      timestamp: new Date(),
      metadata: {
        workflow: {
          stage: 'Streaming',
          status: 'streaming',
          isStreaming: true,
          progress: 75,
        },
      },
    },
    {
      id: 'assistant-1',
      role: 'assistant',
      content:
        'Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed for every task. It works by using algorithms to identify patterns in large datasets, then uses these patterns to make predictions or decisions about new, unseen data.',
      timestamp: new Date(),
      metadata: {
        model: 'gpt-4',
        tokens: 256,
        processingTime: 1200,
        workflow: {
          stage: 'Complete',
          status: 'complete',
          isStreaming: false,
          progress: 100,
        },
      },
    },
  ];

  const nextStep = () => {
    if (demoStep < demoSteps.length - 1) {
      const nextStepIndex = demoStep + 1;
      setDemoStep(nextStepIndex);

      // Update the messages array
      if (nextStepIndex === 1) {
        // Add user message and initial assistant placeholder
        setDemoMessages([demoSteps[0], demoSteps[1]]);
      } else {
        // Update the assistant message with new workflow state
        setDemoMessages([demoSteps[0], demoSteps[nextStepIndex]]);
      }
    }
  };

  const resetDemo = () => {
    setDemoStep(0);
    setDemoMessages([]);
  };

  const getCurrentStepDescription = () => {
    switch (demoStep) {
      case 0:
        return 'Ready to start demo';
      case 1:
        return 'User message sent, assistant shows "Thinking" state with spinner';
      case 2:
        return 'Assistant bubble shows "Processing" workflow stage';
      case 3:
        return 'Assistant bubble shows "Streaming" with partial content';
      case 4:
        return 'Assistant bubble shows "Complete" with full response and metadata';
      default:
        return '';
    }
  };

  return (
    <Card sx={{ maxWidth: 800, margin: 'auto', mt: 2 }}>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          Chat Bubble Demo: Merged Working State
        </Typography>

        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          This demo shows how the chat &quot;working&quot; indicator is now
          merged with the assistant response bubble, displaying workflow
          progress directly in the message.
        </Typography>

        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Current Step: {getCurrentStepDescription()}
          </Typography>

          <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
            <Button
              variant="contained"
              onClick={nextStep}
              disabled={demoStep >= demoSteps.length - 1}
            >
              Next Step ({demoStep + 1}/{demoSteps.length})
            </Button>
            <Button variant="outlined" onClick={resetDemo}>
              Reset Demo
            </Button>
          </Box>
        </Box>

        <Divider sx={{ mb: 2 }} />

        {/* Demo Messages */}
        <Box sx={{ minHeight: 200 }}>
          {demoMessages.map((message, index) => (
            <EnhancedMessage
              key={`${message.id}-${index}`}
              message={message}
              canEdit={false}
              canRegenerate={false}
              canDelete={false}
            />
          ))}

          {demoMessages.length === 0 && (
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                height: 150,
                color: 'text.secondary',
              }}
            >
              <Typography>
                Click &quot;Next Step&quot; to start the demo
              </Typography>
            </Box>
          )}
        </Box>

        <Divider sx={{ mt: 2, mb: 2 }} />

        <Box>
          <Typography variant="h6" gutterBottom>
            Key Improvements:
          </Typography>
          <Box component="ul" sx={{ pl: 2, mt: 1 }}>
            <Typography component="li" variant="body2">
              <strong>Space Efficient:</strong> No separate loading indicator
            </Typography>
            <Typography component="li" variant="body2">
              <strong>Progress Visibility:</strong> Workflow stage shown in
              assistant title
            </Typography>
            <Typography component="li" variant="body2">
              <strong>Real-time Updates:</strong> Progress updates appear in the
              message bubble
            </Typography>
            <Typography component="li" variant="body2">
              <strong>Consistent UI:</strong> Same bubble format for all
              assistant states
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default ChatBubbleDemo;
