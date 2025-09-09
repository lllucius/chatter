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
  Box,
  Chip,
  Typography,
} from '@mui/material';
import { PromptCreate, PromptUpdate } from 'chatter-sdk';
import { CrudFormProps } from './CrudDataTable';

interface PromptFormProps extends CrudFormProps<PromptCreate, PromptUpdate> {}

const PromptForm: React.FC<PromptFormProps> = ({
  open,
  mode,
  initialData,
  onClose,
  onSubmit,
}) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    content: '',
    category: 'general',
    prompt_type: 'template' as 'template' | 'system' | 'few_shot' | 'chain_of_thought',
    variables: [] as string[],
  });

  const [variableInput, setVariableInput] = useState('');
  const [saving, setSaving] = useState(false);

  const categories = ['general', 'chat', 'analysis', 'creative', 'technical', 'business'];
  const promptTypes: Array<'template' | 'system' | 'few_shot' | 'chain_of_thought'> = 
    ['template', 'system', 'few_shot', 'chain_of_thought'];

  useEffect(() => {
    if (open) {
      if (mode === 'edit' && initialData) {
        setFormData({
          name: initialData.name || '',
          description: initialData.description || '',
          content: initialData.content || '',
          category: initialData.category || 'general',
          prompt_type: (initialData.prompt_type || 'template') as any,
          variables: initialData.variables || [],
        });
      } else {
        setFormData({
          name: '',
          description: '',
          content: '',
          category: 'general',
          prompt_type: 'template',
          variables: [],
        });
      }
      setVariableInput('');
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

  const handleAddVariable = () => {
    if (variableInput.trim() && !formData.variables.includes(variableInput.trim())) {
      setFormData({
        ...formData,
        variables: [...formData.variables, variableInput.trim()],
      });
      setVariableInput('');
    }
  };

  const handleRemoveVariable = (variable: string) => {
    setFormData({
      ...formData,
      variables: formData.variables.filter(v => v !== variable),
    });
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      handleAddVariable();
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {mode === 'create' ? 'Create Prompt' : 'Edit Prompt'}
      </DialogTitle>
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
          <TextField
            label="Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            fullWidth
            required
          />

          <TextField
            label="Description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            fullWidth
            multiline
            rows={2}
          />

          <FormControl fullWidth>
            <InputLabel>Category</InputLabel>
            <Select
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              label="Category"
            >
              {categories.map((category) => (
                <MenuItem key={category} value={category}>
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl fullWidth>
            <InputLabel>Type</InputLabel>
            <Select
              value={formData.prompt_type}
              onChange={(e) => setFormData({ ...formData, prompt_type: e.target.value as any })}
              label="Type"
            >
              {promptTypes.map((type) => (
                <MenuItem key={type} value={type}>
                  {type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <TextField
            label="Content"
            value={formData.content}
            onChange={(e) => setFormData({ ...formData, content: e.target.value })}
            fullWidth
            multiline
            rows={6}
            required
            placeholder="Enter your prompt template here..."
          />

          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Variables
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
              {formData.variables.map((variable) => (
                <Chip
                  key={variable}
                  label={variable}
                  onDelete={() => handleRemoveVariable(variable)}
                  color="primary"
                  variant="outlined"
                />
              ))}
            </Box>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <TextField
                label="Add Variable"
                value={variableInput}
                onChange={(e) => setVariableInput(e.target.value)}
                onKeyPress={handleKeyPress}
                size="small"
                placeholder="e.g., user_input, context"
              />
              <Button variant="outlined" onClick={handleAddVariable}>
                Add
              </Button>
            </Box>
          </Box>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={saving}>
          Cancel
        </Button>
        <Button 
          onClick={handleSubmit} 
          variant="contained" 
          disabled={saving || !formData.name.trim() || !formData.content.trim()}
        >
          {saving ? 'Saving...' : (mode === 'create' ? 'Create' : 'Update')}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default PromptForm;