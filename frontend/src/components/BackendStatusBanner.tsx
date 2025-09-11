import React, { useState, useEffect } from 'react';
import {
  Alert,
  AlertTitle,
  Box,
  Button,
  Collapse,
  IconButton,
  Typography,
} from '@mui/material';
import {
  Warning as WarningIcon,
  Refresh as RefreshIcon,
  Close as CloseIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
} from '@mui/icons-material';
import { backendHealthService, BackendHealthStatus } from '../services/backend-health';

interface BackendStatusBannerProps {
  onDismiss?: () => void;
  showRefreshButton?: boolean;
}

const BackendStatusBanner: React.FC<BackendStatusBannerProps> = ({
  onDismiss,
  showRefreshButton = true,
}) => {
  const [healthStatus, setHealthStatus] = useState<BackendHealthStatus>(
    backendHealthService.getCurrentHealthStatus()
  );
  const [isExpanded, setIsExpanded] = useState(false);
  const [isChecking, setIsChecking] = useState(false);

  useEffect(() => {
    // Initial check
    checkHealth();

    // Set up periodic checks
    const interval = setInterval(checkHealth, 30000); // Check every 30 seconds

    return () => clearInterval(interval);
  }, []);

  const checkHealth = async () => {
    const status = await backendHealthService.checkBackendHealth();
    setHealthStatus(status);
  };

  const handleRefresh = async () => {
    setIsChecking(true);
    await checkHealth();
    setIsChecking(false);
  };

  // Don't show banner if backend is available
  if (healthStatus.available) {
    return null;
  }

  return (
    <Alert
      severity="warning"
      icon={<WarningIcon />}
      sx={{
        mb: 2,
        '& .MuiAlert-message': {
          width: '100%',
        },
      }}
      action={
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {showRefreshButton && (
            <Button
              color="inherit"
              size="small"
              onClick={handleRefresh}
              disabled={isChecking}
              startIcon={<RefreshIcon />}
            >
              {isChecking ? 'Checking...' : 'Retry'}
            </Button>
          )}
          <IconButton
            size="small"
            color="inherit"
            onClick={() => setIsExpanded(!isExpanded)}
            title={isExpanded ? 'Show less' : 'Show more'}
          >
            {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </IconButton>
          {onDismiss && (
            <IconButton
              size="small"
              color="inherit"
              onClick={onDismiss}
              title="Dismiss"
            >
              <CloseIcon />
            </IconButton>
          )}
        </Box>
      }
    >
      <AlertTitle>Backend Server Unavailable</AlertTitle>
      <Typography variant="body2">
        The backend server is not responding. Some features may not work correctly.
      </Typography>
      
      <Collapse in={isExpanded}>
        <Box sx={{ mt: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
          <Typography variant="body2" gutterBottom>
            <strong>Technical Details:</strong>
          </Typography>
          <Typography variant="body2" component="div" sx={{ mb: 1 }}>
            • Last checked: {healthStatus.lastChecked.toLocaleTimeString()}
          </Typography>
          {healthStatus.error && (
            <Typography variant="body2" component="div" sx={{ mb: 1 }}>
              • Error: {healthStatus.error}
            </Typography>
          )}
          <Typography variant="body2" component="div" sx={{ mb: 2 }}>
            • Expected URL: {import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}
          </Typography>
          
          <Typography variant="body2" gutterBottom>
            <strong>Possible Solutions:</strong>
          </Typography>
          <Typography variant="body2" component="ul" sx={{ pl: 2, mb: 0 }}>
            <li>Check if the backend server is running</li>
            <li>Verify the server is accessible at the expected URL</li>
            <li>Check your network connection</li>
            <li>Contact your system administrator if the issue persists</li>
          </Typography>
        </Box>
      </Collapse>
    </Alert>
  );
};

export default BackendStatusBanner;