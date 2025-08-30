/* eslint-disable no-console */
import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Button,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Switch,
  FormControlLabel,
  Alert,
  CircularProgress,
  Snackbar,
  Tabs,
  Tab,
  Menu,
  MenuItem,
  Paper,
} from '@mui/material';
import {
  Build as ToolsIcon,
  Storage as ServersIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Settings as SettingsIcon,
  MoreVert as MoreVertIcon,
  PlayArrow as StartIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  PowerSettingsNew as ToggleIcon,
} from '@mui/icons-material';
import { chatterSDK } from '../services/chatter-sdk';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tools-tabpanel-${index}`}
      aria-labelledby={`tools-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const ToolsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogType, setDialogType] = useState<'server' | 'tool'>('server');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  
  // Action menu state
  const [actionAnchorEl, setActionAnchorEl] = useState<HTMLElement | null>(null);
  const [actionItem, setActionItem] = useState<any>(null);
  const [actionType, setActionType] = useState<'server' | 'tool'>('server');

  // Data state
  const [toolServers, setToolServers] = useState([
    {
      id: 'file-ops',
      name: 'File Operations Server',
      display_name: 'File Operations Server',
      status: 'ENABLED',
      url: 'http://localhost:3000',
      toolsCount: 8,
      is_builtin: false,
    },
    {
      id: 'web-search',
      name: 'Web Search Server',
      display_name: 'Web Search Server',
      status: 'DISABLED',
      url: 'http://localhost:3001',
      toolsCount: 4,
      is_builtin: true,
    }
  ]);

  const [tools, setTools] = useState([
    {
      id: 'file-read',
      name: 'file_read',
      display_name: 'Read File',
      description: 'Read the contents of a file',
      server_id: 'file-ops',
      server_name: 'File Operations Server',
      enabled: true,
    },
    {
      id: 'file-write',
      name: 'file_write',
      display_name: 'Write File',
      description: 'Write contents to a file',
      server_id: 'file-ops',
      server_name: 'File Operations Server',
      enabled: true,
    },
    {
      id: 'web-search',
      name: 'web_search',
      display_name: 'Web Search',
      description: 'Search the web for information',
      server_id: 'web-search',
      server_name: 'Web Search Server',
      enabled: false,
    },
  ]);

  const [formData, setFormData] = useState({
    serverName: '',
    serverDisplayName: '',
    serverCommand: '',
    serverDescription: '',
  });

  const showSnackbar = (message: string) => {
    setSnackbarMessage(message);
    setSnackbarOpen(true);
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const openDialog = (type: 'server' | 'tool') => {
    setDialogType(type);
    setDialogOpen(true);
    setError('');
    setFormData({
      serverName: '',
      serverDisplayName: '',
      serverCommand: '',
      serverDescription: '',
    });
  };

  const handleFormChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleFormSubmit = async () => {
    try {
      setLoading(true);
      setError('');
      
      if (dialogType === 'server') {
        await chatterSDK.toolServers.createToolServerApiV1ToolserversServersPost({
          toolServerCreate: {
            name: formData.serverName,
            display_name: formData.serverDisplayName || formData.serverName,
            command: formData.serverCommand,
            description: formData.serverDescription,
          }
        });
        showSnackbar('Tool server created successfully!');
        // TODO: Refresh server list from API
      }
      
      setDialogOpen(false);
    } catch (error: any) {
      console.error('Error submitting form:', error);
      setError(error.response?.data?.detail || error.message || 'An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const openActionMenu = (e: React.MouseEvent<HTMLElement>, item: any, type: 'server' | 'tool') => {
    setActionAnchorEl(e.currentTarget);
    setActionItem(item);
    setActionType(type);
  };

  const closeActionMenu = () => {
    setActionAnchorEl(null);
    setActionItem(null);
  };

  const handleServerToggle = async (serverId: string, enable: boolean) => {
    try {
      setLoading(true);
      if (enable) {
        await chatterSDK.toolServers.enableToolServerApiV1ToolserversServersServerIdEnablePost({
          serverId
        });
        showSnackbar('Server enabled successfully');
      } else {
        await chatterSDK.toolServers.disableToolServerApiV1ToolserversServersServerIdDisablePost({
          serverId
        });
        showSnackbar('Server disabled successfully');
      }
      // TODO: Refresh server list from API
      closeActionMenu();
    } catch (error: any) {
      console.error('Error toggling server:', error);
      setError('Failed to toggle server status');
    } finally {
      setLoading(false);
    }
  };

  const handleToolToggle = async (toolId: string, enable: boolean) => {
    try {
      setLoading(true);
      if (enable) {
        await chatterSDK.toolServers.enableToolApiV1ToolserversToolsToolIdEnablePost({
          toolId
        });
        showSnackbar('Tool enabled successfully');
      } else {
        await chatterSDK.toolServers.disableToolApiV1ToolserversToolsToolIdDisablePost({
          toolId
        });
        showSnackbar('Tool disabled successfully');
      }
      // TODO: Refresh tools list from API
      closeActionMenu();
    } catch (error: any) {
      console.error('Error toggling tool:', error);
      setError('Failed to toggle tool status');
    } finally {
      setLoading(false);
    }
  };

  const handleServerStart = async (serverId: string) => {
    try {
      setLoading(true);
      await chatterSDK.toolServers.startToolServerApiV1ToolserversServersServerIdStartPost({
        serverId
      });
      showSnackbar('Server started successfully');
      // TODO: Refresh server list from API
      closeActionMenu();
    } catch (error: any) {
      console.error('Error starting server:', error);
      setError('Failed to start server');
    } finally {
      setLoading(false);
    }
  };

  const handleServerStop = async (serverId: string) => {
    try {
      setLoading(true);
      await chatterSDK.toolServers.stopToolServerApiV1ToolserversServersServerIdStopPost({
        serverId
      });
      showSnackbar('Server stopped successfully');
      // TODO: Refresh server list from API
      closeActionMenu();
    } catch (error: any) {
      console.error('Error stopping server:', error);
      setError('Failed to stop server');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteServer = async (serverId: string) => {
    const server = toolServers.find(s => s.id === serverId);
    const toolCount = server?.toolsCount || 0;
    
    const confirmMessage = toolCount > 0 
      ? `Are you sure you want to delete this server? This will also remove all ${toolCount} associated tools.`
      : 'Are you sure you want to delete this server?';
      
    if (window.confirm(confirmMessage)) {
      try {
        setLoading(true);
        setError('');
        await chatterSDK.toolServers.deleteToolServerApiV1ToolserversServersServerIdDelete({
          serverId
        });
        showSnackbar('Tool server deleted successfully!');
        // TODO: Refresh server list from API
        closeActionMenu();
      } catch (error: any) {
        console.error('Error deleting server:', error);
        setError(error.response?.data?.detail || error.message || 'Failed to delete server');
      } finally {
        setLoading(false);
      }
    }
  };

  const getServerStatusColor = (status: string) => {
    switch (status) {
      case 'ENABLED':
        return 'success';
      case 'DISABLED':
        return 'default';
      case 'ERROR':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold' }}>
          Tools Management
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={() => {
              // TODO: Refresh data from API
              showSnackbar('Data refreshed');
            }}
            disabled={loading}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Paper sx={{ width: '100%' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={activeTab} onChange={handleTabChange} aria-label="tools management tabs">
            <Tab
              icon={<ServersIcon />}
              iconPosition="start"
              label="Servers"
              id="tools-tab-0"
              aria-controls="tools-tabpanel-0"
            />
            <Tab
              icon={<ToolsIcon />}
              iconPosition="start"
              label="Tools"
              id="tools-tab-1"
              aria-controls="tools-tabpanel-1"
            />
          </Tabs>
        </Box>

        <TabPanel value={activeTab} index={0}>
          <Box sx={{ mb: 2 }}>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => openDialog('server')}
            >
              Add Server
            </Button>
          </Box>
          <List>
            {toolServers.map((server) => (
              <ListItem key={server.id}>
                <ListItemText
                  primary={server.display_name || server.name}
                  secondary={`Status: ${server.status} | Tools: ${server.toolsCount}${server.is_builtin ? ' | Built-in' : ''}`}
                />
                <Chip 
                  label={server.status} 
                  color={getServerStatusColor(server.status) as any}
                  size="small" 
                  sx={{ mr: 1 }} 
                />
                <ListItemSecondaryAction>
                  <IconButton edge="end" onClick={(e) => openActionMenu(e, server, 'server')}>
                    <MoreVertIcon />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        </TabPanel>

        <TabPanel value={activeTab} index={1}>
          <List>
            {tools.map((tool) => (
              <ListItem key={tool.id}>
                <ListItemText
                  primary={tool.display_name || tool.name}
                  secondary={`${tool.description} | Server: ${tool.server_name}`}
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={tool.enabled}
                      onChange={(e) => handleToolToggle(tool.id, e.target.checked)}
                      disabled={loading}
                    />
                  }
                  label={tool.enabled ? 'Enabled' : 'Disabled'}
                  sx={{ mr: 1 }}
                />
                <ListItemSecondaryAction>
                  <IconButton edge="end" onClick={(e) => openActionMenu(e, tool, 'tool')}>
                    <MoreVertIcon />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        </TabPanel>
      </Paper>

      {/* Add Server Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {dialogType === 'server' && 'Add Tool Server'}
        </DialogTitle>
        <DialogContent>
          {dialogType === 'server' && (
            <Box sx={{ mt: 2 }}>
              <TextField
                fullWidth
                label="Server Name"
                margin="normal"
                placeholder="my-tool-server"
                helperText="Unique name for the server"
                value={formData.serverName}
                onChange={(e) => handleFormChange('serverName', e.target.value)}
              />
              <TextField
                fullWidth
                label="Display Name"
                margin="normal"
                placeholder="My Tool Server"
                value={formData.serverDisplayName}
                onChange={(e) => handleFormChange('serverDisplayName', e.target.value)}
              />
              <TextField
                fullWidth
                label="Command"
                margin="normal"
                placeholder="node server.js"
                helperText="Command to start the server"
                value={formData.serverCommand}
                onChange={(e) => handleFormChange('serverCommand', e.target.value)}
              />
              <TextField
                fullWidth
                label="Description"
                margin="normal"
                multiline
                rows={3}
                placeholder="Description of the server's capabilities"
                value={formData.serverDescription}
                onChange={(e) => handleFormChange('serverDescription', e.target.value)}
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleFormSubmit} 
            variant="contained" 
            disabled={loading || !formData.serverName || !formData.serverCommand}
          >
            {loading ? <CircularProgress size={20} /> : 'Add'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Action Menu */}
      <Menu
        anchorEl={actionAnchorEl}
        open={Boolean(actionAnchorEl)}
        onClose={closeActionMenu}
      >
        {actionType === 'server' && actionItem && (
          [
            <MenuItem key="toggle" onClick={() => handleServerToggle(actionItem.id, actionItem.status !== 'ENABLED')}>
              <ToggleIcon sx={{ mr: 1 }} />
              {actionItem.status === 'ENABLED' ? 'Disable' : 'Enable'} Server
            </MenuItem>,
            <MenuItem key="start" onClick={() => handleServerStart(actionItem.id)}>
              <StartIcon sx={{ mr: 1 }} />
              Start Server
            </MenuItem>,
            <MenuItem key="stop" onClick={() => handleServerStop(actionItem.id)}>
              <StopIcon sx={{ mr: 1 }} />
              Stop Server
            </MenuItem>,
            <MenuItem key="settings" onClick={closeActionMenu}>
              <SettingsIcon sx={{ mr: 1 }} />
              Settings
            </MenuItem>,
            !actionItem.is_builtin && (
              <MenuItem key="delete" onClick={() => handleDeleteServer(actionItem.id)} sx={{ color: 'error.main' }}>
                <DeleteIcon sx={{ mr: 1 }} />
                Delete Server
              </MenuItem>
            )
          ].filter(Boolean)
        )}
        {actionType === 'tool' && actionItem && (
          [
            <MenuItem key="toggle" onClick={() => handleToolToggle(actionItem.id, !actionItem.enabled)}>
              <ToggleIcon sx={{ mr: 1 }} />
              {actionItem.enabled ? 'Disable' : 'Enable'} Tool
            </MenuItem>,
            <MenuItem key="settings" onClick={closeActionMenu}>
              <SettingsIcon sx={{ mr: 1 }} />
              Settings
            </MenuItem>
          ]
        )}
      </Menu>

      {/* Snackbar */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={4000}
        onClose={() => setSnackbarOpen(false)}
        message={snackbarMessage}
      />
    </Box>
  );
};

export default ToolsPage;