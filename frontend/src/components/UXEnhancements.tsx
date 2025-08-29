import React, { useState, useEffect } from 'react';
import {
  Snackbar,
  Alert,
  LinearProgress,
  Box,
  Typography,
  IconButton,
  Fab,
  Tooltip,
} from '@mui/material';
import {
  Close as CloseIcon,
  KeyboardArrowUp as ArrowUpIcon,
  Refresh as RefreshIcon,
  WifiOff as OfflineIcon,
} from '@mui/icons-material';

/**
 * Global notification system
 */
interface Notification {
  id: string;
  message: string;
  severity: 'success' | 'error' | 'warning' | 'info';
  autoHideDuration?: number;
}

let notificationId = 0;
const notificationCallbacks: ((notification: Notification) => void)[] = [];

export const NotificationSystem = {
  show: (notification: Omit<Notification, 'id'>) => {
    const fullNotification = {
      ...notification,
      id: (++notificationId).toString(),
    };
    notificationCallbacks.forEach(callback => callback(fullNotification));
  },
  
  success: (message: string, autoHideDuration?: number) => {
    NotificationSystem.show({ message, severity: 'success', autoHideDuration });
  },
  
  error: (message: string, autoHideDuration?: number) => {
    NotificationSystem.show({ message, severity: 'error', autoHideDuration });
  },
  
  warning: (message: string, autoHideDuration?: number) => {
    NotificationSystem.show({ message, severity: 'warning', autoHideDuration });
  },
  
  info: (message: string, autoHideDuration?: number) => {
    NotificationSystem.show({ message, severity: 'info', autoHideDuration });
  },
};

export const NotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  useEffect(() => {
    const callback = (notification: Notification) => {
      setNotifications(prev => [...prev, notification]);
    };
    
    notificationCallbacks.push(callback);
    
    return () => {
      const index = notificationCallbacks.indexOf(callback);
      if (index > -1) {
        notificationCallbacks.splice(index, 1);
      }
    };
  }, []);

  const handleClose = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  return (
    <>
      {children}
      {notifications.map((notification) => (
        <Snackbar
          key={notification.id}
          open={true}
          autoHideDuration={notification.autoHideDuration || 6000}
          onClose={() => handleClose(notification.id)}
          anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
        >
          <Alert
            onClose={() => handleClose(notification.id)}
            severity={notification.severity}
            variant="filled"
          >
            {notification.message}
          </Alert>
        </Snackbar>
      ))}
    </>
  );
};

/**
 * Progressive loading indicator
 */
interface ProgressiveLoaderProps {
  stages: string[];
  currentStage: number;
  isLoading: boolean;
}

export const ProgressiveLoader: React.FC<ProgressiveLoaderProps> = ({
  stages,
  currentStage,
  isLoading,
}) => {
  const progress = isLoading ? (currentStage / stages.length) * 100 : 100;

  if (!isLoading && currentStage === stages.length) {
    return null;
  }

  return (
    <Box sx={{ width: '100%', mb: 2 }}>
      <LinearProgress 
        variant="determinate" 
        value={progress}
        sx={{ height: 8, borderRadius: 4 }}
      />
      <Typography 
        variant="body2" 
        color="text.secondary" 
        sx={{ mt: 1, textAlign: 'center' }}
      >
        {isLoading && currentStage < stages.length 
          ? stages[currentStage] 
          : 'Complete'
        }
      </Typography>
    </Box>
  );
};

/**
 * Offline status indicator and handler
 */
export const OfflineHandler: React.FC = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [showOfflineMessage, setShowOfflineMessage] = useState(false);

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      setShowOfflineMessage(false);
      NotificationSystem.success('Connection restored');
    };

    const handleOffline = () => {
      setIsOnline(false);
      setShowOfflineMessage(true);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (!showOfflineMessage) {
    return null;
  }

  return (
    <Snackbar
      open={showOfflineMessage}
      anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
    >
      <Alert 
        severity="warning" 
        icon={<OfflineIcon />}
        action={
          <IconButton
            size="small"
            aria-label="close"
            color="inherit"
            onClick={() => setShowOfflineMessage(false)}
          >
            <CloseIcon fontSize="small" />
          </IconButton>
        }
      >
        You're currently offline. Some features may not work properly.
      </Alert>
    </Snackbar>
  );
};

/**
 * Scroll to top button
 */
export const ScrollToTop: React.FC = () => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsVisible(window.pageYOffset > 300);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    });
  };

  if (!isVisible) {
    return null;
  }

  return (
    <Fab
      size="small"
      aria-label="scroll to top"
      onClick={scrollToTop}
      sx={{
        position: 'fixed',
        bottom: 16,
        right: 16,
        zIndex: 1000,
      }}
    >
      <ArrowUpIcon />
    </Fab>
  );
};

/**
 * Page refresh prompt for stale content
 */
interface RefreshPromptProps {
  lastUpdated: Date;
  maxAge: number; // in minutes
}

export const RefreshPrompt: React.FC<RefreshPromptProps> = ({ lastUpdated, maxAge }) => {
  const [shouldRefresh, setShouldRefresh] = useState(false);

  useEffect(() => {
    const checkAge = () => {
      const now = new Date();
      const age = (now.getTime() - lastUpdated.getTime()) / (1000 * 60); // minutes
      setShouldRefresh(age > maxAge);
    };

    checkAge();
    const interval = setInterval(checkAge, 60000); // Check every minute

    return () => clearInterval(interval);
  }, [lastUpdated, maxAge]);

  const handleRefresh = () => {
    window.location.reload();
  };

  if (!shouldRefresh) {
    return null;
  }

  return (
    <Snackbar
      open={shouldRefresh}
      anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
    >
      <Alert
        severity="info"
        action={
          <Tooltip title="Refresh page">
            <IconButton
              size="small"
              aria-label="refresh"
              color="inherit"
              onClick={handleRefresh}
            >
              <RefreshIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        }
      >
        New content is available. Refresh to see the latest updates.
      </Alert>
    </Snackbar>
  );
};

/**
 * Context for managing application-wide UI state
 */
interface UIState {
  isLoading: boolean;
  loadingMessage: string;
  hasError: boolean;
  errorMessage: string;
}

const UIContext = React.createContext<{
  state: UIState;
  setState: React.Dispatch<React.SetStateAction<UIState>>;
} | null>(null);

export const UIProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, setState] = useState<UIState>({
    isLoading: false,
    loadingMessage: '',
    hasError: false,
    errorMessage: '',
  });

  return (
    <UIContext.Provider value={{ state, setState }}>
      {children}
    </UIContext.Provider>
  );
};

export const useUI = () => {
  const context = React.useContext(UIContext);
  if (!context) {
    throw new Error('useUI must be used within a UIProvider');
  }
  return context;
};