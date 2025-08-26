# Dynamic Embedding Models Implementation

This implementation provides a flexible, scalable solution for storing and searching embeddings from multiple LLM providers with different vector dimensions, following the pattern outlined in the ChatGPT conversation.

## Overview

The system creates separate database tables for each embedding model, each optimized for its specific vector dimension and use case. This approach eliminates the inefficiencies of fixed-dimension schemas and provides optimal performance for each provider.

## Architecture

### Core Components

1. **Dynamic Model Factory** (`chatter/core/dynamic_embeddings.py`)
   - Creates SQLAlchemy models on-demand for each embedding provider
   - Automatically handles table and index creation
   - Supports configurable distance metrics and index types

2. **Dynamic Vector Store Service** (`chatter/services/dynamic_vector_store.py`)
   - Manages embedding storage across multiple provider tables
   - Handles similarity search with provider-specific optimization
   - Provides unified interface for multi-model operations

3. **Enhanced Document Model** (`chatter/models/document.py`)
   - Tracks which embedding models have been applied to each chunk
   - Maintains backward compatibility with legacy embeddings
   - Supports multiple concurrent embedding models per chunk

## Provider Support

| Provider  | Dimensions | Table Name            | Default Index |
|-----------|------------|-----------------------|---------------|
| OpenAI    | 1536       | `openai_embeddings`   | ivfflat       |
| Anthropic | 768        | `anthropic_embeddings`| hnsw          |
| Cohere    | 1024       | `cohere_embeddings`   | ivfflat       |
| Mistral   | 4096       | `mistral_embeddings`  | ivfflat       |

## Usage Examples

### Basic Setup

```python
from chatter.core.dynamic_embeddings import get_embedding_model
from chatter.services.dynamic_vector_store import DynamicVectorStoreService

# Create embedding models for different providers
openai_model = get_embedding_model("openai", 1536, engine)
anthropic_model = get_embedding_model("anthropic", 768, engine)

# Initialize dynamic vector store
vector_store = DynamicVectorStoreService(async_session)
```

### Storing Embeddings

```python
# Store embeddings for different providers
await vector_store.store_embedding(
    chunk_id="chunk_001",
    embedding=openai_embedding,  # 1536 dimensions
    provider_name="openai"
)

await vector_store.store_embedding(
    chunk_id="chunk_001", 
    embedding=anthropic_embedding,  # 768 dimensions
    provider_name="anthropic"
)
```

### Similarity Search

```python
# Search using OpenAI embeddings
results = await vector_store.similarity_search(
    query_embedding=query_vector,
    provider_name="openai",
    limit=10,
    score_threshold=0.7
)

# Search using Anthropic embeddings
results = await vector_store.similarity_search(
    query_embedding=query_vector,
    provider_name="anthropic", 
    limit=10,
    score_threshold=0.7
)
```

### Index Configuration

```python
# Configure different index types per provider
get_embedding_model(
    "openai", 
    1536, 
    engine,
    metric="cosine",
    index_type="ivfflat",
    lists=100
)

get_embedding_model(
    "anthropic",
    768,
    engine, 
    metric="l2",
    index_type="hnsw",
    m=16,
    ef_construction=64
)
```

## Database Schema

### Per-Provider Embedding Tables

Each provider gets its own optimized table:

```sql
-- Example: openai_embeddings table
CREATE TABLE openai_embeddings (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(12) NOT NULL,
    chunk_id VARCHAR(12) NOT NULL,
    embedding vector(1536) NOT NULL,
    content TEXT NOT NULL,
    metadata TEXT,
    INDEX USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)
);

-- Example: anthropic_embeddings table  
CREATE TABLE anthropic_embeddings (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(12) NOT NULL,
    chunk_id VARCHAR(12) NOT NULL,
    embedding vector(768) NOT NULL,
    content TEXT NOT NULL,
    metadata TEXT,
    INDEX USING hnsw (embedding vector_l2_ops) WITH (m = 16, ef_construction = 64)
);
```

### Enhanced DocumentChunk Table

