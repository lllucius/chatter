import React, { useState, useMemo, lazy, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box, CircularProgress, Typography } from '@mui/material';

// Components
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import ErrorBoundary from './components/ErrorBoundary';
import SuspenseWrapper from './components/SuspenseWrapper';
import ThemedToastContainer from './components/ThemedToastContainer';
import { SSEProvider } from './services/sse-context';

// Initialize SDK at app startup
import { initializeSDK } from './services/auth-service';

// Lazy load pages for better performance
const LoginPage = lazy(() => import('./pages/LoginPage'));
const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const ConversationsPage = lazy(() => import('./pages/ConversationsPage'));
const DocumentsPage = lazy(() => import('./pages/DocumentsPage'));
const ProfilesPage = lazy(() => import('./pages/ProfilesPageRefactored'));
const PromptsPage = lazy(() => import('./pages/PromptsPageRefactored'));
const ChatPage = lazy(() => import('./pages/ChatPage'));
const HealthPage = lazy(() => import('./pages/HealthPage'));
const AgentsPage = lazy(() => import('./pages/AgentsPageRefactored'));
const AdministrationPage = lazy(() => import('./pages/AdministrationPage'));
const ModelManagementPage = lazy(() => import('./pages/ModelManagementPageRefactored'));
const ToolsPage = lazy(() => import('./pages/ToolsPageRefactored'));
const WorkflowManagementPage = lazy(() => import('./pages/WorkflowManagementPage'));
const ABTestingPage = lazy(() => import('./pages/ABTestingPage'));
const UserSettingsPage = lazy(() => import('./pages/UserSettingsPage'));

// Create theme context
export const ThemeContext = React.createContext<{
  darkMode: boolean;
  toggleDarkMode: () => void;
}>({
  darkMode: false,
  toggleDarkMode: () => {},
});

function App() {
  const [darkMode, setDarkMode] = useState(true);
  const [authInitialized, setAuthInitialized] = useState(false);

  // Initialize SDK at app startup
  useEffect(() => {
    const initAuth = async () => {
      try {
        await initializeSDK();
      } catch (error) {
        console.error('Failed to initialize SDK:', error);
      } finally {
        setAuthInitialized(true);
      }
    };
    initAuth();
  }, []);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  const theme = useMemo(() => createTheme({
    palette: {
      mode: darkMode ? 'dark' : 'light',
      primary: {
        main: '#1976d2',
      },
      secondary: {
        main: '#dc004e',
      },
      background: {
        default: darkMode ? '#121212' : '#f5f5f5',
        paper: darkMode ? '#1e1e1e' : '#ffffff',
      },
    },
    typography: {
      fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
      h4: {
        fontWeight: 600,
      },
      h5: {
        fontWeight: 600,
      },
      h6: {
        fontWeight: 600,
      },
    },
    components: {
      MuiCard: {
        styleOverrides: {
          root: {
            boxShadow: darkMode 
              ? '0 2px 4px rgba(0,0,0,0.3)' 
              : '0 2px 4px rgba(0,0,0,0.1)',
            borderRadius: 8,
          },
        },
      },
      MuiButton: {
        styleOverrides: {
          root: {
            textTransform: 'none',
            borderRadius: 8,
          },
        },
      },
    },
  }), [darkMode]);

  // Show loading screen while authentication is being initialized
  if (!authInitialized) {
    return (
      <ThemeContext.Provider value={{ darkMode, toggleDarkMode }}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <Box 
            sx={{ 
              display: 'flex', 
              justifyContent: 'center', 
              alignItems: 'center', 
              height: '100vh',
              flexDirection: 'column',
              gap: 2
            }}
          >
            <CircularProgress size={60} />
            <Typography variant="h6" color="text.secondary">
              Initializing...
            </Typography>
          </Box>
        </ThemeProvider>
      </ThemeContext.Provider>
    );
  }

  return (
    <ErrorBoundary>
      <ThemeContext.Provider value={{ darkMode, toggleDarkMode }}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <SSEProvider autoConnect={true}>
            <Router>
              <Routes>
                {/* Public routes */}
                <Route path="/login" element={
                  <SuspenseWrapper loadingMessage="Loading login page...">
                    <LoginPage />
                  </SuspenseWrapper>
                } />
                
                {/* Protected routes */}
                <Route path="/" element={
                  <ProtectedRoute>
                    <Layout />
                  </ProtectedRoute>
                }>
                  <Route index element={<Navigate to="/dashboard" replace />} />
                  <Route path="dashboard" element={
                    <SuspenseWrapper loadingMessage="Loading dashboard...">
                      <DashboardPage />
                    </SuspenseWrapper>
                  } />
                  <Route path="chat" element={
                    <SuspenseWrapper loadingMessage="Loading chat...">
                      <ChatPage />
                    </SuspenseWrapper>
                  } />
                  <Route path="conversations" element={
                    <SuspenseWrapper loadingMessage="Loading conversations...">
                      <ConversationsPage />
                    </SuspenseWrapper>
                  } />
                  <Route path="documents" element={
                    <SuspenseWrapper loadingMessage="Loading documents...">
                      <DocumentsPage />
                    </SuspenseWrapper>
                  } />
                  <Route path="profiles" element={
                    <SuspenseWrapper loadingMessage="Loading profiles...">
                      <ProfilesPage />
                    </SuspenseWrapper>
                  } />
                  <Route path="prompts" element={
                    <SuspenseWrapper loadingMessage="Loading prompts...">
                      <PromptsPage />
                    </SuspenseWrapper>
                  } />
                  <Route path="models" element={
                    <SuspenseWrapper loadingMessage="Loading models...">
                      <ModelManagementPage />
                    </SuspenseWrapper>
                  } />
                  <Route path="agents" element={
                    <SuspenseWrapper loadingMessage="Loading agents...">
                      <AgentsPage />
                    </SuspenseWrapper>
                  } />
                  <Route path="tools" element={
                    <SuspenseWrapper loadingMessage="Loading tools...">
                      <ToolsPage />
                    </SuspenseWrapper>
                  } />
                  <Route path="workflows" element={
                    <SuspenseWrapper loadingMessage="Loading workflow management...">
                      <WorkflowManagementPage />
                    </SuspenseWrapper>
                  } />
                  <Route path="ab-testing" element={
                    <SuspenseWrapper loadingMessage="Loading AB testing...">
                      <ABTestingPage />
                    </SuspenseWrapper>
                  } />
                  <Route path="health" element={
                    <SuspenseWrapper loadingMessage="Loading health status...">
                      <HealthPage />
                    </SuspenseWrapper>
                  } />
                  <Route path="administration" element={
                    <SuspenseWrapper loadingMessage="Loading administration...">
                      <AdministrationPage />
                    </SuspenseWrapper>
                  } />
                  <Route path="settings" element={
                    <SuspenseWrapper loadingMessage="Loading settings...">
                      <UserSettingsPage />
                    </SuspenseWrapper>
                  } />
                </Route>
              </Routes>
            </Router>
          </SSEProvider>
          <ThemedToastContainer />
        </ThemeProvider>
      </ThemeContext.Provider>
    </ErrorBoundary>
  );
}

export default App;
