import React, { useState, useMemo, lazy, useEffect } from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box, CircularProgress, Typography } from '@mui/material';

// Components
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import ErrorBoundary from './components/ErrorBoundary';
import SectionErrorBoundary from './components/SectionErrorBoundary';
import SuspenseWrapper from './components/SuspenseWrapper';
import ThemedToastContainer from './components/ThemedToastContainer';
import { NotificationProvider } from './components/NotificationSystem';
import { SSEProvider } from './services/sse-context';

// Initialize SDK at app startup
import { initializeSDK } from './services/auth-service';

// Initialize global error handling
import { initializeGlobalErrorHandling } from './utils/global-error-handler';

// Lazy load pages for better performance
const LoginPage = lazy(() => import('./pages/LoginPage'));
const DashboardPage = lazy(() => import('./pages/NewDashboardPage'));
const ConversationsPage = lazy(() => import('./pages/ConversationsPage'));
const DocumentsPage = lazy(() => import('./pages/DocumentsPage'));
const ProfilesPage = lazy(() => import('./pages/ProfilesPage'));
const PromptsPage = lazy(() => import('./pages/PromptsPage'));
const ChatPage = lazy(() => import('./pages/ChatPage'));
const HealthPage = lazy(() => import('./pages/HealthPage'));
const AgentsPage = lazy(() => import('./pages/AgentsPage'));
const AdministrationPage = lazy(() => import('./pages/AdministrationPage'));
const ModelManagementPage = lazy(() => import('./pages/ModelManagementPage'));
const ToolsPage = lazy(() => import('./pages/ToolsPage'));
const WorkflowManagementPage = lazy(
  () => import('./pages/WorkflowManagementPage')
);
const ABTestingPage = lazy(() => import('./pages/ABTestingPage'));
const UserSettingsPage = lazy(() => import('./pages/UserSettingsPage'));
const NotificationDemo = lazy(() => import('./pages/NotificationDemo'));
const ErrorTestPage = lazy(() => import('./pages/ErrorTestPage'));
const SSEMonitorPage = lazy(() => import('./pages/SSEMonitorPage'));
const ChatBubbleDemo = lazy(() => import('./components/ChatBubbleDemo'));

// Create theme context
export const ThemeContext = React.createContext<{
  darkMode: boolean;
  toggleDarkMode: () => void;
}>({
  darkMode: false,
  toggleDarkMode: () => {
    // Implementation will be added when needed
  },
});

