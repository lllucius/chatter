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
  Add as AddIcon,
  Delete as DeleteIcon,
  Download as DownloadIcon,
  Upload as UploadIcon,
  Settings as SettingsIcon,
  Refresh as RefreshIcon,
  MoreVert as MoreVertIcon,
  DeleteSweep as BulkDeleteIcon,
} from '@mui/icons-material';
import { getSDK } from '../services/auth-service';
import {
  BackupResponse,
  PluginResponse,
  JobResponse,
  JobCreateRequest,
  JobStatus,
  JobPriority,
  JobStatsResponse,
} from 'chatter-sdk';
import { useSSE } from '../services/sse-context';
import { toastService } from '../services/toast-service';
import { handleError } from '../utils/error-handler';
import PageLayout from '../components/PageLayout';
import { useNotifications } from '../components/NotificationSystem';

// SSE Event interfaces for type safety
interface JobSSEEventData {
  job_id: string;
  job_name?: string;
  error?: string;
}

interface BackupSSEEventData {
  backup_id: string;
  backup_name?: string;
  error?: string;
}

interface PluginSSEEventData {
  plugin_id: string;
  plugin_name?: string;
  error?: string;
}

interface SSEEvent {
  data: JobSSEEventData | BackupSSEEventData | PluginSSEEventData;
}

interface User {
  id: string;
  email: string;
  role: string;
  lastLogin: string;
  status: string;
  name: string;
  isActive: boolean;
}

