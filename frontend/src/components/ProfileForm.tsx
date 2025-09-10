import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  Typography,
  Box,
  CircularProgress,
  Alert,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import { ProfileCreate, ProfileUpdate } from 'chatter-sdk';
import { CrudFormProps } from './CrudDataTable';
import { getSDK } from '../services/auth-service';

interface Provider {
  name: string;
  display_name: string;
  description: string;
  models: Array<{
    name: string;
    model_name: string;
    display_name: string;
    is_default: boolean;
    max_tokens: number;
  }>;
}

interface ProvidersData {
  providers: Record<string, Provider>;
  default_provider: string;
}

interface ProfileFormProps extends CrudFormProps<ProfileCreate, ProfileUpdate> {}

const ProfileForm: React.FC<ProfileFormProps> = ({
  open,
  mode,
  initialData,
  onClose,
  onSubmit,
}) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    llmModel: '',
    llmProvider: '',
    temperature: 0.7,
    max_tokens: 1000,
    top_p: 1.0,
    frequency_penalty: 0.0,
    presence_penalty: 0.0,
  });

  const [saving, setSaving] = useState(false);
  const [loadingProviders, setLoadingProviders] = useState(false);
  const [providersData, setProvidersData] = useState<ProvidersData | null>(null);
  const [providersError, setProvidersError] = useState<string | null>(null);

  // Fetch providers data from API
  const fetchProviders = async () => {
    setLoadingProviders(true);
    setProvidersError(null);
    try {
      const response = await getSDK().profiles.getAvailableProvidersApiV1ProfilesProvidersAvailable();
      setProvidersData(response as ProvidersData);
    } catch (error) {
      console.error('Failed to fetch providers:', error);
      setProvidersError('Failed to load available providers');
    } finally {
      setLoadingProviders(false);
    }
  };

  useEffect(() => {
    if (open && !providersData && !loadingProviders) {
      fetchProviders();
    }
  }, [open, providersData, loadingProviders]);

  useEffect(() => {
    if (open) {
      if (mode === 'edit' && initialData) {
        setFormData({
          name: initialData.name || '',
          description: initialData.description || '',
          llmModel: initialData.llm_model || '',
          llmProvider: initialData.llm_provider || '',
          temperature: initialData.temperature ?? 0.7,
          max_tokens: initialData.max_tokens || 1000,
          top_p: initialData.top_p || 1.0,
          frequency_penalty: initialData.frequency_penalty || 0.0,
          presence_penalty: initialData.presence_penalty || 0.0,
        });
      } else {
        setFormData({
          name: '',
          description: '',
          llmModel: '',
          llmProvider: '',
          temperature: 0.7,
          max_tokens: 1000,
          top_p: 1.0,
          frequency_penalty: 0.0,
          presence_penalty: 0.0,
        });
      }
    }
  }, [open, mode, initialData]);

  const handleSubmit = async () => {
    try {
      setSaving(true);
      // Transform camelCase form data to snake_case for API
      const apiData: ProfileCreate | ProfileUpdate = {
        name: formData.name,
        description: formData.description,
        llm_provider: formData.llmProvider,
        llm_model: formData.llmModel,
        temperature: formData.temperature,
        max_tokens: formData.max_tokens,
        top_p: formData.top_p,
        frequency_penalty: formData.frequency_penalty,
        presence_penalty: formData.presence_penalty,
      };
      await onSubmit(apiData);
    } finally {
      setSaving(false);
    }
  };

  const getAvailableProviders = (): string[] => {
    if (!providersData) return [];
    return Object.keys(providersData.providers);
  };

  const getAvailableModels = (): Array<{name: string, display_name: string}> => {
    if (!providersData || !formData.llmProvider) return [];
    const provider = providersData.providers[formData.llmProvider];
    if (!provider) return [];
    return provider.models.map(model => ({
      name: model.model_name,
      display_name: model.display_name || model.name
    }));
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {mode === 'create' ? 'Create Profile' : 'Edit Profile'}
      </DialogTitle>
      <DialogContent>
        <Box sx={{ pt: 1 }}>
          {providersError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {providersError}
            </Alert>
          )}
          
          <Grid container spacing={3}>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <FormControl fullWidth required>
                <InputLabel>Provider</InputLabel>
                <Select
                  value={formData.llmProvider}
                  label="Provider"
                  onChange={(e) => setFormData({
                    ...formData,
                    llmProvider: e.target.value,
                    llmModel: '' // Reset model when provider changes
                  })}
                  disabled={loadingProviders}
                >
                  {loadingProviders ? (
                    <MenuItem disabled>
                      <CircularProgress size={20} sx={{ mr: 1 }} />
                      Loading providers...
                    </MenuItem>
                  ) : (
                    getAvailableProviders().map((provider) => {
                      const providerData = providersData?.providers[provider];
                      return (
                        <MenuItem key={provider} value={provider}>
                          {providerData?.display_name || provider}
                        </MenuItem>
                      );
                    })
                  )}
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
            <Grid size={{ xs: 12, sm: 6 }}>
              <FormControl fullWidth required>
                <InputLabel>Model</InputLabel>
                <Select
                  value={formData.llmModel}
                  label="Model"
                  onChange={(e) => setFormData({ ...formData, llmModel: e.target.value })}
                  disabled={!formData.llmProvider || loadingProviders}
                >
                  {getAvailableModels().map((model) => (
                    <MenuItem key={model.name} value={model.name}>
                      {model.display_name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Max Tokens"
                type="number"
                value={formData.max_tokens}
                onChange={(e) => setFormData({ ...formData, max_tokens: parseInt(e.target.value) })}
                inputProps={{ min: 1, max: 32000 }}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
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
            <Grid size={{ xs: 12, sm: 6 }}>
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
            <Grid size={{ xs: 12, sm: 6 }}>
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
            <Grid size={{ xs: 12, sm: 6 }}>
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
        <Button onClick={onClose} disabled={saving}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={!formData.name || !formData.llmProvider || !formData.llmModel || saving}
        >
          {saving ? 'Saving...' : (mode === 'create' ? 'Create' : 'Update')}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ProfileForm;