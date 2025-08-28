import React, { useEffect, useMemo, useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Chip,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Switch,
  FormControlLabel,
  Alert,
  Snackbar,
  Tooltip,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import {
  Add as AddIcon,
  Refresh as RefreshIcon,
  Star as DefaultIcon,
  StarBorder as NotDefaultIcon,
} from '@mui/icons-material';

import { chatterSDK } from '../services/chatter-sdk';
import {
  listProviders,
  createProvider,
  listModels,
  createModel,
  listEmbeddingSpaces,
  createEmbeddingSpace,
  setDefaultProvider,
  setDefaultModel,
  setDefaultEmbeddingSpace,
  Provider,
  ModelDef,
  EmbeddingSpace,
  CreateProvider,
  CreateModel,
  CreateEmbeddingSpace,
} from '../sdk';

type TabKey = 'providers' | 'models' | 'spaces';

const ModelManagementPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabKey>('providers');

  const [providers, setProviders] = useState<Provider[]>([]);
  const [models, setModels] = useState<ModelDef[]>([]);
  const [spaces, setSpaces] = useState<EmbeddingSpace[]>([]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');

  // Dialogs
  const [providerDialogOpen, setProviderDialogOpen] = useState(false);
  const [modelDialogOpen, setModelDialogOpen] = useState(false);
  const [spaceDialogOpen, setSpaceDialogOpen] = useState(false);

  // Forms
  const [providerForm, setProviderForm] = useState<CreateProvider>({
    name: '',
    provider_type: 'openai',
    display_name: '',
    description: '',
    api_key_required: true,
    base_url: '',
    is_active: true,
  });

  const providerOptions = [
    { value: 'openai', label: 'OpenAI' },
    { value: 'anthropic', label: 'Anthropic' },
    { value: 'google', label: 'Google' },
    { value: 'cohere', label: 'Cohere' },
    { value: 'mistral', label: 'Mistral' },
  ];

  const [modelForm, setModelForm] = useState<CreateModel>({
    provider_id: '',
    name: '',
    model_type: 'embedding',
    display_name: '',
    description: '',
    model_name: '',
    dimensions: 1536,
    supports_batch: true,
    is_active: true,
  });

  const [spaceForm, setSpaceForm] = useState<CreateEmbeddingSpace>({
    model_id: '',
    name: '',
    display_name: '',
    description: '',
    base_dimensions: 1536,
    effective_dimensions: 1536,
    reduction_strategy: 'none',
    distance_metric: 'cosine',
    table_name: '',
    index_type: 'hnsw',
    normalize_vectors: true,
    is_active: true,
  });

  const embeddingModels = useMemo(
    () => models.filter((m) => m.model_type === 'embedding'),
    [models]
  );

  const showSnackbar = (message: string) => {
    setSnackbarMessage(message);
    setSnackbarOpen(true);
  };

  const loadData = async () => {
    setLoading(true);
    setError('');
    try {
      const [p, m, s] = await Promise.all([
        listProviders(),
        listModels(),
        listEmbeddingSpaces(),
      ]);
      setProviders(p.items);
      setModels(m.items);
      setSpaces(s.items);
    } catch (e: any) {
      console.error(e);
      setError(e?.message || 'Failed to load model registry data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Defaults for dialogs
  useEffect(() => {
    if (providerDialogOpen) {
      setProviderForm((f) => ({
        ...f,
        provider_type: f.provider_type || 'openai',
        api_key_required: f.api_key_required ?? true,
        is_active: f.is_active ?? true,
      }));
    }
  }, [providerDialogOpen]);

  useEffect(() => {
    if (modelDialogOpen) {
      setModelForm((f) => ({
        ...f,
        provider_id: f.provider_id || providers[0]?.id || '',
        model_type: f.model_type || 'embedding',
        supports_batch: f.supports_batch ?? true,
        is_active: f.is_active ?? true,
        dimensions:
          f.model_type === 'embedding'
            ? f.dimensions ?? 1536
            : undefined,
      }));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [modelDialogOpen, providers]);

  useEffect(() => {
    if (spaceDialogOpen) {
      const firstEmbedding = embeddingModels[0];
      setSpaceForm((f) => ({
        ...f,
        model_id: f.model_id || firstEmbedding?.id || '',
        base_dimensions: f.base_dimensions ?? (firstEmbedding?.dimensions || 1536),
        effective_dimensions: f.effective_dimensions ?? (firstEmbedding?.dimensions || 1536),
        reduction_strategy: f.reduction_strategy || 'none',
        distance_metric: f.distance_metric || 'cosine',
        index_type: f.index_type || 'hnsw',
        normalize_vectors: f.normalize_vectors ?? true,
        is_active: f.is_active ?? true,
      }));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [spaceDialogOpen, embeddingModels]);

  const handleCreateProvider = async () => {
    try {
      await createProvider(providerForm);
      setProviderDialogOpen(false);
      showSnackbar('Provider created');
      loadData();
    } catch (e: any) {
      setError(e?.message || 'Failed to create provider');
    }
  };

  const handleCreateModel = async () => {
    try {
      await createModel(modelForm);
      setModelDialogOpen(false);
      showSnackbar('Model created');
      loadData();
    } catch (e: any) {
      setError(e?.message || 'Failed to create model');
    }
  };

  const handleCreateSpace = async () => {
    try {
      await createEmbeddingSpace(spaceForm);
      setSpaceDialogOpen(false);
      showSnackbar('Embedding space created');
      loadData();
    } catch (e: any) {
      setError(e?.message || 'Failed to create embedding space');
    }
  };

  const handleSetDefaultProvider = async (id: string, provider_type: string) => {
    try {
      await setDefaultProvider(id, provider_type);
      showSnackbar('Default provider updated');
      loadData();
    } catch (e: any) {
      setError(e?.message || 'Failed to set default provider');
    }
  };

  const handleSetDefaultModel = async (id: string) => {
    try {
      await setDefaultModel(id);
      showSnackbar('Default model updated');
      loadData();
    } catch (e: any) {
      setError(e?.message || 'Failed to set default model');
    }
  };

  const handleSetDefaultSpace = async (id: string) => {
    try {
      await setDefaultEmbeddingSpace(id);
      showSnackbar('Default embedding space updated');
      loadData();
    } catch (e: any) {
      setError(e?.message || 'Failed to set default embedding space');
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold' }}>
          Model Management
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadData}
            disabled={loading}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Tabs
        value={activeTab}
        onChange={(_, v) => setActiveTab(v)}
        variant="scrollable"
        scrollButtons="auto"
        sx={{ mb: 2 }}
      >
        <Tab value="providers" label="Providers" />
        <Tab value="models" label="Models" />
        <Tab value="spaces" label="Embedding Spaces" />
      </Tabs>

      {/* Providers */}
      {activeTab === 'providers' && (
        <Box>
          <Box sx={{ mb: 2 }}>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setProviderDialogOpen(true)}
            >
              Add Provider
            </Button>
          </Box>

          {loading ? (
            <List>
              <ListItem>
                <CircularProgress size={20} sx={{ mr: 2 }} />
                <ListItemText primary="Loading providers..." />
              </ListItem>
            </List>
          ) : providers.length === 0 ? (
            <List>
              <ListItem>
                <ListItemText
                  primary="No providers found"
                  secondary="Add a provider to get started"
                />
              </ListItem>
            </List>
          ) : (
            <List>
              {providers.map((p) => (
                <ListItem key={p.id} sx={{ bgcolor: 'background.paper', mb: 1, borderRadius: 1 }}>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                          {p.display_name}
                        </Typography>
                        <Chip
                          size="small"
                          label={p.is_active ? 'Active' : 'Inactive'}
                          color={p.is_active ? 'success' : 'default'}
                        />
                        {p.is_default && (
                          <Chip size="small" label="Default" color="primary" />
                        )}
                      </Box>
                    }
                    secondary={
                      <>
                        <Typography variant="body2" color="text.secondary">
                          {p.name} ({p.provider_type})
                        </Typography>
                        {p.description && (
                          <Typography variant="body2" color="text.secondary">
                            {p.description}
                          </Typography>
                        )}
                      </>
                    }
                  />
                  <ListItemSecondaryAction>
                    {!p.is_default && (
                      <Tooltip title="Set as default">
                        <IconButton onClick={() => handleSetDefaultProvider(p.id, p.provider_type)}>
                          <NotDefaultIcon />
                        </IconButton>
                      </Tooltip>
                    )}
                    {p.is_default && (
                      <Tooltip title="Default provider">
                        <span>
                          <IconButton disabled>
                            <DefaultIcon color="primary" />
                          </IconButton>
                        </span>
                      </Tooltip>
                    )}
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          )}
        </Box>
      )}

      {/* Models */}
      {activeTab === 'models' && (
        <Box>
          <Box sx={{ mb: 2 }}>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setModelDialogOpen(true)}
              disabled={providers.length === 0}
            >
              Add Model
            </Button>
            {providers.length === 0 && (
              <Typography variant="body2" color="text.secondary" sx={{ ml: 2, display: 'inline' }}>
                Add a provider first to create models
              </Typography>
            )}
          </Box>

          {loading ? (
            <List>
              <ListItem>
                <CircularProgress size={20} sx={{ mr: 2 }} />
                <ListItemText primary="Loading models..." />
              </ListItem>
            </List>
          ) : models.length === 0 ? (
            <List>
              <ListItem>
                <ListItemText
                  primary="No models found"
                  secondary="Add a model to get started"
                />
              </ListItem>
            </List>
          ) : (
            <List>
              {models.map((m) => (
                <ListItem key={m.id} sx={{ bgcolor: 'background.paper', mb: 1, borderRadius: 1 }}>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                          {m.display_name}
                        </Typography>
                        <Chip
                          size="small"
                          label={m.is_active ? 'Active' : 'Inactive'}
                          color={m.is_active ? 'success' : 'default'}
                        />
                        {m.is_default && (
                          <Chip size="small" label="Default" color="primary" />
                        )}
                      </Box>
                    }
                    secondary={
                      <Grid container spacing={0.5}>
                      <Grid
                        size={{
                          xs: 12,
                          sm: 6,
                          md: 3
                        }}>
                          <Typography variant="body2" color="text.secondary">
                            {m.name} ({m.model_type}) • Provider: {m.provider?.display_name || '—'}
                          </Typography>
                        </Grid>
                      <Grid
                        size={{
                          xs: 12,
                          sm: 6,
                          md: 3
                        }}>
                          <Typography variant="body2" color="text.secondary">
                            API Model: {m.model_name}{' '}
                            {m.dimensions ? `• Dimensions: ${m.dimensions}` : ''}
                          </Typography>
                        </Grid>
                        {m.description && (
                        <Grid
                          size={{
                            xs: 12,
                            sm: 6,
                            md: 3
                          }}>
                            <Typography variant="body2" color="text.secondary">
                              {m.description}
                            </Typography>
                          </Grid>
                        )}
                      </Grid>
                    }
                  />
                  <ListItemSecondaryAction>
                    {!m.is_default && (
                      <Tooltip title="Set as default">
                        <IconButton onClick={() => handleSetDefaultModel(m.id)}>
                          <NotDefaultIcon />
                        </IconButton>
                      </Tooltip>
                    )}
                    {m.is_default && (
                      <Tooltip title="Default model">
                        <span>
                          <IconButton disabled>
                            <DefaultIcon color="primary" />
                          </IconButton>
                        </span>
                      </Tooltip>
                    )}
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          )}
        </Box>
      )}

      {/* Embedding Spaces */}
      {activeTab === 'spaces' && (
        <Box>
          <Box sx={{ mb: 2 }}>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setSpaceDialogOpen(true)}
              disabled={embeddingModels.length === 0}
            >
              Add Embedding Space
            </Button>
            {embeddingModels.length === 0 && (
              <Typography variant="body2" color="text.secondary" sx={{ ml: 2, display: 'inline' }}>
                Create an embedding model first
              </Typography>
            )}
          </Box>

          {loading ? (
            <List>
              <ListItem>
                <CircularProgress size={20} sx={{ mr: 2 }} />
                <ListItemText primary="Loading embedding spaces..." />
              </ListItem>
            </List>
          ) : spaces.length === 0 ? (
            <List>
              <ListItem>
                <ListItemText
                  primary="No embedding spaces found"
                  secondary="Add an embedding space to get started"
                />
              </ListItem>
            </List>
          ) : (
            <List>
              {spaces.map((s) => (
                <ListItem key={s.id} sx={{ bgcolor: 'background.paper', mb: 1, borderRadius: 1 }}>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                          {s.display_name}
                        </Typography>
                        <Chip
                          size="small"
                          label={s.is_active ? 'Active' : 'Inactive'}
                          color={s.is_active ? 'success' : 'default'}
                        />
                        {s.is_default && (
                          <Chip size="small" label="Default" color="primary" />
                        )}
                      </Box>
                    }
                    secondary={
                      <Grid container spacing={0.5}>
                        <Grid
                          size={{
                            xs: 12,
                            sm: 6,
                            md: 3
                          }}>
                          <Typography variant="body2" color="text.secondary">
                            {s.name} • Model: {s.model?.display_name || '—'}
                          </Typography>
                        </Grid>
                        <Grid
                          size={{
                            xs: 12,
                            sm: 6,
                            md: 3
                          }}>
                          <Typography variant="body2" color="text.secondary">
                            Dimensions: {s.base_dimensions} → {s.effective_dimensions} • Strategy: {s.reduction_strategy} • Metric: {s.distance_metric} • Index: {s.index_type}
                          </Typography>
                        </Grid>
                        <Grid
                          size={{
                            xs: 12,
                            sm: 6,
                            md: 3
                          }}>
                          <Typography variant="body2" color="text.secondary">
                            Table: {s.table_name}
                          </Typography>
                        </Grid>
                        {s.description && (
                          <Grid
                            size={{
                              xs: 12,
                              sm: 6,
                              md: 3
                            }}>
                            <Typography variant="body2" color="text.secondary">
                              {s.description}
                            </Typography>
                          </Grid>
                        )}
                      </Grid>
                    }
                  />
                  <ListItemSecondaryAction>
                    {!s.is_default && (
                      <Tooltip title="Set as default">
                        <IconButton onClick={() => handleSetDefaultSpace(s.id)}>
                          <NotDefaultIcon />
                        </IconButton>
                      </Tooltip>
                    )}
                    {s.is_default && (
                      <Tooltip title="Default space">
                        <span>
                          <IconButton disabled>
                            <DefaultIcon color="primary" />
                          </IconButton>
                        </span>
                      </Tooltip>
                    )}
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          )}
        </Box>
      )}

      {/* Provider Dialog */}
      <Dialog open={providerDialogOpen} onClose={() => setProviderDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Provider</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Name"
            margin="normal"
            required
            value={providerForm.name}
            onChange={(e) => setProviderForm({ ...providerForm, name: e.target.value })}
          />
          <TextField
            select
            fullWidth
            label="Provider Type"
            margin="normal"
            value={providerForm.provider_type}
            onChange={(e) => setProviderForm({ ...providerForm, provider_type: e.target.value as any })}
          >
            {providerOptions.map((opt) => (
              <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
            ))}
          </TextField>
          <TextField
            fullWidth
            label="Display Name"
            margin="normal"
            required
            value={providerForm.display_name}
            onChange={(e) => setProviderForm({ ...providerForm, display_name: e.target.value })}
          />
          <TextField
            fullWidth
            label="Description"
            margin="normal"
            multiline
            rows={3}
            value={providerForm.description}
            onChange={(e) => setProviderForm({ ...providerForm, description: e.target.value })}
          />
          <TextField
            fullWidth
            label="Base URL (optional)"
            margin="normal"
            value={providerForm.base_url}
            onChange={(e) => setProviderForm({ ...providerForm, base_url: e.target.value })}
          />
          <FormControlLabel
            control={
              <Switch
                checked={providerForm.api_key_required}
                onChange={(e) => setProviderForm({ ...providerForm, api_key_required: e.target.checked })}
              />
            }
            label="API Key Required"
          />
          <FormControlLabel
            control={
              <Switch
                checked={providerForm.is_active}
                onChange={(e) => setProviderForm({ ...providerForm, is_active: e.target.checked })}
              />
            }
            label="Active"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setProviderDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleCreateProvider}>Create Provider</Button>
        </DialogActions>
      </Dialog>

      {/* Model Dialog */}
      <Dialog open={modelDialogOpen} onClose={() => setModelDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Model</DialogTitle>
        <DialogContent>
          <TextField
            select
            fullWidth
            label="Provider"
            margin="normal"
            required
            value={modelForm.provider_id}
            onChange={(e) => setModelForm({ ...modelForm, provider_id: e.target.value })}
          >
            {providers.map((p) => (
              <MenuItem key={p.id} value={p.id}>
                {p.display_name}
              </MenuItem>
            ))}
          </TextField>
          <TextField
            fullWidth
            label="Name"
            margin="normal"
            required
            value={modelForm.name}
            onChange={(e) => setModelForm({ ...modelForm, name: e.target.value })}
          />
          <TextField
            select
            fullWidth
            label="Model Type"
            margin="normal"
            value={modelForm.model_type}
            onChange={(e) => {
              const model_type = e.target.value as CreateModel['model_type'];
              setModelForm((f) => ({
                ...f,
                model_type,
                dimensions: model_type === 'embedding' ? (f.dimensions ?? 1536) : undefined,
              }));
            }}
          >
            <MenuItem value="embedding">Embedding</MenuItem>
            <MenuItem value="llm">LLM</MenuItem>
          </TextField>
          <TextField
            fullWidth
            label="Display Name"
            margin="normal"
            required
            value={modelForm.display_name}
            onChange={(e) => setModelForm({ ...modelForm, display_name: e.target.value })}
          />
          <TextField
            fullWidth
            label="Model Name (API)"
            margin="normal"
            required
            value={modelForm.model_name}
            onChange={(e) => setModelForm({ ...modelForm, model_name: e.target.value })}
          />
          {modelForm.model_type === 'embedding' && (
            <TextField
              fullWidth
              type="number"
              label="Dimensions"
              margin="normal"
              value={modelForm.dimensions ?? 1536}
              onChange={(e) => setModelForm({ ...modelForm, dimensions: parseInt(e.target.value) || 0 })}
            />
          )}
          <TextField
            fullWidth
            label="Description"
            margin="normal"
            multiline
            rows={3}
            value={modelForm.description}
            onChange={(e) => setModelForm({ ...modelForm, description: e.target.value })}
          />
          <FormControlLabel
            control={
              <Switch
                checked={modelForm.supports_batch}
                onChange={(e) => setModelForm({ ...modelForm, supports_batch: e.target.checked })}
              />
            }
            label="Supports Batch"
          />
          <FormControlLabel
            control={
              <Switch
                checked={modelForm.is_active}
                onChange={(e) => setModelForm({ ...modelForm, is_active: e.target.checked })}
              />
            }
            label="Active"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setModelDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleCreateModel}>Create Model</Button>
        </DialogActions>
      </Dialog>

      {/* Embedding Space Dialog */}
      <Dialog open={spaceDialogOpen} onClose={() => setSpaceDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Embedding Space</DialogTitle>
        <DialogContent>
          <TextField
            select
            fullWidth
            label="Embedding Model"
            margin="normal"
            required
            value={spaceForm.model_id}
            onChange={(e) => setSpaceForm({ ...spaceForm, model_id: e.target.value })}
          >
            {embeddingModels.map((m) => (
              <MenuItem key={m.id} value={m.id}>
                {m.display_name} {m.dimensions ? `(${m.dimensions}d)` : ''}
              </MenuItem>
            ))}
          </TextField>
          <TextField
            fullWidth
            label="Name"
            margin="normal"
            required
            value={spaceForm.name}
            onChange={(e) => setSpaceForm({ ...spaceForm, name: e.target.value })}
          />
          <TextField
            fullWidth
            label="Display Name"
            margin="normal"
            required
            value={spaceForm.display_name}
            onChange={(e) => setSpaceForm({ ...spaceForm, display_name: e.target.value })}
          />
          <TextField
            fullWidth
            label="Table Name"
            margin="normal"
            required
            value={spaceForm.table_name}
            onChange={(e) => setSpaceForm({ ...spaceForm, table_name: e.target.value })}
          />
          <Grid container spacing={2} sx={{ mt: 0 }}>
            <Grid
              size={{
                xs: 12,
                sm: 6,
                md: 3
              }}>
              <TextField
                fullWidth
                type="number"
                label="Base Dimensions"
                margin="normal"
                required
                value={spaceForm.base_dimensions}
                onChange={(e) => setSpaceForm({ ...spaceForm, base_dimensions: parseInt(e.target.value) || 0 })}
              />
            </Grid>
            <Grid
              size={{
                xs: 12,
                sm: 6,
                md: 3
              }}>
              <TextField
                fullWidth
                type="number"
                label="Effective Dimensions"
                margin="normal"
                required
                value={spaceForm.effective_dimensions}
                onChange={(e) => setSpaceForm({ ...spaceForm, effective_dimensions: parseInt(e.target.value) || 0 })}
              />
            </Grid>
          </Grid>
          <Grid container spacing={2}>
            <Grid
              size={{
                xs: 12,
                sm: 6,
                md: 3
              }}>
              <TextField
                select
                fullWidth
                label="Reduction Strategy"
                margin="normal"
                value={spaceForm.reduction_strategy}
                onChange={(e) => setSpaceForm({ ...spaceForm, reduction_strategy: e.target.value as any })}
              >
                <MenuItem value="none">None</MenuItem>
                <MenuItem value="truncate">Truncate</MenuItem>
                <MenuItem value="reducer">Reducer (PCA/SVD)</MenuItem>
              </TextField>
            </Grid>
            <Grid
              size={{
                xs: 12,
                sm: 6,
                md: 3
              }}>
              <TextField
                select
                fullWidth
                label="Distance Metric"
                margin="normal"
                value={spaceForm.distance_metric}
                onChange={(e) => setSpaceForm({ ...spaceForm, distance_metric: e.target.value as any })}
              >
                <MenuItem value="cosine">Cosine</MenuItem>
                <MenuItem value="l2">L2 (Euclidean)</MenuItem>
                <MenuItem value="ip">Inner Product</MenuItem>
              </TextField>
            </Grid>
          </Grid>
          {spaceForm.reduction_strategy === 'reducer' && (
            <TextField
              fullWidth
              label="Reducer Path"
              margin="normal"
              placeholder="Path to joblib reducer file"
              value={spaceForm.reducer_path || ''}
              onChange={(e) => setSpaceForm({ ...spaceForm, reducer_path: e.target.value })}
            />
          )}
          <Grid container spacing={2}>
            <Grid
              size={{
                xs: 12,
                sm: 6,
                md: 3
              }}>
              <TextField
                select
                fullWidth
                label="Index Type"
                margin="normal"
                value={spaceForm.index_type}
                onChange={(e) => setSpaceForm({ ...spaceForm, index_type: e.target.value as any })}
              >
                <MenuItem value="hnsw">HNSW</MenuItem>
                <MenuItem value="ivfflat">IVFFlat</MenuItem>
              </TextField>
            </Grid>
          </Grid>
          <TextField
            fullWidth
            label="Description"
            margin="normal"
            multiline
            rows={3}
            value={spaceForm.description}
            onChange={(e) => setSpaceForm({ ...spaceForm, description: e.target.value })}
          />
          <FormControlLabel
            control={
              <Switch
                checked={spaceForm.normalize_vectors}
                onChange={(e) => setSpaceForm({ ...spaceForm, normalize_vectors: e.target.checked })}
              />
            }
            label="Normalize Vectors"
          />
          <FormControlLabel
            control={
              <Switch
                checked={spaceForm.is_active}
                onChange={(e) => setSpaceForm({ ...spaceForm, is_active: e.target.checked })}
              />
            }
            label="Active"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSpaceDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleCreateSpace}>Create Embedding Space</Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={() => setSnackbarOpen(false)}
        message={snackbarMessage}
      />
    </Box>
  );
};

export default ModelManagementPage;
