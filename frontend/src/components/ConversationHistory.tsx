import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  IconButton,
  Typography,
  TextField,
  InputAdornment,
  Chip,
  Avatar,
  Menu,
  MenuItem,
  Alert,
  CircularProgress,
} from '@mui/material';
import CustomScrollbar from './CustomScrollbar';
import {
  History as HistoryIcon,
  Message as MessageIcon,
  Search as SearchIcon,
  Delete as DeleteIcon,
  Download as DownloadIcon,
  MoreVert as MoreVertIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { getSDK } from "../services/auth-service";
import { ConversationResponse } from 'chatter-sdk';

interface ConversationHistoryProps {
  open: boolean;
  onClose: () => void;
  onSelectConversation: (conversation: ConversationResponse) => void;
  currentConversationId?: string;
}

const ConversationHistory: React.FC<ConversationHistoryProps> = ({
  open,
  onClose,
  onSelectConversation,
  currentConversationId,
}) => {
  const [conversations, setConversations] = useState<ConversationResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [actionAnchorEl, setActionAnchorEl] = useState<HTMLElement | null>(null);
  const [actionConversation, setActionConversation] = useState<ConversationResponse | null>(null);

  const loadConversations = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      const response = await getSDK().chat.listConversationsApiV1ChatConversations({
        limit: 20
      });
      setConversations(response.conversations || []);
    } catch {
      setError('Failed to load conversation history');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (open) {
      loadConversations();
    }
  }, [open, loadConversations]);

  const handleSelectConversation = (conversation: ConversationResponse) => {
    onSelectConversation(conversation);
    onClose();
  };

  const handleActionClick = (event: React.MouseEvent<HTMLElement>, conversation: ConversationResponse) => {
    event.stopPropagation();
    setActionAnchorEl(event.currentTarget);
    setActionConversation(conversation);
  };

  const handleActionClose = () => {
    setActionAnchorEl(null);
    setActionConversation(null);
  };

  const handleDeleteConversation = async () => {
    if (!actionConversation) return;
    
    try {
      await getSDK().chat.deleteConversationApiV1ChatConversationsConversationId(
        actionConversation.id
      );
      setConversations(prev => prev.filter(c => c.id !== actionConversation.id));
      handleActionClose();
    } catch {
      setError('Failed to delete conversation');
    }
  };

  const handleExportConversation = async () => {
    if (!actionConversation) return;
    
    try {
      // This would be implemented with a proper export API
      const blob = new Blob([JSON.stringify(actionConversation, null, 2)], {
        type: 'application/json',
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `conversation-${actionConversation.id}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      handleActionClose();
    } catch {
      setError('Failed to export conversation');
    }
  };

  const filteredConversations = conversations.filter(conversation =>
    (conversation.title?.toLowerCase().includes(searchTerm.toLowerCase()) || 
     conversation.id.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <>
      <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <HistoryIcon />
            Conversation History
            <IconButton size="small" onClick={loadConversations} disabled={loading}>
              <RefreshIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        
        <DialogContent>
          <Box sx={{ mb: 2 }}>
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
            />
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
              <CircularProgress />
            </Box>
          ) : (
            <Box sx={{ maxHeight: 400 }}>
              <CustomScrollbar>
                <List>
                  {filteredConversations.length === 0 ? (
                    <ListItem>
                      <ListItemText
                        primary="No conversations found"
                        secondary={searchTerm ? "Try adjusting your search terms" : "Start a new conversation to see it here"}
                      />
                    </ListItem>
                  ) : (
                    filteredConversations.map((conversation): void => (
                  <ListItem
                    key={conversation.id}
                    component="div"
                    onClick={() => handleSelectConversation(conversation)}
                    sx={{
                      borderRadius: 1,
                      mb: 1,
                      border: conversation.id === currentConversationId ? '2px solid' : '1px solid',
                      borderColor: conversation.id === currentConversationId ? 'primary.main' : 'divider',
                      cursor: 'pointer',
                      '&:hover': {
                        backgroundColor: 'action.hover'
                      }
                    }}
                  >
                    <ListItemIcon>
                      <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main' }}>
                        <MessageIcon fontSize="small" />
                      </Avatar>
                    </ListItemIcon>
                    
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="subtitle2" noWrap>
                            {conversation.title || `Conversation ${conversation.id.slice(0, 8)}`}
                          </Typography>
                          {conversation.id === currentConversationId && (
                            <Chip label="Current" size="small" color="primary" />
                          )}
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="caption" color="text.secondary">
                            {conversation.created_at
                              ? format(new Date(conversation.created_at), 'MMM dd, yyyy HH:mm')
                              : 'Unknown date'}
                          </Typography>
                          <br />
                          <Typography variant="caption" color="text.secondary" noWrap>
                            ID: {conversation.id}
                          </Typography>
                        </Box>
                      }
                    />
                    
                    <ListItemSecondaryAction>
                      <IconButton
                        edge="end"
                        onClick={(e) => handleActionClick(e, conversation)}
                        size="small"
                      >
                        <MoreVertIcon />
                      </IconButton>
                    </ListItemSecondaryAction>
                  </ListItem>
                ))
              )}
                </List>
              </CustomScrollbar>
            </Box>
          )}
        </DialogContent>
        
        <DialogActions>
          <Button onClick={onClose}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Action Menu */}
      <Menu
        anchorEl={actionAnchorEl}
        open={Boolean(actionAnchorEl)}
        onClose={handleActionClose}
      >
        <MenuItem onClick={handleExportConversation}>
          <ListItemIcon>
            <DownloadIcon fontSize="small" />
          </ListItemIcon>
          Export
        </MenuItem>
        <MenuItem onClick={handleDeleteConversation}>
          <ListItemIcon>
            <DeleteIcon fontSize="small" />
          </ListItemIcon>
          Delete
        </MenuItem>
      </Menu>
    </>
  );
};

export default ConversationHistory;