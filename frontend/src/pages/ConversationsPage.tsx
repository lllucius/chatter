import React, { useState, useCallback, useMemo, memo } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  IconButton,
  Chip,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  InputAdornment,
  Avatar,
  Paper,
  Menu,
  MenuItem,
  ListItemIcon,
} from '@mui/material';
import {
  Visibility as ViewIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
  Refresh as RefreshIcon,
  Message as MessageIcon,
  Person as PersonIcon,
  SmartToy as BotIcon,
  MoreVert as MoreVertIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { chatterSDK } from '../services/chatter-sdk';
import { ConversationResponse, MessageResponse } from '../sdk';
import { useApi } from '../hooks/useApi';

// Memoized conversation table row component
const ConversationTableRow = memo(({ 
  conversation, 
  onView, 
  onDelete, 
  onActionClick 
}: {
  conversation: ConversationResponse;
  onView: (conversation: ConversationResponse) => void;
  onDelete: (conversationId: string) => void;
  onActionClick: (event: React.MouseEvent<HTMLElement>, conversation: ConversationResponse) => void;
}) => (
  <TableRow hover>
    <TableCell>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main' }}>
          <MessageIcon fontSize="small" />
        </Avatar>
        <Box>
          <Typography variant="body2" fontWeight="medium">
            {conversation.title || `Conversation ${conversation.id.slice(0, 8)}`}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {conversation.id}
          </Typography>
        </Box>
      </Box>
    </TableCell>
    <TableCell>
      <Chip
        label="Active"
        size="small"
        color="success"
        variant="outlined"
      />
    </TableCell>
    <TableCell>
      <Typography variant="body2">
        {conversation.created_at ? format(new Date(conversation.created_at), 'MMM dd, yyyy HH:mm') : 'Unknown'}
      </Typography>
    </TableCell>
    <TableCell>
      <Typography variant="body2">
        {conversation.updated_at ? format(new Date(conversation.updated_at), 'MMM dd, yyyy HH:mm') : 'Unknown'}
      </Typography>
    </TableCell>
    <TableCell align="right">
      <IconButton
        size="small"
        onClick={() => onView(conversation)}
        aria-label="View conversation"
      >
        <ViewIcon />
      </IconButton>
      <IconButton
        size="small"
        onClick={(event) => onActionClick(event, conversation)}
        aria-label="More actions"
      >
        <MoreVertIcon />
      </IconButton>
    </TableCell>
  </TableRow>
));

ConversationTableRow.displayName = 'ConversationTableRow';

const ConversationsPage: React.FC = () => {
  // Use custom API hook for conversations
  const conversationsApi = useApi(
    () => chatterSDK.conversations.listConversationsApiV1ChatConversationsGet({}),
    { immediate: true }
  );

  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedConversation, setSelectedConversation] = useState<ConversationResponse | null>(null);
  const [conversationMessages, setConversationMessages] = useState<MessageResponse[]>([]);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [loadingMessages, setLoadingMessages] = useState(false);

  // Actions menu state
  const [actionAnchorEl, setActionAnchorEl] = useState<HTMLElement | null>(null);
  const [actionConversation, setActionConversation] = useState<ConversationResponse | null>(null);

  const conversations = conversationsApi.data?.data?.conversations || [];

  const handleViewConversation = useCallback(async (conversation: ConversationResponse) => {
    setSelectedConversation(conversation);
    setViewDialogOpen(true);
    setLoadingMessages(true);

    try {
      const response =
        await chatterSDK.conversations.getConversationMessagesApiV1ChatConversationsConversationIdMessagesGet(
          { conversationId: conversation.id }
        );
      const messages = response.data;
      setConversationMessages(messages);
    } catch (err: any) {
      console.error('Failed to load messages:', err);
      setConversationMessages([]);
    } finally {
      setLoadingMessages(false);
    }
  }, []);

  const handleDeleteConversation = useCallback(async (conversationId: string) => {
    if (!window.confirm('Are you sure you want to delete this conversation?')) {
      return;
    }

    try {
      // Note: This endpoint might not exist in the current API
      // await api.deleteConversation(conversationId);
      // For now, just remove from local state
      conversationsApi.reset();
      conversationsApi.execute();
    } catch (err: any) {
      console.error('Failed to delete conversation:', err);
    }
  }, [conversationsApi]);

  const handleActionClick = useCallback((event: React.MouseEvent<HTMLElement>, conversation: ConversationResponse) => {
    setActionAnchorEl(event.currentTarget);
    setActionConversation(conversation);
  }, []);

  const handleActionClose = useCallback(() => {
    setActionAnchorEl(null);
    setActionConversation(null);
  }, []);

  // Memoized filtered and paginated conversations
  const filteredConversations = useMemo(() => 
    conversations.filter(conversation =>
      conversation.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      conversation.id.toLowerCase().includes(searchTerm.toLowerCase())
    ), [conversations, searchTerm]
  );

  const paginatedConversations = useMemo(() => 
    filteredConversations.slice(
      page * rowsPerPage,
      page * rowsPerPage + rowsPerPage
    ), [filteredConversations, page, rowsPerPage]
  );

  const handleChangePage = useCallback((_event: unknown, newPage: number) => {
    setPage(newPage);
  }, []);

  const handleChangeRowsPerPage = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  }, []);

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

  if (conversationsApi.loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold' }}>
          Conversation Management
        </Typography>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={conversationsApi.execute}
          disabled={conversationsApi.loading}
        >
          Refresh
        </Button>
      </Box>

      {conversationsApi.error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {conversationsApi.error}
        </Alert>
      )}

      {/* Search and Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <TextField
            fullWidth
            placeholder="Search conversations..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
            size="small"
          />
        </CardContent>
      </Card>

      {/* Conversations Table */}
      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Conversation</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Created</TableCell>
                <TableCell>Updated</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {paginatedConversations.map((conversation) => (
                <ConversationTableRow
                  key={conversation.id}
                  conversation={conversation}
                  onView={handleViewConversation}
                  onDelete={handleDeleteConversation}
                  onActionClick={handleActionClick}
                />
              ))}
              {paginatedConversations.length === 0 && (
                <TableRow>
                  <TableCell colSpan={5} align="center">
                    <Typography variant="body2" color="text.secondary" sx={{ py: 3 }}>
                      No conversations found
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25, 50]}
          component="div"
          count={filteredConversations.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Card>

      {/* Actions Menu */}
      <Menu
        anchorEl={actionAnchorEl}
        open={Boolean(actionAnchorEl)}
        onClose={handleActionClose}
      >
        <MenuItem
          onClick={() => {
            if (actionConversation) handleViewConversation(actionConversation);
            handleActionClose();
          }}
        >
          <ListItemIcon>
            <ViewIcon fontSize="small" />
          </ListItemIcon>
          View
        </MenuItem>
        <MenuItem
          onClick={() => {
            if (actionConversation) handleDeleteConversation(actionConversation.id);
            handleActionClose();
          }}
        >
          <ListItemIcon>
            <DeleteIcon fontSize="small" />
          </ListItemIcon>
          Delete
        </MenuItem>
      </Menu>

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
            <Box sx={{
              maxHeight: 400,
              overflow: 'auto',
              p: 2,
              display: 'flex',
              flexDirection: 'column',
            }}>
              {conversationMessages.map((message) => (
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
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default memo(ConversationsPage);
