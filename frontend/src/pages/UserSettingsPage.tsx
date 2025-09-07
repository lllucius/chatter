import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  TextField,
  Alert,
  Tabs,
  Tab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  CircularProgress,
  Divider,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import {
  Save as SaveIcon,
  Key as KeyIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { chatterSDK } from '../services/chatter-sdk';
import { toastService } from '../services/toast-service';
import { useForm } from '../hooks/useForm';
import PageLayout from '../components/PageLayout';

interface UserProfile {
  id: string;
  username: string;
  email: string;
  full_name: string | null;
  created_at: string;
  updated_at: string;
}

interface APIKey {
  id: string;
  name: string;
  created_at: string;
  expires_at?: string;
  last_used?: string;
}

interface ProfileFormValues {
  full_name: string;
  email: string;
}

interface PasswordFormValues {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

interface ApiKeyFormValues {
  name: string;
  expires_in_days: number;
}

const UserSettingsPage: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [apiKeys, setApiKeys] = useState<APIKey[]>([]);
  const [loading, setLoading] = useState(true);
  const [apiKeysLoading, setApiKeysLoading] = useState(false);
  const [apiKeyDialogOpen, setApiKeyDialogOpen] = useState(false);
  const [deactivateDialogOpen, setDeactivateDialogOpen] = useState(false);

  const profileForm = useForm<ProfileFormValues>({
    initialValues: {
      full_name: '',
      email: '',
    },
    onSubmit: async (values) => {
      try {
        const updatedProfile = await chatterSDK.updateProfile(values);
        setUserProfile({ ...userProfile!, ...updatedProfile });
        toastService.success('Profile updated successfully');
      } catch (error: any) {
        toastService.error('Failed to update profile: ' + error.message);
        throw error;
      }
    },
  });

  const passwordForm = useForm<PasswordFormValues>({
    initialValues: {
      current_password: '',
      new_password: '',
      confirm_password: '',
    },
    validate: (values) => {
      const errors: Partial<Record<keyof PasswordFormValues, string>> = {};
      
      if (!values.current_password) {
        errors.current_password = 'Current password is required';
      }
      
      if (!values.new_password) {
        errors.new_password = 'New password is required';
      } else if (values.new_password.length < 6) {
        errors.new_password = 'Password must be at least 6 characters';
      }
      
      if (values.new_password !== values.confirm_password) {
        errors.confirm_password = 'Passwords do not match';
      }
      
      return errors;
    },
    onSubmit: async (values) => {
      try {
        await chatterSDK.changePassword({
          current_password: values.current_password,
          new_password: values.new_password,
        });
        toastService.success('Password changed successfully');
        passwordForm.reset();
      } catch (error: any) {
        toastService.error('Failed to change password: ' + error.message);
        throw error;
      }
    },
  });

  const apiKeyForm = useForm<ApiKeyFormValues>({
    initialValues: {
      name: '',
      expires_in_days: 90,
    },
    onSubmit: async (values) => {
      try {
        const newKey = await chatterSDK.createApiKey(values);
        setApiKeys([...apiKeys, newKey]);
        toastService.success('API key created successfully');
        setApiKeyDialogOpen(false);
        apiKeyForm.reset();
      } catch (error: any) {
        toastService.error('Failed to create API key: ' + error.message);
        throw error;
      }
    },
  });

  const loadUserProfile = async () => {
    try {
      const profile = await chatterSDK.getCurrentUser();
      setUserProfile(profile);
      profileForm.setValues({
        full_name: profile.full_name || '',
        email: profile.email || '',
      });
    } catch (error: any) {
      toastService.error('Failed to load user profile: ' + error.message);
    }
  };

  const loadApiKeys = async () => {
    try {
      setApiKeysLoading(true);
      const keys = await chatterSDK.listApiKeys();
      setApiKeys(keys);
    } catch (error: any) {
      toastService.error('Failed to load API keys: ' + error.message);
    } finally {
      setApiKeysLoading(false);
    }
  };

  const handleRevokeApiKey = async (keyId: string) => {
    try {
      await chatterSDK.revokeApiKey(keyId);
      setApiKeys(apiKeys.filter(key => key.id !== keyId));
      toastService.success('API key revoked successfully');
    } catch (error: any) {
      toastService.error('Failed to revoke API key: ' + error.message);
    }
  };

  const handleDeactivateAccount = async () => {
    try {
      await chatterSDK.deactivateAccount();
      toastService.success('Account deactivated successfully');
      // The SDK will handle logout and redirect
    } catch (error: any) {
      toastService.error('Failed to deactivate account: ' + error.message);
    } finally {
      setDeactivateDialogOpen(false);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([
        loadUserProfile(),
        loadApiKeys(),
      ]);
      setLoading(false);
    };

    loadData();
  }, []);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <PageLayout title="User Settings">
      <Card>
        <Tabs value={tabValue} onChange={handleTabChange} sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tab label="Profile" />
          <Tab label="Security" />
          <Tab label="API Keys" />
          <Tab label="Account" />
        </Tabs>

        {/* Profile Tab */}
        {tabValue === 0 && (
          <CardContent>
            <Typography variant="h6" sx={{ mb: 3 }}>
              Profile Information
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Username"
                  value={userProfile?.username || ''}
                  disabled
                  helperText="Username cannot be changed"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Email"
                  type="email"
                  value={profileForm.values.email}
                  onChange={profileForm.handleChange('email')}
                  error={Boolean(profileForm.errors.email)}
                  helperText={profileForm.errors.email}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Full Name"
                  value={profileForm.values.full_name}
                  onChange={profileForm.handleChange('full_name')}
                  error={Boolean(profileForm.errors.full_name)}
                  helperText={profileForm.errors.full_name}
                />
              </Grid>
              <Grid item xs={12}>
                <Typography variant="body2" color="text.secondary">
                  Account created: {userProfile?.created_at ? format(new Date(userProfile.created_at), 'PPpp') : 'Unknown'}
                </Typography>
              </Grid>
            </Grid>
            <CardActions>
              <Button
                variant="contained"
                startIcon={<SaveIcon />}
                onClick={profileForm.handleSubmit}
                loading={profileForm.submitting}
              >
                Save Changes
              </Button>
            </CardActions>
          </CardContent>
        )}

        {/* Security Tab */}
        {tabValue === 1 && (
          <CardContent>
            <Typography variant="h6" sx={{ mb: 3 }}>
              Change Password
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Current Password"
                  type="password"
                  value={passwordForm.values.current_password}
                  onChange={passwordForm.handleChange('current_password')}
                  error={Boolean(passwordForm.errors.current_password)}
                  helperText={passwordForm.errors.current_password}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="New Password"
                  type="password"
                  value={passwordForm.values.new_password}
                  onChange={passwordForm.handleChange('new_password')}
                  error={Boolean(passwordForm.errors.new_password)}
                  helperText={passwordForm.errors.new_password}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Confirm New Password"
                  type="password"
                  value={passwordForm.values.confirm_password}
                  onChange={passwordForm.handleChange('confirm_password')}
                  error={Boolean(passwordForm.errors.confirm_password)}
                  helperText={passwordForm.errors.confirm_password}
                />
              </Grid>
            </Grid>
            <CardActions>
              <Button
                variant="contained"
                onClick={passwordForm.handleSubmit}
                loading={passwordForm.submitting}
              >
                Change Password
              </Button>
            </CardActions>
          </CardContent>
        )}

        {/* API Keys Tab */}
        {tabValue === 2 && (
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
              <Typography variant="h6">
                API Keys
              </Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setApiKeyDialogOpen(true)}
              >
                Create API Key
              </Button>
            </Box>

            {apiKeysLoading ? (
              <Box display="flex" justifyContent="center" p={3}>
                <CircularProgress />
              </Box>
            ) : (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Name</TableCell>
                      <TableCell>Created</TableCell>
                      <TableCell>Expires</TableCell>
                      <TableCell>Last Used</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {apiKeys.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={5} align="center">
                          No API keys found
                        </TableCell>
                      </TableRow>
                    ) : (
                      apiKeys.map((key) => (
                        <TableRow key={key.id}>
                          <TableCell>{key.name}</TableCell>
                          <TableCell>
                            {key.created_at ? format(new Date(key.created_at), 'PP') : 'Unknown'}
                          </TableCell>
                          <TableCell>
                            {key.expires_at ? (
                              <Chip
                                label={format(new Date(key.expires_at), 'PP')}
                                color={new Date(key.expires_at) < new Date() ? 'error' : 'default'}
                                size="small"
                              />
                            ) : (
                              'Never'
                            )}
                          </TableCell>
                          <TableCell>
                            {key.last_used ? format(new Date(key.last_used), 'PP') : 'Never'}
                          </TableCell>
                          <TableCell>
                            <IconButton
                              size="small"
                              color="error"
                              onClick={() => handleRevokeApiKey(key.id)}
                            >
                              <DeleteIcon />
                            </IconButton>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </CardContent>
        )}

        {/* Account Tab */}
        {tabValue === 3 && (
          <CardContent>
            <Typography variant="h6" sx={{ mb: 3 }}>
              Account Management
            </Typography>

            <Alert severity="warning" sx={{ mb: 3 }}>
              <Typography variant="body2">
                <strong>Warning:</strong> Account deactivation is permanent and cannot be undone.
                All your data will be removed and you will lose access to the system.
              </Typography>
            </Alert>

            <Box>
              <Typography variant="body1" sx={{ mb: 2 }}>
                If you no longer need your account, you can deactivate it permanently.
                This action will:
              </Typography>
              <ul>
                <li>Remove all your personal data</li>
                <li>Revoke all API keys</li>
                <li>Delete all conversations and documents</li>
                <li>Log you out of all sessions</li>
              </ul>
              
              <Button
                variant="contained"
                color="error"
                startIcon={<WarningIcon />}
                onClick={() => setDeactivateDialogOpen(true)}
                sx={{ mt: 2 }}
              >
                Deactivate Account
              </Button>
            </Box>
          </CardContent>
        )}
      </Card>

      {/* Create API Key Dialog */}
      <Dialog open={apiKeyDialogOpen} onClose={() => setApiKeyDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create API Key</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TextField
              fullWidth
              label="Key Name"
              value={apiKeyForm.values.name}
              onChange={apiKeyForm.handleChange('name')}
              error={Boolean(apiKeyForm.errors.name)}
              helperText={apiKeyForm.errors.name}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Expires in Days"
              type="number"
              value={apiKeyForm.values.expires_in_days}
              onChange={apiKeyForm.handleChange('expires_in_days')}
              error={Boolean(apiKeyForm.errors.expires_in_days)}
              helperText={apiKeyForm.errors.expires_in_days || 'Set to 0 for no expiration'}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setApiKeyDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={apiKeyForm.handleSubmit}
            loading={apiKeyForm.submitting}
          >
            Create Key
          </Button>
        </DialogActions>
      </Dialog>

      {/* Deactivate Account Dialog */}
      <Dialog open={deactivateDialogOpen} onClose={() => setDeactivateDialogOpen(false)}>
        <DialogTitle>Confirm Account Deactivation</DialogTitle>
        <DialogContent>
          <Alert severity="error" sx={{ mb: 2 }}>
            This action cannot be undone!
          </Alert>
          <Typography>
            Are you absolutely sure you want to deactivate your account? This will permanently
            delete all your data and you will lose access to the system.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeactivateDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            color="error"
            onClick={handleDeactivateAccount}
          >
            Yes, Deactivate Account
          </Button>
        </DialogActions>
      </Dialog>
    </PageLayout>
  );
};

export default UserSettingsPage;