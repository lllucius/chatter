import React, { useState } from 'react';
import {
  Box,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Switch,
  FormControlLabel,
  Alert,
  Tabs,
  Tab,
  FormControl,
  InputLabel,
  Select,
  Grid,
  MenuItem,
} from '../utils/mui';
import {
  BackupIcon,
  JobIcon,
  PluginIcon,
  UsersIcon,
  RefreshIcon,
  AddIcon,
  BulkDeleteIcon,
} from '../utils/icons';
import { getSDK } from '../services/auth-service';
import { BackupResponse, BackupType, JobPriority } from 'chatter-sdk';
import { toastService } from '../services/toast-service';
import { handleError } from '../utils/error-handler';
import PageLayout from '../components/PageLayout';
import { useAdministrationData } from '../hooks/useAdministrationData';

// Import tab components
import BackupsTab from '../components/administration/BackupsTab';
import JobsTab from '../components/administration/JobsTab';
import UsersTab from '../components/administration/UsersTab';

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
  // Use custom hook for data management
  const { backups, jobs, jobStats, users, dataLoading, loadBackups, loadJobs } =
    useAdministrationData();

  const [activeTab, setActiveTab] = useState<
    'backups' | 'jobs' | 'plugins' | 'users' | 'bulk'
  >('backups');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogType, setDialogType] = useState<
    'user' | 'backup' | 'plugin' | 'job'
  >('user');
  const [loading, setLoading] = useState(false);

  // User action menu state
  const [actionAnchorEl, setActionAnchorEl] = useState<HTMLElement | null>(
    null
  );
  const [actionUser, setActionUser] = useState<User | null>(null);

  // User settings dialog state
  const [userSettingsOpen, setUserSettingsOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);

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

  // Helper functions
  const resetFormData = () => {
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

  const handleFormChange = (
    field: string,
    value: string | number | boolean
  ) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  // Action handlers
  const openUserActionsMenu = (
    e: React.MouseEvent<HTMLElement>,
    user: User
  ) => {
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

  // Dialog handlers
  const openDialog = (type: 'user' | 'backup' | 'plugin' | 'job') => {
    setDialogType(type);
    setDialogOpen(true);
    resetFormData();
  };

  const closeDialog = () => {
    setDialogOpen(false);
    resetFormData();
  };

  // CRUD operations
  const handleCreateItem = async () => {
    try {
      setLoading(true);

      switch (dialogType) {
        case 'backup':
          await getSDK().dataManagement.createBackupApiV1DataBackup({
            name: formData.backupName,
            description: formData.description,
            backup_type: BackupType.full,
            include_files: formData.includeUserData,
            include_logs: formData.includeDocuments,
            compress: formData.includeConfigurations,
          });
          toastService.success('Backup created successfully!');
          loadBackups();
          break;
        case 'job':
          await getSDK().jobs.createJobApiV1Jobs({
            name: formData.jobName,
            function: formData.jobFunction,
            args: formData.jobArgs ? JSON.parse(formData.jobArgs) : [],
            kwargs: formData.jobKwargs ? JSON.parse(formData.jobKwargs) : {},
            priority: formData.jobPriority as JobPriority,
            schedule_at: formData.scheduleAt || null,
            max_retries: formData.maxRetries,
          });
          toastService.success('Job created successfully!');
          loadJobs();
          break;
        default:
          break;
      }
      closeDialog();
    } catch (error) {
      handleError(error, {
        source: 'AdministrationPage.handleCreateItem',
        operation: `create ${dialogType}`,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadBackup = async (_backup: BackupResponse) => {
    try {
      // Implementation for backup download
      toastService.info('Backup download started');
    } catch (error) {
      handleError(error, {
        source: 'AdministrationPage.handleDownloadBackup',
        operation: 'download backup',
      });
    }
  };

  // Bulk operations
  const performBulkOperation = async () => {
    try {
      setLoading(true);

      const filters: Record<string, string | boolean> = {};

      // Build filters based on form data
      if (bulkOperationData.filters.olderThan) {
        filters.older_than = bulkOperationData.filters.olderThan;
      }
      if (bulkOperationData.filters.userId) {
        filters.user_id = bulkOperationData.filters.userId;
      }
      if (bulkOperationData.filters.status) {
        filters.status = bulkOperationData.filters.status;
      }

      // Add dry_run flag
      filters.dry_run = bulkOperationData.dryRun;

      // Simulate bulk operation - in real app, this would call appropriate API
      const message = bulkOperationData.dryRun
        ? `Dry run completed for ${bulkOperationData.operationType}`
        : `Bulk operation completed for ${bulkOperationData.operationType}`;

      toastService.success(message);
    } catch (error) {
      handleError(error, {
        source: 'AdministrationPage.performBulkOperation',
        operation: 'bulk operation',
      });
    } finally {
      setLoading(false);
    }
  };

  // Toolbar content
  const toolbar = (
    <>
      <Button
        variant="outlined"
        startIcon={<RefreshIcon />}
        onClick={() => {
          loadBackups();
          loadJobs();
        }}
        disabled={dataLoading}
      >
        Refresh All
      </Button>
      {activeTab === 'backups' && (
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => openDialog('backup')}
        >
          Create Backup
        </Button>
      )}
      {activeTab === 'jobs' && (
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => openDialog('job')}
        >
          Create Job
        </Button>
      )}
      {activeTab === 'users' && (
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => openDialog('user')}
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

      {/* Tab Content */}
      {activeTab === 'backups' && (
        <BackupsTab
          backups={backups}
          loading={dataLoading}
          onCreateBackup={() => openDialog('backup')}
          onDownloadBackup={handleDownloadBackup}
        />
      )}

      {activeTab === 'jobs' && (
        <JobsTab
          jobs={jobs}
          jobStats={jobStats}
          loading={dataLoading}
          onRefresh={loadJobs}
          onCreateJob={() => openDialog('job')}
        />
      )}

      {activeTab === 'plugins' && (
        <Box>
          <Alert severity="info">
            Plugin management functionality will be implemented here.
          </Alert>
        </Box>
      )}

      {activeTab === 'users' && (
        <UsersTab
          users={users}
          loading={dataLoading}
          onAddUser={() => openDialog('user')}
          onEditUser={handleUserSettings}
          actionAnchorEl={actionAnchorEl}
          actionUser={actionUser}
          onOpenUserActions={openUserActionsMenu}
          onCloseActions={closeActionsMenu}
        />
      )}

      {activeTab === 'bulk' && (
        <Box>
          <Alert severity="warning" sx={{ mb: 3 }}>
            <strong>Warning:</strong> Bulk operations can delete large amounts
            of data permanently. Always test with &quot;Dry Run&quot; first.
          </Alert>

          <Box
            sx={{ mb: 3, p: 3, border: '1px solid #e0e0e0', borderRadius: 1 }}
          >
            <Grid container spacing={3}>
              <Grid size={{ xs: 12, md: 6 }}>
                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Operation Type</InputLabel>
                  <Select
                    value={bulkOperationData.operationType}
                    label="Operation Type"
                    onChange={(e) =>
                      setBulkOperationData((prev) => ({
                        ...prev,
                        operationType: e.target.value as
                          | 'conversations'
                          | 'documents'
                          | 'prompts',
                      }))
                    }
                  >
                    <MenuItem value="conversations">Conversations</MenuItem>
                    <MenuItem value="documents">Documents</MenuItem>
                    <MenuItem value="prompts">Prompts</MenuItem>
                  </Select>
                </FormControl>

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
                    />
                  }
                  label="Dry Run (recommended)"
                />
              </Grid>
            </Grid>

            <Button
              variant="contained"
              color={bulkOperationData.dryRun ? 'primary' : 'error'}
              onClick={performBulkOperation}
              disabled={loading}
              sx={{ mt: 2 }}
            >
              {bulkOperationData.dryRun
                ? 'Preview Operation'
                : 'Execute Operation'}
            </Button>
          </Box>
        </Box>
      )}

      {/* Create/Edit Dialog */}
      <Dialog open={dialogOpen} onClose={closeDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {dialogType === 'user' && 'Add New User'}
          {dialogType === 'backup' && 'Create Backup'}
          {dialogType === 'plugin' && 'Install Plugin'}
          {dialogType === 'job' && 'Create Background Job'}
        </DialogTitle>
        <DialogContent>
          {dialogType === 'backup' && (
            <Box sx={{ pt: 1 }}>
              <TextField
                fullWidth
                label="Backup Name"
                value={formData.backupName}
                onChange={(e) => handleFormChange('backupName', e.target.value)}
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                label="Description"
                multiline
                rows={3}
                value={formData.description}
                onChange={(e) =>
                  handleFormChange('description', e.target.value)
                }
                sx={{ mb: 2 }}
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
                label="Include User Data"
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
                label="Include Documents"
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
                label="Include Configurations"
              />
            </Box>
          )}

          {dialogType === 'job' && (
            <Box sx={{ pt: 1 }}>
              <TextField
                fullWidth
                label="Job Name"
                value={formData.jobName}
                onChange={(e) => handleFormChange('jobName', e.target.value)}
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                label="Function"
                value={formData.jobFunction}
                onChange={(e) =>
                  handleFormChange('jobFunction', e.target.value)
                }
                sx={{ mb: 2 }}
              />
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Priority</InputLabel>
                <Select
                  value={formData.jobPriority}
                  label="Priority"
                  onChange={(e) =>
                    handleFormChange('jobPriority', e.target.value)
                  }
                >
                  <MenuItem value={JobPriority.low}>Low</MenuItem>
                  <MenuItem value={JobPriority.normal}>Normal</MenuItem>
                  <MenuItem value={JobPriority.high}>High</MenuItem>
                </Select>
              </FormControl>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={closeDialog}>Cancel</Button>
          <Button
            onClick={handleCreateItem}
            variant="contained"
            disabled={loading}
          >
            {loading ? 'Creating...' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* User Settings Dialog */}
      <Dialog
        open={userSettingsOpen}
        onClose={() => setUserSettingsOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>User Settings</DialogTitle>
        <DialogContent>
          {editingUser && (
            <Box sx={{ pt: 1 }}>
              <TextField
                fullWidth
                label="Name"
                value={editingUser.name}
                disabled
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                label="Email"
                value={editingUser.email}
                disabled
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                label="Role"
                value={editingUser.role}
                disabled
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUserSettingsOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </PageLayout>
  );
};

export default AdministrationPage;
