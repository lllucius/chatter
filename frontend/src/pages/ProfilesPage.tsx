import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  IconButton,
  Chip,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  Menu,
  ListItemIcon,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  Refresh as RefreshIcon,
  MoreVert as MoreVertIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { chatterSDK } from '../services/chatter-sdk';
import { toastService } from '../services/toast-service';
import { ProfileResponse, ProfileCreate, ProfileUpdate } from '../sdk';
import PageLayout from '../components/PageLayout';

const ProfilesPage: React.FC = () => {
  const [profiles, setProfiles] = useState<ProfileResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogError, setDialogError] = useState('');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingProfile, setEditingProfile] = useState<ProfileResponse | null>(null);
  const [saving, setSaving] = useState(false);

  // Actions menu state
  const [actionAnchorEl, setActionAnchorEl] = useState<HTMLElement | null>(null);
  const [actionProfile, setActionProfile] = useState<ProfileResponse | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    llm_model: '',
    llm_provider: '',
    temperature: 0.7,
    max_tokens: 1000,
    top_p: 1.0,
    frequency_penalty: 0.0,
    presence_penalty: 0.0,
  });

  const providers = ['openai', 'anthropic', 'google', 'cohere'];
  const models = {
    openai: ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo'],
    anthropic: ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku'],
    google: ['gemini-pro', 'gemini-pro-vision'],
    cohere: ['command', 'command-light'],
  };

  useEffect(() => {
    loadProfiles();
  }, []);

  const loadProfiles = async () => {
    try {
      setLoading(true);
      
      const response = await chatterSDK.profiles.listProfilesApiV1ProfilesGet({});
      setProfiles(response.data.profiles);
    } catch (err: any) {
      toastService.error(err, 'Failed to load profiles');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (profile?: ProfileResponse) => {
    setDialogError(''); // Clear any previous dialog errors
    if (profile) {
      setEditingProfile(profile);
      setFormData({
        name: profile.name,
        description: profile.description || '',
        llm_model: profile.llm_model,
        llm_provider: profile.llm_provider,
        temperature: profile.temperature ?? 0.7,
        max_tokens: profile.max_tokens || 1000,
        top_p: profile.top_p || 1.0,
        frequency_penalty: profile.frequency_penalty || 0.0,
        presence_penalty: profile.presence_penalty || 0.0,
      });
    } else {
      setEditingProfile(null);
      setFormData({
        name: '',
        description: '',
        llm_model: '',
        llm_provider: '',
        temperature: 0.7,
        max_tokens: 1000,
        top_p: 1.0,
        frequency_penalty: 0.0,
        presence_penalty: 0.0,
      });
    }
    setDialogOpen(true);
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setDialogError(''); // Clear any previous dialog errors
      if (editingProfile) {
        const updateRequest: ProfileUpdate = {
          name: formData.name,
          description: formData.description,
          llm_model: formData.llm_model,
          llm_provider: formData.llm_provider,
          temperature: formData.temperature,
          max_tokens: formData.max_tokens,
          top_p: formData.top_p,
          frequency_penalty: formData.frequency_penalty,
          presence_penalty: formData.presence_penalty,
        };
        const response = await chatterSDK.profiles.updateProfileApiV1ProfilesProfileIdPut({ profileId: editingProfile.id, profileUpdate: updateRequest });
        setProfiles(prev => prev.map(p => p.id === editingProfile.id ? response.data : p));
      } else {
        const createRequest: ProfileCreate = {
          name: formData.name,
          description: formData.description,
          llm_model: formData.llm_model,
          llm_provider: formData.llm_provider,
          temperature: formData.temperature,
          max_tokens: formData.max_tokens,
          top_p: formData.top_p,
          frequency_penalty: formData.frequency_penalty,
          presence_penalty: formData.presence_penalty,
        };
        const response = await chatterSDK.profiles.createProfileApiV1ProfilesPost({ profileCreate: createRequest });
        setProfiles(prev => [response.data, ...prev]);
      }
      setDialogOpen(false);
    } catch (err: any) {
      toastService.error(err, 'Failed to save profile');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (profileId: string) => {
    if (!window.confirm('Are you sure you want to delete this profile?')) {
      return;
    }

    try {
      await chatterSDK.profiles.deleteProfileApiV1ProfilesProfileIdDelete({ profileId: profileId });
      setProfiles(prev => prev.filter(p => p.id !== profileId));
    } catch (err: any) {
      setError('Failed to delete profile');
    }
  };

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const paginatedProfiles = profiles.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  // IMPORTANT: accept the click event, and read e.currentTarget here
  const openActionsMenu = (e: React.MouseEvent<HTMLElement>, profile: ProfileResponse) => {
    setActionAnchorEl(e.currentTarget);
    setActionProfile(profile);
  };

  const closeActionsMenu = () => {
    setActionAnchorEl(null);
    setActionProfile(null);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress size={60} />
      </Box>
    );
  }

  const toolbar = (
    <>
      <Button
        variant="outlined"
        startIcon={<RefreshIcon />}
        onClick={loadProfiles}
        disabled={loading}
      >
        Refresh
      </Button>
      <Button
        variant="contained"
        startIcon={<AddIcon />}
        onClick={() => handleOpenDialog()}
      >
        Create Profile
      </Button>
    </>
  );

  return (
    <PageLayout title="Profile Management" toolbar={toolbar}>
      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Provider</TableCell>
                <TableCell>Model</TableCell>
                <TableCell>Temperature</TableCell>
                <TableCell>Max Tokens</TableCell>
                <TableCell>Created</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {paginatedProfiles.map((profile) => (
                <TableRow key={profile.id} hover>
                  <TableCell>
                    <Box>
                      <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
                        {profile.name}
                      </Typography>
                      {profile.description && (
                        <Typography variant="body2" color="text.secondary">
                          {profile.description}
                        </Typography>
                      )}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={profile.llm_provider}
                      color="primary"
                      variant="outlined"
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                      {profile.llm_model}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={profile.temperature}
                      color="secondary"
                      variant="outlined"
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {profile.max_tokens ? (
                      <Typography variant="body2">
                        {profile.max_tokens.toLocaleString()}
                      </Typography>
                    ) : (
                      '-'
                    )}
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {format(new Date(profile.created_at), 'MMM dd, yyyy')}
                    </Typography>
                  </TableCell>
                  <TableCell align="center">
                    <IconButton
                      size="small"
                      onClick={(e) => openActionsMenu(e, profile)} // pass the event, not e.currentTarget
                      color="primary"
                    >
                      <MoreVertIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
              {paginatedProfiles.length === 0 && (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    <Typography variant="body2" color="text.secondary" sx={{ py: 3 }}>
                      No profiles found
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={profiles.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Card>

      {/* Actions Menu */}
      <Menu
        anchorEl={actionAnchorEl}
        open={Boolean(actionAnchorEl)}
        onClose={closeActionsMenu}
      >
        <MenuItem
          onClick={() => {
            if (actionProfile) handleOpenDialog(actionProfile);
            closeActionsMenu();
          }}
        >
          <ListItemIcon>
            <EditIcon fontSize="small" />
          </ListItemIcon>
          Edit
        </MenuItem>
        <MenuItem
          onClick={() => {
            if (actionProfile) handleDelete(actionProfile.id);
            closeActionsMenu();
          }}
        >
          <ListItemIcon>
            <DeleteIcon fontSize="small" />
          </ListItemIcon>
          Delete
        </MenuItem>
      </Menu>

      {/* Create/Edit Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingProfile ? 'Edit Profile' : 'Create Profile'}
        </DialogTitle>
        <DialogContent>
          {dialogError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {dialogError}
            </Alert>
          )}
          <Box sx={{ pt: 1 }}>
            <Grid container spacing={3}>
            <Grid
              size={{
                xs: 12,
                sm: 6
              }}>
              <TextField
                fullWidth
                label="Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </Grid>
            <Grid
              size={{
                xs: 12,
                sm: 6
              }}>
              <FormControl fullWidth required>
                <InputLabel>Provider</InputLabel>
                <Select
                  value={formData.llm_provider}
                  label="Provider"
                  onChange={(e) => setFormData({ 
                    ...formData, 
                    llm_provider: e.target.value,
                    llm_model: '' // Reset model when provider changes
                  })}
                >
                  {providers.map((provider) => (
                    <MenuItem key={provider} value={provider}>
                      {provider.charAt(0).toUpperCase() + provider.slice(1)}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid size={12}>
              <TextField
                fullWidth
                label="Description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                multiline
                rows={2}
              />
            </Grid>
            <Grid
              size={{
                xs: 12,
                sm: 6
              }}>
              <FormControl fullWidth required>
                <InputLabel>Model</InputLabel>
                <Select
                  value={formData.llm_model}
                  label="Model"
                  onChange={(e) => setFormData({ ...formData, llm_model: e.target.value })}
                  disabled={!formData.llm_provider}
                >
                  {formData.llm_provider && models[formData.llm_provider as keyof typeof models]?.map((model) => (
                    <MenuItem key={model} value={model}>
                      {model}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid
              size={{
                xs: 12,
                sm: 6
              }}>
              <TextField
                fullWidth
                label="Max Tokens"
                type="number"
                value={formData.max_tokens}
                onChange={(e) => setFormData({ ...formData, max_tokens: parseInt(e.target.value) })}
                inputProps={{ min: 1, max: 32000 }}
              />
            </Grid>
            <Grid
              size={{
                xs: 12,
                sm: 6
              }}>
              <Typography gutterBottom>Temperature: {formData.temperature}</Typography>
              <Slider
                value={formData.temperature}
                onChange={(_, value) => setFormData({ ...formData, temperature: value as number })}
                min={0}
                max={2}
                step={0.1}
                marks={[
                  { value: 0, label: '0 (Deterministic)' },
                  { value: 1, label: '1 (Balanced)' },
                  { value: 2, label: '2 (Creative)' },
                ]}
              />
            </Grid>
            <Grid
              size={{
                xs: 12,
                sm: 6
              }}>
              <Typography gutterBottom>Top P: {formData.top_p}</Typography>
              <Slider
                value={formData.top_p}
                onChange={(_, value) => setFormData({ ...formData, top_p: value as number })}
                min={0}
                max={1}
                step={0.1}
                marks={[
                  { value: 0, label: '0' },
                  { value: 0.5, label: '0.5' },
                  { value: 1, label: '1' },
                ]}
              />
            </Grid>
            <Grid
              size={{
                xs: 12,
                sm: 6
              }}>
              <Typography gutterBottom>Frequency Penalty: {formData.frequency_penalty}</Typography>
              <Slider
                value={formData.frequency_penalty}
                onChange={(_, value) => setFormData({ ...formData, frequency_penalty: value as number })}
                min={-2}
                max={2}
                step={0.1}
                marks={[
                  { value: -2, label: '-2' },
                  { value: 0, label: '0' },
                  { value: 2, label: '2' },
                ]}
              />
            </Grid>
            <Grid
              size={{
                xs: 12,
                sm: 6
              }}>
              <Typography gutterBottom>Presence Penalty: {formData.presence_penalty}</Typography>
              <Slider
                value={formData.presence_penalty}
                onChange={(_, value) => setFormData({ ...formData, presence_penalty: value as number })}
                min={-2}
                max={2}
                step={0.1}
                marks={[
                  { value: -2, label: '-2' },
                  { value: 0, label: '0' },
                  { value: 2, label: '2' },
                ]}
              />
            </Grid>
          </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)} disabled={saving}>
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            variant="contained"
            disabled={!formData.name || !formData.llm_provider || !formData.llm_model || saving}
          >
            {saving ? 'Saving...' : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>
    </PageLayout>
  );
};

export default ProfilesPage;
