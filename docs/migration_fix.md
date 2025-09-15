# Embedding Column Migration Fix

## Problem
The application was failing with database column errors:
```
(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column "computed_embedding" of relation "document_chunks" does not exist
```
and
```
column document_chunks.raw_embedding does not exist
```

## Root Cause
The migration chain was broken. The `add_embedding_field.py` migration had `down_revision = None` instead of connecting to the existing migration chain, so it was never applied to databases that already had previous migrations.

## Fix Applied
Changed in `alembic/versions/add_embedding_field.py`:
```python
# Before (broken)
down_revision = None  # Set to appropriate revision when integrating

# After (fixed)  
down_revision = 'c7a2069f99cb'
```

This connects the embedding field migration to the existing migration chain.

## Migration Chain (Fixed)
```
001_workflow_templates
    ↓
ef29b1af6dfe (workflow config)  
    ↓
add_audit_logs
    ↓
c7a2069f99cb (rating columns)
    ↓
add_embedding_field (adds: embedding, embedding_model, embedding_dimensions)
    ↓ 
hybrid_vector_search (adds: raw_embedding, computed_embedding, raw_dim, embedding_provider, embedding_created_at)
```

## Production Deployment
To fix the production database:

1. **Backup your database first** (important!)

2. Run the migrations:
   ```bash
   alembic upgrade head
   ```

3. Verify the columns exist:
   ```sql
   \d document_chunks
   -- Should show all embedding columns including:
   -- - embedding
   -- - raw_embedding  
   -- - computed_embedding
   -- - raw_dim
   -- - embedding_provider
   -- - embedding_model
   -- - embedding_dimensions
   -- - embedding_created_at
   ```

4. Test document processing to ensure it works correctly.

## Columns Added
The fix adds these columns to the `document_chunks` table:

### From add_embedding_field migration:
- `embedding` - VECTOR(1536) - Fixed dimension embedding for fast search
- `embedding_model` - VARCHAR(100) - Model used for embedding
- `embedding_dimensions` - INTEGER - Embedding dimension count

### From hybrid_vector_search migration:
- `raw_embedding` - JSON - Raw embedding vector of any dimension  
- `computed_embedding` - VECTOR(1536) - Computed embedding (padded/truncated to 1536)
- `raw_dim` - INTEGER - Original embedding dimension for filtering
- `embedding_provider` - VARCHAR(50) - Embedding provider name
- `embedding_created_at` - DATETIME - When embedding was created

## Verification
After applying the fix, these operations should work:
- Document chunk INSERT operations with embedding data
- Document chunk SELECT operations accessing embedding columns
- Document processing pipeline end-to-end