import React, { useState, useCallback, useRef, memo } from 'react';
import {
  Box,
  Typography,
  Button,
  IconButton,
  Chip,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Avatar,
  Paper,
} from '@mui/material';
import {
  Visibility as ViewIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  Message as MessageIcon,
  Person as PersonIcon,
  SmartToy as BotIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { getSDK } from "../services/auth-service";
import { ConversationResponse, MessageResponse } from 'chatter-sdk';
import CustomScrollbar from '../components/CustomScrollbar';
import PageLayout from '../components/PageLayout';
import CrudDataTable, { CrudConfig, CrudService, CrudColumn, CrudDataTableRef } from '../components/CrudDataTable';
import { createDateRenderer } from '../components/CrudRenderers';



const ConversationsPage: React.FC = () => {
  const crudTableRef = useRef<CrudDataTableRef>(null);
  
  // View conversation dialog state
  const [selectedConversation, setSelectedConversation] = useState<ConversationResponse | null>(null);
  const [conversationMessages, setConversationMessages] = useState<MessageResponse[]>([]);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [loadingMessages, setLoadingMessages] = useState(false);

  // Handle view conversation action
  const handleViewConversation = useCallback(async (conversation: ConversationResponse) => {
    setSelectedConversation(conversation);
    setViewDialogOpen(true);
    setLoadingMessages(true);

    try {
      const response =
        await getSDK().chat.getConversationApiV1ChatConversationsConversationId(
          conversation.id,
          { includeMessages: true }
        );
      const messages = response.messages || [];
      setConversationMessages(messages);
    } catch (err: unknown) {
      setConversationMessages([]);
    } finally {
      setLoadingMessages(false);
    }
  }, []);

  // Conversation title renderer
  const renderConversationTitle = (title: string | null, conversation: ConversationResponse): void => (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main' }}>
        <MessageIcon fontSize="small" />
      </Avatar>
      <Box>
        <Typography variant="body2" fontWeight="medium">
          {title || `Conversation ${conversation.id.slice(0, 8)}`}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {conversation.id}
        </Typography>
      </Box>
    </Box>
  );

  // Status renderer - for now all are active
  const renderStatus = (): void => (
    <Chip
      label="Active"
      size="small"
      color="success"
      variant="outlined"
    />
  );

  // Message count renderer
  const renderMessageCount = (count: number): void => (
    <Typography variant="body2">
      {count} {count === 1 ? 'message' : 'messages'}
    </Typography>
  );

  // Define columns
  const columns: CrudColumn<ConversationResponse>[] = [
    {
      id: 'title',
      label: 'Conversation',
      width: '300px',
      render: renderConversationTitle,
    },
    {
      id: 'status',
      label: 'Status',
      width: '120px',
      render: renderStatus,
    },
    {
      id: 'message_count',
      label: 'Messages',
      width: '100px',
      render: renderMessageCount,
    },
    {
      id: 'created_at',
      label: 'Created',
      width: '140px',
      render: createDateRenderer<ConversationResponse>('MMM dd, yyyy HH:mm'),
    },
    {
      id: 'updated_at',
      label: 'Updated',
      width: '140px',
      render: createDateRenderer<ConversationResponse>('MMM dd, yyyy HH:mm'),
    },
  ];

  // Define CRUD configuration
  const config: CrudConfig<ConversationResponse> = {
    entityName: 'Conversation',
    entityNamePlural: 'Conversations',
    columns,
    actions: [
      {
        icon: <ViewIcon />,
        label: 'View Messages',
        onClick: handleViewConversation,
      },
    ],
    enableCreate: false, // Conversations are created from chat interface
    enableEdit: false,   // Conversations don't have direct edit functionality
    enableDelete: true,
    enableRefresh: true,
    pageSize: 10,
  };

  // Define service methods
  const service: CrudService<ConversationResponse, never, never> = {
    list: async (page: number, pageSize: number) => {
      const response = await getSDK().chat.listConversationsApiV1ChatConversations({
        limit: pageSize,
        offset: page * pageSize,
      });
      return {
        items: response.conversations || [],
        total: response.total || 0,
      };
    },

    delete: async (id: string) => {
      await getSDK().chat.deleteConversationApiV1ChatConversationsConversationId(id);
    },
  };

  const getItemId = (item: ConversationResponse) => item.id;

  const getMessageIcon = useCallback((role: string) => {
    switch (role) {
      case 'user':
        return <PersonIcon fontSize="small" />;
      case 'assistant':
        return <BotIcon fontSize="small" />;
      default:
        return <MessageIcon fontSize="small" />;
    }
  }, []);

  const getMessageColor = useCallback((role: string) => {
    switch (role) {
      case 'user':
        return 'primary.main';
      case 'assistant':
        return 'secondary.main';
      case 'system':
        return 'info.main';
      default:
        return 'grey.500';
    }
  }, []);

  const toolbar = (
    <Button
      variant="outlined"
      startIcon={<RefreshIcon />}
      onClick={() => crudTableRef.current?.handleRefresh()}
    >
      Refresh
    </Button>
  );

  return (
    <PageLayout title="Conversation Management" toolbar={toolbar}>
      <CrudDataTable
        ref={crudTableRef}
        config={config}
        service={service}
        getItemId={getItemId}
      />

      {/* View Conversation Dialog */}
      <Dialog
        open={viewDialogOpen}
        onClose={() => setViewDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Typography variant="h6">
            {selectedConversation?.title || 'Conversation Details'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            ID: {selectedConversation?.id}
          </Typography>
        </DialogTitle>
        <DialogContent sx={{ p: 0 }}>
          {loadingMessages ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 3 }}>
              <CircularProgress />
            </Box>
          ) : (
            <Box sx={{ maxHeight: 400, p: 2 }}>
              <CustomScrollbar>
                <Box sx={{ display: 'flex', flexDirection: 'column' }}>
                  {conversationMessages.map((message): void => (
                    <Box
                      key={message.id}
                      sx={{
                        display: 'flex',
                        mb: 2,
                        alignItems: 'flex-start',
                        ...(message.role === 'user' && {
                          flexDirection: 'row-reverse',
                        }),
                      }}
                    >
                      <Avatar
                        sx={{
                          bgcolor: getMessageColor(message.role),
                          ...(message.role === 'user' ? { ml: 1 } : { mr: 1 }),
                        }}
                      >
                        {getMessageIcon(message.role)}
                      </Avatar>
                      <Paper
                        sx={{
                          p: 2,
                          maxWidth: '70%',
                          bgcolor: message.role === 'user'
                            ? 'primary.light'
                            : (theme) => theme.palette.mode === 'dark' ? 'grey.800' : 'grey.100',
                          color: message.role === 'user'
                            ? 'primary.contrastText'
                            : 'text.primary',
                        }}
                      >
                        <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                          {message.content}
                        </Typography>
                        <Typography
                          variant="caption"
                          sx={{
                            display: 'block',
                            mt: 1,
                            opacity: 0.7,
                          }}
                        >
                          {format(new Date(message.created_at), 'HH:mm:ss')}
                        </Typography>
                        {message.total_tokens && (
                          <Chip
                            label={`${message.total_tokens} tokens`}
                            size="small"
                            variant="outlined"
                            sx={{ mt: 1 }}
                          />
                        )}
                      </Paper>
                    </Box>
                  ))}
                  {conversationMessages.length === 0 && (
                    <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 3 }}>
                      No messages in this conversation
                    </Typography>
                  )}
                </Box>
              </CustomScrollbar>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </PageLayout>
  );
};

export default memo(ConversationsPage);
