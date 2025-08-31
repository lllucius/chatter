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
  Select,
  FormControl,
  InputLabel,
  Grid,
  Card,
  CardContent,
  CardActions,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Tooltip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  ListItemIcon,
  TableSortLabel,
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
  Security as SecurityIcon,
  ExpandMore as ExpandMoreIcon,
  Cloud as CloudIcon,
  Http as HttpIcon,
  Sync as SseIcon,
  Edit as EditIcon,
  Close as CloseIcon,
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
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

interface RemoteServer {
  id: string;
  name: string;
  display_name: string;
  description?: string;
  base_url: string;
  transport_type: 'http' | 'sse';
  status: 'enabled' | 'disabled' | 'error' | 'starting' | 'stopping';
  oauth_config?: {
    client_id: string;
    client_secret: string;
    token_url: string;
    scope?: string;
  };
  headers?: Record<string, string>;
  timeout: number;
  auto_start: boolean;
  tools_count?: number;
  last_health_check?: string;
  created_at: string;
  updated_at: string;
}

interface Tool {
  id: string;
  name: string;
  display_name: string;
  description?: string;
  server_name: string;
  status: 'enabled' | 'disabled' | 'unavailable' | 'error';
  is_available: boolean;
  total_calls: number;
  total_errors: number;
  avg_response_time_ms?: number;
  last_called?: string;
}

interface PermissionData {
  user_id: string;
  tool_id?: string;
  server_id?: string;
  access_level: 'none' | 'read' | 'execute' | 'admin';
  rate_limit_per_hour?: number;
  rate_limit_per_day?: number;
  expires_at?: string;
}

const ToolsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogType, setDialogType] = useState<'server' | 'tool' | 'permission' | 'edit-server'>('server');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [editingServer, setEditingServer] = useState<RemoteServer | null>(null);

  // Menu state
  const [actionAnchorEl, setActionAnchorEl] = useState<HTMLElement | null>(null);
  const [actionItem, setActionItem] = useState<any>(null);
  const [actionType, setActionType] = useState<'server' | 'tool'>('server');

  // Data state
  const [remoteServers, setRemoteServers] = useState<RemoteServer[]>([]);
  const [tools, setTools] = useState<Tool[]>([]);
  const [permissions, setPermissions] = useState<any[]>([]);

  // Pagination state
  const [toolsPage, setToolsPage] = useState(0);
  const [toolsRowsPerPage, setToolsRowsPerPage] = useState(10);
  const [serversPage, setServersPage] = useState(0);
  const [serversRowsPerPage, setServersRowsPerPage] = useState(10);

  // Filtering state
  const [serversFilter, setServersFilter] = useState('');
  const [toolsFilter, setToolsFilter] = useState('');

  // Sorting state
  const [serversSort, setServersSort] = useState<{field: string, direction: 'asc' | 'desc'}>({field: 'display_name', direction: 'asc'});
  const [toolsSort, setToolsSort] = useState<{field: string, direction: 'asc' | 'desc'}>({field: 'display_name', direction: 'asc'});

  // Form state for remote servers
  const [serverFormData, setServerFormData] = useState({
    name: '',
    display_name: '',
    description: '',
    base_url: '',
    transport_type: 'http' as 'http' | 'sse',
    oauth_enabled: false,
    oauth_client_id: '',
    oauth_client_secret: '',
    oauth_token_url: '',
    oauth_scope: '',
    headers: '{}',
    timeout: 30,
    auto_start: true,
  });

  // Form state for permissions
  const [permissionFormData, setPermissionFormData] = useState<PermissionData>({
    user_id: '',
    access_level: 'execute',
  });

  const showSnackbar = (message: string) => {
    setSnackbarMessage(message);
    setSnackbarOpen(true);
  };

  // Filtering and sorting helpers
  const filterServers = (servers: RemoteServer[]) => {
    if (!serversFilter) return servers;
    const filter = serversFilter.toLowerCase();
    return servers.filter(server =>
      server.display_name.toLowerCase().includes(filter) ||
      server.name.toLowerCase().includes(filter) ||
      server.base_url.toLowerCase().includes(filter) ||
      server.transport_type.toLowerCase().includes(filter) ||
      server.status.toLowerCase().includes(filter) ||
      (server.description && server.description.toLowerCase().includes(filter))
    );
  };

  const sortServers = (servers: RemoteServer[]) => {
    return [...servers].sort((a, b) => {
      let aValue: any = '';
      let bValue: any = '';
      
      switch (serversSort.field) {
        case 'display_name':
          aValue = a.display_name || a.name;
          bValue = b.display_name || b.name;
          break;
        case 'base_url':
          aValue = a.base_url;
          bValue = b.base_url;
          break;
        case 'transport_type':
          aValue = a.transport_type;
          bValue = b.transport_type;
          break;
        case 'status':
          aValue = a.status;
          bValue = b.status;
          break;
        case 'tools_count':
          aValue = a.tools_count || 0;
          bValue = b.tools_count || 0;
          break;
        default:
          aValue = a.display_name || a.name;
          bValue = b.display_name || b.name;
      }

      if (typeof aValue === 'string') {
        aValue = aValue.toLowerCase();
        bValue = bValue.toLowerCase();
      }

      if (serversSort.direction === 'asc') {
        return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
      } else {
        return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
      }
    });
  };

  const filterTools = (tools: Tool[]) => {
    if (!toolsFilter) return tools;
    const filter = toolsFilter.toLowerCase();
    return tools.filter(tool =>
      (tool.display_name || tool.name).toLowerCase().includes(filter) ||
      tool.name.toLowerCase().includes(filter) ||
      tool.server_name.toLowerCase().includes(filter) ||
      tool.status.toLowerCase().includes(filter) ||
      (tool.description && tool.description.toLowerCase().includes(filter))
    );
  };

  const sortTools = (tools: Tool[]) => {
    return [...tools].sort((a, b) => {
      let aValue: any = '';
      let bValue: any = '';
      
      switch (toolsSort.field) {
        case 'display_name':
          aValue = a.display_name || a.name;
          bValue = b.display_name || b.name;
          break;
        case 'server_name':
          aValue = a.server_name;
          bValue = b.server_name;
          break;
        case 'status':
          aValue = a.status;
          bValue = b.status;
          break;
        case 'total_calls':
          aValue = a.total_calls;
          bValue = b.total_calls;
          break;
        case 'avg_response_time_ms':
          aValue = a.avg_response_time_ms || 0;
          bValue = b.avg_response_time_ms || 0;
          break;
        default:
          aValue = a.display_name || a.name;
          bValue = b.display_name || b.name;
      }

      if (typeof aValue === 'string') {
        aValue = aValue.toLowerCase();
        bValue = bValue.toLowerCase();
      }

      if (toolsSort.direction === 'asc') {
        return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
      } else {
        return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
      }
    });
  };

  const handleServerSort = (field: string) => {
    setServersSort(prev => ({
      field,
      direction: prev.field === field && prev.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  const handleToolSort = (field: string) => {
    setToolsSort(prev => ({
      field,
      direction: prev.field === field && prev.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const openDialog = (type: 'server' | 'tool' | 'permission' | 'edit-server', item?: any) => {
    setDialogType(type);
    setDialogOpen(true);
    if (type === 'server') {
      setServerFormData({
        name: '',
        display_name: '',
        description: '',
        base_url: '',
        transport_type: 'http',
        oauth_enabled: false,
        oauth_client_id: '',
        oauth_client_secret: '',
        oauth_token_url: '',
        oauth_scope: '',
        headers: '{}',
        timeout: 30,
        auto_start: true,
      });
      setEditingServer(null);
    } else if (type === 'edit-server' && item) {
      setEditingServer(item);
      setServerFormData({
        name: item.name || '',
        display_name: item.display_name || '',
        description: item.description || '',
        base_url: item.base_url || '',
        transport_type: item.transport_type || 'http',
        oauth_enabled: Boolean(item.oauth_config),
        oauth_client_id: item.oauth_config?.client_id || '',
        oauth_client_secret: item.oauth_config?.client_secret || '',
        oauth_token_url: item.oauth_config?.token_url || '',
        oauth_scope: item.oauth_config?.scope || '',
        headers: item.headers ? JSON.stringify(item.headers) : '{}',
        timeout: item.timeout || 30,
        auto_start: item.auto_start !== undefined ? item.auto_start : true,
      });
    }
  };

  const closeDialog = () => {
    setDialogOpen(false);
    setError('');
    setEditingServer(null);
  };

  const handleActionClick = (event: React.MouseEvent<HTMLElement>, item: any, type: 'server' | 'tool') => {
    setActionAnchorEl(event.currentTarget);
    setActionItem(item);
    setActionType(type);
  };

  const handleActionClose = () => {
    setActionAnchorEl(null);
    setActionItem(null);
  };

  // Load data
  const loadRemoteServers = useCallback(async () => {
    try {
      setLoading(true);
      const response = await chatterSDK.getToolServers();
      setRemoteServers(response.data || []);
      setError('');
    } catch (err) {
      console.error('Failed to load remote servers:', err);
      const errorMessage = 'Failed to load remote servers';
      setError(errorMessage);
      showSnackbar(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadTools = useCallback(async () => {
    try {
      setLoading(true);
      const response = await chatterSDK.getAllTools();
      setTools(response.data || []);
      setError('');
    } catch (err) {
      console.error('Failed to load tools:', err);
      const errorMessage = 'Failed to load tools';
      setError(errorMessage);
      showSnackbar(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadPermissions = useCallback(async () => {
    try {
      setLoading(true);
      const response = await chatterSDK.getUserPermissions('current-user'); // Using placeholder for now
      setPermissions(response.data || []);
      setError('');
    } catch (err) {
      console.error('Failed to load permissions:', err);
      const errorMessage = 'Failed to load permissions';
      setError(errorMessage);
      showSnackbar(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadRemoteServers();
    loadTools();
    loadPermissions();
  }, [loadRemoteServers, loadTools, loadPermissions]);

  // Server operations
  const createRemoteServer = async () => {
    try {
      setLoading(true);
      setError('');

      const serverData = {
        name: serverFormData.name,
        display_name: serverFormData.display_name,
        description: serverFormData.description,
        base_url: serverFormData.base_url,
        transport_type: serverFormData.transport_type,
        oauth_config: serverFormData.oauth_enabled ? {
          client_id: serverFormData.oauth_client_id,
          client_secret: serverFormData.oauth_client_secret,
          token_url: serverFormData.oauth_token_url,
          scope: serverFormData.oauth_scope || undefined,
        } : undefined,
        headers: serverFormData.headers ? JSON.parse(serverFormData.headers) : undefined,
        timeout: serverFormData.timeout,
        auto_start: serverFormData.auto_start,
      };

      await chatterSDK.createToolServer(serverData);
      showSnackbar('Remote server created successfully');
      closeDialog();
      loadRemoteServers();
    } catch (err) {
      console.error('Failed to create remote server:', err);
      const errorMessage = 'Failed to create remote server';
      setError(errorMessage);
      showSnackbar(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const updateRemoteServer = async () => {
    if (!editingServer) return;
    
    try {
      setLoading(true);
      setError('');

      const updateData = {
        display_name: serverFormData.display_name,
        description: serverFormData.description,
        auto_start: serverFormData.auto_start,
        timeout: serverFormData.timeout,
        oauth_config: serverFormData.oauth_enabled ? {
          client_id: serverFormData.oauth_client_id,
          client_secret: serverFormData.oauth_client_secret,
          token_url: serverFormData.oauth_token_url,
          scope: serverFormData.oauth_scope || undefined,
        } : undefined,
        headers: serverFormData.headers ? JSON.parse(serverFormData.headers) : undefined,
      };

      await chatterSDK.updateToolServer(editingServer.id, updateData);
      showSnackbar('Server updated successfully');
      closeDialog();
      loadRemoteServers();
    } catch (err) {
      console.error('Failed to update server:', err);
      const errorMessage = 'Failed to update server';
      setError(errorMessage);
      showSnackbar(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const toggleServer = async (serverId: string, enable: boolean) => {
    try {
      if (enable) {
        await chatterSDK.enableToolServer(serverId);
      } else {
        await chatterSDK.disableToolServer(serverId);
      }
      showSnackbar(`Server ${enable ? 'enabled' : 'disabled'} successfully`);
      loadRemoteServers();
    } catch (err) {
      console.error(`Failed to ${enable ? 'enable' : 'disable'} server:`, err);
      showSnackbar(`Failed to ${enable ? 'enable' : 'disable'} server`);
    }
    handleActionClose();
  };

  const refreshServerTools = async (serverId: string) => {
    try {
      await chatterSDK.refreshServerTools(serverId);
      showSnackbar('Server tools refreshed successfully');
      loadTools();
    } catch (err) {
      console.error('Failed to refresh server tools:', err);
      showSnackbar('Failed to refresh server tools');
    }
    handleActionClose();
  };

  const deleteServer = async (serverId: string) => {
    try {
      await chatterSDK.deleteToolServer(serverId);
      showSnackbar('Server deleted successfully');
      loadRemoteServers();
      loadTools();
    } catch (err) {
      console.error('Failed to delete server:', err);
      showSnackbar('Failed to delete server');
    }
    handleActionClose();
  };

  const toggleTool = async (toolId: string, enable: boolean) => {
    try {
      if (enable) {
        await chatterSDK.enableTool(toolId);
      } else {
        await chatterSDK.disableTool(toolId);
      }
      showSnackbar(`Tool ${enable ? 'enabled' : 'disabled'} successfully`);
      loadTools();
    } catch (err) {
      console.error(`Failed to ${enable ? 'enable' : 'disable'} tool:`, err);
      showSnackbar(`Failed to ${enable ? 'enable' : 'disable'} tool`);
    }
    handleActionClose();
  };

  // Pagination handlers
  const handleToolsPageChange = (event: unknown, newPage: number) => {
    setToolsPage(newPage);
  };

  const handleToolsRowsPerPageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setToolsRowsPerPage(parseInt(event.target.value, 10));
    setToolsPage(0);
  };

  const handleServersPageChange = (event: unknown, newPage: number) => {
    setServersPage(newPage);
  };

  const handleServersRowsPerPageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setServersRowsPerPage(parseInt(event.target.value, 10));
    setServersPage(0);
  };

  // Paginated data with filtering and sorting
  const filteredAndSortedTools = sortTools(filterTools(tools));
  const filteredAndSortedServers = sortServers(filterServers(remoteServers));

  const paginatedTools = filteredAndSortedTools.slice(
    toolsPage * toolsRowsPerPage,
    toolsPage * toolsRowsPerPage + toolsRowsPerPage
  );

  const paginatedServers = filteredAndSortedServers.slice(
    serversPage * serversRowsPerPage,
    serversPage * serversRowsPerPage + serversRowsPerPage
  );

  const renderServerDialog = () => (
    <Dialog open={dialogOpen && (dialogType === 'server' || dialogType === 'edit-server')} onClose={closeDialog} maxWidth="md" fullWidth>
      <DialogTitle>{dialogType === 'edit-server' ? 'Edit Server Configuration' : 'Add Remote MCP Server'}</DialogTitle>
      <DialogContent>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        
        <Grid container spacing={3} sx={{ mt: 1 }}>
          {/* Basic Information */}
          <Grid item xs={12}>
            <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
              <SettingsIcon sx={{ mr: 1 }} />
              Basic Information
            </Typography>
          </Grid>
          
          {dialogType === 'server' && (
            <>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Server Name"
                  value={serverFormData.name}
                  onChange={(e) => setServerFormData({ ...serverFormData, name: e.target.value })}
                  required
                  helperText="Internal identifier for the server"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Display Name"
                  value={serverFormData.display_name}
                  onChange={(e) => setServerFormData({ ...serverFormData, display_name: e.target.value })}
                  required
                  helperText="Human-readable name shown in the UI"
                />
              </Grid>
            </>
          )}
          {dialogType === 'edit-server' && (
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Display Name"
                value={serverFormData.display_name}
                onChange={(e) => setServerFormData({ ...serverFormData, display_name: e.target.value })}
                required
                helperText="Human-readable name shown in the UI"
              />
            </Grid>
          )}
          
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Description"
              value={serverFormData.description}
              onChange={(e) => setServerFormData({ ...serverFormData, description: e.target.value })}
              multiline
              rows={2}
              helperText="Optional description of the server's purpose"
            />
          </Grid>

          {/* Connection Settings */}
          {dialogType === 'server' && (
            <>
              <Grid item xs={12}>
                <Typography variant="h6" sx={{ mb: 2, mt: 2, display: 'flex', alignItems: 'center' }}>
                  <CloudIcon sx={{ mr: 1 }} />
                  Connection Settings
                </Typography>
              </Grid>
              
              <Grid item xs={12} md={8}>
                <TextField
                  fullWidth
                  label="Base URL"
                  value={serverFormData.base_url}
                  onChange={(e) => setServerFormData({ ...serverFormData, base_url: e.target.value })}
                  placeholder="https://api.example.com"
                  required
                  helperText="The base URL for the MCP server"
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <FormControl fullWidth>
                  <InputLabel>Transport Type</InputLabel>
                  <Select
                    value={serverFormData.transport_type}
                    onChange={(e) => setServerFormData({ ...serverFormData, transport_type: e.target.value as 'http' | 'sse' })}
                    label="Transport Type"
                  >
                    <MenuItem value="http">
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <HttpIcon sx={{ mr: 1 }} />
                        HTTP
                      </Box>
                    </MenuItem>
                    <MenuItem value="sse">
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <SseIcon sx={{ mr: 1 }} />
                        Server-Sent Events
                      </Box>
                    </MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Timeout (seconds)"
                  type="number"
                  value={serverFormData.timeout}
                  onChange={(e) => setServerFormData({ ...serverFormData, timeout: parseInt(e.target.value) || 30 })}
                  inputProps={{ min: 5, max: 300 }}
                  helperText="Request timeout in seconds (5-300)"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={serverFormData.auto_start}
                      onChange={(e) => setServerFormData({ ...serverFormData, auto_start: e.target.checked })}
                    />
                  }
                  label="Auto-connect on startup"
                />
              </Grid>
            </>
          )}

          {/* Settings for Edit Mode */}
          {dialogType === 'edit-server' && (
            <>
              <Grid item xs={12}>
                <Typography variant="h6" sx={{ mb: 2, mt: 2, display: 'flex', alignItems: 'center' }}>
                  <SettingsIcon sx={{ mr: 1 }} />
                  Server Settings
                </Typography>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Timeout (seconds)"
                  type="number"
                  value={serverFormData.timeout}
                  onChange={(e) => setServerFormData({ ...serverFormData, timeout: parseInt(e.target.value) || 30 })}
                  inputProps={{ min: 5, max: 300 }}
                  helperText="Request timeout in seconds (5-300)"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={serverFormData.auto_start}
                      onChange={(e) => setServerFormData({ ...serverFormData, auto_start: e.target.checked })}
                    />
                  }
                  label="Auto-connect on startup"
                />
              </Grid>
            </>
          )}

          {/* OAuth Configuration */}
          <Grid item xs={12}>
            <Typography variant="h6" sx={{ mb: 2, mt: 2, display: 'flex', alignItems: 'center' }}>
              <SecurityIcon sx={{ mr: 1 }} />
              OAuth Authentication
            </Typography>
          </Grid>
          
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={serverFormData.oauth_enabled}
                  onChange={(e) => setServerFormData({ ...serverFormData, oauth_enabled: e.target.checked })}
                />
              }
              label="Enable OAuth 2.0 Authentication"
            />
          </Grid>
          
          {serverFormData.oauth_enabled && (
            <>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Client ID"
                  value={serverFormData.oauth_client_id}
                  onChange={(e) => setServerFormData({ ...serverFormData, oauth_client_id: e.target.value })}
                  helperText="OAuth client identifier"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Client Secret"
                  type="password"
                  value={serverFormData.oauth_client_secret}
                  onChange={(e) => setServerFormData({ ...serverFormData, oauth_client_secret: e.target.value })}
                  helperText="OAuth client secret"
                />
              </Grid>
              <Grid item xs={12} md={8}>
                <TextField
                  fullWidth
                  label="Token URL"
                  value={serverFormData.oauth_token_url}
                  onChange={(e) => setServerFormData({ ...serverFormData, oauth_token_url: e.target.value })}
                  placeholder="https://oauth.example.com/token"
                  helperText="OAuth token endpoint URL"
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="Scope (optional)"
                  value={serverFormData.oauth_scope}
                  onChange={(e) => setServerFormData({ ...serverFormData, oauth_scope: e.target.value })}
                  placeholder="read write"
                  helperText="OAuth scope(s)"
                />
              </Grid>
            </>
          )}

          {/* Custom Headers */}
          <Grid item xs={12}>
            <Typography variant="h6" sx={{ mb: 2, mt: 2, display: 'flex', alignItems: 'center' }}>
              <SettingsIcon sx={{ mr: 1 }} />
              Custom Headers
            </Typography>
          </Grid>
          
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Custom Headers (JSON)"
              value={serverFormData.headers}
              onChange={(e) => setServerFormData({ ...serverFormData, headers: e.target.value })}
              placeholder='{"Authorization": "Bearer token", "X-API-Key": "your-key"}'
              multiline
              rows={3}
              helperText="Additional HTTP headers as JSON object"
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={closeDialog}>Cancel</Button>
        <Button 
          onClick={dialogType === 'edit-server' ? updateRemoteServer : createRemoteServer}
          variant="contained" 
          disabled={loading || (dialogType === 'server' && (!serverFormData.name || !serverFormData.base_url)) || (dialogType === 'edit-server' && !serverFormData.display_name)}
        >
          {loading ? <CircularProgress size={20} /> : dialogType === 'edit-server' ? 'Update Server' : 'Create Server'}
        </Button>
      </DialogActions>
    </Dialog>
  );

  const renderPermissionDialog = () => (
    <Dialog open={dialogOpen && dialogType === 'permission'} onClose={closeDialog} maxWidth="sm" fullWidth>
      <DialogTitle>Grant Tool Permission</DialogTitle>
      <DialogContent>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="User ID"
              value={permissionFormData.user_id}
              onChange={(e) => setPermissionFormData({ ...permissionFormData, user_id: e.target.value })}
              placeholder="Enter user ID or email"
              required
            />
          </Grid>
          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel>Access Level</InputLabel>
              <Select
                value={permissionFormData.access_level}
                onChange={(e) => setPermissionFormData({ 
                  ...permissionFormData, 
                  access_level: e.target.value as 'none' | 'read' | 'execute' | 'admin'
                })}
                label="Access Level"
              >
                <MenuItem value="none">None</MenuItem>
                <MenuItem value="read">Read Only</MenuItem>
                <MenuItem value="execute">Execute</MenuItem>
                <MenuItem value="admin">Admin</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Tool ID (optional)"
              value={permissionFormData.tool_id || ''}
              onChange={(e) => setPermissionFormData({ ...permissionFormData, tool_id: e.target.value })}
              placeholder="Specific tool ID"
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Server ID (optional)"
              value={permissionFormData.server_id || ''}
              onChange={(e) => setPermissionFormData({ ...permissionFormData, server_id: e.target.value })}
              placeholder="Specific server ID"
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Rate Limit (per hour)"
              type="number"
              value={permissionFormData.rate_limit_per_hour || ''}
              onChange={(e) => setPermissionFormData({ 
                ...permissionFormData, 
                rate_limit_per_hour: parseInt(e.target.value) || undefined 
              })}
              placeholder="Optional rate limit"
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Rate Limit (per day)"
              type="number"
              value={permissionFormData.rate_limit_per_day || ''}
              onChange={(e) => setPermissionFormData({ 
                ...permissionFormData, 
                rate_limit_per_day: parseInt(e.target.value) || undefined 
              })}
              placeholder="Optional rate limit"
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={closeDialog}>Cancel</Button>
        <Button 
          onClick={() => {
            // TODO: Implement when permission endpoints are available
            showSnackbar('Permission grant feature will be available when backend endpoints are integrated');
            closeDialog();
          }} 
          variant="contained" 
          disabled={loading || !permissionFormData.user_id}
        >
          {loading ? <CircularProgress size={20} /> : 'Grant Permission'}
        </Button>
      </DialogActions>
    </Dialog>
  );

  const renderRemoteServers = () => (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>Remote MCP Servers</Typography>
        
        {/* Filter field */}
        <TextField
          fullWidth
          size="small"
          placeholder="Filter servers by name, URL, transport type, status, or description..."
          value={serversFilter}
          onChange={(e) => setServersFilter(e.target.value)}
          sx={{ mb: 2 }}
        />
      </Box>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress size={60} />
        </Box>
      ) : filteredAndSortedServers.length === 0 ? (
        <Alert severity="info">
          {serversFilter ? 'No servers match your filter criteria.' : 'No remote servers configured. Add your first remote MCP server to get started.'}
        </Alert>
      ) : (
        <Card>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>
                    <TableSortLabel
                      active={serversSort.field === 'display_name'}
                      direction={serversSort.direction}
                      onClick={() => handleServerSort('display_name')}
                    >
                      Name
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>
                    <TableSortLabel
                      active={serversSort.field === 'base_url'}
                      direction={serversSort.direction}
                      onClick={() => handleServerSort('base_url')}
                    >
                      URL
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>
                    <TableSortLabel
                      active={serversSort.field === 'transport_type'}
                      direction={serversSort.direction}
                      onClick={() => handleServerSort('transport_type')}
                    >
                      Transport
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>
                    <TableSortLabel
                      active={serversSort.field === 'status'}
                      direction={serversSort.direction}
                      onClick={() => handleServerSort('status')}
                    >
                      Status
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>
                    <TableSortLabel
                      active={serversSort.field === 'tools_count'}
                      direction={serversSort.direction}
                      onClick={() => handleServerSort('tools_count')}
                    >
                      Tools
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>Security</TableCell>
                  <TableCell align="center">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {paginatedServers.map((server) => (
                  <TableRow key={server.id} hover>
                    <TableCell>
                      <Box>
                        <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
                          {server.display_name}
                        </Typography>
                        {server.description && (
                          <Typography variant="body2" color="text.secondary">
                            {server.description}
                          </Typography>
                        )}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {server.base_url}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={server.transport_type.toUpperCase()} 
                        variant="outlined"
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={server.status} 
                        color={server.status === 'enabled' ? 'success' : server.status === 'error' ? 'error' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {server.tools_count !== undefined ? `${server.tools_count} tools` : 'Unknown'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      {server.oauth_config && (
                        <Chip 
                          label="OAuth" 
                          color="primary"
                          variant="outlined"
                          size="small"
                        />
                      )}
                    </TableCell>
                    <TableCell align="center">
                      <IconButton
                        onClick={(e) => handleActionClick(e, server, 'server')}
                      >
                        <MoreVertIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination
            component="div"
            count={filteredAndSortedServers.length}
            page={serversPage}
            onPageChange={handleServersPageChange}
            rowsPerPage={serversRowsPerPage}
            onRowsPerPageChange={handleServersRowsPerPageChange}
            rowsPerPageOptions={[5, 10, 25]}
          />
        </Card>
      )}
    </Box>
  );

  const renderTools = () => (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>Available Tools</Typography>
        
        {/* Filter field */}
        <TextField
          fullWidth
          size="small"
          placeholder="Filter tools by name, server, status, or description..."
          value={toolsFilter}
          onChange={(e) => setToolsFilter(e.target.value)}
          sx={{ mb: 2 }}
        />
      </Box>
      
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress size={60} />
        </Box>
      ) : filteredAndSortedTools.length === 0 ? (
        <Alert severity="info">
          {toolsFilter ? 'No tools match your filter criteria.' : 'No tools available. Add remote servers to discover tools.'}
        </Alert>
      ) : (
        <Card>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>
                    <TableSortLabel
                      active={toolsSort.field === 'display_name'}
                      direction={toolsSort.direction}
                      onClick={() => handleToolSort('display_name')}
                    >
                      Name
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>
                    <TableSortLabel
                      active={toolsSort.field === 'server_name'}
                      direction={toolsSort.direction}
                      onClick={() => handleToolSort('server_name')}
                    >
                      Server
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>
                    <TableSortLabel
                      active={toolsSort.field === 'status'}
                      direction={toolsSort.direction}
                      onClick={() => handleToolSort('status')}
                    >
                      Status
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>
                    <TableSortLabel
                      active={toolsSort.field === 'total_calls'}
                      direction={toolsSort.direction}
                      onClick={() => handleToolSort('total_calls')}
                    >
                      Usage
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>
                    <TableSortLabel
                      active={toolsSort.field === 'avg_response_time_ms'}
                      direction={toolsSort.direction}
                      onClick={() => handleToolSort('avg_response_time_ms')}
                    >
                      Performance
                    </TableSortLabel>
                  </TableCell>
                  <TableCell align="center">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {paginatedTools.map((tool) => (
                  <TableRow key={tool.id} hover>
                    <TableCell>
                      <Box>
                        <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
                          {tool.display_name || tool.name}
                        </Typography>
                        {tool.description && (
                          <Typography variant="body2" color="text.secondary">
                            {tool.description}
                          </Typography>
                        )}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {tool.server_name}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                        <Chip 
                          label={tool.status} 
                          color={tool.status === 'enabled' ? 'success' : tool.status === 'error' ? 'error' : 'default'}
                          size="small"
                        />
                        {!tool.is_available && (
                          <Chip label="Unavailable" color="warning" size="small" />
                        )}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box>
                        <Typography variant="body2">
                          Calls: {tool.total_calls}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Errors: {tool.total_errors}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {tool.avg_response_time_ms ? `${tool.avg_response_time_ms.toFixed(0)}ms` : 'N/A'}
                      </Typography>
                    </TableCell>
                    <TableCell align="center">
                      <IconButton
                        onClick={(e) => handleActionClick(e, tool, 'tool')}
                      >
                        <MoreVertIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination
            component="div"
            count={filteredAndSortedTools.length}
            page={toolsPage}
            onPageChange={handleToolsPageChange}
            rowsPerPage={toolsRowsPerPage}
            onRowsPerPageChange={handleToolsRowsPerPageChange}
            rowsPerPageOptions={[5, 10, 25]}
          />
        </Card>
      )}
    </Box>
  );

  const renderPermissions = () => (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>Access Permissions</Typography>
        
        <Alert severity="info" sx={{ mb: 2 }}>
          Tool access control allows you to grant specific permissions to users for tools and servers.
          This feature requires role-based access control to be configured.
        </Alert>
      </Box>

      {loading && <CircularProgress />}

      {permissions.length === 0 && !loading ? (
        <Alert severity="info">
          No permissions configured yet. Grant permissions to users to control access to tools and servers.
        </Alert>
      ) : (
        <Box>
          <Typography variant="h6" gutterBottom>
            Current Permissions
          </Typography>
          <List>
            {permissions.map((permission: any, index: number) => (
              <ListItem key={index} divider>
                <SecurityIcon sx={{ mr: 2, color: 'primary.main' }} />
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="subtitle1">
                        {permission.user_id || 'User'}
                      </Typography>
                      <Chip 
                        label={permission.access_level || 'execute'} 
                        color="primary"
                        size="small"
                      />
                    </Box>
                  }
                  secondary={
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        {permission.tool_id ? `Tool: ${permission.tool_id}` : 
                         permission.server_id ? `Server: ${permission.server_id}` : 
                         'Global access'}
                      </Typography>
                      {permission.rate_limit_per_hour && (
                        <Typography variant="caption" display="block">
                          Rate limit: {permission.rate_limit_per_hour}/hour
                        </Typography>
                      )}
                    </Box>
                  }
                />
                <ListItemSecondaryAction>
                  <IconButton edge="end" color="error">
                    <DeleteIcon />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        </Box>
      )}
    </Box>
  );

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold' }}>
          Tool Server Management
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={() => {
              if (activeTab === 0) {
                loadRemoteServers();
              } else if (activeTab === 1) {
                loadTools();
              } else {
                loadPermissions();
              }
            }}
            disabled={loading}
          >
            Refresh
          </Button>
          {activeTab === 0 && (
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => openDialog('server')}
            >
              Add Remote Server
            </Button>
          )}
          {activeTab === 2 && (
            <Button
              variant="contained"
              startIcon={<SecurityIcon />}
              onClick={() => openDialog('permission')}
            >
              Grant Permissions
            </Button>
          )}
        </Box>
      </Box>
      
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={activeTab} onChange={handleTabChange}>
          <Tab 
            label="Remote Servers" 
            icon={<ServersIcon />} 
            iconPosition="start"
          />
          <Tab 
            label="Available Tools" 
            icon={<ToolsIcon />} 
            iconPosition="start"
          />
          <Tab 
            label="Access Control" 
            icon={<SecurityIcon />} 
            iconPosition="start"
          />
        </Tabs>
      </Box>

      <TabPanel value={activeTab} index={0}>
        {renderRemoteServers()}
      </TabPanel>

      <TabPanel value={activeTab} index={1}>
        {renderTools()}
      </TabPanel>

      <TabPanel value={activeTab} index={2}>
        {renderPermissions()}
      </TabPanel>

      {/* Dialogs */}
      {renderServerDialog()}
      {renderPermissionDialog()}

      {/* Action Menu */}
      <Menu
        anchorEl={actionAnchorEl}
        open={Boolean(actionAnchorEl)}
        onClose={handleActionClose}
      >
        {actionType === 'server' && actionItem && (
          [
            <MenuItem key="edit" onClick={() => { openDialog('edit-server', actionItem); handleActionClose(); }}>
              <EditIcon sx={{ mr: 1 }} />
              Edit
            </MenuItem>,
            <MenuItem key="toggle" onClick={() => toggleServer(actionItem.id, actionItem.status !== 'enabled')}>
              <ToggleIcon sx={{ mr: 1 }} />
              {actionItem.status === 'enabled' ? 'Disable' : 'Enable'}
            </MenuItem>,
            <MenuItem key="refresh" onClick={() => refreshServerTools(actionItem.id)}>
              <RefreshIcon sx={{ mr: 1 }} />
              Refresh Tools
            </MenuItem>,
            <MenuItem key="delete" onClick={() => deleteServer(actionItem.id)}>
              <DeleteIcon sx={{ mr: 1 }} />
              Delete
            </MenuItem>
          ]
        )}
        {actionType === 'tool' && actionItem && (
          <MenuItem onClick={() => toggleTool(actionItem.id, actionItem.status !== 'enabled')}>
            <ToggleIcon sx={{ mr: 1 }} />
            {actionItem.status === 'enabled' ? 'Disable' : 'Enable'}
          </MenuItem>
        )}
      </Menu>

      {/* Enhanced Snackbar */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={() => setSnackbarOpen(false)}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
        action={
          <IconButton
            size="small"
            aria-label="close"
            color="inherit"
            onClick={() => setSnackbarOpen(false)}
          >
            <CloseIcon fontSize="small" />
          </IconButton>
        }
        message={snackbarMessage}
      />
    </Box>
  );
};

export default ToolsPage;