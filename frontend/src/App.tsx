import React, { useState, useMemo } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// Pages
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import ConversationsPage from './pages/ConversationsPage';
import DocumentsPage from './pages/DocumentsPage';
import ProfilesPage from './pages/ProfilesPage';
import PromptsPage from './pages/PromptsPage';
import ChatPage from './pages/ChatPage';
import HealthPage from './pages/HealthPage';
import AgentsPage from './pages/AgentsPage';
import AdministrationPage from './pages/AdministrationPage';
import ModelManagementPage from './pages/ModelManagementPage';

// Components
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import { SSEProvider } from './services/sse-context';

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

  return (
    <ThemeContext.Provider value={{ darkMode, toggleDarkMode }}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <SSEProvider autoConnect={true}>
          <Router>
            <Routes>
              {/* Public routes */}
              <Route path="/login" element={<LoginPage />} />
              
              {/* Protected routes */}
              <Route path="/" element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }>
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="dashboard" element={<DashboardPage />} />
                <Route path="chat" element={<ChatPage />} />
                <Route path="conversations" element={<ConversationsPage />} />
                <Route path="documents" element={<DocumentsPage />} />
                <Route path="profiles" element={<ProfilesPage />} />
                <Route path="prompts" element={<PromptsPage />} />
                <Route path="models" element={<ModelManagementPage />} />
                <Route path="agents" element={<AgentsPage />} />
                <Route path="health" element={<HealthPage />} />
                <Route path="administration" element={<AdministrationPage />} />
              </Route>
            </Routes>
          </Router>
        </SSEProvider>
      </ThemeProvider>
    </ThemeContext.Provider>
  );
}

export default App;
