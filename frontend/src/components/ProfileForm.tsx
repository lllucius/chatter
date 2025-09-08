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
} from '@mui/material';
import Grid from '@mui/material/Grid';
import { ProfileCreate, ProfileUpdate } from '../sdk';
import { CrudFormProps } from './CrudDataTable';

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

  const providers = ['openai', 'anthropic', 'google', 'cohere'];
  const models = {
    openai: ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo'],
    anthropic: ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku'],
    google: ['gemini-pro', 'gemini-pro-vision'],
    cohere: ['command', 'command-light'],
  };

  useEffect(() => {
    if (open) {
      if (mode === 'edit' && initialData) {
        setFormData({
          name: initialData.name || '',
          description: initialData.description || '',
          llmModel: initialData.llmModel || '',
          llmProvider: initialData.llmProvider || '',
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
      await onSubmit(formData);
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {mode === 'create' ? 'Create Profile' : 'Edit Profile'}
      </DialogTitle>
      <DialogContent>
        <Box sx={{ pt: 1 }}>
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
            <Grid size={{ xs: 12, sm: 6 }}>
              <FormControl fullWidth required>
                <InputLabel>Model</InputLabel>
                <Select
                  value={formData.llmModel}
                  label="Model"
                  onChange={(e) => setFormData({ ...formData, llmModel: e.target.value })}
                  disabled={!formData.llmProvider}
                >
                  {formData.llmProvider && models[formData.llmProvider as keyof typeof models]?.map((model) => (
                    <MenuItem key={model} value={model}>
                      {model}
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