```sql
-- Updated document_chunks table
ALTER TABLE document_chunks 
ADD COLUMN embedding_models JSON,
ADD COLUMN primary_embedding_model VARCHAR(100);
```

## Configuration Options

### Distance Metrics

- **cosine**: Cosine similarity (default for most use cases)
- **l2**: Euclidean distance
- **ip**: Inner product

### Index Types

- **ivfflat**: Good for large datasets, configurable `lists` parameter
- **hnsw**: Better recall, configurable `m` and `ef_construction` parameters

### Index Tuning

```python
# IVFFlat configuration
{
    "index_type": "ivfflat",
    "metric": "cosine", 
    "lists": 100  # Adjust based on dataset size
}

# HNSW configuration
{
    "index_type": "hnsw",
    "metric": "l2",
    "m": 16,              # Graph connectivity
    "ef_construction": 64  # Build-time accuracy
}
```

## Migration Guide

### From Fixed-Dimension Schema

1. **Backup existing data**
   ```bash
   pg_dump -t document_chunks > backup_chunks.sql
   ```

2. **Run migration**
   ```bash
   alembic upgrade add_dynamic_embeddings
   ```

3. **Migrate existing embeddings**
   ```python
   # Script to migrate legacy embeddings to provider-specific tables
   await migrate_legacy_embeddings()
   ```

### Benefits of Migration

- ✅ **Storage Efficiency**: No wasted dimensions (was losing 768 dims for Anthropic, 512 for Cohere)
- ✅ **Performance**: Optimized indexes per model
- ✅ **Scalability**: Add new models without schema changes
- ✅ **Flexibility**: Different index types per provider

## Performance Characteristics

### Storage Savings

| Provider  | Old Size (1536d) | New Size | Savings |
|-----------|------------------|----------|---------|
| OpenAI    | 6,144 bytes     | 6,144 bytes | 0% |
| Anthropic | 6,144 bytes     | 3,072 bytes | 50% |
| Cohere    | 6,144 bytes     | 4,096 bytes | 33% |
| Mistral   | 6,144 bytes*    | 16,384 bytes | -166%** |

*Truncated in old system  
**Proper storage vs truncated data

### Query Performance

- **Index Optimization**: Each table has indexes tuned for its dimension
- **Reduced I/O**: Smaller vectors = fewer disk reads
- **Better Caching**: More vectors fit in memory

## Testing

### Run Basic Tests

```bash
python standalone_demo.py
```

### Run Integration Demo

```bash  
python integration_demo.py
```

### Expected Output

```
✅ Multiple embedding providers working simultaneously
✅ Different vector dimensions properly handled  
✅ Automatic table creation per provider
✅ Efficient similarity search per model
✅ Proper metadata tracking
✅ Scalable architecture for new providers
```

## Troubleshooting

### Common Issues

1. **pgvector not available**
   - Falls back to Text storage
   - No vector indexes created
   - Similarity search uses fallback methods

2. **Provider not found**
   - Check provider is registered in `get_model_dimensions()`
   - Verify provider initialization

3. **Dimension mismatch**
   - Embedding service logs warnings
   - Check provider configuration

### Debug Commands

```python
# List registered models
from chatter.core.dynamic_embeddings import list_embedding_models
print(list_embedding_models())

# Check table creation
# Tables are created automatically on first use
```

## Future Enhancements

### Planned Features

- [ ] **Automatic dimension detection** from embedding responses
- [ ] **Multi-model search** across different providers
- [ ] **Embedding versioning** support
- [ ] **Index optimization** based on usage patterns
- [ ] **Compression** for large embeddings

### Extension Points

The system is designed for easy extension:

1. **New Providers**: Add to `get_model_dimensions()`
2. **Custom Indexes**: Extend `ensure_table_and_index()`
3. **Search Algorithms**: Implement in `DynamicVectorStoreService`

## Contributing

When adding new embedding providers:

1. Update `get_model_dimensions()` with provider dimensions
2. Add provider to embedding service initialization  
3. Create tests for the new provider
4. Update documentation

## License

This implementation follows the same license as the main chatter project.