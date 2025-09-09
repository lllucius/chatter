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
import { ModelDefCreate, ModelDefUpdate, Provider } from 'chatter-sdk';
import { CrudFormProps } from './CrudDataTable';

interface ModelFormProps extends CrudFormProps<ModelDefCreate, ModelDefUpdate> {
  providers: Provider[];
}

const ModelForm: React.FC<ModelFormProps> = ({
  open,
  mode,
  initialData,
  onClose,
  onSubmit,
  providers,
}) => {
  const [formData, setFormData] = useState<ModelDefCreate>({
    providerId: '',
    name: '',
    modelType: 'embedding' as any,
    displayName: '',
    description: '',
    modelName: '',
    dimensions: 1536,
    supportsBatch: true,
    isActive: true,
  });

  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (open) {
      if (mode === 'edit' && initialData) {
        setFormData({
          providerId: (initialData as any).providerId || '',
          name: (initialData as any).name || '',
          modelType: (initialData as any).modelType || 'embedding',
          displayName: initialData.displayName || '',
          description: initialData.description || '',
          modelName: (initialData as any).modelName || '',
          dimensions: initialData.dimensions,
          supportsBatch: initialData.supportsBatch ?? true,
          isActive: initialData.isActive ?? true,
        });
      } else {
        setFormData({
          providerId: providers[0]?.id || '',
          name: '',
          modelType: 'embedding' as any,
          displayName: '',
          description: '',
          modelName: '',
          dimensions: 1536,
          supportsBatch: true,
          isActive: true,
        });
      }
    }
  }, [open, mode, initialData, providers]);

  const handleSubmit = async () => {
    try {
      setSaving(true);
      await onSubmit(formData);
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>{mode === 'edit' ? 'Edit Model' : 'Add Model'}</DialogTitle>
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
          <FormControl fullWidth required>
            <InputLabel>Provider</InputLabel>
            <Select
              value={formData.providerId}
              onChange={(e) => setFormData({ ...formData, providerId: e.target.value })}
              disabled={mode === 'edit'}
              label="Provider"
              helperText={mode === 'edit' ? "Provider cannot be changed after creation" : ""}
            >
              {providers.map((p) => (
                <MenuItem key={p.id} value={p.id}>
                  {p.displayName}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          
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
            <InputLabel>Model Type</InputLabel>
            <Select
              value={formData.modelType}
              onChange={(e) => {
                const modelType = e.target.value as ModelDefCreate['modelType'];
                setFormData((f) => ({
                  ...f,
                  modelType,
                  dimensions: modelType === 'embedding' ? (f.dimensions ?? 1536) : undefined,
                }));
              }}
              disabled={mode === 'edit'}
              label="Model Type"
              helperText={mode === 'edit' ? "Model type cannot be changed after creation" : ""}
            >
              <MenuItem value="embedding">Embedding</MenuItem>
              <MenuItem value="llm">LLM</MenuItem>
            </Select>
          </FormControl>
          
          <TextField
            fullWidth
            label="Display Name"
            required
            value={formData.displayName}
            onChange={(e) => setFormData({ ...formData, displayName: e.target.value })}
          />
          
          <TextField
            fullWidth
            label="Model Name (API)"
            required
            value={formData.modelName}
            onChange={(e) => setFormData({ ...formData, modelName: e.target.value })}
          />
          
          {formData.modelType === 'embedding' && (
            <TextField
              fullWidth
              type="number"
              label="Dimensions"
              value={formData.dimensions ?? 1536}
              onChange={(e) => setFormData({ ...formData, dimensions: parseInt(e.target.value) || 0 })}
            />
          )}
          
          <TextField
            fullWidth
            label="Description"
            multiline
            rows={3}
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          />
          
          <FormControlLabel
            control={
              <Switch
                checked={formData.supportsBatch}
                onChange={(e) => setFormData({ ...formData, supportsBatch: e.target.checked })}
              />
            }
            label="Supports Batch"
          />
          
          <FormControlLabel
            control={
              <Switch
                checked={formData.isActive}
                onChange={(e) => setFormData({ ...formData, isActive: e.target.checked })}
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
          disabled={!formData.name || !formData.displayName || !formData.modelName || saving}
        >
          {saving ? 'Saving...' : (mode === 'edit' ? 'Update Model' : 'Create Model')}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ModelForm;