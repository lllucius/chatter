/**
 * Generated API client for Model Registry
 */
import { DefaultProvider, EmbeddingSpaceCreate, EmbeddingSpaceDefaultResponse, EmbeddingSpaceDeleteResponse, EmbeddingSpaceList, EmbeddingSpaceUpdate, EmbeddingSpaceWithModel, ModelDefCreate, ModelDefList, ModelDefUpdate, ModelDefWithProvider, ModelDefaultResponse, ModelDeleteResponse, Provider, ProviderCreate, ProviderDefaultResponse, ProviderDeleteResponse, ProviderList, ProviderUpdate } from '../models/index';
import { BaseAPI, Configuration, RequestOptions } from '../runtime';

export class ModelRegistryApi extends BaseAPI {
  constructor(configuration?: Configuration) {
    super(configuration);
  }

  /**List Providers
   * List all providers.
   */
  public async listProvidersApiV1ModelsProviders(options?: RequestOptions): Promise<ProviderList> {
    const requestOptions: RequestOptions = {
      method: 'GET',
      headers: options?.headers,
      query: {
        'page': options?.page,
        'per_page': options?.perPage,
        'active_only': options?.activeOnly,
      },
    };

    return this.request<ProviderList>(`/api/v1/models/providers`, requestOptions);
  }
  /**Create Provider
   * Create a new provider.
   */
  public async createProviderApiV1ModelsProviders(data: ProviderCreate): Promise<Provider> {
    const requestOptions: RequestOptions = {
      method: 'POST',
      body: data,
    };

    return this.request<Provider>(`/api/v1/models/providers`, requestOptions);
  }
  /**Get Provider
   * Get a specific provider.
   */
  public async getProviderApiV1ModelsProvidersProviderId(providerId: string): Promise<Provider> {
    const requestOptions: RequestOptions = {
      method: 'GET',
    };

    return this.request<Provider>(`/api/v1/models/providers/${providerId}`, requestOptions);
  }
  /**Update Provider
   * Update a provider.
   */
  public async updateProviderApiV1ModelsProvidersProviderId(providerId: string, data: ProviderUpdate): Promise<Provider> {
    const requestOptions: RequestOptions = {
      method: 'PUT',
      body: data,
    };

    return this.request<Provider>(`/api/v1/models/providers/${providerId}`, requestOptions);
  }
  /**Delete Provider
   * Delete a provider and all its dependent models and embedding spaces.
   */
  public async deleteProviderApiV1ModelsProvidersProviderId(providerId: string): Promise<ProviderDeleteResponse> {
    const requestOptions: RequestOptions = {
      method: 'DELETE',
    };

    return this.request<ProviderDeleteResponse>(`/api/v1/models/providers/${providerId}`, requestOptions);
  }
  /**Set Default Provider
   * Set a provider as default for a model type.
   */
  public async setDefaultProviderApiV1ModelsProvidersProviderIdSetDefault(providerId: string, data: DefaultProvider): Promise<ProviderDefaultResponse> {
    const requestOptions: RequestOptions = {
      method: 'POST',
      body: data,
    };

    return this.request<ProviderDefaultResponse>(`/api/v1/models/providers/${providerId}/set-default`, requestOptions);
  }
  /**List Models
   * List all model definitions.
   */
  public async listModelsApiV1ModelsModels(options?: RequestOptions): Promise<ModelDefList> {
    const requestOptions: RequestOptions = {
      method: 'GET',
      headers: options?.headers,
      query: {
        'provider_id': options?.providerId,
        'model_type': options?.modelType,
        'page': options?.page,
        'per_page': options?.perPage,
        'active_only': options?.activeOnly,
      },
    };

    return this.request<ModelDefList>(`/api/v1/models/models`, requestOptions);
  }
  /**Create Model
   * Create a new model definition.
   */
  public async createModelApiV1ModelsModels(data: ModelDefCreate): Promise<ModelDefWithProvider> {
    const requestOptions: RequestOptions = {
      method: 'POST',
      body: data,
    };

    return this.request<ModelDefWithProvider>(`/api/v1/models/models`, requestOptions);
  }
  /**Get Model
   * Get a specific model definition.
   */
  public async getModelApiV1ModelsModelsModelId(modelId: string): Promise<ModelDefWithProvider> {
    const requestOptions: RequestOptions = {
      method: 'GET',
    };

    return this.request<ModelDefWithProvider>(`/api/v1/models/models/${modelId}`, requestOptions);
  }
  /**Update Model
   * Update a model definition.
   */
  public async updateModelApiV1ModelsModelsModelId(modelId: string, data: ModelDefUpdate): Promise<ModelDefWithProvider> {
    const requestOptions: RequestOptions = {
      method: 'PUT',
      body: data,
    };

    return this.request<ModelDefWithProvider>(`/api/v1/models/models/${modelId}`, requestOptions);
  }
  /**Delete Model
   * Delete a model definition and its dependent embedding spaces.
   */
  public async deleteModelApiV1ModelsModelsModelId(modelId: string): Promise<ModelDeleteResponse> {
    const requestOptions: RequestOptions = {
      method: 'DELETE',
    };

    return this.request<ModelDeleteResponse>(`/api/v1/models/models/${modelId}`, requestOptions);
  }
  /**Set Default Model
   * Set a model as default for its type.
   */
  public async setDefaultModelApiV1ModelsModelsModelIdSetDefault(modelId: string): Promise<ModelDefaultResponse> {
    const requestOptions: RequestOptions = {
      method: 'POST',
    };

    return this.request<ModelDefaultResponse>(`/api/v1/models/models/${modelId}/set-default`, requestOptions);
  }
  /**List Embedding Spaces
   * List all embedding spaces.
   */
  public async listEmbeddingSpacesApiV1ModelsEmbeddingSpaces(options?: RequestOptions): Promise<EmbeddingSpaceList> {
    const requestOptions: RequestOptions = {
      method: 'GET',
      headers: options?.headers,
      query: {
        'model_id': options?.modelId,
        'page': options?.page,
        'per_page': options?.perPage,
        'active_only': options?.activeOnly,
      },
    };

    return this.request<EmbeddingSpaceList>(`/api/v1/models/embedding-spaces`, requestOptions);
  }
  /**Create Embedding Space
   * Create a new embedding space with backing table and index.
   */
  public async createEmbeddingSpaceApiV1ModelsEmbeddingSpaces(data: EmbeddingSpaceCreate): Promise<EmbeddingSpaceWithModel> {
    const requestOptions: RequestOptions = {
      method: 'POST',
      body: data,
    };

    return this.request<EmbeddingSpaceWithModel>(`/api/v1/models/embedding-spaces`, requestOptions);
  }
  /**Get Embedding Space
   * Get a specific embedding space.
   */
  public async getEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceId(spaceId: string): Promise<EmbeddingSpaceWithModel> {
    const requestOptions: RequestOptions = {
      method: 'GET',
    };

    return this.request<EmbeddingSpaceWithModel>(`/api/v1/models/embedding-spaces/${spaceId}`, requestOptions);
  }
  /**Update Embedding Space
   * Update an embedding space.
   */
  public async updateEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceId(spaceId: string, data: EmbeddingSpaceUpdate): Promise<EmbeddingSpaceWithModel> {
    const requestOptions: RequestOptions = {
      method: 'PUT',
      body: data,
    };

    return this.request<EmbeddingSpaceWithModel>(`/api/v1/models/embedding-spaces/${spaceId}`, requestOptions);
  }
  /**Delete Embedding Space
   * Delete an embedding space (does not drop the table).
   */
  public async deleteEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceId(spaceId: string): Promise<EmbeddingSpaceDeleteResponse> {
    const requestOptions: RequestOptions = {
      method: 'DELETE',
    };

    return this.request<EmbeddingSpaceDeleteResponse>(`/api/v1/models/embedding-spaces/${spaceId}`, requestOptions);
  }
  /**Set Default Embedding Space
   * Set an embedding space as default.
   */
  public async setDefaultEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdSetDefault(spaceId: string): Promise<EmbeddingSpaceDefaultResponse> {
    const requestOptions: RequestOptions = {
      method: 'POST',
    };

    return this.request<EmbeddingSpaceDefaultResponse>(`/api/v1/models/embedding-spaces/${spaceId}/set-default`, requestOptions);
  }
  /**Get Default Provider
   * Get the default provider for a model type.
   */
  public async getDefaultProviderApiV1ModelsDefaultsProviderModelType(modelType: ModelType): Promise<Provider> {
    const requestOptions: RequestOptions = {
      method: 'GET',
    };

    return this.request<Provider>(`/api/v1/models/defaults/provider/${modelType}`, requestOptions);
  }
  /**Get Default Model
   * Get the default model for a type.
   */
  public async getDefaultModelApiV1ModelsDefaultsModelModelType(modelType: ModelType): Promise<ModelDefWithProvider> {
    const requestOptions: RequestOptions = {
      method: 'GET',
    };

    return this.request<ModelDefWithProvider>(`/api/v1/models/defaults/model/${modelType}`, requestOptions);
  }
  /**Get Default Embedding Space
   * Get the default embedding space.
   */
  public async getDefaultEmbeddingSpaceApiV1ModelsDefaultsEmbeddingSpace(): Promise<EmbeddingSpaceWithModel> {
    const requestOptions: RequestOptions = {
      method: 'GET',
    };

    return this.request<EmbeddingSpaceWithModel>(`/api/v1/models/defaults/embedding-space`, requestOptions);
  }
}