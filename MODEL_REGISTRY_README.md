# Model Registry and Dimensional Reduction Implementation

This implementation provides a comprehensive solution for managing AI model providers, model definitions, and embedding spaces with support for dimensional reduction to work around pgvector limitations.

## Key Features

### 1. Database-Backed Model Registry
- **Providers**: Manage AI service providers (OpenAI, Anthropic, Google, Cohere, etc.)
- **Model Definitions**: Define specific models with their configurations and capabilities
- **Embedding Spaces**: Configure vector storage with dimensional reduction and indexing options

### 2. Dimensional Reduction Support
- **Truncation Strategy**: Simple truncation to target dimensions
- **Reducer Strategy**: Use fitted PCA/TruncatedSVD models for better quality reduction
- **Normalization**: Optional L2 normalization after reduction for cosine similarity preservation

### 3. API Management
- Full CRUD operations for providers, models, and embedding spaces
- RESTful API endpoints with authentication
- Default model/provider selection and management

### 4. Frontend Administration
- React-based admin interface for model management
- Tabbed interface for providers, models, and embedding spaces
- Forms for creating and configuring new entries

## Solving PGVector Dimension Limits

The implementation addresses the 2000-dimension limit in pgvector 0.6.x:

1. **Registry-Based Approach**: Each embedding space can have different dimensions and reduction strategies
2. **Dynamic Table Creation**: Automatically creates pgvector tables with appropriate dimensions
3. **HNSW Index Support**: Uses HNSW indexes which work better with reduced dimensions
4. **Reduction Strategies**: Multiple approaches for dimensional reduction

## Configuration

Add these settings to your `.env` file:

```bash
# Enable dimensional reduction
EMBEDDING_REDUCTION_ENABLED=true

# Target dimensions (must be <= 2000 for pgvector 0.6.x)
EMBEDDING_REDUCTION_TARGET_DIM=1536

# Reduction strategy: "truncate" or "reducer"
EMBEDDING_REDUCTION_STRATEGY=truncate

# Path to trained reducer (for "reducer" strategy)
EMBEDDING_REDUCER_PATH=./data/reducers/svd_3072_to_1536.joblib

# L2 normalization after reduction
EMBEDDING_REDUCTION_NORMALIZE=true
```

## Usage Examples

### 1. Basic Usage with Truncation

```python
# The embedding service will automatically apply dimensional reduction
# if enabled in configuration
embedding_service = EmbeddingService()
provider = embedding_service.get_provider("openai")

# This will automatically reduce dimensions if configured
embeddings = provider.embed_documents(["text1", "text2"])
```

### 2. Training a Dimensional Reducer

```bash
# Create a corpus file (one text per line)
echo "Sample text for training" > corpus.txt
echo "Another document" >> corpus.txt

# Train a TruncatedSVD reducer (requires scikit-learn)
python scripts/train_truncated_svd.py \
    --corpus corpus.txt \
    --provider openai \
    --target-dim 1536 \
    --output svd_reducer.joblib
```

### 3. Using the Model Registry API

```python
from chatter.core.model_registry import ModelRegistryService
from chatter.schemas.model_registry import ProviderCreate, ModelDefCreate

# Create a provider
provider_data = ProviderCreate(
    name="custom_openai",
    provider_type="openai",
    display_name="Custom OpenAI",
    description="Custom OpenAI configuration"
)

# Create a model with dimensional reduction
model_data = ModelDefCreate(
    provider_id=provider.id,
    name="text-embedding-3-large-reduced",
    model_type="embedding",
    display_name="OpenAI 3-Large (Reduced)",
    model_name="text-embedding-3-large",
    dimensions=3072  # Original dimensions
)

# Create embedding space with reduction
space_data = EmbeddingSpaceCreate(
    model_id=model.id,
    name="openai_3large_1536",
    display_name="OpenAI 3-Large Reduced to 1536",
    base_dimensions=3072,
    effective_dimensions=1536,
    reduction_strategy="truncate",
    table_name="openai_3large_1536_embed"
)
```

### 4. Frontend Administration

Access the admin interface at `/admin/models` to:
- Add new providers and configure their settings
- Define models with their capabilities and dimensions
- Create embedding spaces with reduction configurations
- Set default providers and models

## Database Migration

Run the migration to create the registry tables:

```bash
alembic upgrade head
```

This creates three new tables:
- `providers`: AI service providers
- `model_defs`: Model definitions with capabilities
- `embedding_spaces`: Vector storage configurations

## API Endpoints

The implementation adds these API endpoints under `/api/v1/models/`:

### Providers
- `GET /providers` - List providers
- `POST /providers` - Create provider
- `GET /providers/{id}` - Get provider details
- `PUT /providers/{id}` - Update provider
- `DELETE /providers/{id}` - Delete provider
- `POST /providers/{id}/set-default` - Set as default

### Models
- `GET /models` - List models
- `POST /models` - Create model
- `GET /models/{id}` - Get model details
- `PUT /models/{id}` - Update model
- `DELETE /models/{id}` - Delete model
- `POST /models/{id}/set-default` - Set as default

### Embedding Spaces
- `GET /embedding-spaces` - List spaces
- `POST /embedding-spaces` - Create space (with table/index)
- `GET /embedding-spaces/{id}` - Get space details
- `PUT /embedding-spaces/{id}` - Update space
- `DELETE /embedding-spaces/{id}` - Delete space
- `POST /embedding-spaces/{id}/set-default` - Set as default

### Defaults
- `GET /defaults/provider/{model_type}` - Get default provider
- `GET /defaults/model/{model_type}` - Get default model
- `GET /defaults/embedding-space` - Get default embedding space

## Implementation Notes

1. **Backward Compatibility**: The system works alongside existing .env-based configuration
2. **Dynamic Tables**: Creating an embedding space automatically creates the pgvector table and HNSW index
3. **Performance**: Dimensional reduction is applied at embedding time for optimal performance
4. **Flexibility**: Multiple reduction strategies and configurations can coexist
5. **Monitoring**: All operations are logged for debugging and monitoring

## Dependencies

Core functionality requires:
- SQLAlchemy 2.0+
- FastAPI
- Pydantic v2
- pgvector
- numpy

Optional dependencies:
- scikit-learn (for training dimensional reducers)
- joblib (for loading/saving reducers)

## Error Handling

The implementation handles common pgvector dimension errors:
- Automatic detection of dimension limits
- Graceful fallback to exact search for unsupported configurations
- Clear error messages for configuration issues
- Validation of dimensional reduction parameters

This provides a complete solution for managing AI models while working around pgvector dimension limitations through intelligent dimensional reduction strategies.