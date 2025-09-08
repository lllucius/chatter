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
  Tabs,
  Tab,
  Menu,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import {
  Backup as BackupIcon,
  Work as JobIcon,
  Extension as PluginIcon,
  People as UsersIcon,
  Build as ToolsIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Download as DownloadIcon,
  Upload as UploadIcon,
  Settings as SettingsIcon,
  Notifications as NotificationsIcon,
  Close as CloseIcon,
  Refresh as RefreshIcon,
  MoreVert as MoreVertIcon,
  Edit as EditIcon,
  DeleteSweep as BulkDeleteIcon,
} from '@mui/icons-material';
import { chatterClient } from '../sdk/client';
import { BackupResponse, PluginResponse, JobResponse, JobCreateRequest, JobStatus, JobPriority, JobStatsResponse } from '../sdk';
import { useSSE } from '../services/sse-context';
import { toastService } from '../services/toast-service';
import CustomScrollbar from '../components/CustomScrollbar';
import PageLayout from '../components/PageLayout';

const AdministrationPage: React.FC = () => {
  const { isConnected, on } = useSSE();
  
  const [activeTab, setActiveTab] = useState<'backups' | 'jobs' | 'plugins' | 'users' | 'bulk'>('backups');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogType, setDialogType] = useState<'user' | 'backup' | 'plugin' | 'job'>('user');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // More options menu state
  const [actionAnchorEl, setActionAnchorEl] = useState<HTMLElement | null>(null);
  const [actionUser, setActionUser] = useState<any>(null);
  
  // User settings dialog state
  const [userSettingsOpen, setUserSettingsOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<any>(null);
  
  const [backups, setBackups] = useState<BackupResponse[]>([]);
  const [plugins, setPlugins] = useState<PluginResponse[]>([]);
  const [jobs, setJobs] = useState<JobResponse[]>([]);
  const [jobStats, setJobStats] = useState<JobStatsResponse | null>(null);
  const [dataLoading, setDataLoading] = useState(false);
  
  // Mock user data - in real app this would come from API
  const [users] = useState([
    {
      id: 'admin@chatter.ai',
      email: 'admin@chatter.ai',
      role: 'Administrator',
      lastLogin: '2 hours ago',
      status: 'Active',
      name: 'Admin User',
      isActive: true
    },
    {
      id: 'user@example.com',
      email: 'user@example.com',
      role: 'User',
      lastLogin: '1 day ago',
      status: 'Active',
      name: 'Regular User',
      isActive: true
    }
  ]);

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
    description: '',
    backupName: '',
    includeUserData: true,
    includeDocuments: true,
    includeConfigurations: true,
    pluginUrl: '',
    jobName: '',
    jobFunction: '',
    jobPriority: 'normal' as const,
    jobArgs: '',
    jobKwargs: '',
    scheduleAt: '',
    maxRetries: 3,
  });

  // Bulk operations state
  const [bulkOperationData, setBulkOperationData] = useState({
    operationType: 'conversations' as 'conversations' | 'documents' | 'prompts',
    filters: {
      olderThan: '',
      userId: '',
      status: '',
    },
    dryRun: true,
  });

  const addNotification = useCallback((notification: Omit<typeof notifications[0], 'id' | 'timestamp'>) => {
    const newNotification = {
      ...notification,
      id: Math.random().toString(36).substr(2, 9),
      timestamp: new Date(),
    };
    setNotifications(prev => [newNotification, ...prev.slice(0, 9)]);
  }, []);

  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  const loadJobs = useCallback(async () => {
    try {
      setDataLoading(true);
      const response = await chatterClient.jobs.listJobsApiV1JobsGet({});
      const newJobs = response.jobs || [];
      newJobs.forEach(job => {
        const previousState = lastJobStates.get(job.id);
        if (previousState && previousState !== job.status) {
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
      const newStates = new Map<string, JobStatus>();
      newJobs.forEach(job => newStates.set(job.id, job.status));
      setLastJobStates(newStates);
      setJobs(newJobs);
    } catch (error: any) {
      // eslint-disable-next-line no-console
      console.error('Failed to load jobs:', error);
      setError('Failed to load jobs');
    } finally {
      setDataLoading(false);
    }
  }, [lastJobStates, addNotification]);

  const loadJobStats = useCallback(async () => {
    try {
      const response = await chatterClient.jobs.getJobStatsApiV1JobsStatsOverviewGet();
      setJobStats(response.data);
    } catch (error: any) {
      console.error('Failed to load job stats:', error);
    }
  }, []);

  const loadBackups = useCallback(async () => {
    try {
      setDataLoading(true);
      const response = await chatterClient.dataManagement.listBackupsApiV1DataBackupsGet({});
      const items = response.backups || [];
      setBackups(items);
    } catch (error: any) {
      console.error('Failed to load backups:', error);
      setError('Failed to load backups');
    } finally {
      setDataLoading(false);
    }
  }, []);

  const loadPlugins = useCallback(async () => {
    try {
      const response = await chatterClient.plugins.listPluginsApiV1PluginsGet({});
      setPlugins(response.plugins || []);
    } catch (error: any) {
      console.error('Failed to load plugins:', error);
    }
  }, []);

  useEffect(() => {
    loadBackups();
    loadPlugins();
    loadJobs();
    loadJobStats();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!isConnected) return;

    const unsubscribeJobStarted = on('job.started', (event) => {
      addNotification({
        title: 'Job Started',
        message: `Job "${(event as any).data.job_name || (event as any).data.job_id}" has started`,
        type: 'info',
        jobId: (event as any).data.job_id
      });
      loadJobs();
      loadJobStats();
    });

    const unsubscribeJobCompleted = on('job.completed', (event) => {
      addNotification({
        title: 'Job Completed',
        message: `Job "${(event as any).data.job_name || (event as any).data.job_id}" completed successfully`,
        type: 'success',
        jobId: (event as any).data.job_id
      });
      loadJobs();
      loadJobStats();
    });

    const unsubscribeJobFailed = on('job.failed', (event) => {
      addNotification({
        title: 'Job Failed',
        message: `Job "${(event as any).data.job_name || (event as any).data.job_id}" failed: ${(event as any).data.error}`,
        type: 'error',
        jobId: (event as any).data.job_id
      });
      loadJobs();
      loadJobStats();
    });

    const unsubscribeBackupStarted = on('backup.started', (event) => {
      addNotification({
        title: 'Backup Started',
        message: `Backup "${(event as any).data.backup_id}" has started`,
        type: 'info'
      });
      loadBackups();
    });

    const unsubscribeBackupCompleted = on('backup.completed', (event) => {
      addNotification({
        title: 'Backup Completed',
        message: `Backup "${(event as any).data.backup_id}" completed successfully`,
        type: 'success'
      });
      loadBackups();
    });

    const unsubscribeBackupFailed = on('backup.failed', (event) => {
      addNotification({
        title: 'Backup Failed',
        message: `Backup "${(event as any).data.backup_id}" failed: ${(event as any).data.error}`,
        type: 'error'
      });
      loadBackups();
    });

    return () => {
      unsubscribeJobStarted();
      unsubscribeJobCompleted();
      unsubscribeJobFailed();
      unsubscribeBackupStarted();
      unsubscribeBackupCompleted();
      unsubscribeBackupFailed();
    };
  }, [isConnected, on, addNotification, loadJobs, loadJobStats, loadBackups]);

  const handleJobAction = async (action: 'cancel', jobId: string) => {
    try {
      setLoading(true);
      setError('');
      switch (action) {
        case 'cancel':
          await chatterClient.jobs.cancelJobApiV1JobsJobIdCancelPost({ jobId });
          console.log('Job cancelled successfully!');
          loadJobs();
          loadJobStats();
          break;
      }
    } catch (error: any) {
      console.error(`Error ${action} job:`, error);
      const errorMsg = error.response?.data?.detail || error.message || `Failed to ${action} job`;
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const showToast = (messageOrError: string | any, type: 'success' | 'error' | 'info' | 'warning' = 'info', fallback?: string) => {
    switch (type) {
      case 'success':
        toastService.success(messageOrError);
        break;
      case 'error':
        toastService.error(messageOrError, fallback);
        break;
      case 'warning':
        toastService.warning(messageOrError, fallback);
        break;
      default:
        toastService.info(messageOrError);
    }
  };

  // Bulk operations functions
  const performBulkOperation = async () => {
    try {
      setLoading(true);
      setError('');
      
      const filters: any = {};
      
      // Build filters based on form data
      if (bulkOperationData.filters.olderThan) {
        filters.created_before = bulkOperationData.filters.olderThan;
      }
      if (bulkOperationData.filters.userId) {
        filters.user_id = bulkOperationData.filters.userId;
      }
      if (bulkOperationData.filters.status) {
        filters.status = bulkOperationData.filters.status;
      }

      let result;
      switch (bulkOperationData.operationType) {
        case 'conversations':
          result = await chatterClient.dataManagement.bulkDeleteConversationsApiV1DataBulkDeleteConversationsPost(
            { 
              filters,
              dry_run: bulkOperationData.dryRun
            }
          );
          break;
        case 'documents':
          result = await chatterClient.dataManagement.bulkDeleteDocumentsApiV1DataBulkDeleteDocumentsPost(
            { 
              filters,
              dry_run: bulkOperationData.dryRun
            }
          );
          break;
        case 'prompts':
          result = await chatterClient.dataManagement.bulkDeletePromptsApiV1DataBulkDeletePromptsPost(
            { 
              filters,
              dry_run: bulkOperationData.dryRun
            }
          );
          break;
      }

      const operation = bulkOperationData.dryRun ? 'Preview' : 'Deleted';
      showToast(
        `${operation}: ${result?.data.affected_count || 0} ${bulkOperationData.operationType}`, 
        bulkOperationData.dryRun ? 'info' : 'success'
      );

      addNotification({
        title: 'Bulk Operation Complete',
        message: `${operation} ${result?.data.affected_count || 0} ${bulkOperationData.operationType}`,
        type: bulkOperationData.dryRun ? 'info' : 'success'
      });

    } catch (error: any) {
      console.error('Bulk operation failed:', error);
      setError(error.response?.data?.detail || error.message || 'Bulk operation failed');
      showToast(error, 'error', 'Bulk operation failed');
    } finally {
      setLoading(false);
    }
  };

  const openUserActionsMenu = (e: React.MouseEvent<HTMLElement>, user: any) => {
    setActionAnchorEl(e.currentTarget);
    setActionUser(user);
  };

  const closeActionsMenu = () => {
    setActionAnchorEl(null);
    setActionUser(null);
  };

  const handleUserSettings = (user: any) => {
    setEditingUser(user);
    setUserSettingsOpen(true);
    closeActionsMenu();
  };

  const handleUserSettingsSave = async () => {
    try {
      // In a real app, this would call the API to update the user
      showToast('User settings updated successfully!', 'success');
      setUserSettingsOpen(false);
      setEditingUser(null);
    } catch (error: any) {
      showToast(error, 'error', 'Failed to update user settings');
    }
  };

  const handleBackupDownload = async () => {
    try {
      setLoading(true);
      showToast('Backup download functionality will be available soon', 'info');
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
        await chatterClient.plugins.enablePluginApiV1PluginsPluginIdEnablePost({ pluginId });
        showToast('Plugin enabled successfully', 'success');
      } else {
        await chatterClient.plugins.disablePluginApiV1PluginsPluginIdDisablePost({ pluginId });
        showToast('Plugin disabled successfully', 'success');
      }
      loadPlugins();
    } catch (error: any) {
      console.error('Error toggling plugin:', error);
      setError('Failed to toggle plugin status');
    }
  };

  const openDialog = (type: 'user' | 'backup' | 'plugin' | 'job') => {
    setDialogType(type);
    setDialogOpen(true);
    setError('');
    setFormData({
      userId: '',
      email: '',
      password: '',
      role: 'user',
      description: '',
      backupName: '',
      includeUserData: true,
      includeDocuments: true,
      includeConfigurations: true,
      pluginUrl: '',
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
          await chatterClient.auth.registerApiV1AuthRegisterPost({
            userCreate: {
              username: formData.userId,
              email: formData.email,
              password: formData.password,
            }
          });
          showToast('User created successfully!', 'success');
          break;
        case 'backup':
          await chatterClient.dataManagement.createBackupApiV1DataBackupPost({
            backupRequest: {
              name: formData.backupName,
              description: formData.description,
              backup_type: 'full' as any,
              include_files: formData.includeDocuments,
            }
          });
          showToast('Backup created successfully!', 'success');
          loadBackups();
          break;
        case 'plugin':
          await chatterClient.plugins.installPluginApiV1PluginsInstallPost({
            pluginInstallRequest: {
              plugin_path: formData.pluginUrl,
              enable_on_install: true,
            }
          });
          showToast('Plugin installation started successfully!', 'success');
          loadPlugins();
          break;
        case 'job':
          {
            const jobCreateRequest: JobCreateRequest = {
              name: formData.jobName,
              function_name: formData.jobFunction,
              args: formData.jobArgs ? JSON.parse(formData.jobArgs) : [],
              kwargs: formData.jobKwargs ? JSON.parse(formData.jobKwargs) : {},
              priority: formData.jobPriority as JobPriority,
              max_retries: formData.maxRetries,
              schedule_at: formData.scheduleAt ? new Date(formData.scheduleAt).toISOString() : undefined,
            };
            await chatterClient.jobs.createJobApiV1JobsPost({ jobCreateRequest });
            showToast('Job created successfully!', 'success');
            addNotification({
              title: 'Job Created',
              message: `Job "${formData.jobName}" has been created and ${formData.scheduleAt ? 'scheduled' : 'queued for execution'}`,
              type: 'success'
            });
            loadJobs();
            loadJobStats();
          }
          break;
      }
      setDialogOpen(false);
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
      const errorMsg = error.response?.data?.detail || error.message || 'An error occurred. Please try again.';
      setError(errorMsg);
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
            showToast('User deletion functionality requires implementation of admin user management API', 'warning');
            break;
          case 'backup':
            showToast('Backup deletion is not yet supported by the API', 'warning');
            break;
          case 'plugin':
            await chatterClient.plugins.uninstallPluginApiV1PluginsPluginIdDelete({
              pluginId: id
            });
            showToast('Plugin uninstalled successfully!', 'success');
            loadPlugins();
            break;
          case 'job':
            await chatterClient.jobs.cancelJobApiV1JobsJobIdCancelPost({ jobId: id });
            showToast('Job cancelled successfully!', 'success');
            loadJobs();
            loadJobStats();
            break;
        }
      } catch (error: any) {
        console.error(`Error deleting ${type}:`, error);
        const errorMsg = error.response?.data?.detail || error.message || `Failed to delete ${type}`;
        setError(errorMsg);
      } finally {
        setLoading(false);
      }
    }
  };

  const handleEditAction = async (type: string) => {
    try {
      setLoading(true);
      setError('');
      switch (type) {
        case 'user':
          showToast('User editing functionality requires implementation of admin user management API', 'warning');
          break;
        case 'backup':
          showToast('Backup editing functionality would be implemented with backup management API', 'warning');
          break;
        case 'plugin':
          showToast('Plugin editing functionality would be implemented based on plugin architecture', 'warning');
          break;
      }
    } catch (error: any) {
      console.error(`Error editing ${type}:`, error);
      const errorMsg = error.response?.data?.detail || error.message || `Failed to edit ${type}`;
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const toolbar = (
    <Button
      variant="outlined"
      startIcon={<RefreshIcon />}
      onClick={() => {
        loadBackups();
        loadPlugins();
        loadJobs();
        loadJobStats();
      }}
      disabled={loading}
    >
      Refresh
    </Button>
  );

  return (
    <PageLayout title="Administration" toolbar={toolbar}>

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
          <Box sx={{ maxHeight: 200 }}>
            <CustomScrollbar>
              <List>
                {notifications.map((notification) => (
                  <ListItem key={notification.id} sx={{ bgcolor: 'background.paper', mb: 1, borderRadius: 1 }}>
                    <ListItemText
                      primary={notification.title}
                      secondary={`${notification.message} • ${new Date(notification.timestamp).toLocaleString()}`}
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
            </CustomScrollbar>
          </Box>
        </Box>
      )}

      <Tabs
        value={activeTab}
        onChange={(_, v) => setActiveTab(v)}
        variant="scrollable"
        scrollButtons="auto"
        sx={{ mb: 2 }}
      >
        <Tab value="backups" icon={<BackupIcon />} iconPosition="start" label="Backups" />
        <Tab value="jobs" icon={<JobIcon />} iconPosition="start" label="Background Jobs" />
        <Tab value="plugins" icon={<PluginIcon />} iconPosition="start" label="Plugins" />
        <Tab value="users" icon={<UsersIcon />} iconPosition="start" label="User Management" />
        <Tab value="bulk" icon={<BulkDeleteIcon />} iconPosition="start" label="Bulk Operations" />
      </Tabs>

      {/* Backups Tab */}
      {activeTab === 'backups' && (
        <Box>
          <Box sx={{ mb: 2 }}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={8}>
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
                  sx={{ mr: 1 }}
                >
                  Restore Backup
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<SettingsIcon />}
                  onClick={loadBackups}
                >
                  Refresh
                </Button>
              </Grid>
              <Grid item xs={12} sm={4}>
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
                    secondary={`Type: ${backup.backup_type} | Status: ${backup.status} | Created: ${backup.created_at ? new Date(backup.created_at).toLocaleString() : 'Unknown'}`}
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
        </Box>
      )}

      {/* Jobs Tab */}
      {activeTab === 'jobs' && (
        <Box>
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
                  const parts: string[] = [];
                  if (job.function_name) parts.push(`Function: ${job.function_name}`);
                  if (job.priority) parts.push(`Priority: ${job.priority}`);
                  if (job.progress !== undefined) parts.push(`Progress: ${job.progress}%`);
                  if (job.created_at) parts.push(`Created: ${new Date(job.created_at).toLocaleString()}`);
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
        </Box>
      )}

      {/* Plugins Tab */}
      {activeTab === 'plugins' && (
        <Box>
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
                  <ListItemIcon />
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
        </Box>
      )}

      {/* Users Tab */}
      {activeTab === 'users' && (
        <Box>
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
            {users.map((user) => (
              <ListItem key={user.id}>
                <ListItemText
                  primary={user.email}
                  secondary={`Role: ${user.role} | Last login: ${user.lastLogin} | Status: ${user.status}`}
                />
                <ListItemSecondaryAction>
                  <IconButton edge="end" onClick={(e) => openUserActionsMenu(e, user)}>
                    <MoreVertIcon />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        </Box>
      )}

      {/* Bulk Operations Tab */}
      {activeTab === 'bulk' && (
        <Box>
          <Alert severity="warning" sx={{ mb: 3 }}>
            <strong>Warning:</strong> Bulk operations can delete large amounts of data permanently. Always test with "Dry Run" first.
          </Alert>
          
          <Box sx={{ mb: 3, p: 3, border: '1px solid #e0e0e0', borderRadius: 1 }}>
            <Typography variant="h6" gutterBottom>
              Bulk Delete Configuration
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Operation Type</InputLabel>
                  <Select
                    value={bulkOperationData.operationType}
                    label="Operation Type"
                    onChange={(e) => setBulkOperationData(prev => ({
                      ...prev,
                      operationType: e.target.value as any
                    }))}
                  >
                    <MenuItem value="conversations">Delete Conversations</MenuItem>
                    <MenuItem value="documents">Delete Documents</MenuItem>
                    <MenuItem value="prompts">Delete Prompts</MenuItem>
                  </Select>
                </FormControl>

                <TextField
                  fullWidth
                  label="Created Before (YYYY-MM-DD)"
                  type="date"
                  value={bulkOperationData.filters.olderThan}
                  onChange={(e) => setBulkOperationData(prev => ({
                    ...prev,
                    filters: { ...prev.filters, olderThan: e.target.value }
                  }))}
                  sx={{ mb: 2 }}
                  InputLabelProps={{ shrink: true }}
                />

                <TextField
                  fullWidth
                  label="User ID (optional)"
                  value={bulkOperationData.filters.userId}
                  onChange={(e) => setBulkOperationData(prev => ({
                    ...prev,
                    filters: { ...prev.filters, userId: e.target.value }
                  }))}
                  sx={{ mb: 2 }}
                />

                <FormControlLabel
                  control={
                    <Switch
                      checked={bulkOperationData.dryRun}
                      onChange={(e) => setBulkOperationData(prev => ({
                        ...prev,
                        dryRun: e.target.checked
                      }))}
                      color="warning"
                    />
                  }
                  label="Dry Run (Preview Only)"
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" gutterBottom>
                  Operation Summary
                </Typography>
                <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                  <Typography variant="body2" gutterBottom>
                    <strong>Type:</strong> {bulkOperationData.operationType}
                  </Typography>
                  <Typography variant="body2" gutterBottom>
                    <strong>Mode:</strong> {bulkOperationData.dryRun ? 'Preview (Safe)' : 'Delete (Permanent)'}
                  </Typography>
                  <Typography variant="body2" gutterBottom>
                    <strong>Filters:</strong>
                  </Typography>
                  <Box component="ul" sx={{ pl: 2, mt: 1 }}>
                    {bulkOperationData.filters.olderThan && (
                      <Typography component="li" variant="body2">
                        Created before: {bulkOperationData.filters.olderThan}
                      </Typography>
                    )}
                    {bulkOperationData.filters.userId && (
                      <Typography component="li" variant="body2">
                        User ID: {bulkOperationData.filters.userId}
                      </Typography>
                    )}
                    {!bulkOperationData.filters.olderThan && !bulkOperationData.filters.userId && (
                      <Typography component="li" variant="body2" color="text.secondary">
                        No filters applied (affects all data)
                      </Typography>
                    )}
                  </Box>
                </Box>
              </Grid>
            </Grid>

            <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                color={bulkOperationData.dryRun ? "info" : "error"}
                onClick={performBulkOperation}
                disabled={loading}
                startIcon={loading ? <CircularProgress size={20} /> : <BulkDeleteIcon />}
              >
                {loading ? 'Processing...' : bulkOperationData.dryRun ? 'Preview Changes' : 'Execute Delete'}
              </Button>
              
              <Button
                variant="outlined"
                onClick={() => setBulkOperationData(prev => ({
                  ...prev,
                  filters: { olderThan: '', userId: '', status: '' },
                  dryRun: true
                }))}
              >
                Reset Filters
              </Button>
            </Box>
          </Box>
        </Box>
      )}

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {dialogType === 'user' && 'Add New User'}
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

      {/* User Actions Menu */}
      <Menu
        anchorEl={actionAnchorEl}
        open={Boolean(actionAnchorEl) && Boolean(actionUser)}
        onClose={closeActionsMenu}
      >
        <MenuItem onClick={() => handleUserSettings(actionUser)}>
          <ListItemIcon>
            <SettingsIcon fontSize="small" />
          </ListItemIcon>
          Settings
        </MenuItem>
        <MenuItem onClick={() => {
          if (actionUser) handleDeleteAction('user', actionUser.id);
          closeActionsMenu();
        }}>
          <ListItemIcon>
            <DeleteIcon fontSize="small" />
          </ListItemIcon>
          Delete
        </MenuItem>
      </Menu>

      {/* User Settings Dialog */}
      <Dialog open={userSettingsOpen} onClose={() => setUserSettingsOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>User Settings - {editingUser?.email}</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <TextField
              fullWidth
              label="Name"
              value={editingUser?.name || ''}
              onChange={(e) => setEditingUser({...editingUser, name: e.target.value})}
              sx={{ mb: 2 }}
            />
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Role</InputLabel>
              <Select
                value={editingUser?.role || 'User'}
                label="Role"
                onChange={(e) => setEditingUser({...editingUser, role: e.target.value})}
              >
                <MenuItem value="User">User</MenuItem>
                <MenuItem value="Administrator">Administrator</MenuItem>
                <MenuItem value="Moderator">Moderator</MenuItem>
              </Select>
            </FormControl>
            <FormControlLabel
              control={
                <Switch
                  checked={editingUser?.isActive || false}
                  onChange={(e) => setEditingUser({...editingUser, isActive: e.target.checked})}
                />
              }
              label="Active"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUserSettingsOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleUserSettingsSave}>Save</Button>
        </DialogActions>
      </Dialog>
    </PageLayout>
  );
};

export default AdministrationPage;
