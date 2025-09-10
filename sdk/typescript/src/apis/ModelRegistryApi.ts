/**
 * Generated API client for Model Registry
 */
import { DefaultProvider, EmbeddingSpaceCreate, EmbeddingSpaceDefaultResponse, EmbeddingSpaceDeleteResponse, EmbeddingSpaceList, EmbeddingSpaceUpdate, EmbeddingSpaceWithModel, ModelDefCreate, ModelDefList, ModelDefUpdate, ModelDefWithProvider, ModelDefaultResponse, ModelDeleteResponse, ModelType, Provider, ProviderCreate, ProviderDefaultResponse, ProviderDeleteResponse, ProviderList, ProviderUpdate } from '../models/index';
import { BaseAPI, Configuration, RequestOpts, HTTPMethod, HTTPQuery, HTTPHeaders } from '../runtime';

export class ModelRegistryApi extends BaseAPI {
  constructor(configuration?: Configuration) {
    super(configuration);
  }

  /**List Providers
   * List all providers.
   */
  public async listProvidersApiV1ModelsProviders(options?: { page?: number; perPage?: number; activeOnly?: boolean; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<ProviderList> {
    const requestContext: RequestOpts = {
      path: `/api/v1/models/providers`,
      method: 'GET' as HTTPMethod,
      headers: {
        ...options?.headers,
      },
      query: {
        'page': options?.page,
        'per_page': options?.perPage,
        'active_only': options?.activeOnly,
        ...options?.query
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ProviderList>;
  }
  /**Create Provider
   * Create a new provider.
   */
  public async createProviderApiV1ModelsProviders(data: ProviderCreate): Promise<Provider> {
    const requestContext: RequestOpts = {
      path: `/api/v1/models/providers`,
      method: 'POST' as HTTPMethod,
      headers: {
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Provider>;
  }
  /**Get Provider
   * Get a specific provider.
   */
  public async getProviderApiV1ModelsProvidersProviderId(providerId: string): Promise<Provider> {
    const requestContext: RequestOpts = {
      path: `/api/v1/models/providers/${providerId}`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Provider>;
  }
  /**Update Provider
   * Update a provider.
   */
  public async updateProviderApiV1ModelsProvidersProviderId(providerId: string, data: ProviderUpdate): Promise<Provider> {
    const requestContext: RequestOpts = {
      path: `/api/v1/models/providers/${providerId}`,
      method: 'PUT' as HTTPMethod,
      headers: {
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Provider>;
  }
  /**Delete Provider
   * Delete a provider and all its dependent models and embedding spaces.
   */
  public async deleteProviderApiV1ModelsProvidersProviderId(providerId: string): Promise<ProviderDeleteResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/models/providers/${providerId}`,
      method: 'DELETE' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ProviderDeleteResponse>;
  }
  /**Set Default Provider
   * Set a provider as default for a model type.
   */
  public async setDefaultProviderApiV1ModelsProvidersProviderIdSetDefault(providerId: string, data: DefaultProvider): Promise<ProviderDefaultResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/models/providers/${providerId}/set-default`,
      method: 'POST' as HTTPMethod,
      headers: {
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ProviderDefaultResponse>;
  }
  /**List Models
   * List all model definitions.
   */
  public async listModelsApiV1ModelsModels(options?: { providerId?: string; modelType?: ModelType; page?: number; perPage?: number; activeOnly?: boolean; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<ModelDefList> {
    const requestContext: RequestOpts = {
      path: `/api/v1/models/models`,
      method: 'GET' as HTTPMethod,
      headers: {
        ...options?.headers,
      },
      query: {
        'provider_id': options?.providerId,
        'model_type': options?.modelType,
        'page': options?.page,
        'per_page': options?.perPage,
        'active_only': options?.activeOnly,
        ...options?.query
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ModelDefList>;
  }
  /**Create Model
   * Create a new model definition.
   */
  public async createModelApiV1ModelsModels(data: ModelDefCreate): Promise<ModelDefWithProvider> {
    const requestContext: RequestOpts = {
      path: `/api/v1/models/models`,
      method: 'POST' as HTTPMethod,
      headers: {
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ModelDefWithProvider>;
  }
  /**Get Model
   * Get a specific model definition.
   */
  public async getModelApiV1ModelsModelsModelId(modelId: string): Promise<ModelDefWithProvider> {
    const requestContext: RequestOpts = {
      path: `/api/v1/models/models/${modelId}`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ModelDefWithProvider>;
  }
  /**Update Model
   * Update a model definition.
   */
  public async updateModelApiV1ModelsModelsModelId(modelId: string, data: ModelDefUpdate): Promise<ModelDefWithProvider> {
    const requestContext: RequestOpts = {
      path: `/api/v1/models/models/${modelId}`,
      method: 'PUT' as HTTPMethod,
      headers: {
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ModelDefWithProvider>;
  }
  /**Delete Model
   * Delete a model definition and its dependent embedding spaces.
   */
  public async deleteModelApiV1ModelsModelsModelId(modelId: string): Promise<ModelDeleteResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/models/models/${modelId}`,
      method: 'DELETE' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ModelDeleteResponse>;
  }
  /**Set Default Model
   * Set a model as default for its type.
   */
  public async setDefaultModelApiV1ModelsModelsModelIdSetDefault(modelId: string): Promise<ModelDefaultResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/models/models/${modelId}/set-default`,
      method: 'POST' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ModelDefaultResponse>;
  }
  /**List Embedding Spaces
   * List all embedding spaces.
   */
  public async listEmbeddingSpacesApiV1ModelsEmbeddingSpaces(options?: { modelId?: string; page?: number; perPage?: number; activeOnly?: boolean; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<EmbeddingSpaceList> {
    const requestContext: RequestOpts = {
      path: `/api/v1/models/embedding-spaces`,
      method: 'GET' as HTTPMethod,
      headers: {
        ...options?.headers,
      },
      query: {
        'model_id': options?.modelId,
        'page': options?.page,
        'per_page': options?.perPage,
        'active_only': options?.activeOnly,
        ...options?.query
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<EmbeddingSpaceList>;
  }
  /**Create Embedding Space
   * Create a new embedding space with backing table and index.
   */
  public async createEmbeddingSpaceApiV1ModelsEmbeddingSpaces(data: EmbeddingSpaceCreate): Promise<EmbeddingSpaceWithModel> {
    const requestContext: RequestOpts = {
      path: `/api/v1/models/embedding-spaces`,
      method: 'POST' as HTTPMethod,
      headers: {
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<EmbeddingSpaceWithModel>;
  }
  /**Get Embedding Space
   * Get a specific embedding space.
   */
  public async getEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceId(spaceId: string): Promise<EmbeddingSpaceWithModel> {
    const requestContext: RequestOpts = {
      path: `/api/v1/models/embedding-spaces/${spaceId}`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<EmbeddingSpaceWithModel>;
  }
  /**Update Embedding Space
   * Update an embedding space.
   */
  public async updateEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceId(spaceId: string, data: EmbeddingSpaceUpdate): Promise<EmbeddingSpaceWithModel> {
    const requestContext: RequestOpts = {
      path: `/api/v1/models/embedding-spaces/${spaceId}`,
      method: 'PUT' as HTTPMethod,
      headers: {
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<EmbeddingSpaceWithModel>;
  }
  /**Delete Embedding Space
   * Delete an embedding space (does not drop the table).
   */
  public async deleteEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceId(spaceId: string): Promise<EmbeddingSpaceDeleteResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/models/embedding-spaces/${spaceId}`,
      method: 'DELETE' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<EmbeddingSpaceDeleteResponse>;
  }
  /**Set Default Embedding Space
   * Set an embedding space as default.
   */
  public async setDefaultEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdSetDefault(spaceId: string): Promise<EmbeddingSpaceDefaultResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/models/embedding-spaces/${spaceId}/set-default`,
      method: 'POST' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<EmbeddingSpaceDefaultResponse>;
  }
  /**Get Default Provider
   * Get the default provider for a model type.
   */
  public async getDefaultProviderApiV1ModelsDefaultsProviderModelType(modelType: ModelType): Promise<Provider> {
    const requestContext: RequestOpts = {
      path: `/api/v1/models/defaults/provider/${modelType}`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Provider>;
  }
  /**Get Default Model
   * Get the default model for a type.
   */
  public async getDefaultModelApiV1ModelsDefaultsModelModelType(modelType: ModelType): Promise<ModelDefWithProvider> {
    const requestContext: RequestOpts = {
      path: `/api/v1/models/defaults/model/${modelType}`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ModelDefWithProvider>;
  }
  /**Get Default Embedding Space
   * Get the default embedding space.
   */
  public async getDefaultEmbeddingSpaceApiV1ModelsDefaultsEmbeddingSpace(): Promise<EmbeddingSpaceWithModel> {
    const requestContext: RequestOpts = {
      path: `/api/v1/models/defaults/embedding-space`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<EmbeddingSpaceWithModel>;
  }
}