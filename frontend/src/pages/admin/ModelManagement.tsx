import React, { useEffect, useState } from "react";
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
} from "../../api/modelRegistry";

interface TabProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

const TabNavigation: React.FC<TabProps> = ({ activeTab, setActiveTab }) => {
  const tabs = [
    { id: "providers", label: "Providers" },
    { id: "models", label: "Models" },
    { id: "spaces", label: "Embedding Spaces" },
  ];

  return (
    <div className="border-b border-gray-200 mb-6">
      <nav className="-mb-px flex">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`py-2 px-4 border-b-2 font-medium text-sm ${
              activeTab === tab.id
                ? "border-blue-500 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </nav>
    </div>
  );
};

interface ProviderFormProps {
  onSubmit: (data: CreateProvider) => void;
  onCancel: () => void;
}

const ProviderForm: React.FC<ProviderFormProps> = ({ onSubmit, onCancel }) => {
  const [formData, setFormData] = useState<CreateProvider>({
    name: "",
    provider_type: "openai",
    display_name: "",
    description: "",
    api_key_required: true,
    base_url: "",
    is_active: true,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 bg-gray-50 p-4 rounded">
      <div>
        <label className="block text-sm font-medium text-gray-700">Name</label>
        <input
          type="text"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          required
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700">Provider Type</label>
        <select
          value={formData.provider_type}
          onChange={(e) => setFormData({ ...formData, provider_type: e.target.value })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          <option value="openai">OpenAI</option>
          <option value="anthropic">Anthropic</option>
          <option value="google">Google</option>
          <option value="cohere">Cohere</option>
          <option value="mistral">Mistral</option>
        </select>
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700">Display Name</label>
        <input
          type="text"
          value={formData.display_name}
          onChange={(e) => setFormData({ ...formData, display_name: e.target.value })}
          required
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700">Description</label>
        <textarea
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          rows={3}
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700">Base URL (optional)</label>
        <input
          type="url"
          value={formData.base_url}
          onChange={(e) => setFormData({ ...formData, base_url: e.target.value })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>
      
      <div className="flex items-center">
        <input
          type="checkbox"
          checked={formData.api_key_required}
          onChange={(e) => setFormData({ ...formData, api_key_required: e.target.checked })}
          className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
        <label className="ml-2 block text-sm text-gray-700">API Key Required</label>
      </div>
      
      <div className="flex items-center">
        <input
          type="checkbox"
          checked={formData.is_active}
          onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
          className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
        <label className="ml-2 block text-sm text-gray-700">Active</label>
      </div>
      
      <div className="flex space-x-2">
        <button
          type="submit"
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Create Provider
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400"
        >
          Cancel
        </button>
      </div>
    </form>
  );
};

interface ModelFormProps {
  providers: Provider[];
  onSubmit: (data: CreateModel) => void;
  onCancel: () => void;
}

const ModelForm: React.FC<ModelFormProps> = ({ providers, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState<CreateModel>({
    provider_id: providers[0]?.id || "",
    name: "",
    model_type: "embedding",
    display_name: "",
    description: "",
    model_name: "",
    dimensions: 1536,
    supports_batch: true,
    is_active: true,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 bg-gray-50 p-4 rounded">
      <div>
        <label className="block text-sm font-medium text-gray-700">Provider</label>
        <select
          value={formData.provider_id}
          onChange={(e) => setFormData({ ...formData, provider_id: e.target.value })}
          required
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          {providers.map((provider) => (
            <option key={provider.id} value={provider.id}>
              {provider.display_name}
            </option>
          ))}
        </select>
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700">Name</label>
        <input
          type="text"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          required
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700">Model Type</label>
        <select
          value={formData.model_type}
          onChange={(e) => setFormData({ ...formData, model_type: e.target.value })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          <option value="embedding">Embedding</option>
          <option value="llm">LLM</option>
        </select>
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700">Display Name</label>
        <input
          type="text"
          value={formData.display_name}
          onChange={(e) => setFormData({ ...formData, display_name: e.target.value })}
          required
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700">Model Name (API)</label>
        <input
          type="text"
          value={formData.model_name}
          onChange={(e) => setFormData({ ...formData, model_name: e.target.value })}
          required
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>
      
      {formData.model_type === "embedding" && (
        <div>
          <label className="block text-sm font-medium text-gray-700">Dimensions</label>
          <input
            type="number"
            value={formData.dimensions || ""}
            onChange={(e) => setFormData({ ...formData, dimensions: parseInt(e.target.value) || undefined })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
        </div>
      )}
      
      <div>
        <label className="block text-sm font-medium text-gray-700">Description</label>
        <textarea
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          rows={3}
        />
      </div>
      
      <div className="flex space-x-2">
        <button
          type="submit"
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Create Model
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400"
        >
          Cancel
        </button>
      </div>
    </form>
  );
};

interface EmbeddingSpaceFormProps {
  models: ModelDef[];
  onSubmit: (data: CreateEmbeddingSpace) => void;
  onCancel: () => void;
}

const EmbeddingSpaceForm: React.FC<EmbeddingSpaceFormProps> = ({ models, onSubmit, onCancel }) => {
  const embeddingModels = models.filter(m => m.model_type === "embedding");
  
  const [formData, setFormData] = useState<CreateEmbeddingSpace>({
    model_id: embeddingModels[0]?.id || "",
    name: "",
    display_name: "",
    description: "",
    base_dimensions: 1536,
    effective_dimensions: 1536,
    reduction_strategy: "none",
    distance_metric: "cosine",
    table_name: "",
    index_type: "hnsw",
    normalize_vectors: true,
    is_active: true,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 bg-gray-50 p-4 rounded">
      <div>
        <label className="block text-sm font-medium text-gray-700">Embedding Model</label>
        <select
          value={formData.model_id}
          onChange={(e) => setFormData({ ...formData, model_id: e.target.value })}
          required
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          {embeddingModels.map((model) => (
            <option key={model.id} value={model.id}>
              {model.display_name} ({model.dimensions}d)
            </option>
          ))}
        </select>
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700">Name</label>
        <input
          type="text"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          required
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700">Display Name</label>
        <input
          type="text"
          value={formData.display_name}
          onChange={(e) => setFormData({ ...formData, display_name: e.target.value })}
          required
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700">Table Name</label>
        <input
          type="text"
          value={formData.table_name}
          onChange={(e) => setFormData({ ...formData, table_name: e.target.value })}
          required
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Base Dimensions</label>
          <input
            type="number"
            value={formData.base_dimensions}
            onChange={(e) => setFormData({ ...formData, base_dimensions: parseInt(e.target.value) })}
            required
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700">Effective Dimensions</label>
          <input
            type="number"
            value={formData.effective_dimensions}
            onChange={(e) => setFormData({ ...formData, effective_dimensions: parseInt(e.target.value) })}
            required
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
        </div>
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700">Reduction Strategy</label>
        <select
          value={formData.reduction_strategy}
          onChange={(e) => setFormData({ ...formData, reduction_strategy: e.target.value })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          <option value="none">None</option>
          <option value="truncate">Truncate</option>
          <option value="reducer">Reducer (PCA/SVD)</option>
        </select>
      </div>
      
      {formData.reduction_strategy === "reducer" && (
        <div>
          <label className="block text-sm font-medium text-gray-700">Reducer Path</label>
          <input
            type="text"
            value={formData.reducer_path || ""}
            onChange={(e) => setFormData({ ...formData, reducer_path: e.target.value })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            placeholder="Path to joblib reducer file"
          />
        </div>
      )}
      
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Distance Metric</label>
          <select
            value={formData.distance_metric}
            onChange={(e) => setFormData({ ...formData, distance_metric: e.target.value })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="cosine">Cosine</option>
            <option value="l2">L2 (Euclidean)</option>
            <option value="ip">Inner Product</option>
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700">Index Type</label>
          <select
            value={formData.index_type}
            onChange={(e) => setFormData({ ...formData, index_type: e.target.value })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="hnsw">HNSW</option>
            <option value="ivfflat">IVFFlat</option>
          </select>
        </div>
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700">Description</label>
        <textarea
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          rows={3}
        />
      </div>
      
      <div className="flex items-center">
        <input
          type="checkbox"
          checked={formData.normalize_vectors}
          onChange={(e) => setFormData({ ...formData, normalize_vectors: e.target.checked })}
          className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
        <label className="ml-2 block text-sm text-gray-700">Normalize Vectors</label>
      </div>
      
      <div className="flex space-x-2">
        <button
          type="submit"
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Create Embedding Space
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400"
        >
          Cancel
        </button>
      </div>
    </form>
  );
};

const ModelManagement: React.FC = () => {
  const [activeTab, setActiveTab] = useState("providers");
  const [providers, setProviders] = useState<Provider[]>([]);
  const [models, setModels] = useState<ModelDef[]>([]);
  const [embeddingSpaces, setEmbeddingSpaces] = useState<EmbeddingSpace[]>([]);
  const [loading, setLoading] = useState(false);
  const [showProviderForm, setShowProviderForm] = useState(false);
  const [showModelForm, setShowModelForm] = useState(false);
  const [showSpaceForm, setShowSpaceForm] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [providersData, modelsData, spacesData] = await Promise.all([
        listProviders(),
        listModels(),
        listEmbeddingSpaces(),
      ]);
      setProviders(providersData.items);
      setModels(modelsData.items);
      setEmbeddingSpaces(spacesData.items);
    } catch (error) {
      console.error("Failed to load data:", error);
    }
    setLoading(false);
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateProvider = async (data: CreateProvider) => {
    try {
      await createProvider(data);
      setShowProviderForm(false);
      loadData();
    } catch (error) {
      console.error("Failed to create provider:", error);
    }
  };

  const handleCreateModel = async (data: CreateModel) => {
    try {
      await createModel(data);
      setShowModelForm(false);
      loadData();
    } catch (error) {
      console.error("Failed to create model:", error);
    }
  };

  const handleCreateEmbeddingSpace = async (data: CreateEmbeddingSpace) => {
    try {
      await createEmbeddingSpace(data);
      setShowSpaceForm(false);
      loadData();
    } catch (error) {
      console.error("Failed to create embedding space:", error);
    }
  };

  if (loading) {
    return <div className="p-6">Loading...</div>;
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Model Management</h1>
      
      <TabNavigation activeTab={activeTab} setActiveTab={setActiveTab} />
      
      {activeTab === "providers" && (
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Providers</h2>
            <button
              onClick={() => setShowProviderForm(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Add Provider
            </button>
          </div>
          
          {showProviderForm && (
            <div className="mb-6">
              <ProviderForm
                onSubmit={handleCreateProvider}
                onCancel={() => setShowProviderForm(false)}
              />
            </div>
          )}
          
          <div className="grid gap-4">
            {providers.map((provider) => (
              <div key={provider.id} className="border rounded p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-semibold">{provider.display_name}</h3>
                    <p className="text-sm text-gray-600">{provider.name} ({provider.provider_type})</p>
                    {provider.description && (
                      <p className="text-sm text-gray-700 mt-1">{provider.description}</p>
                    )}
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 rounded text-xs ${
                      provider.is_active ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
                    }`}>
                      {provider.is_active ? "Active" : "Inactive"}
                    </span>
                    {provider.is_default && (
                      <span className="px-2 py-1 rounded text-xs bg-blue-100 text-blue-800">
                        Default
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {activeTab === "models" && (
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Models</h2>
            <button
              onClick={() => setShowModelForm(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Add Model
            </button>
          </div>
          
          {showModelForm && (
            <div className="mb-6">
              <ModelForm
                providers={providers}
                onSubmit={handleCreateModel}
                onCancel={() => setShowModelForm(false)}
              />
            </div>
          )}
          
          <div className="grid gap-4">
            {models.map((model) => (
              <div key={model.id} className="border rounded p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-semibold">{model.display_name}</h3>
                    <p className="text-sm text-gray-600">
                      {model.name} ({model.model_type}) - {model.provider?.display_name}
                    </p>
                    <p className="text-sm text-gray-600">API Model: {model.model_name}</p>
                    {model.dimensions && (
                      <p className="text-sm text-gray-600">Dimensions: {model.dimensions}</p>
                    )}
                    {model.description && (
                      <p className="text-sm text-gray-700 mt-1">{model.description}</p>
                    )}
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 rounded text-xs ${
                      model.is_active ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
                    }`}>
                      {model.is_active ? "Active" : "Inactive"}
                    </span>
                    {model.is_default && (
                      <span className="px-2 py-1 rounded text-xs bg-blue-100 text-blue-800">
                        Default
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {activeTab === "spaces" && (
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Embedding Spaces</h2>
            <button
              onClick={() => setShowSpaceForm(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Add Embedding Space
            </button>
          </div>
          
          {showSpaceForm && (
            <div className="mb-6">
              <EmbeddingSpaceForm
                models={models}
                onSubmit={handleCreateEmbeddingSpace}
                onCancel={() => setShowSpaceForm(false)}
              />
            </div>
          )}
          
          <div className="grid gap-4">
            {embeddingSpaces.map((space) => (
              <div key={space.id} className="border rounded p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-semibold">{space.display_name}</h3>
                    <p className="text-sm text-gray-600">
                      {space.name} - {space.model?.display_name}
                    </p>
                    <p className="text-sm text-gray-600">
                      Dimensions: {space.base_dimensions} → {space.effective_dimensions}
                    </p>
                    <p className="text-sm text-gray-600">
                      Strategy: {space.reduction_strategy}, Metric: {space.distance_metric}
                    </p>
                    <p className="text-sm text-gray-600">Table: {space.table_name}</p>
                    {space.description && (
                      <p className="text-sm text-gray-700 mt-1">{space.description}</p>
                    )}
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 rounded text-xs ${
                      space.is_active ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
                    }`}>
                      {space.is_active ? "Active" : "Inactive"}
                    </span>
                    {space.is_default && (
                      <span className="px-2 py-1 rounded text-xs bg-blue-100 text-blue-800">
                        Default
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ModelManagement;