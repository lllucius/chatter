import React, { createContext, useContext, useState, useCallback } from 'react';
import {
  Snackbar,
  Alert,
  AlertTitle,
  IconButton,
  Badge,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Typography,
  Box,
  Divider,
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  Close as CloseIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  AccountTree as WorkflowIcon,
  SmartToy as AgentIcon,
  Analytics as TestIcon,
  Speed as PerformanceIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  category: 'workflow' | 'agent' | 'test' | 'system' | 'performance';
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
  persistent?: boolean;
  actions?: {
    label: string;
    action: () => void;
  }[];
}

interface NotificationContextType {
  notifications: Notification[];
  showNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  clearNotification: (id: string) => void;
  clearAll: () => void;
  unreadCount: number;
}

const NotificationContext = createContext<NotificationContextType>({
  notifications: [],
  showNotification: () => {
    // Default implementation - will be overridden by provider
  },
  markAsRead: () => {
    // Default implementation - will be overridden by provider
  },
  markAllAsRead: () => {
    // Default implementation - will be overridden by provider
  },
  clearNotification: () => {
    // Default implementation - will be overridden by provider
  },
  clearAll: () => {
    // Default implementation - will be overridden by provider
  },
  unreadCount: 0,
});

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
};

interface NotificationProviderProps {
  children: React.ReactNode;
}

// Helper functions for icons
const getIcon = (type: Notification['type']) => {
  switch (type) {
    case 'success': return <SuccessIcon />;
    case 'error': return <ErrorIcon />;
    case 'warning': return <WarningIcon />;
    case 'info': return <InfoIcon />;
    default: return <InfoIcon />;
  }
};

const getCategoryIcon = (category: Notification['category']) => {
  switch (category) {
    case 'workflow': return <WorkflowIcon fontSize="small" />;
    case 'agent': return <AgentIcon fontSize="small" />;
    case 'test': return <TestIcon fontSize="small" />;
    case 'performance': return <PerformanceIcon fontSize="small" />;
    default: return <InfoIcon fontSize="small" />;
  }
};

export const NotificationProvider: React.FC<NotificationProviderProps> = ({ children }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [currentSnackbar, setCurrentSnackbar] = useState<Notification | null>(null);

  const showNotification = useCallback((notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => {
    const newNotification: Notification = {
      ...notification,
      id: Math.random().toString(36).substring(7),
      timestamp: new Date(),
      read: false,
    };

    setNotifications(prev => [newNotification, ...prev]);

    // Show snackbar for non-persistent notifications
    if (!notification.persistent) {
      setCurrentSnackbar(newNotification);
    }
  }, []);

  const markAsRead = useCallback((id: string) => {
    setNotifications(prev =>
      prev.map(notification =>
        notification.id === id ? { ...notification, read: true } : notification
      )
    );
  }, []);

  const markAllAsRead = useCallback(() => {
    setNotifications(prev =>
      prev.map(notification => ({ ...notification, read: true }))
    );
  }, []);

  const clearNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  }, []);

  const clearAll = useCallback(() => {
    setNotifications([]);
  }, []);

  const unreadCount = notifications.filter(n => !n.read).length;

  const handleCloseSnackbar = () => {
    setCurrentSnackbar(null);
  };

  return (
    <NotificationContext.Provider
      value={{
        notifications,
        showNotification,
        markAsRead,
        markAllAsRead,
        clearNotification,
        clearAll,
        unreadCount,
      }}
    >
      {children}
      
      {/* Snackbar for real-time notifications */}
      <Snackbar
        open={!!currentSnackbar}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        {currentSnackbar && (
          <Alert
            onClose={handleCloseSnackbar}
            severity={currentSnackbar.type}
            variant="filled"
            action={
              <IconButton
                size="small"
                aria-label="close"
                color="inherit"
                onClick={handleCloseSnackbar}
              >
                <CloseIcon fontSize="small" />
              </IconButton>
            }
          >
            <AlertTitle>{currentSnackbar.title}</AlertTitle>
            {currentSnackbar.message}
          </Alert>
        )}
      </Snackbar>
    </NotificationContext.Provider>
  );
};

interface NotificationMenuProps {
  anchorEl: HTMLElement | null;
  open: boolean;
  onClose: () => void;
}

