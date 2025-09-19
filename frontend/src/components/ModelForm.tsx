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
  FormHelperText,
  Box,
} from '@mui/material';
import {
  ModelDefCreate,
  ModelDefUpdate,
  Provider,
  ModelType,
} from 'chatter-sdk';
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
    provider_id: '',
    name: '',
    model_type: ModelType.embedding,
    display_name: '',
    description: '',
    model_name: '',
    dimensions: 1536,
    supports_batch: true,
    is_active: true,
  });

  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (open) {
      if (mode === 'edit' && initialData) {
        setFormData({
          provider_id: '',
          name: '',
          model_type: ModelType.embedding,
          display_name: initialData.display_name || '',
          description: initialData.description || '',
          model_name: initialData.model_name || '',
          dimensions: initialData.dimensions || 1536,
          supports_batch: initialData.supports_batch ?? true,
          is_active: initialData.is_active ?? true,
        });
      } else {
        setFormData({
          provider_id: providers[0]?.id || '',
          name: '',
          model_type: ModelType.embedding,
          display_name: '',
          description: '',
          model_name: '',
          dimensions: 1536,
          supports_batch: true,
          is_active: true,
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
              value={formData.provider_id}
              onChange={(e) =>
                setFormData({ ...formData, provider_id: e.target.value })
              }
              disabled={mode === 'edit'}
              label="Provider"
            >
              {providers.length === 0 ? (
                <MenuItem disabled value="">
                  No active providers available
                </MenuItem>
              ) : (
                providers.map((p) => (
                  <MenuItem key={p.id} value={p.id}>
                    {p.display_name}
                  </MenuItem>
                ))
              )}
            </Select>
            {mode === 'edit' && (
              <FormHelperText>
                Provider cannot be changed after creation
              </FormHelperText>
            )}
          </FormControl>

          <TextField
            fullWidth
            label="Name"
            required
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            disabled={mode === 'edit'}
            helperText={
              mode === 'edit' ? 'Name cannot be changed after creation' : ''
            }
          />

          <FormControl fullWidth>
            <InputLabel>Model Type</InputLabel>
            <Select
              value={formData.model_type}
              onChange={(e) => {
                const modelType = e.target
                  .value as ModelDefCreate['model_type'];
                setFormData((f) => ({
                  ...f,
                  model_type: modelType,
                  dimensions:
                    modelType === 'embedding'
                      ? (f.dimensions ?? 1536)
                      : undefined,
                }));
              }}
              disabled={mode === 'edit'}
              label="Model Type"
            >
              <MenuItem value="embedding">Embedding</MenuItem>
              <MenuItem value="llm">LLM</MenuItem>
            </Select>
            {mode === 'edit' && (
              <FormHelperText>
                Model type cannot be changed after creation
              </FormHelperText>
            )}
          </FormControl>

          <TextField
            fullWidth
            label="Display Name"
            required
            value={formData.display_name}
            onChange={(e) =>
              setFormData({ ...formData, display_name: e.target.value })
            }
          />

          <TextField
            fullWidth
            label="Model Name (API)"
            required
            value={formData.model_name}
            onChange={(e) =>
              setFormData({ ...formData, model_name: e.target.value })
            }
          />

          {formData.model_type === 'embedding' && (
            <TextField
              fullWidth
              type="number"
              label="Dimensions"
              value={formData.dimensions ?? 1536}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  dimensions: parseInt(e.target.value) || 0,
                })
              }
            />
          )}

          <TextField
            fullWidth
            label="Description"
            multiline
            rows={3}
            value={formData.description}
            onChange={(e) =>
              setFormData({ ...formData, description: e.target.value })
            }
          />

          <FormControlLabel
            control={
              <Switch
                checked={formData.supports_batch}
                onChange={(e) =>
                  setFormData({ ...formData, supports_batch: e.target.checked })
                }
              />
            }
            label="Supports Batch"
          />

          <FormControlLabel
            control={
              <Switch
                checked={formData.is_active}
                onChange={(e) =>
                  setFormData({ ...formData, is_active: e.target.checked })
                }
              />
            }
            label="Active"
          />
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={saving}>
          Cancel
        </Button>
        <Button
          variant="contained"
          onClick={handleSubmit}
          disabled={
            !formData.name ||
            !formData.display_name ||
            !formData.model_name ||
            providers.length === 0 ||
            saving
          }
        >
          {saving
            ? 'Saving...'
            : mode === 'edit'
              ? 'Update Model'
              : 'Create Model'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ModelForm;
