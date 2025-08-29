import React, { Suspense } from 'react';
import {
  Box,
  CircularProgress,
  Typography,
  Fade,
  LinearProgress,
} from '@mui/material';
import ErrorBoundary from './ErrorBoundary';

interface SuspenseWrapperProps {
  children: React.ReactNode;
  loadingMessage?: string;
  minLoadingTime?: number;
  showProgressBar?: boolean;
  fallbackComponent?: React.ComponentType;
}

/**
 * Loading fallback component for Suspense
 */
const LoadingFallback: React.FC<{
  message?: string;
  showProgressBar?: boolean;
}> = ({ message = 'Loading...', showProgressBar = false }) => {
  return (
    <Fade in timeout={300}>
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '200px',
          p: 3,
          gap: 2,
        }}
      >
        {showProgressBar ? (
          <Box sx={{ width: '100%', maxWidth: 400 }}>
            <LinearProgress />
          </Box>
        ) : (
          <CircularProgress size={40} />
        )}
        
        <Typography 
          variant="body2" 
          color="text.secondary"
          sx={{ textAlign: 'center' }}
        >
          {message}
        </Typography>
      </Box>
    </Fade>
  );
};

/**
 * Enhanced Suspense wrapper with error boundary and customizable loading states
 */
const SuspenseWrapper: React.FC<SuspenseWrapperProps> = ({
  children,
  loadingMessage = 'Loading...',
  showProgressBar = false,
  fallbackComponent,
}) => {
  const FallbackComponent = fallbackComponent || (() => (
    <LoadingFallback message={loadingMessage} showProgressBar={showProgressBar} />
  ));

  return (
    <ErrorBoundary>
      <Suspense fallback={<FallbackComponent />}>
        {children}
      </Suspense>
    </ErrorBoundary>
  );
};

export default SuspenseWrapper;