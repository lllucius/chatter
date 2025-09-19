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
  CircularProgress,
} from '@mui/material';
import {
  Person as PersonIcon,
  SmartToy as BotIcon,
  MoreVert as MoreVertIcon,
  Edit as EditIcon,
  Refresh as RefreshIcon,
  ContentCopy as CopyIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { format, isValid } from 'date-fns';

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
    workflow?: {
      stage?: string;
      progress?: number;
      isStreaming?: boolean;
      status?: 'thinking' | 'processing' | 'streaming' | 'complete';
      currentStep?: number;
      totalSteps?: number;
      stepDescriptions?: string[];
    };
  };
}

interface EnhancedMessageProps {
  message: ChatMessage;
  onEdit?: (messageId: string, newContent: string) => void;
  onRegenerate?: (messageId: string) => void;
  onDelete?: (messageId: string) => void;
  onRate?: (messageId: string, rating: number) => Promise<void> | void;
  canEdit?: boolean;
  canRegenerate?: boolean;
  canDelete?: boolean;
}

// Helper function to safely format timestamps
const formatTimestamp = (timestamp: Date, formatString: string): string => {
  if (!timestamp || !isValid(timestamp)) {
    return '--:--';
  }
  return format(timestamp, formatString);
};

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
  const [ratingLoading, setRatingLoading] = useState(false);

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
    } catch {
      // Copy failed - user will notice no text was copied
    }
    handleMenuClose();
  }, [message.content]);

  const handleDelete = () => {
    if (
      onDelete &&
      window.confirm('Are you sure you want to delete this message?')
    ) {
      onDelete(message.id);
    }
    handleMenuClose();
  };

  const handleRatingChange = async (newRating: number | null) => {
    const ratingValue = newRating || 0;
    setRatingLoading(true);
    setRating(ratingValue);

    try {
      if (onRate) {
        await onRate(message.id, ratingValue);
      }
    } finally {
      setRatingLoading(false);
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
          mb: 1,
          bgcolor:
            message.role === 'user'
              ? 'primary.50'
              : message.role === 'assistant'
                ? (theme) =>
                    theme.palette.mode === 'dark' ? 'grey.800' : 'grey.100'
                : 'background.paper',
          border: '1px solid',
          borderColor:
            message.role === 'user'
              ? 'primary.200'
              : message.role === 'assistant'
                ? (theme) =>
                    theme.palette.mode === 'dark' ? 'grey.600' : 'grey.300'
                : 'grey.200',
        }}
      >
        <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
          <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1.5 }}>
            <Avatar sx={{ bgcolor: getAvatarColor(), width: 36, height: 36 }}>
              {getAvatarIcon()}
            </Avatar>

            <Box sx={{ flex: 1, minWidth: 0 }}>
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  mb: 0.5,
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="subtitle2" fontWeight="bold">
                    {getRoleLabel()}
                  </Typography>
                  {/* Workflow progress indicator for assistant messages */}
                  {message.role === 'assistant' &&
                    message.metadata?.workflow && (
                      <Box
                        sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
                      >
                        {message.metadata.workflow.isStreaming && (
                          <CircularProgress size={16} sx={{ mr: 0.5 }} />
                        )}
                        {message.metadata.workflow.stage && (
                          <Chip
                            label={message.metadata.workflow.stage}
                            size="small"
                            variant="outlined"
                            color={
                              message.metadata.workflow.status === 'complete'
                                ? 'success'
                                : message.metadata.workflow.status ===
                                    'streaming'
                                  ? 'primary'
                                  : 'default'
                            }
                          />
                        )}
                      </Box>
                    )}
                  {message.edited && (
                    <Chip label="Edited" size="small" variant="outlined" />
                  )}
                  {message.metadata?.model && (
                    <Chip
                      label={message.metadata.model}
                      size="small"
                      variant="outlined"
                    />
                  )}
                </Box>

                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    {formatTimestamp(message.timestamp, 'HH:mm')}
                  </Typography>
                  <IconButton size="small" onClick={handleMenuOpen}>
                    <MoreVertIcon fontSize="small" />
                  </IconButton>
                </Box>
              </Box>

              <Typography
                variant="body1"
                sx={{ whiteSpace: 'pre-wrap', mb: 0.5 }}
              >
                {message.content}
              </Typography>

              {message.role === 'assistant' && onRate && (
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <Typography variant="caption" color="text.secondary">
                      Rate this response:
                    </Typography>
                    <Rating
                      value={rating}
                      onChange={(_, newValue) => handleRatingChange(newValue)}
                      size="small"
                      disabled={ratingLoading}
                    />
                    {ratingLoading && <CircularProgress size={16} />}
                  </Box>
                  {message.metadata &&
                    (message.metadata.tokens ||
                      message.metadata.processingTime) && (
                      <Box
                        sx={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: 1,
                          ml: 'auto', // Right align the stats
                        }}
                      >
                        {message.metadata.tokens && (
                          <Typography variant="caption" color="text.secondary">
                            {message.metadata.tokens} tokens
                          </Typography>
                        )}
                        {message.metadata.processingTime && (
                          <Typography variant="caption" color="text.secondary">
                            {(message.metadata.processingTime / 1000).toFixed(
                              2
                            )}
                            s
                          </Typography>
                        )}
                        {message.metadata.tokens &&
                          message.metadata.processingTime && (
                            <Typography
                              variant="caption"
                              color="text.secondary"
                            >
                              {Math.round(
                                (message.metadata.tokens /
                                  message.metadata.processingTime) *
                                  1000
                              )}{' '}
                              tok/s
                            </Typography>
                          )}
                      </Box>
                    )}
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
      <Dialog
        open={editDialogOpen}
        onClose={handleEditCancel}
        maxWidth="md"
        fullWidth
      >
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
            disabled={
              !editContent.trim() || editContent.trim() === message.content
            }
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default EnhancedMessage;