export const NotificationMenu: React.FC<NotificationMenuProps> = ({
  anchorEl,
  open,
  onClose,
}) => {
  const { notifications, markAsRead, clearNotification, markAllAsRead, clearAll } = useNotifications();

  const handleNotificationClick = (notification: Notification) => {
    if (!notification.read) {
      markAsRead(notification.id);
    }
    
    // Execute any actions
    if (notification.actions && notification.actions.length > 0) {
      notification.actions[0].action();
    }
  };

  return (
    <Menu
      anchorEl={anchorEl}
      open={open}
      onClose={onClose}
      PaperProps={{
        sx: {
          width: 400,
          maxHeight: 600,
        },
      }}
      anchorOrigin={{
        vertical: 'bottom',
        horizontal: 'right',
      }}
      transformOrigin={{
        vertical: 'top',
        horizontal: 'right',
      }}
    >
      <Box sx={{ p: 2, pb: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">Notifications</Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Typography
              variant="button"
              sx={{ cursor: 'pointer', color: 'primary.main' }}
              onClick={markAllAsRead}
            >
              Mark all read
            </Typography>
            <Typography
              variant="button"
              sx={{ cursor: 'pointer', color: 'error.main' }}
              onClick={clearAll}
            >
              Clear all
            </Typography>
          </Box>
        </Box>
      </Box>
      <Divider />
      
      {notifications.length === 0 ? (
        <MenuItem disabled>
          <Typography variant="body2" color="text.secondary">
            No notifications
          </Typography>
        </MenuItem>
      ) : (
        notifications.slice(0, 10).map((notification): void => (
          <MenuItem
            key={notification.id}
            onClick={() => handleNotificationClick(notification)}
            sx={{
              bgcolor: notification.read ? 'transparent' : 'action.hover',
              '&:hover': { bgcolor: 'action.selected' },
              py: 2,
            }}
          >
            <ListItemIcon>
              <Box sx={{ position: 'relative' }}>
                {getCategoryIcon(notification.category)}
                <Box
                  sx={{
                    position: 'absolute',
                    top: -4,
                    right: -4,
                    width: 12,
                    height: 12,
                  }}
                >
                  {getIcon(notification.type)}
                </Box>
              </Box>
            </ListItemIcon>
            <ListItemText
              primary={
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Typography variant="subtitle2" noWrap>
                    {notification.title}
                  </Typography>
                  {!notification.read && (
                    <Box
                      sx={{
                        width: 8,
                        height: 8,
                        borderRadius: '50%',
                        bgcolor: 'primary.main',
                        ml: 1,
                      }}
                    />
                  )}
                </Box>
              }
              secondary={
                <Box>
                  <Typography variant="body2" color="text.secondary" noWrap>
                    {notification.message}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {format(notification.timestamp, 'MMM dd, HH:mm')}
                  </Typography>
                </Box>
              }
            />
            <IconButton
              size="small"
              onClick={(e) => {
                e.stopPropagation();
                clearNotification(notification.id);
              }}
            >
              <CloseIcon fontSize="small" />
            </IconButton>
          </MenuItem>
        ))
      )}
      
      {notifications.length > 10 && (
        <MenuItem disabled>
          <Typography variant="caption" color="text.secondary">
            Showing 10 of {notifications.length} notifications
          </Typography>
        </MenuItem>
      )}
    </Menu>
  );
};

interface NotificationIconProps {
  onClick: (event: React.MouseEvent<HTMLElement>) => void;
}

export const NotificationIcon: React.FC<NotificationIconProps> = ({ onClick }) => {
  const { unreadCount } = useNotifications();

  return (
    <IconButton color="inherit" onClick={onClick}>
      <Badge badgeContent={unreadCount} color="error" max={99}>
        <NotificationsIcon />
      </Badge>
    </IconButton>
  );
};

// Helper hook for workflow notifications
export const useWorkflowNotifications = () => {
  const { showNotification } = useNotifications();

  const notifyWorkflowStarted = useCallback((workflowName: string) => {
    showNotification({
      type: 'info',
      category: 'workflow',
      title: 'Workflow Started',
      message: `${workflowName} execution has begun`,
    });
  }, [showNotification]);

  const notifyWorkflowCompleted = useCallback((workflowName: string, duration: string) => {
    showNotification({
      type: 'success',
      category: 'workflow',
      title: 'Workflow Completed',
      message: `${workflowName} finished successfully in ${duration}`,
    });
  }, [showNotification]);

  const notifyWorkflowFailed = useCallback((workflowName: string, error: string) => {
    showNotification({
      type: 'error',
      category: 'workflow',
      title: 'Workflow Failed',
      message: `${workflowName}: ${error}`,
      persistent: true,
    });
  }, [showNotification]);

  return {
    notifyWorkflowStarted,
    notifyWorkflowCompleted,
    notifyWorkflowFailed,
  };
};

// Helper hook for agent notifications
export const useAgentNotifications = () => {
  const { showNotification } = useNotifications();

  const notifyAgentActivated = useCallback((agentName: string) => {
    showNotification({
      type: 'success',
      category: 'agent',
      title: 'Agent Activated',
      message: `${agentName} is now active and ready`,
    });
  }, [showNotification]);

  const notifyAgentError = useCallback((agentName: string, error: string) => {
    showNotification({
      type: 'error',
      category: 'agent',
      title: 'Agent Error',
      message: `${agentName}: ${error}`,
    });
  }, [showNotification]);

  return {
    notifyAgentActivated,
    notifyAgentError,
  };
};

// Helper hook for A/B test notifications
export const useTestNotifications = () => {
  const { showNotification } = useNotifications();

  const notifyTestSignificant = useCallback((testName: string, winner: string) => {
    showNotification({
      type: 'success',
      category: 'test',
      title: 'Test Reached Significance',
      message: `${testName}: ${winner} is the winner`,
      persistent: true,
    });
  }, [showNotification]);

  const notifyTestStarted = useCallback((testName: string) => {
    showNotification({
      type: 'info',
      category: 'test',
      title: 'A/B Test Started',
      message: `${testName} is now collecting data`,
    });
  }, [showNotification]);

  return {
    notifyTestSignificant,
    notifyTestStarted,
  };
};