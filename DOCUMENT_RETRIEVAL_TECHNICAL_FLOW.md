# Document Retrieval Fix - Technical Flow

## Before (Broken)

```
User uploads document
    ↓
EmbeddingPipeline
    ↓
SimpleVectorStore.store_embeddings()
    ↓
Writes to: document_chunks table
    - document_id
    - content
    - chunk_index  
    - embedding (pgvector)
    - raw_embedding (pgvector)
    - computed_embedding (pgvector)

User sends chat with enable_retrieval=True
    ↓
get_vector_store_retriever()
    ↓
Creates: PGVectorStore (langchain-postgres)
    ↓
Looks in: langchain_pg_collection & langchain_pg_embedding tables
    ❌ THESE TABLES ARE EMPTY!
    ↓
Retriever returns: [] (no documents)
    ↓
Chat response: No context used
```

## After (Fixed)

```
User uploads document
    ↓
EmbeddingPipeline
    ↓
SimpleVectorStore.store_embeddings()
    ↓
Writes to: document_chunks table
    - document_id
    - content
    - chunk_index
    - embedding (pgvector)
    - raw_embedding (pgvector)  
    - computed_embedding (pgvector)

User sends chat with enable_retrieval=True
    ↓
get_vector_store_retriever()
    ↓
Creates: DocumentChunkRetriever (custom)
    ↓
Looks in: document_chunks table ✅
    ↓
SimpleVectorStore.search_similar()
    - Generates query embedding
    - Performs vector similarity search
    - Filters by user_id and document_ids
    - Returns top k chunks
    ↓
Retriever returns: [Document(...), Document(...), ...]
    ↓
RetrievalNode.execute()
    - Formats documents as context
    - Updates state: retrieval_context = "..."
    ↓
LLM Node receives context
    - Adds context to system message
    - "You are a helpful assistant.\n\nContext:\n[document content]"
    ↓
Chat response: Uses retrieved documents! ✅
```

## Key Components

### DocumentChunkRetriever (New)
```python
class DocumentChunkRetriever:
    def __init__(self, embeddings, user_id=None, document_ids=None, k=5):
        # Store configuration
        
    async def ainvoke(self, query: str) -> list[Document]:
        # 1. Generate query embedding
        query_embedding = await self.embeddings.aembed_query(query)
        
        # 2. Search document_chunks table
        results = await SimpleVectorStore.search_similar(
            query_embedding=query_embedding,
            limit=self.k,
            document_ids=self.document_ids,
        )
        
        # 3. Convert to langchain Documents
        return [Document(page_content=chunk.content, ...) for chunk, score in results]
```

### Workflow Flow
```
Workflow Execution
    ↓
1. RetrievalNode (if enable_retrieval=True)
    - Calls retriever.ainvoke(last_human_message)
    - Returns: {"retrieval_context": "document content..."}
    ↓
2. LangGraph merges state
    - state["retrieval_context"] = "document content..."
    ↓
3. LLM Node
    - Reads state["retrieval_context"]
    - Adds to system message
    - Calls LLM with enriched context
    ↓
4. Response generated with document context
```

## Database Schema

### document_chunks (Used by SimpleVectorStore and DocumentChunkRetriever)
```sql
CREATE TABLE document_chunks (
    id VARCHAR(26) PRIMARY KEY,
    document_id VARCHAR(26) REFERENCES documents(id),
    content TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    
    -- Hybrid vector columns (1536-dim and dynamic dimensions)
    embedding vector(1536),           -- Standard OpenAI embeddings
    raw_embedding vector,              -- Original dimension embeddings  
    computed_embedding vector(768),    -- Compressed embeddings
    raw_dim INTEGER,                   -- Track original dimension
    
    -- Metadata
    extra_metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_document_chunks_embedding ON document_chunks 
    USING hnsw (embedding vector_cosine_ops);
```

### langchain_pg_* tables (NO LONGER USED)
```sql
-- These were created by langchain-postgres but are NOT populated
-- The old code tried to use these, which is why retrieval failed
CREATE TABLE langchain_pg_collection (...);
CREATE TABLE langchain_pg_embedding (...);
```

## Logging Added

To help debug retrieval issues, comprehensive logging was added:

1. **get_vector_store_retriever()** - Logs retriever creation
2. **DocumentChunkRetriever.ainvoke()** - Logs each retrieval attempt
3. **WorkflowGraphBuilder._create_nodes()** - Logs when retriever is set on nodes
4. **RetrievalNode.set_retriever()** - Logs when retriever is configured
5. **RetrievalNode.execute()** - Logs retrieval execution and results
6. **LLM Node._apply_context()** - Logs when retrieval context is applied

Example log output:
```
INFO: Creating vector store retriever user_id=user_123 document_ids=['doc_abc']
INFO: Custom document chunk retriever created successfully
INFO: Creating workflow nodes node_count=2 has_retriever=True
INFO: Setting retriever on node retrieve_context (type: retrieval)
INFO: Retriever set on RetrievalNode retrieve_context has_retriever=True
INFO: RetrievalNode retrieve_context executing has_retriever=True
INFO: RetrievalNode retrieve_context retrieving for query query="What is Python?"
INFO: Generated query embedding embedding_dim=1536
INFO: SimpleVectorStore returned results result_count=3
INFO: RetrievalNode retrieve_context retrieved documents doc_count=3
INFO: RetrievalNode retrieve_context generated context context_length=850
INFO: LLM Node call_model applying context has_retrieval_context=True retrieval_context_length=850
```