function App() {
  const [darkMode, setDarkMode] = useState(true);
  const [authInitialized, setAuthInitialized] = useState(false);

  // Initialize SDK at app startup
  useEffect(() => {
    const initAuth = async () => {
      try {
        // Initialize global error handling first
        initializeGlobalErrorHandling();

        await initializeSDK();
      } catch {
        // Failed to initialize SDK - handled gracefully by setting authInitialized to true
      } finally {
        setAuthInitialized(true);
      }
    };
    initAuth();
  }, []);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  const theme = useMemo(
    () =>
      createTheme({
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
      }),
    [darkMode]
  );

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
              gap: 2,
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
          <NotificationProvider>
            <SSEProvider autoConnect={true}>
              <Router>
                <Routes>
                  {/* Public routes */}
                  <Route
                    path="/login"
                    element={
                      <SectionErrorBoundary
                        level="page"
                        name="LoginPage"
                        showHomeButton={false}
                      >
                        <SuspenseWrapper loadingMessage="Loading login page...">
                          <LoginPage />
                        </SuspenseWrapper>
                      </SectionErrorBoundary>
                    }
                  />
                  <Route
                    path="/error-test-public"
                    element={
                      <SectionErrorBoundary
                        level="page"
                        name="ErrorTestPage"
                        showHomeButton={true}
                      >
                        <SuspenseWrapper loadingMessage="Loading error test page...">
                          <ErrorTestPage />
                        </SuspenseWrapper>
                      </SectionErrorBoundary>
                    }
                  />
                  <Route
                    path="/chat-bubble-demo-public"
                    element={
                      <SectionErrorBoundary
                        level="page"
                        name="ChatBubbleDemo"
                        showHomeButton={true}
                      >
                        <SuspenseWrapper loadingMessage="Loading chat demo...">
                          <ChatBubbleDemo />
                        </SuspenseWrapper>
                      </SectionErrorBoundary>
                    }
                  />

                  {/* Protected routes */}
                  <Route
                    path="/"
                    element={
                      <ProtectedRoute>
                        <Layout />
                      </ProtectedRoute>
                    }
                  >
                    <Route
                      index
                      element={<Navigate to="/dashboard" replace />}
                    />
                    <Route
                      path="dashboard"
                      element={
                        <SectionErrorBoundary
                          level="page"
                          name="DashboardPage"
                          showHomeButton={true}
                        >
                          <SuspenseWrapper loadingMessage="Loading dashboard...">
                            <DashboardPage />
                          </SuspenseWrapper>
                        </SectionErrorBoundary>
                      }
                    />
                    <Route
                      path="chat"
                      element={
                        <SectionErrorBoundary
                          level="page"
                          name="ChatPage"
                          showHomeButton={true}
                        >
                          <SuspenseWrapper loadingMessage="Loading chat...">
                            <ChatPage />
                          </SuspenseWrapper>
                        </SectionErrorBoundary>
                      }
                    />
                    <Route
                      path="conversations"
                      element={
                        <SectionErrorBoundary
                          level="page"
                          name="ConversationsPage"
                          showHomeButton={true}
                        >
                          <SuspenseWrapper loadingMessage="Loading conversations...">
                            <ConversationsPage />
                          </SuspenseWrapper>
                        </SectionErrorBoundary>
                      }
                    />
                    <Route
                      path="documents"
                      element={
                        <SectionErrorBoundary
                          level="page"
                          name="DocumentsPage"
                          showHomeButton={true}
                        >
                          <SuspenseWrapper loadingMessage="Loading documents...">
                            <DocumentsPage />
                          </SuspenseWrapper>
                        </SectionErrorBoundary>
                      }
                    />
                    <Route
                      path="profiles"
                      element={
                        <SectionErrorBoundary
                          level="page"
                          name="ProfilesPage"
                          showHomeButton={true}
                        >
                          <SuspenseWrapper loadingMessage="Loading profiles...">
                            <ProfilesPage />
                          </SuspenseWrapper>
                        </SectionErrorBoundary>
                      }
                    />
                    <Route
                      path="prompts"
                      element={
                        <SectionErrorBoundary
                          level="page"
                          name="PromptsPage"
                          showHomeButton={true}
                        >
                          <SuspenseWrapper loadingMessage="Loading prompts...">
                            <PromptsPage />
                          </SuspenseWrapper>
                        </SectionErrorBoundary>
                      }
                    />
                    <Route
                      path="models"
                      element={
                        <SectionErrorBoundary
                          level="page"
                          name="ModelManagementPage"
                          showHomeButton={true}
                        >
                          <SuspenseWrapper loadingMessage="Loading models...">
                            <ModelManagementPage />
                          </SuspenseWrapper>
                        </SectionErrorBoundary>
                      }
                    />
                    <Route
                      path="agents"
                      element={
                        <SectionErrorBoundary
                          level="page"
                          name="AgentsPage"
                          showHomeButton={true}
                        >
                          <SuspenseWrapper loadingMessage="Loading agents...">
                            <AgentsPage />
                          </SuspenseWrapper>
                        </SectionErrorBoundary>
                      }
                    />
                    <Route
                      path="tools"
                      element={
                        <SuspenseWrapper loadingMessage="Loading tools...">
                          <ToolsPage />
                        </SuspenseWrapper>
                      }
                    />
                    <Route
                      path="workflows"
                      element={
                        <SuspenseWrapper loadingMessage="Loading workflow management...">
                          <WorkflowManagementPage />
                        </SuspenseWrapper>
                      }
                    />
                    <Route
                      path="ab-testing"
                      element={
                        <SuspenseWrapper loadingMessage="Loading AB testing...">
                          <ABTestingPage />
                        </SuspenseWrapper>
                      }
                    />
                    <Route
                      path="health"
                      element={
                        <SuspenseWrapper loadingMessage="Loading health status...">
                          <HealthPage />
                        </SuspenseWrapper>
                      }
                    />
                    <Route
                      path="administration"
                      element={
                        <SuspenseWrapper loadingMessage="Loading administration...">
                          <AdministrationPage />
                        </SuspenseWrapper>
                      }
                    />
                    <Route
                      path="settings"
                      element={
                        <SuspenseWrapper loadingMessage="Loading settings...">
                          <UserSettingsPage />
                        </SuspenseWrapper>
                      }
                    />
                    <Route
                      path="notifications-demo"
                      element={
                        <SuspenseWrapper loadingMessage="Loading demo...">
                          <NotificationDemo />
                        </SuspenseWrapper>
                      }
                    />
                    <Route
                      path="chat-bubble-demo"
                      element={
                        <SuspenseWrapper loadingMessage="Loading chat demo...">
                          <ChatBubbleDemo />
                        </SuspenseWrapper>
                      }
                    />
                    <Route
                      path="error-test"
                      element={
                        <SectionErrorBoundary
                          level="page"
                          name="ErrorTestPage"
                          showHomeButton={true}
                        >
                          <SuspenseWrapper loadingMessage="Loading error test page...">
                            <ErrorTestPage />
                          </SuspenseWrapper>
                        </SectionErrorBoundary>
                      }
                    />
                    <Route
                      path="sse-monitor"
                      element={
                        <SectionErrorBoundary
                          level="page"
                          name="SSEMonitorPage"
                          showHomeButton={true}
                        >
                          <SuspenseWrapper loadingMessage="Loading SSE monitor...">
                            <SSEMonitorPage />
                          </SuspenseWrapper>
                        </SectionErrorBoundary>
                      }
                    />
                  </Route>
                </Routes>
              </Router>
            </SSEProvider>
            <ThemedToastContainer />
          </NotificationProvider>
        </ThemeProvider>
      </ThemeContext.Provider>
    </ErrorBoundary>
  );
}

export default App;
