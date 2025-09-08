import React, { useState, useEffect } from 'react';
import { Box, Tabs, Tab, Typography, Chip, Button } from '@mui/material';
import { Star as DefaultIcon, Refresh as RefreshIcon, Add as AddIcon } from '@mui/icons-material';
import PageLayout from '../components/PageLayout';
import CrudDataTable, { CrudConfig, CrudService, CrudColumn, CrudAction } from '../components/CrudDataTable';
import ProviderForm from '../components/ProviderForm';
import ModelForm from '../components/ModelForm';
import { 
  createTypeChipRenderer,
  createStatusChipRenderer,
  createMonospaceTextRenderer,
  createConditionalChipRenderer
} from '../components/CrudRenderers';
import { chatterSDK } from '../services/chatter-sdk';
import { toastService } from '../services/toast-service';
import {
  Provider,
  ProviderCreate,
  ProviderUpdate,
  ModelDefCreate,
  ModelDefUpdate,
  ModelDefWithProvider,
  DefaultProvider,
} from '../sdk';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

const ModelManagementPageRefactored: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [providers, setProviders] = useState<Provider[]>([]);

  // Load providers for model form
  const loadProviders = async () => {
    try {
      const response = await chatterSDK.modelRegistry.listProvidersApiV1ModelsProvidersGet({
        activeOnly: false,
      });
      setProviders(response.data.providers || []);
    } catch {
      // Error loading providers - this is handled elsewhere
    }
  };

  useEffect(() => {
    loadProviders();
  }, []);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  // Provider columns and config
  const providerColumns: CrudColumn<Provider>[] = [
    {
      id: 'display_name',
      label: 'Name',
      render: (value, item) => (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box>
            <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
              {value}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {item.name}
            </Typography>
          </Box>
          {item.is_default && (
            <Chip size="small" label="Default" color="primary" />
          )}
        </Box>
      ),
    },
    {
      id: 'provider_type',
      label: 'Type',
      render: createTypeChipRenderer<Provider>('secondary', 'outlined'),
    },
    {
      id: 'is_active',
      label: 'Status',
      render: (value: boolean) => (
        <Chip
          size="small"
          label={value ? 'Active' : 'Inactive'}
          color={value ? 'success' : 'default'}
        />
      ),
    },
    {
      id: 'description',
      label: 'Description',
      render: (value: string) => (
        <Typography variant="body2" color="text.secondary">
          {value || '—'}
        </Typography>
      ),
    },
  ];

  const providerActions: CrudAction<Provider>[] = [
    {
      icon: <DefaultIcon />,
      label: 'Set as Default',
      onClick: async (provider) => {
        if (!provider.is_default) {
          try {
            const defaultProviderBody: DefaultProvider = {
              provider_id: provider.id as any,
              model_type: 'embedding' as any,
            } as DefaultProvider;

            await chatterSDK.modelRegistry.setDefaultProviderApiV1ModelsProvidersProviderIdSetDefaultPost({
              providerId: provider.id,
              defaultProvider: defaultProviderBody,
            });
            toastService.success('Default provider updated');
          } catch (error) {
            toastService.error('Failed to set default provider');
          }
        }
      },
    },
  ];

  const providerConfig: CrudConfig<Provider> = {
    entityName: 'Provider',
    entityNamePlural: 'Providers',
    columns: providerColumns,
    actions: providerActions,
    enableCreate: true,
    enableEdit: true,
    enableDelete: true,
    enableRefresh: true,
    pageSize: 10,
  };

  const providerService: CrudService<Provider, ProviderCreate, ProviderUpdate> = {
    list: async (page: number, pageSize: number) => {
      const response = await chatterSDK.modelRegistry.listProvidersApiV1ModelsProvidersGet({
        activeOnly: false,
        page: page + 1,
        perPage: pageSize,
      });
      return {
        items: response.data.providers || [],
        total: response.data.total || 0,
      };
    },

    create: async (data: ProviderCreate) => {
      const response = await chatterSDK.modelRegistry.createProviderApiV1ModelsProvidersPost({
        providerCreate: data,
      });
      await loadProviders(); // Refresh providers for model form
      return response.data;
    },

    update: async (id: string, data: ProviderUpdate) => {
      const response = await chatterSDK.modelRegistry.updateProviderApiV1ModelsProvidersProviderIdPut({
        providerId: id,
        providerUpdate: data,
      });
      await loadProviders(); // Refresh providers for model form
      return response.data;
    },

    delete: async (id: string) => {
      await chatterSDK.modelRegistry.deleteProviderApiV1ModelsProvidersProviderIdDelete({
        providerId: id,
      });
      await loadProviders(); // Refresh providers for model form
    },
  };

  // Model columns and config
  const modelColumns: CrudColumn<ModelDefWithProvider>[] = [
    {
      id: 'display_name',
      label: 'Name',
      render: (value, item) => (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box>
            <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
              {value}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {item.name}
            </Typography>
          </Box>
          {item.is_default && (
            <Chip size="small" label="Default" color="primary" />
          )}
        </Box>
      ),
    },
    {
      id: 'provider',
      label: 'Provider',
      render: (value: any) => (
        <Typography variant="body2">
          {value?.display_name || '—'}
        </Typography>
      ),
    },
    {
      id: 'model_type',
      label: 'Type',
      render: createTypeChipRenderer<ModelDefWithProvider>('secondary', 'outlined'),
    },
    {
      id: 'is_active',
      label: 'Status',
      render: (value: boolean) => (
        <Chip
          size="small"
          label={value ? 'Active' : 'Inactive'}
          color={value ? 'success' : 'default'}
        />
      ),
    },
    {
      id: 'model_name',
      label: 'API Model',
      render: createMonospaceTextRenderer<ModelDefWithProvider>(),
    },
    {
      id: 'dimensions',
      label: 'Dimensions',
      render: (value: number) => (
        <Typography variant="body2">
          {value ? value.toLocaleString() : '—'}
        </Typography>
      ),
    },
  ];

  const modelActions: CrudAction<ModelDefWithProvider>[] = [
    {
      icon: <DefaultIcon />,
      label: 'Set as Default',
      onClick: async (model) => {
        if (!model.is_default) {
          try {
            await chatterSDK.modelRegistry.setDefaultModelApiV1ModelsModelsModelIdSetDefaultPost({
              modelId: model.id,
            });
            toastService.success('Default model updated');
          } catch {
            toastService.error('Failed to set default model');
          }
        }
      },
    },
  ];

  const modelConfig: CrudConfig<ModelDefWithProvider> = {
    entityName: 'Model',
    entityNamePlural: 'Models',
    columns: modelColumns,
    actions: modelActions,
    enableCreate: true,
    enableEdit: true,
    enableDelete: true,
    enableRefresh: true,
    pageSize: 10,
  };

  const modelService: CrudService<ModelDefWithProvider, ModelDefCreate, ModelDefUpdate> = {
    list: async (page: number, pageSize: number) => {
      const response = await chatterSDK.modelRegistry.listModelsApiV1ModelsModelsGet({
        activeOnly: false,
        page: page + 1,
        perPage: pageSize,
      });
      return {
        items: response.data.models || [],
        total: response.data.total || 0,
      };
    },

    create: async (data: ModelDefCreate) => {
      const response = await chatterSDK.modelRegistry.createModelApiV1ModelsModelsPost({
        modelDefCreate: data,
      });
      return response.data;
    },

    update: async (id: string, data: ModelDefUpdate) => {
      const response = await chatterSDK.modelRegistry.updateModelApiV1ModelsModelsModelIdPut({
        modelId: id,
        modelDefUpdate: data,
      });
      return response.data;
    },

    delete: async (id: string) => {
      await chatterSDK.modelRegistry.deleteModelApiV1ModelsModelsModelIdDelete({
        modelId: id,
      });
    },
  };

  const getProviderId = (item: Provider) => item.id || '';
  const getModelId = (item: ModelDefWithProvider) => item.id || '';

  // Enhanced ModelForm component that receives providers
  const EnhancedModelForm: React.FC<any> = (props) => (
    <ModelForm {...props} providers={providers} />
  );

  const toolbar = (
    <>
      <Button
        variant="outlined"
        startIcon={<RefreshIcon />}
        onClick={() => {
          if (activeTab === 0) {
            loadProviders();
          }
          // The CRUD table handles its own refresh
        }}
      >
        Refresh
      </Button>
      {activeTab === 0 && (
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => {
            // The CRUD table handles creation
          }}
        >
          Create Provider
        </Button>
      )}
      {activeTab === 1 && (
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => {
            // The CRUD table handles creation
          }}
          disabled={providers.length === 0}
        >
          Create Model
        </Button>
      )}
    </>
  );

  return (
    <PageLayout title="Model Management" toolbar={toolbar}>
      <Tabs
        value={activeTab}
        onChange={handleTabChange}
        variant="scrollable"
        scrollButtons="auto"
        sx={{ mb: 2 }}
      >
        <Tab value={0} label="Providers" />
        <Tab value={1} label="Models" />
      </Tabs>

      <TabPanel value={activeTab} index={0}>
        <CrudDataTable
          config={providerConfig}
          service={providerService}
          FormComponent={ProviderForm}
          getItemId={getProviderId}
        />
      </TabPanel>

      <TabPanel value={activeTab} index={1}>
        <CrudDataTable
          config={modelConfig}
          service={modelService}
          FormComponent={EnhancedModelForm}
          getItemId={getModelId}
        />
      </TabPanel>
    </PageLayout>
  );
};

export default ModelManagementPageRefactored;