import React, { useState, useEffect } from 'react';
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
  List,
  ListItem,
  ListItemText,
  Divider,
  TextField,
  InputAdornment,
} from '@mui/material';
import {
  Visibility as ViewIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
  Refresh as RefreshIcon,
  Message as MessageIcon,
  Person as PersonIcon,
  SmartToy as BotIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { api, Conversation, ConversationMessage } from '../services/api';

const ConversationsPage: React.FC = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null);
  const [conversationMessages, setConversationMessages] = useState<ConversationMessage[]>([]);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [loadingMessages, setLoadingMessages] = useState(false);

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await api.getConversations();
      setConversations(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load conversations');
    } finally {
      setLoading(false);
    }
  };

  const handleViewConversation = async (conversation: Conversation) => {
    setSelectedConversation(conversation);
    setViewDialogOpen(true);
    setLoadingMessages(true);
    
    try {
      const messages = await api.getConversationMessages(conversation.id);
      setConversationMessages(messages);
    } catch (err: any) {
      console.error('Failed to load messages:', err);
      setConversationMessages([]);
    } finally {
      setLoadingMessages(false);
    }
  };

  const handleDeleteConversation = async (conversationId: string) => {
    if (!window.confirm('Are you sure you want to delete this conversation?')) {
      return;
    }

    try {
      // Note: This endpoint might not exist in the current API
      // await api.deleteConversation(conversationId);
      setConversations(prev => prev.filter(c => c.id !== conversationId));
    } catch (err: any) {
      setError('Failed to delete conversation');
    }
  };

  const filteredConversations = conversations.filter(conversation =>
    conversation.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    conversation.id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const paginatedConversations = filteredConversations.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const getMessageIcon = (role: string) => {
    switch (role) {
      case 'user':
        return <PersonIcon fontSize="small" />;
      case 'assistant':
        return <BotIcon fontSize="small" />;
      default:
        return <MessageIcon fontSize="small" />;
    }
  };

  if (loading) {
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
          onClick={loadConversations}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
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
                <TableCell>Title</TableCell>
                <TableCell>ID</TableCell>
                <TableCell>Messages</TableCell>
                <TableCell>Tokens</TableCell>
                <TableCell>Created</TableCell>
                <TableCell>Updated</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {paginatedConversations.map((conversation) => (
                <TableRow key={conversation.id} hover>
                  <TableCell>
                    <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                      {conversation.title || 'Untitled Conversation'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                      {conversation.id}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={conversation.message_count}
                      color="primary"
                      variant="outlined"
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {conversation.total_tokens ? (
                      <Chip
                        label={conversation.total_tokens.toLocaleString()}
                        color="secondary"
                        variant="outlined"
                        size="small"
                      />
                    ) : (
                      '-'
                    )}
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {format(new Date(conversation.created_at), 'MMM dd, yyyy HH:mm')}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    {conversation.updated_at ? (
                      <Typography variant="body2">
                        {format(new Date(conversation.updated_at), 'MMM dd, yyyy HH:mm')}
                      </Typography>
                    ) : (
                      '-'
                    )}
                  </TableCell>
                  <TableCell align="center">
                    <IconButton
                      size="small"
                      onClick={() => handleViewConversation(conversation)}
                      color="primary"
                    >
                      <ViewIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDeleteConversation(conversation.id)}
                      color="error"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
              {paginatedConversations.length === 0 && (
                <TableRow>
                  <TableCell colSpan={7} align="center">
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
        <DialogContent dividers>
          {loadingMessages ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 3 }}>
              <CircularProgress />
            </Box>
          ) : (
            <List sx={{ maxHeight: 400, overflow: 'auto' }}>
              {conversationMessages.map((message, index) => (
                <React.Fragment key={message.id}>
                  <ListItem alignItems="flex-start">
                    <Box sx={{ display: 'flex', alignItems: 'flex-start', width: '100%' }}>
                      <Box sx={{ mr: 2, mt: 0.5 }}>
                        {getMessageIcon(message.role)}
                      </Box>
                      <Box sx={{ flexGrow: 1 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <Chip
                            label={message.role}
                            size="small"
                            color={message.role === 'user' ? 'primary' : 'secondary'}
                            sx={{ mr: 1 }}
                          />
                          <Typography variant="caption" color="text.secondary">
                            {format(new Date(message.created_at), 'MMM dd, yyyy HH:mm:ss')}
                          </Typography>
                          {message.tokens && (
                            <Chip
                              label={`${message.tokens} tokens`}
                              size="small"
                              variant="outlined"
                              sx={{ ml: 1 }}
                            />
                          )}
                        </Box>
                        <Typography
                          variant="body2"
                          sx={{
                            whiteSpace: 'pre-wrap',
                            bgcolor: message.role === 'user' ? 'primary.light' : 'grey.100',
                            p: 1.5,
                            borderRadius: 1,
                            color: message.role === 'user' ? 'primary.contrastText' : 'text.primary',
                          }}
                        >
                          {message.content}
                        </Typography>
                      </Box>
                    </Box>
                  </ListItem>
                  {index < conversationMessages.length - 1 && <Divider />}
                </React.Fragment>
              ))}
              {conversationMessages.length === 0 && (
                <ListItem>
                  <ListItemText
                    primary="No messages found"
                    secondary="This conversation appears to be empty"
                  />
                </ListItem>
              )}
            </List>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ConversationsPage;