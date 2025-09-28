import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
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
  CircularProgress,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import {
  Save as SaveIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { getSDK, authService } from '../services/auth-service';
import { toastService } from '../services/toast-service';
import { handleError } from '../utils/error-handler';
import { useForm } from '../hooks/useForm';
import PageLayout from '../components/PageLayout';
import type { APIKeyResponse, UserResponse } from 'chatter-sdk';

// Use UserResponse from SDK instead of local interface

// Use APIKeyResponse from SDK instead of local interface

interface ProfileFormValues extends Record<string, unknown> {
  full_name: string;
  email: string;
}

interface PasswordFormValues extends Record<string, unknown> {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

interface ApiKeyFormValues extends Record<string, unknown> {
  name: string;
  expires_in_days: number;
}

const UserSettingsPage: React.FC = () => {
  const navigate = useNavigate();
  const [tabValue, setTabValue] = useState(0);
  const [userProfile, setUserProfile] = useState<UserResponse | null>(null);
  const [apiKeys, setApiKeys] = useState<APIKeyResponse[]>([]);
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
        const updatedProfile =
          await getSDK().auth.updateProfileApiV1AuthMe(values);
        setUserProfile({ ...userProfile!, ...updatedProfile });
        toastService.success('Profile updated successfully');
      } catch (error: unknown) {
        handleError(error, {
          source: 'UserSettingsPage.handleSaveProfile',
          operation: 'update user profile',
          additionalData: {
            name: profileForm.values.full_name,
            email: profileForm.values.email,
          },
        });
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
        await getSDK().auth.changePasswordApiV1AuthChangePassword({
          current_password: values.current_password,
          new_password: values.new_password,
        });
        toastService.success('Password changed successfully');
        passwordForm.resetForm();
      } catch (error: unknown) {
        handleError(error, {
          source: 'UserSettingsPage.handleChangePassword',
          operation: 'change password',
        });
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
        const newKey = await getSDK().auth.createApiKeyApiV1AuthApiKey({
          name: values.name,
          // Note: expires_in_days is not supported in the current API
        });
        setApiKeys([...apiKeys, newKey]);
        toastService.success('API key created successfully');
        setApiKeyDialogOpen(false);
        apiKeyForm.resetForm();
      } catch (error: unknown) {
        handleError(error, {
          source: 'UserSettingsPage.handleCreateApiKey',
          operation: 'create API key',
          additionalData: { keyName: apiKeyForm.values.name },
        });
        throw error;
      }
    },
  });

  const loadUserProfile = useCallback(async () => {
    try {
      const profile = await getSDK().auth.getCurrentUserInfoApiV1AuthMe();
      setUserProfile(profile);
      profileForm.setFieldValue('full_name', profile.full_name || '');
      profileForm.setFieldValue('email', profile.email || '');
    } catch (error: unknown) {
      handleError(error, {
        source: 'UserSettingsPage.loadUserProfile',
        operation: 'load user profile',
      });
    }
  }, []);

  const loadApiKeys = async () => {
    try {
      setApiKeysLoading(true);
      const keys = await getSDK().auth.listApiKeysApiV1AuthApiKeys();
      setApiKeys(keys);
    } catch (error: unknown) {
      handleError(error, {
        source: 'UserSettingsPage.loadApiKeys',
        operation: 'load API keys',
      });
    } finally {
      setApiKeysLoading(false);
    }
  };

  const handleRevokeApiKey = async (_keyId: string) => {
    try {
      // Note: The current API only supports revoking the current user's API key
      // It doesn't support revoking specific keys by ID
      await getSDK().auth.revokeApiKeyApiV1AuthApiKey();
      // Refresh the key list after revocation
      await loadApiKeys();
      toastService.success('API key revoked successfully');
    } catch (error: unknown) {
      handleError(error, {
        source: 'UserSettingsPage.handleRevokeKey',
        operation: 'revoke API key',
        additionalData: { keyId: _keyId },
      });
    }
  };

  const handleDeactivateAccount = async () => {
    try {
      await getSDK().auth.deactivateAccountApiV1AuthAccount();
      toastService.success('Account deactivated successfully');
      
      // Clear localStorage and cookies, then redirect
      localStorage.clear();
      sessionStorage.clear();
      
      // Clear auth service tokens
      await authService.logout();
      
      // Redirect to login page
      navigate('/login', { replace: true });
    } catch (error: unknown) {
      handleError(error, {
        source: 'UserSettingsPage.handleDeactivateAccount',
        operation: 'deactivate user account',
      });
    } finally {
      setDeactivateDialogOpen(false);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([loadUserProfile(), loadApiKeys()]);
      setLoading(false);
    };

    loadData();
  }, [loadUserProfile]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  if (loading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="400px"
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <PageLayout title="User Settings">
      <Card>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
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
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Username"
                  value={userProfile?.username || ''}
                  disabled
                  helperText="Username cannot be changed"
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
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
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Full Name"
                  value={profileForm.values.full_name}
                  onChange={profileForm.handleChange('full_name')}
                  error={Boolean(profileForm.errors.full_name)}
                  helperText={profileForm.errors.full_name}
                />
              </Grid>
              <Grid size={{ xs: 12 }}>
                <Typography variant="body2" color="text.secondary">
                  Account created:{' '}
                  {userProfile?.created_at
                    ? format(new Date(userProfile.created_at), 'PPpp')
                    : 'Unknown'}
                </Typography>
              </Grid>
            </Grid>
            <CardActions>
              <Button
                variant="contained"
                startIcon={<SaveIcon />}
                onClick={profileForm.handleSubmit}
                loading={profileForm.isSubmitting}
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
              <Grid size={{ xs: 12 }}>
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
              <Grid size={{ xs: 12 }}>
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
              <Grid size={{ xs: 12 }}>
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
                loading={passwordForm.isSubmitting}
              >
                Change Password
              </Button>
            </CardActions>
          </CardContent>
        )}

        {/* API Keys Tab */}
        {tabValue === 2 && (
          <CardContent>
            <Box
              display="flex"
              justifyContent="space-between"
              alignItems="center"
              sx={{ mb: 3 }}
            >
              <Typography variant="h6">API Keys</Typography>
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
                          <TableCell>{key.api_key_name}</TableCell>
                          <TableCell>
                            {'Not available'}
                          </TableCell>
                          <TableCell>
                            {'Not available'}
                          </TableCell>
                          <TableCell>
                            {'Not available'}
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
                <strong>Warning:</strong> Account deactivation is permanent and
                cannot be undone. All your data will be removed and you will
                lose access to the system.
              </Typography>
            </Alert>

            <Box>
              <Typography variant="body1" sx={{ mb: 2 }}>
                If you no longer need your account, you can deactivate it
                permanently. This action will:
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
      <Dialog
        open={apiKeyDialogOpen}
        onClose={() => setApiKeyDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
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
              helperText={
                apiKeyForm.errors.expires_in_days ||
                'Set to 0 for no expiration'
              }
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setApiKeyDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={apiKeyForm.handleSubmit}
            loading={apiKeyForm.isSubmitting}
          >
            Create Key
          </Button>
        </DialogActions>
      </Dialog>

      {/* Deactivate Account Dialog */}
      <Dialog
        open={deactivateDialogOpen}
        onClose={() => setDeactivateDialogOpen(false)}
      >
        <DialogTitle>Confirm Account Deactivation</DialogTitle>
        <DialogContent>
          <Alert severity="error" sx={{ mb: 2 }}>
            This action cannot be undone!
          </Alert>
          <Typography>
            Are you absolutely sure you want to deactivate your account? This
            will permanently delete all your data and you will lose access to
            the system.
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
