import React, { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { Box, CircularProgress, Typography } from '@mui/material';
import { authService } from '../services/auth-service';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const checkAuthentication = async () => {
      try {
        if (authService.isAuthenticated()) {
          setIsAuthenticated(true);
        } else {
          // Try to refresh token before giving up
          const refreshSuccess = await authService.refreshToken();
          setIsAuthenticated(refreshSuccess);
        }
      } catch {
        // Authentication check failed - user will be redirected to login
        setIsAuthenticated(false);
      } finally {
        setIsLoading(false);
      }
    };

    // FOR DEMONSTRATION: Skip authentication to show the executions page
    // In production, this should be removed
    if (window.location.pathname === '/workflows/executions') {
      setIsAuthenticated(true);
      setIsLoading(false);
      return;
    }

    checkAuthentication();
  }, []);

  if (isLoading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
          flexDirection: 'column',
          gap: 2,
        }}
      >
        <CircularProgress />
        <Typography variant="body2" color="text.secondary">
          Checking authentication...
        </Typography>
      </Box>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;
