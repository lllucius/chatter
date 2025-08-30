import React, { useState, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Chip,
  Avatar,
  Rating,
  Tooltip,
} from '@mui/material';
import {
  Person as PersonIcon,
  SmartToy as BotIcon,
  MoreVert as MoreVertIcon,
  Edit as EditIcon,
  Refresh as RefreshIcon,
  ContentCopy as CopyIcon,
  ThumbUp as ThumbUpIcon,
  ThumbDown as ThumbDownIcon,
  Share as ShareIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  edited?: boolean;
  editedAt?: Date;
  rating?: number;
  metadata?: {
    model?: string;
    tokens?: number;
    processingTime?: number;
  };
}

interface EnhancedMessageProps {
  message: ChatMessage;
  onEdit?: (messageId: string, newContent: string) => void;
  onRegenerate?: (messageId: string) => void;
  onDelete?: (messageId: string) => void;
  onRate?: (messageId: string, rating: number) => void;
  canEdit?: boolean;
  canRegenerate?: boolean;
  canDelete?: boolean;
}

const EnhancedMessage: React.FC<EnhancedMessageProps> = ({
  message,
  onEdit,
  onRegenerate,
  onDelete,
  onRate,
  canEdit = true,
  canRegenerate = true,
  canDelete = true,
}) => {
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editContent, setEditContent] = useState(message.content);
  const [rating, setRating] = useState(message.rating || 0);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleEditClick = () => {
    setEditContent(message.content);
    setEditDialogOpen(true);
    handleMenuClose();
  };

  const handleEditSave = () => {
    if (onEdit && editContent.trim() !== message.content) {
      onEdit(message.id, editContent.trim());
    }
    setEditDialogOpen(false);
  };

  const handleEditCancel = () => {
    setEditContent(message.content);
    setEditDialogOpen(false);
  };

  const handleRegenerate = () => {
    if (onRegenerate) {
      onRegenerate(message.id);
    }
    handleMenuClose();
  };

  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(message.content);
    } catch (err) {
      console.error('Failed to copy message:', err);
    }
    handleMenuClose();
  }, [message.content]);

  const handleDelete = () => {
    if (onDelete && window.confirm('Are you sure you want to delete this message?')) {
      onDelete(message.id);
    }
    handleMenuClose();
  };

  const handleRatingChange = (newRating: number | null) => {
    const ratingValue = newRating || 0;
    setRating(ratingValue);
    if (onRate) {
      onRate(message.id, ratingValue);
    }
  };

  const getAvatarIcon = () => {
    switch (message.role) {
      case 'user':
        return <PersonIcon />;
      case 'assistant':
        return <BotIcon />;
      case 'system':
        return <BotIcon color="secondary" />;
      default:
        return <BotIcon />;
    }
  };

  const getAvatarColor = () => {
    switch (message.role) {
      case 'user':
        return 'primary.main';
      case 'assistant':
        return 'success.main';
      case 'system':
        return 'info.main';
      default:
        return 'grey.500';
    }
  };

  const getRoleLabel = () => {
    switch (message.role) {
      case 'user':
        return 'You';
      case 'assistant':
        return 'Assistant';
      case 'system':
        return 'System';
      default:
        return message.role;
    }
  };

  return (
    <>
      <Card
        sx={{
          mb: 2,
          bgcolor: message.role === 'user' ? 'grey.50' : 'background.paper',
          border: message.role === 'user' ? '1px solid' : 'none',
          borderColor: 'grey.200',
        }}
      >
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
            <Avatar sx={{ bgcolor: getAvatarColor(), width: 40, height: 40 }}>
              {getAvatarIcon()}
            </Avatar>
            
            <Box sx={{ flex: 1, minWidth: 0 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="subtitle2" fontWeight="bold">
                    {getRoleLabel()}
                  </Typography>
                  {message.edited && (
                    <Chip label="Edited" size="small" variant="outlined" />
                  )}
                  {message.metadata?.model && (
                    <Chip label={message.metadata.model} size="small" variant="outlined" />
                  )}
                </Box>
                
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    {format(message.timestamp, 'HH:mm')}
                  </Typography>
                  <IconButton size="small" onClick={handleMenuOpen}>
                    <MoreVertIcon fontSize="small" />
                  </IconButton>
                </Box>
              </Box>
              
              <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', mb: 1 }}>
                {message.content}
              </Typography>
              
              {message.metadata && (
                <Box sx={{ display: 'flex', gap: 2, mb: 1 }}>
                  {message.metadata.tokens && (
                    <Typography variant="caption" color="text.secondary">
                      {message.metadata.tokens} tokens
                    </Typography>
                  )}
                  {message.metadata.processingTime && (
                    <Typography variant="caption" color="text.secondary">
                      {message.metadata.processingTime}ms
                    </Typography>
                  )}
                </Box>
              )}
              
              {message.role === 'assistant' && onRate && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    Rate this response:
                  </Typography>
                  <Rating
                    value={rating}
                    onChange={(_, newValue) => handleRatingChange(newValue)}
                    size="small"
                  />
                </Box>
              )}
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Context Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleCopy}>
          <ListItemIcon>
            <CopyIcon fontSize="small" />
          </ListItemIcon>
          Copy
        </MenuItem>
        
        {canEdit && message.role === 'user' && (
          <MenuItem onClick={handleEditClick}>
            <ListItemIcon>
              <EditIcon fontSize="small" />
            </ListItemIcon>
            Edit
          </MenuItem>
        )}
        
        {canRegenerate && message.role === 'assistant' && (
          <MenuItem onClick={handleRegenerate}>
            <ListItemIcon>
              <RefreshIcon fontSize="small" />
            </ListItemIcon>
            Regenerate
          </MenuItem>
        )}
        
        {canDelete && (
          <MenuItem onClick={handleDelete}>
            <ListItemIcon>
              <DeleteIcon fontSize="small" />
            </ListItemIcon>
            Delete
          </MenuItem>
        )}
      </Menu>

      {/* Edit Dialog */}
      <Dialog open={editDialogOpen} onClose={handleEditCancel} maxWidth="md" fullWidth>
        <DialogTitle>Edit Message</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            multiline
            rows={4}
            value={editContent}
            onChange={(e) => setEditContent(e.target.value)}
            placeholder="Edit your message..."
            sx={{ mt: 1 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleEditCancel}>Cancel</Button>
          <Button
            onClick={handleEditSave}
            variant="contained"
            disabled={!editContent.trim() || editContent.trim() === message.content}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default EnhancedMessage;