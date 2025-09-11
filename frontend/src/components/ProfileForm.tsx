import React, { useState, useEffect } from 'react';
import {
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  Typography,
  Box,
  Alert,
  Grid,
  CircularProgress,
} from '../utils/mui';
import { ProfileCreate, ProfileUpdate } from 'chatter-sdk';
import { CrudFormProps } from './CrudDataTable';
import { FormDialog } from './BaseDialog';
import { useBaseForm } from '../hooks/useBaseForm';
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

const defaultProfileData = {
  name: '',
  description: '',
  llmModel: '',
  llmProvider: '',
  temperature: 0.7,
  max_tokens: 1000,
  top_p: 1.0,
  frequency_penalty: 0.0,
  presence_penalty: 0.0,
};

const ProfileForm: React.FC<ProfileFormProps> = ({
  open,
  mode,
  initialData,
  onClose,
  onSubmit,
}) => {
  const [loadingProviders, setLoadingProviders] = useState(false);
  const [providersData, setProvidersData] = useState<ProvidersData | null>(null);
  const [providersError, setProvidersError] = useState<string | null>(null);

  const {
    formData,
    updateFormData,
    isSubmitting,
    handleSubmit,
    handleClose,
  } = useBaseForm(
    {
      defaultData: defaultProfileData,
      transformInitialData: (data: any) => ({
        name: data.name || '',
        description: data.description || '',
        llmModel: data.llmModel || '',
        llmProvider: data.llmProvider || '',
        temperature: data.temperature ?? 0.7,
        max_tokens: data.max_tokens ?? 1000,
        top_p: data.top_p ?? 1.0,
        frequency_penalty: data.frequency_penalty ?? 0.0,
        presence_penalty: data.presence_penalty ?? 0.0,
      }),
    },
    open,
    mode,
    initialData
  );

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

  const handleFormSubmit = handleSubmit(async (data) => {
    // Transform camelCase form data to snake_case for API
    const apiData: ProfileCreate | ProfileUpdate = {
      name: data.name,
      description: data.description,
      llm_provider: data.llmProvider,
      llm_model: data.llmModel,
      temperature: data.temperature,
      max_tokens: data.max_tokens,
      top_p: data.top_p,
      frequency_penalty: data.frequency_penalty,
      presence_penalty: data.presence_penalty,
    };
    await onSubmit(apiData);
  });

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
    <FormDialog
      open={open}
      mode={mode}
      entityName="Profile"
      onClose={handleClose(onClose)}
      onSubmit={handleFormSubmit}
      maxWidth="md"
      isSubmitting={isSubmitting}
    >
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
            onChange={(e) => updateFormData({ name: e.target.value })}
            required
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6 }}>
          <FormControl fullWidth required>
            <InputLabel>Provider</InputLabel>
            <Select
              value={formData.llmProvider}
              label="Provider"
              onChange={(e) => updateFormData({
                llmProvider: e.target.value,
                llmModel: '' // Reset model when provider changes
              })}
              disabled={loadingProviders}
            >
              {loadingProviders ? (
                <MenuItem disabled>
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
            onChange={(e) => updateFormData({ description: e.target.value })}
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
              onChange={(e) => updateFormData({ llmModel: e.target.value })}
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
                onChange={(e) => updateFormData({ max_tokens: parseInt(e.target.value) || 0 })}
                inputProps={{ min: 1, max: 32000 }}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <Typography gutterBottom>Temperature: {formData.temperature}</Typography>
              <Slider
                value={formData.temperature}
                onChange={(_, value) => updateFormData({ temperature: value as number })}
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
                onChange={(_, value) => updateFormData({ top_p: value as number })}
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
                onChange={(_, value) => updateFormData({ frequency_penalty: value as number })}
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
                onChange={(_, value) => updateFormData({ presence_penalty: value as number })}
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
    </FormDialog>
  );
};

export default ProfileForm;