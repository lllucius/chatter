import React, { useEffect, useMemo, useState, useCallback } from 'react';
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
  Edit as EditIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { chatterSDK } from '../services/chatter-sdk';
import {
  Provider,
  ProviderCreate,
  ProviderUpdate,
  ModelDefCreate,
  ModelDefUpdate,
  ModelDefWithProvider,
  EmbeddingSpaceCreate,
  EmbeddingSpaceUpdate,
  EmbeddingSpaceWithModel,
  DefaultProvider,
} from '../sdk';

type TabKey = 'providers' | 'models' | 'spaces';

const ModelManagementPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabKey>('providers');

  const [providers, setProviders] = useState<Provider[]>([]);
  const [models, setModels] = useState<ModelDefWithProvider[]>([]);
  const [spaces, setSpaces] = useState<EmbeddingSpaceWithModel[]>([]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');

  // Dialogs
  const [providerDialogOpen, setProviderDialogOpen] = useState(false);
  const [modelDialogOpen, setModelDialogOpen] = useState(false);
  const [spaceDialogOpen, setSpaceDialogOpen] = useState(false);

  // Edit state
  const [editingProvider, setEditingProvider] = useState<Provider | null>(null);
  const [editingModel, setEditingModel] = useState<ModelDefWithProvider | null>(null);
  const [editingSpace, setEditingSpace] = useState<EmbeddingSpaceWithModel | null>(null);

  // Forms
  const [providerForm, setProviderForm] = useState<ProviderCreate>({
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

  const [modelForm, setModelForm] = useState<ModelDefCreate>({
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

  const [spaceForm, setSpaceForm] = useState<EmbeddingSpaceCreate>({
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

  const normalizeList = (data: any): any[] => {
    // The generated SDK's list return types vary between projects.
    // Try common fields and fall back to the data itself if it's already an array.
    if (!data) return [];
    if (Array.isArray(data)) return data;
    if (data.items && Array.isArray(data.items)) return data.items;
    if (data.providers && Array.isArray(data.providers)) return data.providers;
    if (data.models && Array.isArray(data.models)) return data.models;
    if (data.embedding_spaces && Array.isArray(data.embedding_spaces)) return data.embedding_spaces;
    // fallback: maybe the response is wrapped inside `.data` already handled earlier — return empty
    return [];
  };

  const loadData = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      // Use the chatterSDK modelRegistry instance (or api variable) — both call the same generated methods.
      const [pResp, mResp, sResp] = await Promise.all([
        chatterSDK.modelRegistry.listProvidersApiV1ModelsProvidersGet({ activeOnly: false }), // Show both active and inactive providers
        chatterSDK.modelRegistry.listModelsApiV1ModelsModelsGet({ activeOnly: false }), // Show both active and inactive models
        chatterSDK.modelRegistry.listEmbeddingSpacesApiV1ModelsEmbeddingSpacesGet({ activeOnly: false }), // Show both active and inactive spaces
      ]);
      const p = pResp.data;
      const m = mResp.data;
      const s = sResp.data;

      setProviders(normalizeList(p) as Provider[]);
      setModels(normalizeList(m) as ModelDefWithProvider[]);
      setSpaces(normalizeList(s) as EmbeddingSpaceWithModel[]);
    } catch (e: any) {
      console.error(e);
      setError(e?.message || 'Failed to load model registry data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

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
      await chatterSDK.modelRegistry.createProviderApiV1ModelsProvidersPost({ providerCreate: providerForm });
      setProviderDialogOpen(false);
      setEditingProvider(null);
      showSnackbar('Provider created');
      loadData();
    } catch (e: any) {
      console.error(e);
      setError(e?.message || 'Failed to create provider');
    }
  };

  const handleCreateModel = async () => {
    try {
      await chatterSDK.modelRegistry.createModelApiV1ModelsModelsPost({ modelDefCreate: modelForm });
      setModelDialogOpen(false);
      setEditingModel(null);
      showSnackbar('Model created');
      loadData();
    } catch (e: any) {
      console.error(e);
      setError(e?.message || 'Failed to create model');
    }
  };

  const handleCreateSpace = async () => {
    try {
      await chatterSDK.modelRegistry.createEmbeddingSpaceApiV1ModelsEmbeddingSpacesPost({ embeddingSpaceCreate: spaceForm });
      setSpaceDialogOpen(false);
      setEditingSpace(null);
      showSnackbar('Embedding space created');
      loadData();
    } catch (e: any) {
      console.error(e);
      setError(e?.message || 'Failed to create embedding space');
    }
  };

  const handleSetDefaultProvider = async (id: string, /* modelTypeOrOther: string */) => {
    try {
      // The generated API expects a DefaultProvider body. Build a minimal sensible object.
      // DefaultProvider typically contains provider_id and model_type (per generated types).
      // We'll set this provider as default for embedding models by default — adjust if you need a different model_type.
      const defaultProviderBody: DefaultProvider = {
        provider_id: id as any,
        model_type: 'embedding' as any,
      } as DefaultProvider;

      await chatterSDK.modelRegistry.setDefaultProviderApiV1ModelsProvidersProviderIdSetDefaultPost({
        providerId: id,
        defaultProvider: defaultProviderBody,
      });
      showSnackbar('Default provider updated');
      loadData();
    } catch (e: any) {
      console.error(e);
      setError(e?.message || 'Failed to set default provider');
    }
  };

  const handleSetDefaultModel = async (id: string) => {
    try {
      await chatterSDK.modelRegistry.setDefaultModelApiV1ModelsModelsModelIdSetDefaultPost({ modelId: id });
      showSnackbar('Default model updated');
      loadData();
    } catch (e: any) {
      console.error(e);
      setError(e?.message || 'Failed to set default model');
    }
  };

  const handleSetDefaultSpace = async (id: string) => {
    try {
      await chatterSDK.modelRegistry.setDefaultEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdSetDefaultPost({ spaceId: id });
      showSnackbar('Default embedding space updated');
      loadData();
    } catch (e: any) {
      console.error(e);
      setError(e?.message || 'Failed to set default embedding space');
    }
  };

  // Update handlers
  const handleUpdateProvider = async () => {
    if (!editingProvider) return;
    try {
      const updateData: ProviderUpdate = {
        display_name: providerForm.display_name,
        description: providerForm.description,
        api_key_required: providerForm.api_key_required,
        base_url: providerForm.base_url,
        is_active: providerForm.is_active,
      };
      await chatterSDK.modelRegistry.updateProviderApiV1ModelsProvidersProviderIdPut({ 
        providerId: editingProvider.id, 
        providerUpdate: updateData 
      });
      setProviderDialogOpen(false);
      setEditingProvider(null);
      showSnackbar('Provider updated');
      loadData();
    } catch (e: any) {
      console.error(e);
      setError(e?.message || 'Failed to update provider');
    }
  };

  const handleUpdateModel = async () => {
    if (!editingModel) return;
    try {
      const updateData: ModelDefUpdate = {
        display_name: modelForm.display_name,
        description: modelForm.description,
        model_name: modelForm.model_name,
        dimensions: modelForm.dimensions,
        supports_batch: modelForm.supports_batch,
        is_active: modelForm.is_active,
      };
      await chatterSDK.modelRegistry.updateModelApiV1ModelsModelsModelIdPut({ 
        modelId: editingModel.id, 
        modelDefUpdate: updateData 
      });
      setModelDialogOpen(false);
      setEditingModel(null);
      showSnackbar('Model updated');
      loadData();
    } catch (e: any) {
      console.error(e);
      setError(e?.message || 'Failed to update model');
    }
  };

  const handleUpdateSpace = async () => {
    if (!editingSpace) return;
    try {
      const updateData: EmbeddingSpaceUpdate = {
        display_name: spaceForm.display_name,
        description: spaceForm.description,
        reduction_strategy: spaceForm.reduction_strategy,
        normalize_vectors: spaceForm.normalize_vectors,
        distance_metric: spaceForm.distance_metric,
        is_active: spaceForm.is_active,
      };
      await chatterSDK.modelRegistry.updateEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdPut({ 
        spaceId: editingSpace.id, 
        embeddingSpaceUpdate: updateData 
      });
      setSpaceDialogOpen(false);
      setEditingSpace(null);
      showSnackbar('Embedding space updated');
      loadData();
    } catch (e: any) {
      console.error(e);
      setError(e?.message || 'Failed to update embedding space');
    }
  };

  // Delete handlers
  const handleDeleteProvider = async (provider: Provider) => {
    if (window.confirm(`Are you sure you want to delete provider "${provider.display_name}"?`)) {
      try {
        await chatterSDK.modelRegistry.deleteProviderApiV1ModelsProvidersProviderIdDelete({ providerId: provider.id });
        showSnackbar('Provider deleted');
        loadData();
      } catch (e: any) {
        console.error(e);
        setError(e?.message || 'Failed to delete provider');
      }
    }
  };

  const handleDeleteModel = async (model: ModelDefWithProvider) => {
    if (window.confirm(`Are you sure you want to delete model "${model.display_name}"?`)) {
      try {
        await chatterSDK.modelRegistry.deleteModelApiV1ModelsModelsModelIdDelete({ modelId: model.id });
        showSnackbar('Model deleted');
        loadData();
      } catch (e: any) {
        console.error(e);
        setError(e?.message || 'Failed to delete model');
      }
    }
  };

  const handleDeleteSpace = async (space: EmbeddingSpaceWithModel) => {
    if (window.confirm(`Are you sure you want to delete embedding space "${space.display_name}"?`)) {
      try {
        await chatterSDK.modelRegistry.deleteEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdDelete({ spaceId: space.id });
        showSnackbar('Embedding space deleted');
        loadData();
      } catch (e: any) {
        console.error(e);
        setError(e?.message || 'Failed to delete embedding space');
      }
    }
  };

  // Dialog close handlers
  const handleProviderDialogClose = () => {
    setProviderDialogOpen(false);
    setEditingProvider(null);
  };

  const handleModelDialogClose = () => {
    setModelDialogOpen(false);
    setEditingModel(null);
  };

  const handleSpaceDialogClose = () => {
    setSpaceDialogOpen(false);
    setEditingSpace(null);
  };

  // Edit handlers
  const handleEditProvider = (provider: Provider) => {
    setEditingProvider(provider);
    setProviderForm({
      name: provider.name,
      provider_type: provider.provider_type,
      display_name: provider.display_name,
      description: provider.description || '',
      api_key_required: provider.api_key_required,
      base_url: provider.base_url || '',
      is_active: provider.is_active,
    });
    setProviderDialogOpen(true);
  };

  const handleEditModel = (model: ModelDefWithProvider) => {
    setEditingModel(model);
    setModelForm({
      provider_id: model.provider_id,
      name: model.name,
      model_type: model.model_type,
      display_name: model.display_name,
      description: model.description || '',
      model_name: model.model_name,
      dimensions: model.dimensions,
      supports_batch: model.supports_batch,
      is_active: model.is_active,
    });
    setModelDialogOpen(true);
  };

  const handleEditSpace = (space: EmbeddingSpaceWithModel) => {
    setEditingSpace(space);
    setSpaceForm({
      model_id: space.model_id,
      name: space.name,
      display_name: space.display_name,
      description: space.description || '',
      base_dimensions: space.base_dimensions,
      effective_dimensions: space.effective_dimensions,
      reduction_strategy: space.reduction_strategy,
      distance_metric: space.distance_metric,
      table_name: space.table_name,
      index_type: space.index_type,
      normalize_vectors: space.normalize_vectors,
      is_active: space.is_active,
    });
    setSpaceDialogOpen(true);
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
              onClick={() => {
                setEditingProvider(null);
                setProviderForm({
                  name: '',
                  provider_type: 'openai',
                  display_name: '',
                  description: '',
                  api_key_required: true,
                  base_url: '',
                  is_active: true,
                });
                setProviderDialogOpen(true);
              }}
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
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Tooltip title="Edit provider">
                        <IconButton onClick={() => handleEditProvider(p)}>
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete provider">
                        <IconButton onClick={() => handleDeleteProvider(p)}>
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                      {!p.is_default && (
                        <Tooltip title="Set as default">
                          <IconButton onClick={() => handleSetDefaultProvider(p.id)}>
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
                    </Box>
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
              onClick={() => {
                setEditingModel(null);
                setModelForm({
                  provider_id: providers[0]?.id || '',
                  name: '',
                  model_type: 'embedding',
                  display_name: '',
                  description: '',
                  model_name: '',
                  dimensions: 1536,
                  supports_batch: true,
                  is_active: true,
                });
                setModelDialogOpen(true);
              }}
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
                        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                          <Typography variant="body2" color="text.secondary">
                            {m.name} ({m.model_type}) • Provider: {m.provider?.display_name || '—'}
                          </Typography>
                        </Grid>
                        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                          <Typography variant="body2" color="text.secondary">
                            API Model: {m.model_name}{' '}
                            {m.dimensions ? `• Dimensions: ${m.dimensions}` : ''}
                          </Typography>
                        </Grid>
                        {m.description && (
                          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                            <Typography variant="body2" color="text.secondary">
                              {m.description}
                            </Typography>
                          </Grid>
                        )}
                      </Grid>
                    }
                  />
                  <ListItemSecondaryAction>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Tooltip title="Edit model">
                        <IconButton onClick={() => handleEditModel(m)}>
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete model">
                        <IconButton onClick={() => handleDeleteModel(m)}>
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
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
                    </Box>
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
              onClick={() => {
                const firstEmbedding = embeddingModels[0];
                setEditingSpace(null);
                setSpaceForm({
                  model_id: firstEmbedding?.id || '',
                  name: '',
                  display_name: '',
                  description: '',
                  base_dimensions: firstEmbedding?.dimensions || 1536,
                  effective_dimensions: firstEmbedding?.dimensions || 1536,
                  reduction_strategy: 'none',
                  distance_metric: 'cosine',
                  table_name: '',
                  index_type: 'hnsw',
                  normalize_vectors: true,
                  is_active: true,
                });
                setSpaceDialogOpen(true);
              }}
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
                        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                          <Typography variant="body2" color="text.secondary">
                            {s.name} • Model: {s.model?.display_name || '—'}
                          </Typography>
                        </Grid>
                        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                          <Typography variant="body2" color="text.secondary">
                            Dimensions: {s.base_dimensions} → {s.effective_dimensions} • Strategy: {s.reduction_strategy} • Metric: {s.distance_metric} • Index: {s.index_type}
                          </Typography>
                        </Grid>
                        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                          <Typography variant="body2" color="text.secondary">
                            Table: {s.table_name}
                          </Typography>
                        </Grid>
                        {s.description && (
                          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                            <Typography variant="body2" color="text.secondary">
                              {s.description}
                            </Typography>
                          </Grid>
                        )}
                      </Grid>
                    }
                  />
                  <ListItemSecondaryAction>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Tooltip title="Edit embedding space">
                        <IconButton onClick={() => handleEditSpace(s)}>
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete embedding space">
                        <IconButton onClick={() => handleDeleteSpace(s)}>
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
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
                    </Box>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          )}
        </Box>
      )}

      {/* Provider Dialog */}
      <Dialog open={providerDialogOpen} onClose={handleProviderDialogClose} maxWidth="sm" fullWidth>
        <DialogTitle>{editingProvider ? 'Edit Provider' : 'Add Provider'}</DialogTitle>
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
          <Button onClick={handleProviderDialogClose}>Cancel</Button>
          <Button variant="contained" onClick={editingProvider ? handleUpdateProvider : handleCreateProvider}>
            {editingProvider ? 'Update Provider' : 'Create Provider'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Model Dialog */}
      <Dialog open={modelDialogOpen} onClose={handleModelDialogClose} maxWidth="sm" fullWidth>
        <DialogTitle>{editingModel ? 'Edit Model' : 'Add Model'}</DialogTitle>
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
              const model_type = e.target.value as ModelDefCreate['model_type'];
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
          <Button onClick={handleModelDialogClose}>Cancel</Button>
          <Button variant="contained" onClick={editingModel ? handleUpdateModel : handleCreateModel}>
            {editingModel ? 'Update Model' : 'Create Model'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Embedding Space Dialog */}
      <Dialog open={spaceDialogOpen} onClose={handleSpaceDialogClose} maxWidth="sm" fullWidth>
        <DialogTitle>{editingSpace ? 'Edit Embedding Space' : 'Add Embedding Space'}</DialogTitle>
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
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
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
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
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
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
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
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
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
              value={(spaceForm as any).reducer_path || ''}
              onChange={(e) => setSpaceForm({ ...spaceForm, ...(spaceForm as any), reducer_path: e.target.value } as any)}
            />
          )}
          <Grid container spacing={2}>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
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
          <Button onClick={handleSpaceDialogClose}>Cancel</Button>
          <Button variant="contained" onClick={editingSpace ? handleUpdateSpace : handleCreateSpace}>
            {editingSpace ? 'Update Embedding Space' : 'Create Embedding Space'}
          </Button>
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
