import React, { Suspense, ReactNode } from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';

interface LoadingFallbackProps {
  message?: string;
  size?: number;
}

export const LoadingFallback: React.FC<LoadingFallbackProps> = ({
  message = 'Loading...',
  size = 40,
}) => (
  <Box
    sx={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: 200,
      gap: 2,
    }}
  >
    <CircularProgress size={size} />
    <Typography variant="body2" color="text.secondary">
      {message}
    </Typography>
  </Box>
);

interface SuspenseWrapperProps {
  children: ReactNode;
  fallback?: ReactNode;
  loadingMessage?: string;
}

export const SuspenseWrapper: React.FC<SuspenseWrapperProps> = ({
  children,
  fallback,
  loadingMessage = 'Loading...',
}) => (
  <Suspense fallback={fallback || <LoadingFallback message={loadingMessage} />}>
    {children}
  </Suspense>
);

export default SuspenseWrapper;
