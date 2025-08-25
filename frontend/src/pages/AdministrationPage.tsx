import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Button,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
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
} from '@mui/material';
import Grid from '@mui/material/GridLegacy';
import {
  ExpandMore as ExpandMoreIcon,
  Backup as BackupIcon,
  Work as JobIcon,
  Extension as PluginIcon,
  People as UsersIcon,
  Build as ToolsIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Download as DownloadIcon,
  Upload as UploadIcon,
  Settings as SettingsIcon,
  Notifications as NotificationsIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { chatterSDK } from '../services/chatter-sdk';
import { BackupResponse, PluginResponse, JobResponse, JobCreateRequest, JobStatus, JobPriority, JobStatsResponse } from '../sdk';

const AdministrationPage: React.FC = () => {
  const [expanded, setExpanded] = useState<string | false>('backups');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogType, setDialogType] = useState<'user' | 'tool' | 'backup' | 'plugin' | 'job'>('user');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  
  // Data states
  const [backups, setBackups] = useState<BackupResponse[]>([]);
  const [plugins, setPlugins] = useState<PluginResponse[]>([]);
  const [jobs, setJobs] = useState<JobResponse[]>([]);
  const [jobStats, setJobStats] = useState<JobStatsResponse | null>(null);
  const [dataLoading, setDataLoading] = useState(false);
  
  // Notification state
  const [notifications, setNotifications] = useState<Array<{
    id: string;
    title: string;
    message: string;
    type: 'success' | 'error' | 'info' | 'warning';
    timestamp: Date;
    jobId?: string;
  }>>([]);
  const [lastJobStates, setLastJobStates] = useState<Map<string, JobStatus>>(new Map());
  
  const [formData, setFormData] = useState({
    userId: '',
    email: '',
    password: '',
    role: 'user',
    serverName: '',
    serverUrl: '',
    description: '',
    backupName: '',
    includeUserData: true,
    includeDocuments: true,
    includeConfigurations: true,
    pluginUrl: '',
    // Job-specific fields
    jobName: '',
    jobFunction: '',
    jobPriority: 'normal' as const,
    jobArgs: '',
    jobKwargs: '',
    scheduleAt: '',
    maxRetries: 3,
  });

  // Helper functions
  const addNotification = useCallback((notification: Omit<typeof notifications[0], 'id' | 'timestamp'>) => {
    const newNotification = {
      ...notification,
      id: Math.random().toString(36).substr(2, 9),
      timestamp: new Date(),
    };
    setNotifications(prev => [newNotification, ...prev.slice(0, 9)]); // Keep only last 10 notifications
  }, []);

  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  const loadJobs = useCallback(async () => {
    try {
      setDataLoading(true);
      const response = await chatterSDK.jobs.listJobsApiV1JobsGet({});
      const newJobs = response.data.jobs || [];
      
      // Check for job state changes and create notifications
      newJobs.forEach(job => {
        const previousState = lastJobStates.get(job.id);
        if (previousState && previousState !== job.status) {
          // Job state changed, create notification
          addNotification({
            title: 'Job Status Update',
            message: `Job "${job.name || job.id.substring(0, 8)}" changed from ${previousState} to ${job.status}`,
            type: job.status === 'completed' ? 'success' : 
                  job.status === 'failed' ? 'error' : 
                  job.status === 'cancelled' ? 'warning' : 'info',
            jobId: job.id
          });
        }
      });
      
      // Update job states
      const newStates = new Map();
      newJobs.forEach(job => newStates.set(job.id, job.status));
      setLastJobStates(newStates);
      
      setJobs(newJobs);
    } catch (error: any) {
      console.error('Failed to load jobs:', error);
      setError('Failed to load jobs');
    } finally {
      setDataLoading(false);
    }
  }, [lastJobStates, addNotification]);

  const loadJobStats = useCallback(async () => {
    try {
      const response = await chatterSDK.jobs.getJobStatsApiV1JobsStatsOverviewGet();
      setJobStats(response.data);
    } catch (error: any) {
      console.error('Failed to load job stats:', error);
    }
  }, []);

  // Load data on component mount
  useEffect(() => {
    loadBackups();
    loadPlugins();
    loadJobs();
    loadJobStats();
  }, [loadJobs, loadJobStats]);

  // Poll for job updates every 10 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      if (expanded === 'jobs') {
        loadJobs();
        loadJobStats();
      }
    }, 10000);

    return () => clearInterval(interval);
  }, [expanded, loadJobs, loadJobStats]);

  const loadBackups = async () => {
    try {
      setDataLoading(true);
      const response = await chatterSDK.dataManagement.listBackupsApiV1DataBackupsGet({});
      setBackups(response.data.backups || []);
    } catch (error: any) {
      console.error('Failed to load backups:', error);
      setError('Failed to load backups');
    } finally {
      setDataLoading(false);
    }
  };

  const loadPlugins = async () => {
    try {
      const response = await chatterSDK.plugins.listPluginsApiV1PluginsGet({});
      setPlugins(response.data.plugins || []);
    } catch (error: any) {
      console.error('Failed to load plugins:', error);
    }
  };

  const handleJobAction = async (action: 'cancel', jobId: string) => {
    try {
      setLoading(true);
      setError('');
      
      switch (action) {
        case 'cancel':
          await chatterSDK.jobs.cancelJobApiV1JobsJobIdCancelPost({ jobId });
          showSnackbar('Job cancelled successfully!');
          loadJobs(); // Reload jobs
          loadJobStats(); // Reload stats
          break;
      }
    } catch (error: any) {
      console.error(`Error ${action} job:`, error);
      setError(error.response?.data?.detail || error.message || `Failed to ${action} job`);
    } finally {
      setLoading(false);
    }
  };

  const showSnackbar = (message: string) => {
    setSnackbarMessage(message);
    setSnackbarOpen(true);
  };

  const handleBackupDownload = async (backupId: string) => {
    try {
      setLoading(true);
      // This would typically return a download URL or stream
      showSnackbar('Backup download functionality will be available soon');
    } catch (error: any) {
      console.error('Error downloading backup:', error);
      setError('Failed to download backup');
    } finally {
      setLoading(false);
    }
  };

  const handlePluginToggle = async (pluginId: string, enabled: boolean) => {
    try {
      if (enabled) {
        await chatterSDK.plugins.enablePluginApiV1PluginsPluginIdEnablePost({ pluginId });
        showSnackbar('Plugin enabled successfully');
      } else {
        await chatterSDK.plugins.disablePluginApiV1PluginsPluginIdDisablePost({ pluginId });
        showSnackbar('Plugin disabled successfully');
      }
      loadPlugins(); // Reload to get updated status
    } catch (error: any) {
      console.error('Error toggling plugin:', error);
      setError('Failed to toggle plugin status');
    }
  };

  const handleChange = (panel: string) => (event: React.SyntheticEvent, isExpanded: boolean) => {
    setExpanded(isExpanded ? panel : false);
  };

  const openDialog = (type: 'user' | 'tool' | 'backup' | 'plugin' | 'job') => {
    setDialogType(type);
    setDialogOpen(true);
    setError(''); // Clear any existing errors
    // Reset form data
    setFormData({
      userId: '',
      email: '',
      password: '',
      role: 'user',
      serverName: '',
      serverUrl: '',
      description: '',
      backupName: '',
      includeUserData: true,
      includeDocuments: true,
      includeConfigurations: true,
      pluginUrl: '',
      // Job-specific fields
      jobName: '',
      jobFunction: '',
      jobPriority: 'normal' as const,
      jobArgs: '',
      jobKwargs: '',
      scheduleAt: '',
      maxRetries: 3,
    });
  };

  const handleFormChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      setError('');
      
      switch (dialogType) {
        case 'user':
          await chatterSDK.auth.registerApiV1AuthRegisterPost({
            userCreate: {
              username: formData.userId,
              email: formData.email,
              password: formData.password,
            }
          });
          showSnackbar('User created successfully!');
          break;
          
        case 'tool':
          await chatterSDK.toolServers.createToolServerApiV1ToolserversServersPost({
            toolServerCreate: {
              name: formData.serverName,
              display_name: formData.serverName,
              command: formData.serverUrl, // Use serverUrl as command for now
              description: formData.description,
            }
          });
          showSnackbar('Tool server created successfully!');
          break;
          
        case 'backup':
          // Create backup using real API
          await chatterSDK.dataManagement.createBackupApiV1DataBackupPost({
            backupRequest: {
              name: formData.backupName,
              description: formData.description,
              backup_type: 'full' as any,
              include_files: formData.includeDocuments,
            }
          });
          showSnackbar('Backup created successfully!');
          loadBackups(); // Reload backups list
          break;
          
        case 'plugin':
          try {
            // Install plugin using the plugins API
            await chatterSDK.plugins.installPluginApiV1PluginsInstallPost({
              pluginInstallRequest: {
                plugin_path: formData.pluginUrl,
                enable_on_install: true,
              }
            });
            showSnackbar('Plugin installation started successfully!');
            loadPlugins(); // Reload plugins list
          } catch (pluginError: any) {
            throw new Error(pluginError.response?.data?.detail || 'Failed to install plugin');
          }
          break;
          
        case 'job':
          try {
            // Create job using the jobs API
            const jobCreateRequest: JobCreateRequest = {
              name: formData.jobName,
              function_name: formData.jobFunction,
              args: formData.jobArgs ? JSON.parse(formData.jobArgs) : [],
              kwargs: formData.jobKwargs ? JSON.parse(formData.jobKwargs) : {},
              priority: formData.jobPriority as JobPriority,
              max_retries: formData.maxRetries,
              schedule_at: formData.scheduleAt ? new Date(formData.scheduleAt).toISOString() : undefined,
            };
            
            await chatterSDK.jobs.createJobApiV1JobsPost({ jobCreateRequest });
            showSnackbar('Job created successfully!');
            addNotification({
              title: 'Job Created',
              message: `Job "${formData.jobName}" has been created and ${formData.scheduleAt ? 'scheduled' : 'queued for execution'}`,
              type: 'success'
            });
            loadJobs(); // Reload jobs list
            loadJobStats(); // Reload job stats
          } catch (jobError: any) {
            throw new Error(jobError.response?.data?.detail || 'Failed to create job');
          }
          break;
      }
      
      setDialogOpen(false);
      
      // Reset form
      setFormData({
        userId: '',
        email: '',
        password: '',
        role: 'user',
        serverName: '',
        serverUrl: '',
        description: '',
        backupName: '',
        includeUserData: true,
        includeDocuments: true,
        includeConfigurations: true,
        pluginUrl: '',
        // Job-specific fields
        jobName: '',
        jobFunction: '',
        jobPriority: 'normal' as const,
        jobArgs: '',
        jobKwargs: '',
        scheduleAt: '',
        maxRetries: 3,
      });
      
    } catch (error: any) {
      console.error('Error submitting form:', error);
      setError(error.response?.data?.detail || error.message || 'An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAction = async (type: string, id: string) => {
    if (window.confirm(`Are you sure you want to delete this ${type}?`)) {
      try {
        setLoading(true);
        setError('');
        
        switch (type) {
          case 'user':
            // Note: There might not be a user deletion API in the current SDK
            // This would typically require admin privileges
            showSnackbar('User deletion functionality requires implementation of admin user management API');
            break;
            
          case 'tool server':
            await chatterSDK.toolServers.deleteToolServerApiV1ToolserversServersServerIdDelete({
              serverId: id
            });
            showSnackbar('Tool server deleted successfully!');
            break;
            
          case 'backup':
            // Real backup deletion - this endpoint might not exist yet, so we'll provide better feedback
            try {
              // Assuming there might be a delete endpoint in the future
              showSnackbar('Backup deletion is not yet supported by the API');
            } catch (backupError: any) {
              showSnackbar('Backup deletion functionality not yet available');
            }
            break;
            
          case 'plugin':
            try {
              await chatterSDK.plugins.uninstallPluginApiV1PluginsPluginIdDelete({
                pluginId: id
              });
              showSnackbar('Plugin uninstalled successfully!');
              loadPlugins(); // Reload plugins list
            } catch (pluginError: any) {
              throw new Error(pluginError.response?.data?.detail || 'Failed to uninstall plugin');
            }
            break;
            
          case 'job':
            try {
              await chatterSDK.jobs.cancelJobApiV1JobsJobIdCancelPost({ jobId: id });
              showSnackbar('Job cancelled successfully!');
              loadJobs(); // Reload jobs list
              loadJobStats(); // Reload job stats
            } catch (jobError: any) {
              throw new Error(jobError.response?.data?.detail || 'Failed to cancel job');
            }
            break;
        }
      } catch (error: any) {
        console.error(`Error deleting ${type}:`, error);
        setError(error.response?.data?.detail || error.message || `Failed to delete ${type}`);
      } finally {
        setLoading(false);
      }
    }
  };

  const handleEditAction = async (type: string, id: string) => {
    try {
      setLoading(true);
      setError('');
      
      switch (type) {
        case 'user':
          showSnackbar('User editing functionality requires implementation of admin user management API');
          break;
          
        case 'tool server':
          // For editing, we would typically fetch the current data and populate the form
          // then call updateToolServerApiV1ToolserversServersServerIdPut
          showSnackbar('Tool server editing functionality would open edit dialog with current data');
          break;
          
        case 'backup':
          showSnackbar('Backup editing functionality would be implemented with backup management API');
          break;
          
        case 'plugin':
          showSnackbar('Plugin editing functionality would be implemented based on plugin architecture');
          break;
      }
    } catch (error: any) {
      console.error(`Error editing ${type}:`, error);
      setError(error.response?.data?.detail || error.message || `Failed to edit ${type}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 3, fontWeight: 'bold' }}>
        Administration Dashboard
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Notifications Panel */}
      {notifications.length > 0 && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
            <NotificationsIcon sx={{ mr: 1 }} />
            Recent Notifications ({notifications.length})
          </Typography>
          <List sx={{ maxHeight: 200, overflow: 'auto' }}>
            {notifications.map((notification) => (
              <ListItem key={notification.id} sx={{ bgcolor: 'background.paper', mb: 1, borderRadius: 1 }}>
                <ListItemText
                  primary={notification.title}
                  secondary={`${notification.message} • ${format(notification.timestamp, 'PPp')}`}
                />
                <Chip 
                  label={notification.type} 
                  color={notification.type === 'success' ? 'success' : 
                         notification.type === 'error' ? 'error' : 
                         notification.type === 'warning' ? 'warning' : 'info'} 
                  size="small" 
                  sx={{ mr: 1 }}
                />
                <IconButton 
                  size="small" 
                  onClick={() => removeNotification(notification.id)}
                  title="Dismiss"
                >
                  <CloseIcon fontSize="small" />
                </IconButton>
              </ListItem>
            ))}
          </List>
        </Box>
      )}

      <Alert severity="info" sx={{ mb: 3 }}>
        Manage system components, users, and configurations from this central dashboard.
      </Alert>

      {/* Backups Section */}
      <Accordion expanded={expanded === 'backups'} onChange={handleChange('backups')}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <BackupIcon sx={{ mr: 2 }} />
          <Typography variant="h6">Backups</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Box sx={{ mb: 2 }}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={6}>
                <Button
                  variant="contained"
                  startIcon={<BackupIcon />}
                  onClick={() => openDialog('backup')}
                  sx={{ mr: 1 }}
                >
                  Create Backup
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<UploadIcon />}
                >
                  Restore Backup
                </Button>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="Automatic Backups"
                />
              </Grid>
            </Grid>
          </Box>
          <List>
            {dataLoading ? (
              <ListItem>
                <CircularProgress size={20} sx={{ mr: 2 }} />
                <ListItemText primary="Loading backups..." />
              </ListItem>
            ) : backups.length === 0 ? (
              <ListItem>
                <ListItemText 
                  primary="No backups found" 
                  secondary="Create your first backup to get started"
                />
              </ListItem>
            ) : (
              backups.map((backup) => (
                <ListItem key={backup.id}>
                  <ListItemText
                    primary={backup.name || `Backup ${backup.id?.substring(0, 8)}`}
                    secondary={`Type: ${backup.backup_type} | Status: ${backup.status} | Created: ${backup.created_at ? format(new Date(backup.created_at), 'PPp') : 'Unknown'}`}
                  />
                  <ListItemSecondaryAction>
                    <IconButton 
                      edge="end" 
                      onClick={() => handleBackupDownload(backup.id)}
                      disabled={backup.status !== 'completed'}
                    >
                      <DownloadIcon />
                    </IconButton>
                    <IconButton edge="end" onClick={() => handleDeleteAction('backup', backup.id)}>
                      <DeleteIcon />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))
            )}
          </List>
        </AccordionDetails>
      </Accordion>

      {/* Jobs Section */}
      <Accordion expanded={expanded === 'jobs'} onChange={handleChange('jobs')}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <JobIcon sx={{ mr: 2 }} />
          <Typography variant="h6">Background Jobs</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Box sx={{ mb: 2 }}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={6}>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => openDialog('job')}
                  sx={{ mr: 1 }}
                >
                  Create Job
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<SettingsIcon />}
                  onClick={loadJobs}
                >
                  Refresh
                </Button>
              </Grid>
              <Grid item xs={12} sm={6}>
                {jobStats && (
                  <Box sx={{ textAlign: 'right' }}>
                    <Typography variant="body2" color="text.secondary">
                      Total: {jobStats.total_jobs} | Pending: {jobStats.pending_jobs} | Running: {jobStats.running_jobs}
                    </Typography>
                  </Box>
                )}
              </Grid>
            </Grid>
          </Box>
          <List>
            {dataLoading ? (
              <ListItem>
                <CircularProgress size={20} sx={{ mr: 2 }} />
                <ListItemText primary="Loading jobs..." />
              </ListItem>
            ) : jobs.length === 0 ? (
              <ListItem>
                <ListItemText 
                  primary="No jobs found" 
                  secondary="Create your first job to get started"
                />
              </ListItem>
            ) : (
              jobs.map((job) => {
                const getStatusColor = (status: JobStatus) => {
                  switch (status) {
                    case 'running': return 'success';
                    case 'pending': return 'warning';
                    case 'completed': return 'info';
                    case 'failed': return 'error';
                    case 'cancelled': return 'default';
                    default: return 'default';
                  }
                };

                const getSecondaryText = () => {
                  const parts = [];
                  if (job.function_name) parts.push(`Function: ${job.function_name}`);
                  if (job.priority) parts.push(`Priority: ${job.priority}`);
                  if (job.progress !== undefined) parts.push(`Progress: ${job.progress}%`);
                  if (job.created_at) parts.push(`Created: ${format(new Date(job.created_at), 'PPp')}`);
                  return parts.join(' | ');
                };

                return (
                  <ListItem key={job.id}>
                    <ListItemText
                      primary={job.name || `Job ${job.id.substring(0, 8)}`}
                      secondary={getSecondaryText()}
                    />
                    <Chip 
                      label={job.status} 
                      color={getStatusColor(job.status)} 
                      size="small" 
                      sx={{ mr: 1 }}
                    />
                    <ListItemSecondaryAction>
                      {(job.status === 'pending' || job.status === 'running') && (
                        <IconButton 
                          edge="end" 
                          onClick={() => handleJobAction('cancel', job.id)}
                          title="Cancel Job"
                        >
                          <DeleteIcon />
                        </IconButton>
                      )}
                    </ListItemSecondaryAction>
                  </ListItem>
                );
              })
            )}
          </List>
        </AccordionDetails>
      </Accordion>

      {/* Plugins Section */}
      <Accordion expanded={expanded === 'plugins'} onChange={handleChange('plugins')}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <PluginIcon sx={{ mr: 2 }} />
          <Typography variant="h6">Plugins</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Box sx={{ mb: 2 }}>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => openDialog('plugin')}
            >
              Install Plugin
            </Button>
          </Box>
          <List>
            {plugins.length === 0 ? (
              <ListItem>
                <ListItemText 
                  primary="No plugins installed" 
                  secondary="Install plugins to extend functionality"
                />
              </ListItem>
            ) : (
              plugins.map((plugin) => (
                <ListItem key={plugin.id}>
                  <ListItemIcon>
                    <PluginIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary={plugin.name || 'Unknown Plugin'}
                    secondary={`Version ${plugin.version || 'Unknown'} | ${plugin.enabled ? 'Enabled' : 'Disabled'} | ${plugin.description || 'No description'}`}
                  />
                  <ListItemSecondaryAction>
                    <Switch 
                      checked={plugin.enabled || false}
                      onChange={(e) => handlePluginToggle(plugin.id, e.target.checked)}
                    />
                    <IconButton edge="end">
                      <SettingsIcon />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))
            )}
          </List>
        </AccordionDetails>
      </Accordion>

      {/* Users Section */}
      <Accordion expanded={expanded === 'users'} onChange={handleChange('users')}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <UsersIcon sx={{ mr: 2 }} />
          <Typography variant="h6">User Management</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Box sx={{ mb: 2 }}>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => openDialog('user')}
            >
              Add User
            </Button>
          </Box>
          <List>
            <ListItem>
              <ListItemText
                primary="admin@chatter.ai"
                secondary="Role: Administrator | Last login: 2 hours ago | Status: Active"
              />
              <ListItemSecondaryAction>
                <IconButton edge="end" onClick={() => handleEditAction('user', 'admin@chatter.ai')}>
                  <EditIcon />
                </IconButton>
                <IconButton edge="end" onClick={() => handleDeleteAction('user', 'admin@chatter.ai')}>
                  <DeleteIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
            <ListItem>
              <ListItemText
                primary="user@example.com"
                secondary="Role: User | Last login: 1 day ago | Status: Active"
              />
              <ListItemSecondaryAction>
                <IconButton edge="end" onClick={() => handleEditAction('user', 'user@example.com')}>
                  <EditIcon />
                </IconButton>
                <IconButton edge="end" onClick={() => handleDeleteAction('user', 'user@example.com')}>
                  <DeleteIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          </List>
        </AccordionDetails>
      </Accordion>

      {/* Tools Section */}
      <Accordion expanded={expanded === 'tools'} onChange={handleChange('tools')}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <ToolsIcon sx={{ mr: 2 }} />
          <Typography variant="h6">Tool Servers</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Box sx={{ mb: 2 }}>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => openDialog('tool')}
            >
              Add Tool Server
            </Button>
          </Box>
          <List>
            <ListItem>
              <ListItemText
                primary="File Operations Server"
                secondary="URL: http://localhost:3000 | Status: Connected | Tools: 8"
              />
              <Chip label="Connected" color="success" size="small" sx={{ mr: 1 }} />
              <ListItemSecondaryAction>
                <IconButton edge="end" sx={{ mr: 1 }} onClick={() => handleEditAction('tool-server', 'file-ops')}>
                  <SettingsIcon />
                </IconButton>
                <IconButton edge="end" onClick={() => handleDeleteAction('tool-server', 'file-ops')}>
                  <DeleteIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
            <ListItem>
              <ListItemText
                primary="Web Search Server"
                secondary="URL: http://localhost:3001 | Status: Disconnected | Tools: 4"
              />
              <Chip label="Disconnected" color="error" size="small" sx={{ mr: 1 }} />
              <ListItemSecondaryAction>
                <IconButton edge="end" sx={{ mr: 1 }} onClick={() => handleEditAction('tool-server', 'web-search')}>
                  <SettingsIcon />
                </IconButton>
                <IconButton edge="end" onClick={() => handleDeleteAction('tool-server', 'web-search')}>
                  <DeleteIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          </List>
        </AccordionDetails>
      </Accordion>

      {/* Generic Dialog for Adding/Editing */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {dialogType === 'user' && 'Add New User'}
          {dialogType === 'tool' && 'Add Tool Server'}
          {dialogType === 'backup' && 'Create Backup'}
          {dialogType === 'plugin' && 'Install Plugin'}
          {dialogType === 'job' && 'Create New Job'}
        </DialogTitle>
        <DialogContent>
          {dialogType === 'user' && (
            <Box sx={{ mt: 2 }}>
              <TextField
                fullWidth
                label="User ID"
                margin="normal"
                placeholder="username"
                helperText="Unique username for the user"
                value={formData.userId}
                onChange={(e) => handleFormChange('userId', e.target.value)}
              />
              <TextField
                fullWidth
                label="Email"
                margin="normal"
                type="email"
                placeholder="user@example.com"
                value={formData.email}
                onChange={(e) => handleFormChange('email', e.target.value)}
              />
              <TextField
                fullWidth
                label="Password"
                margin="normal"
                type="password"
                value={formData.password}
                onChange={(e) => handleFormChange('password', e.target.value)}
              />
              <TextField
                fullWidth
                label="Role"
                margin="normal"
                select
                SelectProps={{ native: true }}
                value={formData.role}
                onChange={(e) => handleFormChange('role', e.target.value)}
              >
                <option value="user">User</option>
                <option value="admin">Administrator</option>
              </TextField>
            </Box>
          )}
          {dialogType === 'tool' && (
            <Box sx={{ mt: 2 }}>
              <TextField
                fullWidth
                label="Server Name"
                margin="normal"
                placeholder="My Tool Server"
                value={formData.serverName}
                onChange={(e) => handleFormChange('serverName', e.target.value)}
              />
              <TextField
                fullWidth
                label="Server URL"
                margin="normal"
                placeholder="http://localhost:3000"
                value={formData.serverUrl}
                onChange={(e) => handleFormChange('serverUrl', e.target.value)}
              />
              <TextField
                fullWidth
                label="Description"
                margin="normal"
                multiline
                rows={3}
                placeholder="Description of the tool server capabilities"
                value={formData.description}
                onChange={(e) => handleFormChange('description', e.target.value)}
              />
            </Box>
          )}
          {dialogType === 'backup' && (
            <Box sx={{ mt: 2 }}>
              <TextField
                fullWidth
                label="Backup Name"
                margin="normal"
                placeholder="Manual Backup - 2024-01-15"
                value={formData.backupName}
                onChange={(e) => handleFormChange('backupName', e.target.value)}
              />
              <FormControlLabel
                control={
                  <Switch 
                    checked={formData.includeUserData}
                    onChange={(e) => handleFormChange('includeUserData', e.target.checked)}
                  />
                }
                label="Include user data"
              />
              <FormControlLabel
                control={
                  <Switch 
                    checked={formData.includeDocuments}
                    onChange={(e) => handleFormChange('includeDocuments', e.target.checked)}
                  />
                }
                label="Include documents"
              />
              <FormControlLabel
                control={
                  <Switch 
                    checked={formData.includeConfigurations}
                    onChange={(e) => handleFormChange('includeConfigurations', e.target.checked)}
                  />
                }
                label="Include configurations"
              />
            </Box>
          )}
          {dialogType === 'plugin' && (
            <Box sx={{ mt: 2 }}>
              <TextField
                fullWidth
                label="Plugin URL or File"
                margin="normal"
                placeholder="https://plugins.chatter.ai/awesome-plugin.zip"
                value={formData.pluginUrl}
                onChange={(e) => handleFormChange('pluginUrl', e.target.value)}
              />
              <Typography variant="body2" sx={{ mt: 2, mb: 1 }}>
                Or upload plugin file:
              </Typography>
              <Button variant="outlined" component="label">
                Choose File
                <input type="file" hidden accept=".zip,.tar.gz" />
              </Button>
            </Box>
          )}

          {dialogType === 'job' && (
            <Box sx={{ mt: 2 }}>
              <TextField
                fullWidth
                label="Job Name"
                margin="normal"
                placeholder="Document Processing Job"
                required
                value={formData.jobName}
                onChange={(e) => handleFormChange('jobName', e.target.value)}
              />
              <TextField
                fullWidth
                label="Function Name"
                margin="normal"
                placeholder="document_processing"
                required
                helperText="Available functions: document_processing, conversation_summarization, vector_store_maintenance, data_export, data_backup"
                value={formData.jobFunction}
                onChange={(e) => handleFormChange('jobFunction', e.target.value)}
              />
              <TextField
                fullWidth
                select
                label="Priority"
                margin="normal"
                value={formData.jobPriority}
                onChange={(e) => handleFormChange('jobPriority', e.target.value)}
                SelectProps={{ native: true }}
              >
                <option value="low">Low</option>
                <option value="normal">Normal</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </TextField>
              <TextField
                fullWidth
                label="Arguments (JSON Array)"
                margin="normal"
                placeholder='["arg1", "arg2"]'
                multiline
                rows={2}
                helperText="Arguments as JSON array, e.g., ['document_id', 'extract_text']"
                value={formData.jobArgs}
                onChange={(e) => handleFormChange('jobArgs', e.target.value)}
              />
              <TextField
                fullWidth
                label="Keyword Arguments (JSON Object)"
                margin="normal"
                placeholder='{"key": "value"}'
                multiline
                rows={2}
                helperText="Keyword arguments as JSON object, e.g., {'timeout': 3600}"
                value={formData.jobKwargs}
                onChange={(e) => handleFormChange('jobKwargs', e.target.value)}
              />
              <TextField
                fullWidth
                label="Schedule At (Optional)"
                margin="normal"
                type="datetime-local"
                helperText="Leave empty to run immediately, or schedule for later"
                value={formData.scheduleAt}
                onChange={(e) => handleFormChange('scheduleAt', e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
              <TextField
                fullWidth
                label="Max Retries"
                margin="normal"
                type="number"
                value={formData.maxRetries}
                onChange={(e) => handleFormChange('maxRetries', parseInt(e.target.value) || 0)}
                inputProps={{ min: 0, max: 10 }}
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)} disabled={loading}>
            Cancel
          </Button>
          <Button variant="contained" onClick={handleSubmit} disabled={loading}>
            {loading ? 'Processing...' : (dialogType === 'backup' ? 'Create' : 'Add')}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Success/Info Snackbar */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={() => setSnackbarOpen(false)}
        message={snackbarMessage}
      />
    </Box>
  );
};

export default AdministrationPage;