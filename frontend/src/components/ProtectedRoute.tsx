import React from 'react';
import { Navigate } from 'react-router-dom';
import { chatterSDK } from '../services/chatter-sdk';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  // Temporarily bypass authentication for testing UI changes
  const isAuthenticated = true; // chatterSDK.isAuthenticated();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;