import React, { useState, useEffect, useRef } from 'react';
import { Box, Tabs, Tab, TabPanel, Typography, Chip, Button } from '../utils/mui';
import { Star as DefaultIcon, RefreshIcon, AddIcon } from '../utils/icons';
import PageLayout from '../components/PageLayout';
import CrudDataTable, { CrudConfig, CrudService, CrudColumn, CrudAction, CrudDataTableRef } from '../components/CrudDataTable';
import ProviderForm from '../components/ProviderForm';
import ModelForm from '../components/ModelForm';
import { 
  createTypeChipRenderer,
  createMonospaceTextRenderer
} from '../components/CrudRenderers';
import { getSDK } from "../services/auth-service";
import { toastService } from '../services/toast-service';
import { handleError } from '../utils/error-handler';
import {
  Provider,
  ProviderCreate,
  ProviderUpdate,
  ModelDefCreate,
  ModelDefUpdate,
  ModelDefWithProvider,
  DefaultProvider,
} from 'chatter-sdk';


const ModelManagementPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [providers, setProviders] = useState<Provider[]>([]);
  const providerCrudRef = useRef<CrudDataTableRef>(null);
  const modelCrudRef = useRef<CrudDataTableRef>(null);

  // Load providers for model form
  const loadProviders = async () => {
    try {
      const response = await getSDK().modelRegistry.listProvidersApiV1ModelsProviders({
        activeOnly: true, // Only load active providers for model creation
      });
      setProviders(response.providers || []);
    } catch (error) {
      console.error('Failed to load providers:', error);
      setProviders([]);
    }
  };

  useEffect(() => {
    loadProviders();
  }, []);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  // Dynamic toolbar based on active tab
  const toolbar = (
    <>
      <Button
        variant="outlined"
        startIcon={<RefreshIcon />}
        onClick={() => {
          loadProviders();
          if (activeTab === 0) {
            providerCrudRef.current?.handleRefresh();
          } else {
            modelCrudRef.current?.handleRefresh();
          }
        }}
        size="small"
      >
        Refresh
      </Button>
      {activeTab === 0 ? (
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => providerCrudRef.current?.handleCreate()}
          size="small"
        >
          Add Provider
        </Button>
      ) : (
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => modelCrudRef.current?.handleCreate()}
          disabled={providers.length === 0}
          size="small"
        >
          Add Model
        </Button>
      )}
    </>
  );

  // Provider columns and config
  const providerColumns: CrudColumn<Provider>[] = [
    {
      id: 'displayName',
      label: 'Name',
      render: (value, item): void => (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box>
            <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
              {value}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {item.name}
            </Typography>
          </Box>
          {item.isDefault && (
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
      render: (value: boolean): void => (
        <Chip
          size="small"
          label={value ? 'Active' : 'Inactive'}
          color={value ? 'success' : 'default'}
        />
      ),
    },
    {
      id: 'api_key_required',
      label: 'API Key',
      render: (value: boolean): void => (
        <Chip
          size="small"
          label={value ? 'Required' : 'Optional'}
          color={value ? 'warning' : 'default'}
          variant="outlined"
        />
      ),
    },
    {
      id: 'description',
      label: 'Description',
      render: (value: string): void => (
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
        if (!provider.isDefault) {
          try {
            const defaultProviderBody: DefaultProvider = {
              provider_id: provider.id as any,
              model_type: 'embedding' as any,
            } as DefaultProvider;

            await getSDK().modelRegistry.setDefaultProviderApiV1ModelsProvidersProviderIdSetDefault(
              provider.id,
              defaultProviderBody
            );
            toastService.success('Default provider updated');
          } catch (error) {
            handleError(error, {
              source: 'ModelManagementPage.setDefaultProvider',
              operation: 'set default provider',
              additionalData: { providerId: provider.id }
            });
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
      const response = await getSDK().modelRegistry.listProvidersApiV1ModelsProviders({
        activeOnly: false,
        page: page + 1,
        perPage: pageSize,
      });
      return {
        items: response.providers || [],
        total: response.total || 0,
      };
    },

    create: async (data: ProviderCreate) => {
      const response = await getSDK().modelRegistry.createProviderApiV1ModelsProviders(data);
      await loadProviders(); // Refresh providers for model form
      return response;
    },

    update: async (id: string, data: ProviderUpdate) => {
      const response = await getSDK().modelRegistry.updateProviderApiV1ModelsProvidersProviderId(id, data);
      await loadProviders(); // Refresh providers for model form
      return response;
    },

    delete: async (id: string) => {
      await getSDK().modelRegistry.deleteProviderApiV1ModelsProvidersProviderId(id);
      await loadProviders(); // Refresh providers for model form
    },
  };

  // Model columns and config
  const modelColumns: CrudColumn<ModelDefWithProvider>[] = [
    {
      id: 'displayName',
      label: 'Name',
      render: (value, item): void => (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box>
            <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
              {value}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {item.name}
            </Typography>
          </Box>
          {item.isDefault && (
            <Chip size="small" label="Default" color="primary" />
          )}
        </Box>
      ),
    },
    {
      id: 'provider',
      label: 'Provider',
      render: (value: any): void => (
        <Typography variant="body2">
          {value?.displayName || '—'}
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
      render: (value: boolean): void => (
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
      render: (value: number): void => (
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
        if (!model.isDefault) {
          try {
            await getSDK().modelRegistry.setDefaultModelApiV1ModelsModelsModelIdSetDefault(model.id);
            toastService.success('Default model updated');
          } catch (error) {
            handleError(error, {
              source: 'ModelManagementPage.setDefaultModel',
              operation: 'set default model',
              additionalData: { modelId: model.id }
            });
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
      const response = await getSDK().modelRegistry.listModelsApiV1ModelsModels({
        activeOnly: false,
        page: page + 1,
        perPage: pageSize,
      });
      return {
        items: response.models || [],
        total: response.total || 0,
      };
    },

    create: async (data: ModelDefCreate) => {
      const response = await getSDK().modelRegistry.createModelApiV1ModelsModels(data);
      return response;
    },

    update: async (id: string, data: ModelDefUpdate) => {
      const response = await getSDK().modelRegistry.updateModelApiV1ModelsModelsModelId(id, data);
      return response;
    },

    delete: async (id: string) => {
      await getSDK().modelRegistry.deleteModelApiV1ModelsModelsModelId(id);
    },
  };

  const getProviderId = (item: Provider) => item.id || '';
  const getModelId = (item: ModelDefWithProvider) => item.id || '';

  // Enhanced ModelForm component that receives providers
  const EnhancedModelForm: React.FC<any> = (props): void => (
    <ModelForm {...props} providers={providers} />
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
        <Tab iconPosition="start" value={0} label="Providers" />
        <Tab iconPosition="start" value={1} label="Models" />
      </Tabs>

      <TabPanel value={activeTab} index={0} idPrefix="model-management">
        <CrudDataTable
          ref={providerCrudRef}
          config={providerConfig}
          service={providerService}
          FormComponent={ProviderForm}
          getItemId={getProviderId}
        />
      </TabPanel>

      <TabPanel value={activeTab} index={1} idPrefix="model-management">
        <CrudDataTable
          ref={modelCrudRef}
          config={modelConfig}
          service={modelService}
          FormComponent={EnhancedModelForm}
          getItemId={getModelId}
        />
      </TabPanel>
    </PageLayout>
  );
};

export default ModelManagementPage;
