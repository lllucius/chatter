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
  Switch,
  FormControlLabel,
  Box,
} from '@mui/material';
import { ProviderCreate, ProviderUpdate } from 'chatter-sdk';
import { CrudFormProps } from './CrudDataTable';

interface ProviderFormProps extends CrudFormProps<ProviderCreate, ProviderUpdate> {}

const ProviderForm: React.FC<ProviderFormProps> = ({
  open,
  mode,
  initialData,
  onClose,
  onSubmit,
}) => {
  const [formData, setFormData] = useState<ProviderCreate>({
    name: '',
    provider_type: 'openai',
    display_name: '',
    description: '',
    api_key_required: true,
    base_url: '',
    is_active: true,
  });

  const [saving, setSaving] = useState(false);

  const providerOptions = [
    { value: 'openai', label: 'OpenAI' },
    { value: 'anthropic', label: 'Anthropic' },
    { value: 'google', label: 'Google' },
    { value: 'cohere', label: 'Cohere' },
    { value: 'mistral', label: 'Mistral' },
  ];

  useEffect(() => {
    if (open) {
      if (mode === 'edit' && initialData) {
        // Defensive programming: Ensure all fields are properly extracted from initialData
        setFormData({
          name: initialData.name || '',
          provider_type: initialData.provider_type || 'openai',
          display_name: initialData.display_name || '',
          description: initialData.description ?? '',  // Use nullish coalescing for description
          api_key_required: initialData.api_key_required ?? true,  // Proper boolean handling
          base_url: initialData.base_url || '',
          is_active: initialData.is_active ?? true,  // Proper boolean handling
        });
      } else {
        // Reset to default values for create mode
        setFormData({
          name: '',
          provider_type: 'openai',
          display_name: '',
          description: '',
          api_key_required: true,
          base_url: '',
          is_active: true,
        });
      }
    }
  }, [open, mode, initialData]);

  const handleSubmit = async () => {
    try {
      setSaving(true);
      
      // Defensive programming: Ensure all fields are properly defined
      const safeFormData = {
        ...formData,
        display_name: formData.display_name ?? '',
        description: formData.description ?? '',
        base_url: formData.base_url || '',
        api_key_required: formData.api_key_required ?? true,
        is_active: formData.is_active ?? true,
      };
      
      await onSubmit(safeFormData);
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>{mode === 'edit' ? 'Edit Provider' : 'Add Provider'}</DialogTitle>
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
          <TextField
            fullWidth
            label="Name"
            required
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            disabled={mode === 'edit'}
            helperText={mode === 'edit' ? "Name cannot be changed after creation" : ""}
          />
          
          <FormControl fullWidth>
            <InputLabel>Provider Type</InputLabel>
            <Select
              value={formData.provider_type}
              onChange={(e) => setFormData({ ...formData, provider_type: e.target.value as any })}
              disabled={mode === 'edit'}
              label="Provider Type"
              helperText={mode === 'edit' ? "Provider type cannot be changed after creation" : ""}
            >
              {providerOptions.map((opt) => (
                <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <TextField
            fullWidth
            label="Display Name"
            required
            value={formData.display_name}
            onChange={(e) => setFormData({ ...formData, display_name: e.target.value })}
          />
          
          <TextField
            fullWidth
            label="Description"
            multiline
            rows={3}
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          />
          
          <TextField
            fullWidth
            label="Base URL (optional)"
            value={formData.base_url}
            onChange={(e) => setFormData({ ...formData, base_url: e.target.value })}
          />
          
          <FormControlLabel
            control={
              <Switch
                checked={formData.api_key_required}
                onChange={(e) => setFormData({ ...formData, api_key_required: e.target.checked })}
              />
            }
            label="API Key Required"
          />
          
          <FormControlLabel
            control={
              <Switch
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
              />
            }
            label="Active"
          />
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={saving}>Cancel</Button>
        <Button 
          variant="contained" 
          onClick={handleSubmit}
          disabled={!formData.name || !formData.display_name || saving}
        >
          {saving ? 'Saving...' : (mode === 'edit' ? 'Update Provider' : 'Create Provider')}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ProviderForm;
