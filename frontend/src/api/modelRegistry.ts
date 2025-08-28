import axios from "axios";

const api = axios.create({
  baseURL: "/api/v1/models",
  headers: {
    "Content-Type": "application/json",
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Types
export interface Provider {
  id: string;
  name: string;
  provider_type: string;
  display_name: string;
  description?: string;
  api_key_required: boolean;
  base_url?: string;
  default_config: Record<string, any>;
  is_active: boolean;
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

export interface ModelDef {
  id: string;
  provider_id: string;
  name: string;
  model_type: string;
  display_name: string;
  description?: string;
  model_name: string;
  max_tokens?: number;
  context_length?: number;
  dimensions?: number;
  chunk_size?: number;
  supports_batch: boolean;
  max_batch_size?: number;
  default_config: Record<string, any>;
  is_active: boolean;
  is_default: boolean;
  created_at: string;
  updated_at: string;
  provider?: Provider;
}

export interface EmbeddingSpace {
  id: string;
  model_id: string;
  name: string;
  display_name: string;
  description?: string;
  base_dimensions: number;
  effective_dimensions: number;
  reduction_strategy: string;
  reducer_path?: string;
  reducer_version?: string;
  normalize_vectors: boolean;
  distance_metric: string;
  table_name: string;
  index_type: string;
  index_config: Record<string, any>;
  is_active: boolean;
  is_default: boolean;
  created_at: string;
  updated_at: string;
  model?: ModelDef;
}

export interface ListResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
}

export interface CreateProvider {
  name: string;
  provider_type: string;
  display_name: string;
  description?: string;
  api_key_required?: boolean;
  base_url?: string;
  default_config?: Record<string, any>;
  is_active?: boolean;
  is_default?: boolean;
}

export interface CreateModel {
  provider_id: string;
  name: string;
  model_type: string;
  display_name: string;
  description?: string;
  model_name: string;
  max_tokens?: number;
  context_length?: number;
  dimensions?: number;
  chunk_size?: number;
  supports_batch?: boolean;
  max_batch_size?: number;
  default_config?: Record<string, any>;
  is_active?: boolean;
  is_default?: boolean;
}

export interface CreateEmbeddingSpace {
  model_id: string;
  name: string;
  display_name: string;
  description?: string;
  base_dimensions: number;
  effective_dimensions: number;
  reduction_strategy?: string;
  reducer_path?: string;
  reducer_version?: string;
  normalize_vectors?: boolean;
  distance_metric?: string;
  table_name: string;
  index_type?: string;
  index_config?: Record<string, any>;
  is_active?: boolean;
  is_default?: boolean;
}

// Provider API
export const listProviders = async (
  page = 1,
  per_page = 20,
  active_only = true
): Promise<ListResponse<Provider>> => {
  const response = await api.get("/providers", {
    params: { page, per_page, active_only },
  });
  return {
    items: response.data.providers,
    total: response.data.total,
    page: response.data.page,
    per_page: response.data.per_page,
  };
};

export const getProvider = async (id: string): Promise<Provider> => {
  const response = await api.get(`/providers/${id}`);
  return response.data;
};

export const createProvider = async (data: CreateProvider): Promise<Provider> => {
  const response = await api.post("/providers", data);
  return response.data;
};

export const updateProvider = async (
  id: string,
  data: Partial<CreateProvider>
): Promise<Provider> => {
  const response = await api.put(`/providers/${id}`, data);
  return response.data;
};

export const deleteProvider = async (id: string): Promise<void> => {
  await api.delete(`/providers/${id}`);
};

export const setDefaultProvider = async (
  id: string,
  model_type: string
): Promise<void> => {
  await api.post(`/providers/${id}/set-default`, {
    provider_id: id,
    model_type,
  });
};

// Model API
export const listModels = async (
  provider_id?: string,
  model_type?: string,
  page = 1,
  per_page = 20,
  active_only = true
): Promise<ListResponse<ModelDef>> => {
  const response = await api.get("/models", {
    params: { provider_id, model_type, page, per_page, active_only },
  });
  return {
    items: response.data.models,
    total: response.data.total,
    page: response.data.page,
    per_page: response.data.per_page,
  };
};

export const getModel = async (id: string): Promise<ModelDef> => {
  const response = await api.get(`/models/${id}`);
  return response.data;
};

export const createModel = async (data: CreateModel): Promise<ModelDef> => {
  const response = await api.post("/models", data);
  return response.data;
};

export const updateModel = async (
  id: string,
  data: Partial<CreateModel>
): Promise<ModelDef> => {
  const response = await api.put(`/models/${id}`, data);
  return response.data;
};

export const deleteModel = async (id: string): Promise<void> => {
  await api.delete(`/models/${id}`);
};

export const setDefaultModel = async (id: string): Promise<void> => {
  await api.post(`/models/${id}/set-default`);
};

// Embedding Space API
export const listEmbeddingSpaces = async (
  model_id?: string,
  page = 1,
  per_page = 20,
  active_only = true
): Promise<ListResponse<EmbeddingSpace>> => {
  const response = await api.get("/embedding-spaces", {
    params: { model_id, page, per_page, active_only },
  });
  return {
    items: response.data.spaces,
    total: response.data.total,
    page: response.data.page,
    per_page: response.data.per_page,
  };
};

export const getEmbeddingSpace = async (id: string): Promise<EmbeddingSpace> => {
  const response = await api.get(`/embedding-spaces/${id}`);
  return response.data;
};

export const createEmbeddingSpace = async (
  data: CreateEmbeddingSpace
): Promise<EmbeddingSpace> => {
  const response = await api.post("/embedding-spaces", data);
  return response.data;
};

export const updateEmbeddingSpace = async (
  id: string,
  data: Partial<CreateEmbeddingSpace>
): Promise<EmbeddingSpace> => {
  const response = await api.put(`/embedding-spaces/${id}`, data);
  return response.data;
};

export const deleteEmbeddingSpace = async (id: string): Promise<void> => {
  await api.delete(`/embedding-spaces/${id}`);
};

export const setDefaultEmbeddingSpace = async (id: string): Promise<void> => {
  await api.post(`/embedding-spaces/${id}/set-default`);
};

// Default lookups
export const getDefaultProvider = async (model_type: string): Promise<Provider> => {
  const response = await api.get(`/defaults/provider/${model_type}`);
  return response.data;
};

export const getDefaultModel = async (model_type: string): Promise<ModelDef> => {
  const response = await api.get(`/defaults/model/${model_type}`);
  return response.data;
};

export const getDefaultEmbeddingSpace = async (): Promise<EmbeddingSpace> => {
  const response = await api.get("/defaults/embedding-space");
  return response.data;
};