const AdministrationPage: React.FC = () => {
  const { isConnected, on } = useSSE();
  const { showNotification } = useNotifications();

  const [activeTab, setActiveTab] = useState<
    'backups' | 'jobs' | 'plugins' | 'users' | 'bulk'
  >('backups');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogType, setDialogType] = useState<
    'user' | 'backup' | 'plugin' | 'job'
  >('user');
  const [loading, setLoading] = useState(false);

  // More options menu state
  const [actionAnchorEl, setActionAnchorEl] = useState<HTMLElement | null>(
    null
  );
  const [actionUser, setActionUser] = useState<User | null>(
    null
  );

  // User settings dialog state
  const [userSettingsOpen, setUserSettingsOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);

  const [backups, setBackups] = useState<BackupResponse[]>([]);
  const [plugins, setPlugins] = useState<PluginResponse[]>([]);
  const [jobs, setJobs] = useState<JobResponse[]>([]);
  const [jobStats, setJobStats] = useState<JobStatsResponse | null>(null);
  const [dataLoading, setDataLoading] = useState(false);

  // Mock user data - in real app this would come from API
  const [users] = useState<User[]>([
    {
      id: 'admin@chatter.ai',
      email: 'admin@chatter.ai',
      role: 'Administrator',
      lastLogin: '2 hours ago',
      status: 'Active',
      name: 'Admin User',
      isActive: true,
    },
    {
      id: 'user@example.com',
      email: 'user@example.com',
      role: 'User',
      lastLogin: '1 day ago',
      status: 'Active',
      name: 'Regular User',
      isActive: true,
    },
  ]);

  const [lastJobStates, setLastJobStates] = useState<Map<string, JobStatus>>(
    new Map()
  );

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

  const loadJobs = useCallback(async () => {
    try {
      setDataLoading(true);
      const response = await getSDK().jobs.listJobsApiV1Jobs(
        {},
        {
          limit: 100, // Load a reasonable amount for admin monitoring
          offset: 0,
        }
      );
      const newJobs = response.jobs || [];
      newJobs.forEach((job) => {
        const previousState = lastJobStates.get(job.id);
        if (previousState && previousState !== job.status) {
          showNotification({
            title: 'Job Status Update',
            message: `Job "${job.name || job.id.substring(0, 8)}" changed from ${previousState} to ${job.status}`,
            type:
              job.status === 'completed'
                ? 'success'
                : job.status === 'failed'
                  ? 'error'
                  : job.status === 'cancelled'
                    ? 'warning'
                    : 'info',
            category: 'system',
          });
        }
      });
      const newStates = new Map<string, JobStatus>();
      newJobs.forEach((job) => newStates.set(job.id, job.status));
      setLastJobStates(newStates);
      setJobs(newJobs);
    } catch (error: unknown) {
      handleError(error, {
        source: 'AdministrationPage.loadJobs',
        operation: 'load job data',
      });
    } finally {
      setDataLoading(false);
    }
  }, [lastJobStates, showNotification]);

  const loadJobStats = useCallback(async () => {
    try {
      const response = await getSDK().jobs.getJobStatsApiV1JobsStatsOverview();
      setJobStats(response.data);
    } catch (error: unknown) {
      handleError(error, {
        source: 'AdministrationPage.loadJobStats',
        operation: 'load job statistics',
      });
    }
  }, []);

  const loadBackups = useCallback(async () => {
    try {
      setDataLoading(true);
      const response =
        await getSDK().dataManagement.listBackupsApiV1DataBackups({});
      const items = response.backups || [];
      setBackups(items);
    } catch (error: unknown) {
      handleError(error, {
        source: 'AdministrationPage.loadBackups',
        operation: 'load backup data',
      });
    } finally {
      setDataLoading(false);
    }
  }, []);

  const loadPlugins = useCallback(async () => {
    try {
      const response = await getSDK().plugins.listPluginsApiV1Plugins({});
      setPlugins(response.plugins || []);
    } catch (error: unknown) {
      handleError(error, {
        source: 'AdministrationPage.loadPlugins',
        operation: 'load plugin data',
      });
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

    const unsubscribeJobStarted = on('job.started', (event: SSEEvent) => {
      const jobData = event.data as JobSSEEventData;
      showNotification({
        title: 'Job Started',
        message: `Job "${jobData.job_name || jobData.job_id}" has started`,
        type: 'info',
        category: 'system',
      });
      loadJobs();
      loadJobStats();
    });

    const unsubscribeJobCompleted = on('job.completed', (event: SSEEvent) => {
      const jobData = event.data as JobSSEEventData;
      showNotification({
        title: 'Job Completed',
        message: `Job "${jobData.job_name || jobData.job_id}" completed successfully`,
        type: 'success',
        category: 'system',
      });
      loadJobs();
      loadJobStats();
    });

    const unsubscribeJobFailed = on('job.failed', (event: SSEEvent) => {
      const jobData = event.data as JobSSEEventData;
      showNotification({
        title: 'Job Failed',
        message: `Job "${jobData.job_name || jobData.job_id}" failed: ${jobData.error}`,
        type: 'error',
        category: 'system',
      });
      loadJobs();
      loadJobStats();
    });

    const unsubscribeBackupStarted = on('backup.started', (event: SSEEvent) => {
      const backupData = event.data as BackupSSEEventData;
      showNotification({
        title: 'Backup Started',
        message: `Backup "${backupData.backup_id}" has started`,
        type: 'info',
        category: 'system',
      });
      loadBackups();
    });

    const unsubscribeBackupCompleted = on('backup.completed', (event: SSEEvent) => {
      const backupData = event.data as BackupSSEEventData;
      showNotification({
        title: 'Backup Completed',
        message: `Backup "${backupData.backup_id}" completed successfully`,
        type: 'success',
        category: 'system',
      });
      loadBackups();
    });

    const unsubscribeBackupFailed = on('backup.failed', (event: SSEEvent) => {
      const backupData = event.data as BackupSSEEventData;
      showNotification({
        title: 'Backup Failed',
        message: `Backup "${backupData.backup_id}" failed: ${backupData.error}`,
        type: 'error',
        category: 'system',
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
  }, [isConnected, on, showNotification, loadJobs, loadJobStats, loadBackups]);

  const handleJobAction = async (action: 'cancel', jobId: string) => {
    try {
      setLoading(true);
      switch (action) {
        case 'cancel':
          await getSDK().jobs.cancelJobApiV1JobsJobIdCancel(jobId);
          toastService.success('Job cancelled successfully!');
          loadJobs();
          loadJobStats();
          break;
      }
    } catch (error: unknown) {
      handleError(error, {
        source: 'AdministrationPage.handleJobAction',
        operation: `${action} job`,
        additionalData: { jobId, action },
      });
    } finally {
      setLoading(false);
    }
  };

  // Bulk operations functions
  const performBulkOperation = async () => {
    try {
      setLoading(true);

      const filters: Record<string, string | boolean> = {};

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

      // Use the new server-side bulk filtering API
      const entityTypeMap = {
        conversations: 'conversations',
        documents: 'documents',
        prompts: 'prompts',
      };

      const entityType = entityTypeMap[bulkOperationData.operationType];
      if (!entityType) {
        throw new Error(
          `Unsupported operation type: ${bulkOperationData.operationType}`
        );
      }

      // Build filters for the new API
      const apiFilters = {
        entity_type: entityType,
        created_before: bulkOperationData.filters.olderThan,
        created_after: null, // Could be added to the UI later
        user_id: bulkOperationData.filters.userId,
        status: bulkOperationData.filters.status,
        limit: 10000, // Increased limit since filtering happens server-side
        dry_run: bulkOperationData.dryRun,
      };

      if (bulkOperationData.dryRun) {
        // Use preview endpoint for dry run
        const previewResponse =
          await getSDK().dataManagement.previewBulkDeleteApiV1DataBulkPreview({
            filters: apiFilters,
          });

        result = {
          data: {
            total_requested: previewResponse.data.total_matching,
            successful_deletions: 0,
            failed_deletions: 0,
            errors: [],
            preview_data: previewResponse.data,
          },
        };
      } else {
        // Use server-side filtered bulk delete
        result =
          await getSDK().dataManagement.bulkDeleteWithFiltersApiV1DataBulkDeleteFiltered(
            {
              filters: apiFilters,
            }
          );
      }

      const operation = bulkOperationData.dryRun ? 'Preview' : 'Deleted';
      const affectedCount = bulkOperationData.dryRun
        ? result?.data.total_requested || 0
        : result?.data.successful_deletions || 0;

      toastService[bulkOperationData.dryRun ? 'info' : 'success'](
        `${operation}: ${affectedCount} ${bulkOperationData.operationType}`
      );

      showNotification({
        title: 'Bulk Operation Complete',
        message: `${operation} ${affectedCount} ${bulkOperationData.operationType}`,
        type: bulkOperationData.dryRun ? 'info' : 'success',
        category: 'system',
      });
    } catch (error: unknown) {
      handleError(error, {
        source: 'AdministrationPage.handleBulkAction',
        operation: 'bulk operation',
        additionalData: {
          operationType: bulkOperationData.operationType,
          dryRun: bulkOperationData.dryRun,
          filters: bulkOperationData.filters,
        },
      });
    } finally {
      setLoading(false);
    }
  };

  const openUserActionsMenu = (e: React.MouseEvent<HTMLElement>, user: User) => {
    setActionAnchorEl(e.currentTarget);
    setActionUser(user);
  };

  const closeActionsMenu = () => {
    setActionAnchorEl(null);
    setActionUser(null);
  };

  const handleUserSettings = (user: User) => {
    setEditingUser(user);
    setUserSettingsOpen(true);
    closeActionsMenu();
  };

  const handleUserSettingsSave = async () => {
    try {
      // In a real app, this would call the API to update the user
      toastService.success('User settings updated successfully!');
      setUserSettingsOpen(false);
      setEditingUser(null);
    } catch (error: unknown) {
      handleError(error, {
        source: 'AdministrationPage.handleUserSettingsSave',
        operation: 'update user settings',
        additionalData: { userId: editingUser?.id },
      });
    }
  };

  const handleBackupDownload = async () => {
    try {
      setLoading(true);
      toastService.info('Backup download functionality will be available soon');
    } catch (error: unknown) {
      handleError(error, {
        source: 'AdministrationPage.handleDownloadBackup',
        operation: 'download backup',
        additionalData: { backupId: backup?.id },
      });
    } finally {
      setLoading(false);
    }
  };

  const handlePluginToggle = async (pluginId: string, enabled: boolean) => {
    try {
      if (enabled) {
        await getSDK().plugins.enablePluginApiV1PluginsPluginIdEnable(pluginId);
        toastService.success('Plugin enabled successfully');
      } else {
        await getSDK().plugins.disablePluginApiV1PluginsPluginIdDisable(
          pluginId
        );
        toastService.success('Plugin disabled successfully');
      }
      loadPlugins();
    } catch (error: unknown) {
      handleError(error, {
        source: 'AdministrationPage.handleTogglePlugin',
        operation: 'toggle plugin status',
        additionalData: { pluginId: plugin.id, pluginName: plugin.name },
      });
    }
  };

  const openDialog = (type: 'user' | 'backup' | 'plugin' | 'job') => {
    setDialogType(type);
    setDialogOpen(true);
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

  const handleFormChange = (field: string, value: string | number | boolean) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      switch (dialogType) {
        case 'user':
          await getSDK().auth.authRegister({
            username: formData.userId,
            email: formData.email,
            password: formData.password,
          });
          toastService.success('User created successfully!');
          break;
        case 'backup':
          await getSDK().dataManagement.createBackupApiV1DataBackup({
            name: formData.backupName,
            description: formData.description,
            backup_type: 'full' as const,
            include_files: formData.includeDocuments,
          });
          toastService.success('Backup created successfully!');
          loadBackups();
          break;
        case 'plugin':
          await getSDK().plugins.installPluginApiV1PluginsInstall({
            plugin_path: formData.pluginUrl,
            enable_on_install: true,
          });
          toastService.success('Plugin installation started successfully!');
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
              schedule_at: formData.scheduleAt
                ? new Date(formData.scheduleAt).toISOString()
                : undefined,
            };
            await getSDK().jobs.createJobApiV1Jobs(jobCreateRequest);
            toastService.success('Job created successfully!');
            showNotification({
              title: 'Job Created',
              message: `Job "${formData.jobName}" has been created and ${formData.scheduleAt ? 'scheduled' : 'queued for execution'}`,
              type: 'success',
              category: 'system',
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
    } catch (error: unknown) {
      handleError(error, {
        source: 'AdministrationPage.handleCreateItem',
        operation: 'create item',
        additionalData: {
          type,
          formData: Object.keys(formData).reduce(
            (acc, key) => ({
              ...acc,
              [key]:
                typeof formData[key] === 'string'
                  ? formData[key].substring(0, 50)
                  : formData[key],
            }),
            {}
          ),
        },
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAction = async (type: string, id: string) => {
    if (window.confirm(`Are you sure you want to delete this ${type}?`)) {
      try {
        setLoading(true);
        switch (type) {
          case 'user':
            toastService.warning(
              'User deletion functionality requires implementation of admin user management API'
            );
            break;
          case 'backup':
            toastService.warning(
              'Backup deletion is not yet supported by the API'
            );
            break;
          case 'plugin':
            await getSDK().plugins.uninstallPluginApiV1PluginsPluginId(id);
            toastService.success('Plugin uninstalled successfully!');
            loadPlugins();
            break;
          case 'job':
            await getSDK().jobs.cancelJobApiV1JobsJobIdCancel(id);
            toastService.success('Job cancelled successfully!');
            loadJobs();
            loadJobStats();
            break;
        }
      } catch (error: unknown) {
        handleError(error, {
          source: 'AdministrationPage.handleDeleteItem',
          operation: `delete ${type}`,
          additionalData: { type, itemId: item?.id },
        });
      } finally {
        setLoading(false);
      }
    }
  };

  const toolbar = (
    <>
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
        size="small"
      >
        Refresh
      </Button>

      {/* Backup tab controls */}
      {activeTab === 'backups' && (
        <>
          <Button
            variant="contained"
            startIcon={<BackupIcon />}
            onClick={() => openDialog('backup')}
            size="small"
          >
            Create Backup
          </Button>
          <Button variant="outlined" startIcon={<UploadIcon />} size="small">
            Restore Backup
          </Button>
        </>
      )}

      {/* Jobs tab controls */}
      {activeTab === 'jobs' && (
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => openDialog('job')}
          size="small"
        >
          Create Job
        </Button>
      )}

      {/* Plugins tab controls */}
      {activeTab === 'plugins' && (
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => openDialog('plugin')}
          size="small"
        >
          Install Plugin
        </Button>
      )}

      {/* Users tab controls */}
      {activeTab === 'users' && (
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => openDialog('user')}
          size="small"
        >
          Add User
        </Button>
      )}
    </>
  );

  return (
    <PageLayout title="Administration" toolbar={toolbar}>
      <Tabs
        value={activeTab}
        onChange={(_, v) => setActiveTab(v)}
        variant="scrollable"
        scrollButtons="auto"
        sx={{ mb: 2 }}
      >
        <Tab
          value="backups"
          icon={<BackupIcon />}
          iconPosition="start"
          label="Backups"
        />
        <Tab
          value="jobs"
          icon={<JobIcon />}
          iconPosition="start"
          label="Background Jobs"
        />
        <Tab
          value="plugins"
          icon={<PluginIcon />}
          iconPosition="start"
          label="Plugins"
        />
        <Tab
          value="users"
          icon={<UsersIcon />}
          iconPosition="start"
          label="User Management"
        />
        <Tab
          value="bulk"
          icon={<BulkDeleteIcon />}
          iconPosition="start"
          label="Bulk Operations"
        />
      </Tabs>

      {/* Backups Tab */}
      {activeTab === 'backups' && (
        <Box>
          <Box sx={{ mb: 2 }}>
            <Grid container spacing={2} alignItems="center">
              <Grid size={{ xs: 12, sm: 4 }}>
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
              backups.map((backup): void => (
                <ListItem key={backup.id}>
                  <ListItemText
                    primary={
                      backup.name || `Backup ${backup.id?.substring(0, 8)}`
                    }
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
                    <IconButton
                      edge="end"
                      onClick={() => handleDeleteAction('backup', backup.id)}
                    >
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
              <Grid size={{ xs: 12, sm: 12 }}>
                {jobStats && (
                  <Box sx={{ textAlign: 'right' }}>
                    <Typography variant="body2" color="text.secondary">
                      Total: {jobStats.total_jobs} | Pending:{' '}
                      {jobStats.pending_jobs} | Running: {jobStats.running_jobs}
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
                    case 'running':
                      return 'success';
                    case 'pending':
                      return 'warning';
                    case 'completed':
                      return 'info';
                    case 'failed':
                      return 'error';
                    case 'cancelled':
                      return 'default';
                    default:
                      return 'default';
                  }
                };

                const getSecondaryText = () => {
                  const parts: string[] = [];
                  if (job.function_name)
                    parts.push(`Function: ${job.function_name}`);
                  if (job.priority) parts.push(`Priority: ${job.priority}`);
                  if (job.progress !== undefined)
                    parts.push(`Progress: ${job.progress}%`);
                  if (job.created_at)
                    parts.push(
                      `Created: ${new Date(job.created_at).toLocaleString()}`
                    );
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
                      {(job.status === 'pending' ||
                        job.status === 'running') && (
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
          <List>
            {plugins.length === 0 ? (
              <ListItem>
                <ListItemText
                  primary="No plugins installed"
                  secondary="Install plugins to extend functionality"
                />
              </ListItem>
            ) : (
              plugins.map((plugin): void => (
                <ListItem key={plugin.id}>
                  <ListItemIcon />
                  <ListItemText
                    primary={plugin.name || 'Unknown Plugin'}
                    secondary={`Version ${plugin.version || 'Unknown'} | ${plugin.enabled ? 'Enabled' : 'Disabled'} | ${plugin.description || 'No description'}`}
                  />
                  <ListItemSecondaryAction>
                    <Switch
                      checked={plugin.enabled || false}
                      onChange={(e) =>
                        handlePluginToggle(plugin.id, e.target.checked)
                      }
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
          <List>
            {users.map((user): void => (
              <ListItem key={user.id}>
                <ListItemText
                  primary={user.email}
                  secondary={`Role: ${user.role} | Last login: ${user.lastLogin} | Status: ${user.status}`}
                />
                <ListItemSecondaryAction>
                  <IconButton
                    edge="end"
                    onClick={(e) => openUserActionsMenu(e, user)}
                  >
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
            <strong>Warning:</strong> Bulk operations can delete large amounts
            of data permanently. Always test with &quot;Dry Run&quot; first.
          </Alert>

          <Box
            sx={{ mb: 3, p: 3, border: '1px solid #e0e0e0', borderRadius: 1 }}
          >
            <Typography variant="h6" gutterBottom>
              Bulk Delete Configuration
            </Typography>

            <Grid container spacing={3}>
              <Grid size={{ xs: 12 }} md={6}>
                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Operation Type</InputLabel>
                  <Select
                    value={bulkOperationData.operationType}
                    label="Operation Type"
                    onChange={(e) =>
                      setBulkOperationData((prev) => ({
                        ...prev,
                        operationType: e.target.value as 'conversations' | 'documents' | 'prompts',
                      }))
                    }
                  >
                    <MenuItem value="conversations">
                      Delete Conversations
                    </MenuItem>
                    <MenuItem value="documents">Delete Documents</MenuItem>
                    <MenuItem value="prompts">Delete Prompts</MenuItem>
                  </Select>
                </FormControl>

                <TextField
                  fullWidth
                  label="Created Before (YYYY-MM-DD)"
                  type="date"
                  value={bulkOperationData.filters.olderThan}
                  onChange={(e) =>
                    setBulkOperationData((prev) => ({
                      ...prev,
                      filters: { ...prev.filters, olderThan: e.target.value },
                    }))
                  }
                  sx={{ mb: 2 }}
                  InputLabelProps={{ shrink: true }}
                />

                <TextField
                  fullWidth
                  label="User ID (optional)"
                  value={bulkOperationData.filters.userId}
                  onChange={(e) =>
                    setBulkOperationData((prev) => ({
                      ...prev,
                      filters: { ...prev.filters, userId: e.target.value },
                    }))
                  }
                  sx={{ mb: 2 }}
                />

                <FormControlLabel
                  control={
                    <Switch
                      checked={bulkOperationData.dryRun}
                      onChange={(e) =>
                        setBulkOperationData((prev) => ({
                          ...prev,
                          dryRun: e.target.checked,
                        }))
                      }
                      color="warning"
                    />
                  }
                  label="Dry Run (Preview Only)"
                />
              </Grid>

              <Grid size={{ xs: 12 }} md={6}>
                <Typography variant="subtitle1" gutterBottom>
                  Operation Summary
                </Typography>
                <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                  <Typography variant="body2" gutterBottom>
                    <strong>Type:</strong> {bulkOperationData.operationType}
                  </Typography>
                  <Typography variant="body2" gutterBottom>
                    <strong>Mode:</strong>{' '}
                    {bulkOperationData.dryRun
                      ? 'Preview (Safe)'
                      : 'Delete (Permanent)'}
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
                    {!bulkOperationData.filters.olderThan &&
                      !bulkOperationData.filters.userId && (
                        <Typography
                          component="li"
                          variant="body2"
                          color="text.secondary"
                        >
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
                color={bulkOperationData.dryRun ? 'info' : 'error'}
                onClick={performBulkOperation}
                disabled={loading}
                startIcon={
                  loading ? <CircularProgress size={20} /> : <BulkDeleteIcon />
                }
              >
                {loading
                  ? 'Processing...'
                  : bulkOperationData.dryRun
                    ? 'Preview Changes'
                    : 'Execute Delete'}
              </Button>

              <Button
                variant="outlined"
                onClick={() =>
                  setBulkOperationData((prev) => ({
                    ...prev,
                    filters: { olderThan: '', userId: '', status: '' },
                    dryRun: true,
                  }))
                }
              >
                Reset Filters
              </Button>
            </Box>
          </Box>
        </Box>
      )}

      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
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
                    onChange={(e) =>
                      handleFormChange('includeUserData', e.target.checked)
                    }
                  />
                }
                label="Include user data"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.includeDocuments}
                    onChange={(e) =>
                      handleFormChange('includeDocuments', e.target.checked)
                    }
                  />
                }
                label="Include documents"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.includeConfigurations}
                    onChange={(e) =>
                      handleFormChange(
                        'includeConfigurations',
                        e.target.checked
                      )
                    }
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
                onChange={(e) =>
                  handleFormChange('jobFunction', e.target.value)
                }
              />
              <TextField
                fullWidth
                select
                label="Priority"
                margin="normal"
                value={formData.jobPriority}
                onChange={(e) =>
                  handleFormChange('jobPriority', e.target.value)
                }
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
                onChange={(e) =>
                  handleFormChange('maxRetries', parseInt(e.target.value) || 0)
                }
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
            {loading
              ? 'Processing...'
              : dialogType === 'backup'
                ? 'Create'
                : 'Add'}
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
        <MenuItem
          onClick={() => {
            if (actionUser) handleDeleteAction('user', actionUser.id);
            closeActionsMenu();
          }}
        >
          <ListItemIcon>
            <DeleteIcon fontSize="small" />
          </ListItemIcon>
          Delete
        </MenuItem>
      </Menu>

      {/* User Settings Dialog */}
      <Dialog
        open={userSettingsOpen}
        onClose={() => setUserSettingsOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>User Settings - {editingUser?.email}</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <TextField
              fullWidth
              label="Name"
              value={editingUser?.name || ''}
              onChange={(e) =>
                setEditingUser({ ...editingUser, name: e.target.value })
              }
              sx={{ mb: 2 }}
            />
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Role</InputLabel>
              <Select
                value={editingUser?.role || 'User'}
                label="Role"
                onChange={(e) =>
                  setEditingUser({ ...editingUser, role: e.target.value })
                }
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
                  onChange={(e) =>
                    setEditingUser({
                      ...editingUser,
                      isActive: e.target.checked,
                    })
                  }
                />
              }
              label="Active"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUserSettingsOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleUserSettingsSave}>
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </PageLayout>
  );
};

export default AdministrationPage;
