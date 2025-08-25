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
} from '@mui/material';
import Grid from '@mui/material/GridLegacy';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  Refresh as RefreshIcon,
  Code as CodeIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { chatterSDK } from '../services/chatter-sdk';
import { PromptResponse, PromptCreate, PromptUpdate } from '../sdk';

const PromptsPage: React.FC = () => {
  const [prompts, setPrompts] = useState<PromptResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [dialogError, setDialogError] = useState('');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingPrompt, setEditingPrompt] = useState<PromptResponse | null>(null);
  const [saving, setSaving] = useState(false);

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    content: '',
    category: 'general',
    prompt_type: 'template',
    variables: [] as string[],
  });

  const categories = ['general', 'chat', 'analysis', 'creative', 'technical', 'business'];
  const promptTypes = ['template', 'system', 'few_shot', 'chain_of_thought'];

  useEffect(() => {
    loadPrompts();
  }, []);

  const loadPrompts = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await chatterSDK.prompts.listPromptsApiV1PromptsGet({}); 
      const data = response.data;
      setPrompts(data.prompts);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load prompts');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (prompt?: PromptResponse) => {
    setDialogError(''); // Clear any previous dialog errors
    if (prompt) {
      setEditingPrompt(prompt);
      setFormData({
        name: prompt.name,
        description: prompt.description || '',
        content: prompt.content,
        category: prompt.category,
        prompt_type: prompt.prompt_type,
        variables: prompt.variables || [],
      });
    } else {
      setEditingPrompt(null);
      setFormData({
        name: '',
        description: '',
        content: '',
        category: 'general',
        prompt_type: 'template',
        variables: [],
      });
    }
    setDialogOpen(true);
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setDialogError(''); // Clear any previous dialog errors
      if (editingPrompt) {
        const response = await chatterSDK.prompts.updatePromptApiV1PromptsPromptIdPut({ promptId: editingPrompt.id, promptUpdate: formData as PromptUpdate });
        setPrompts(prev => prev.map(p => p.id === editingPrompt.id ? response.data : p));
      } else {
        const response = await chatterSDK.prompts.createPromptApiV1PromptsPost({ promptCreate: formData as PromptCreate });
        setPrompts(prev => [response.data, ...prev]);
      }
      setDialogOpen(false);
    } catch (err: any) {
      setDialogError(err.response?.data?.detail || 'Failed to save prompt');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (promptId: string) => {
    if (!window.confirm('Are you sure you want to delete this prompt?')) {
      return;
    }

    try {
      await chatterSDK.prompts.deletePromptApiV1PromptsPromptIdDelete({ promptId: promptId });
      setPrompts(prev => prev.filter(p => p.id !== promptId));
    } catch (err: any) {
      setError('Failed to delete prompt');
    }
  };

  const paginatedPrompts = prompts.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold' }}>
          Prompt Management
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadPrompts}
            disabled={loading}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
          >
            Create Prompt
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Category</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Variables</TableCell>
                <TableCell>Created</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {paginatedPrompts.map((prompt) => (
                <TableRow key={prompt.id} hover>
                  <TableCell>
                    <Box>
                      <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
                        {prompt.name}
                      </Typography>
                      {prompt.description && (
                        <Typography variant="body2" color="text.secondary">
                          {prompt.description}
                        </Typography>
                      )}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={prompt.category}
                      color="primary"
                      variant="outlined"
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={prompt.prompt_type}
                      color="secondary"
                      variant="outlined"
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                      {prompt.variables?.map((variable: string, index: number) => (
                        <Chip
                          key={index}
                          label={variable}
                          size="small"
                          variant="outlined"
                          icon={<CodeIcon />}
                        />
                      )) || '-'}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {format(new Date(prompt.created_at), 'MMM dd, yyyy')}
                    </Typography>
                  </TableCell>
                  <TableCell align="center">
                    <IconButton
                      size="small"
                      onClick={() => handleOpenDialog(prompt)}
                      color="primary"
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDelete(prompt.id)}
                      color="error"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={prompts.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={(_, newPage) => setPage(newPage)}
          onRowsPerPageChange={(e) => {
            setRowsPerPage(parseInt(e.target.value, 10));
            setPage(0);
          }}
        />
      </Card>

      {/* Create/Edit Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingPrompt ? 'Edit Prompt' : 'Create Prompt'}
        </DialogTitle>
        <DialogContent>
          {dialogError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {dialogError}
            </Alert>
          )}
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Category</InputLabel>
                <Select
                  value={formData.category}
                  label="Category"
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                >
                  {categories.map((category) => (
                    <MenuItem key={category} value={category}>
                      {category.charAt(0).toUpperCase() + category.slice(1)}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                multiline
                rows={2}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Type</InputLabel>
                <Select
                  value={formData.prompt_type}
                  label="Type"
                  onChange={(e) => setFormData({ ...formData, prompt_type: e.target.value })}
                >
                  {promptTypes.map((type) => (
                    <MenuItem key={type} value={type}>
                      {type.replace('_', ' ').split(' ').map(word => 
                        word.charAt(0).toUpperCase() + word.slice(1)
                      ).join(' ')}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Prompt Content"
                value={formData.content}
                onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                multiline
                rows={8}
                placeholder="Enter your prompt template here..."
                required
              />
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                Use {'{variable_name}'} for template variables
              </Typography>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)} disabled={saving}>
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            variant="contained"
            disabled={!formData.name || !formData.content || saving}
          >
            {saving ? 'Saving...' : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PromptsPage;
