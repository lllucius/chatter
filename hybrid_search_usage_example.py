"""
Practical usage example of the hybrid vector search system.

This shows how to use the new hybrid vector search concepts without requiring database setup.
"""

from typing import List, Tuple

# Import only the model components we need
from chatter.models.document import DocumentChunk, HybridVectorSearchHelper


def demonstrate_hybrid_usage():
    """Demonstrate practical usage of the hybrid vector search system."""
    
    print("=== Practical Hybrid Vector Search Usage ===\n")
    
    # 1. Create chunks and set embeddings from different models
    print("1. Setting embeddings from different models:")
    
    chunks = []
    embedding_configs = [
        {
            "name": "OpenAI text-embedding-3-small",
            "vector": [0.1 + i * 0.001 for i in range(1536)],
            "provider": "openai",
            "model": "text-embedding-3-small",
            "content": "Machine learning algorithms"
        },
        {
            "name": "Sentence Transformers",
            "vector": [0.2 + i * 0.001 for i in range(768)],
            "provider": "sentence-transformers", 
            "model": "all-MiniLM-L6-v2",
            "content": "Natural language processing"
        },
        {
            "name": "Custom small model",
            "vector": [0.3 + i * 0.001 for i in range(384)],
            "provider": "custom",
            "model": "small-embeddings-v1",
            "content": "Artificial intelligence research"
        },
        {
            "name": "Large custom model",
            "vector": [0.4 + i * 0.001 for i in range(3072)],
            "provider": "custom",
            "model": "large-embeddings-v1",
            "content": "Deep learning neural networks"
        }
    ]
    
    for i, config in enumerate(embedding_configs):
        chunk = DocumentChunk(
            document_id=f"doc-{i+1}",
            content=config["content"],
            chunk_index=0,
            content_hash=f"hash-{i+1}"
        )
        
        # Use the new hybrid system
        chunk.set_embedding_vector(
            vector=config["vector"],
            provider=config["provider"],
            model=config["model"]
        )
        
        chunks.append(chunk)
        
        print(f"✓ {config['name']}: {len(config['vector'])}-dim → raw_dim={chunk.raw_dim}")
    
    print()
    
    # 2. Demonstrate automatic search optimization
    print("2. Automatic search column selection:")
    
    helper = HybridVectorSearchHelper()
    
    search_scenarios = [
        {
            "query": "search query with 1536 dimensions",
            "query_vector": [0.5] * 1536,
            "expected": "embedding"
        },
        {
            "query": "search query with 768 dimensions", 
            "query_vector": [0.5] * 768,
            "expected": "raw_embedding"
        },
        {
            "query": "search query with 512 dimensions",
            "query_vector": [0.5] * 512,
            "expected": "raw_embedding"
        }
    ]
    
    for scenario in search_scenarios:
        column = helper.choose_search_column(scenario["query_vector"], prefer_exact_match=True)
        prepared = helper.prepare_query_vector(scenario["query_vector"], column)
        
        print(f"Query: {len(scenario['query_vector'])}-dim")
        print(f"  → Column: '{column}' (prepared: {len(prepared)}-dim)")
    
    print()
    
    # 3. Show chunk embedding capabilities
    print("3. Chunk embedding capabilities:")
    
    for i, chunk in enumerate(chunks):
        config = embedding_configs[i]
        
        print(f"Chunk {i+1} ({config['name']}):")
        print(f"  Has 1536-dim embedding: {chunk.has_embedding_for_dimension(1536)}")
        print(f"  Has {chunk.raw_dim}-dim embedding: {chunk.has_embedding_for_dimension(chunk.raw_dim)}")
        print(f"  Has 512-dim embedding: {chunk.has_embedding_for_dimension(512)}")
        
        # Show what embedding would be used for different queries
        search_embedding_1536 = chunk.get_search_embedding(1536)
        search_embedding_original = chunk.get_search_embedding(chunk.raw_dim)
        search_embedding_other = chunk.get_search_embedding(512)
        
        print(f"  Search embedding for 1536-dim query: {len(search_embedding_1536) if search_embedding_1536 else 'None'}")
        print(f"  Search embedding for {chunk.raw_dim}-dim query: {len(search_embedding_original) if search_embedding_original else 'None'}")
        print(f"  Search embedding for 512-dim query: {len(search_embedding_other) if search_embedding_other else 'None'}")
        print()


def show_database_benefits():
    """Show the database structure and benefits."""
    
    print("=== Database Structure & Benefits ===\n")
    
    print("Enhanced DocumentChunk table:")
    print("┌─────────────────────────┬─────────────┬────────────────────────────┐")
    print("│ Column                  │ Type        │ Purpose                    │")
    print("├─────────────────────────┼─────────────┼────────────────────────────┤")
    print("│ embedding               │ Vector(1536)│ Fixed-dim, HNSW indexed    │")
    print("│ raw_embedding           │ JSON        │ Original vector, any dim   │") 
    print("│ computed_embedding      │ Vector(1536)│ Normalized, HNSW indexed   │")
    print("│ raw_dim                 │ Integer     │ Original dimension filter  │")
    print("│ embedding_provider      │ String      │ Provider metadata          │")
    print("│ embedding_model         │ String      │ Model metadata             │")
    print("│ embedding_dimensions    │ Integer     │ Dimension metadata         │")
    print("│ embedding_created_at    │ DateTime    │ Timestamp metadata         │")
    print("└─────────────────────────┴─────────────┴────────────────────────────┘")
    print()
    
    print("Indexes created:")
    print("• idx_document_chunks_embedding_cosine (HNSW on embedding)")
    print("• idx_document_chunks_computed_embedding_cosine (HNSW on computed_embedding)")
    print("• idx_document_chunks_raw_dim (B-tree on raw_dim)")
    print()
    
    print("Key benefits:")
    print("✓ Automatic column selection based on query vector size")
    print("✓ Fast pgvector HNSW indexes for optimal performance")
    print("✓ Support for any embedding dimension in raw_embedding")
    print("✓ Automatic normalization via SQLAlchemy event listeners")
    print("✓ Dimension filtering for exact matches")
    print("✓ No Python-side vector math - all done in Postgres")
    print("✓ Backward compatibility with existing code")
    print()


def show_migration_info():
    """Show the migration information."""
    
    print("=== Migration Information ===\n")
    
    print("To apply the hybrid vector search:")
    print("1. Run: alembic upgrade hybrid_vector_search")
    print()
    
    print("Migration adds:")
    print("• raw_embedding column (JSON, nullable)")
    print("• computed_embedding column (Vector(1536), nullable)")
    print("• raw_dim column (Integer, nullable, indexed)")
    print("• Enhanced HNSW indexes with optimized parameters")
    print()
    
    print("Existing data compatibility:")
    print("• Existing 'embedding' column data is preserved")
    print("• Event listeners will populate new columns automatically")
    print("• No data loss during migration")
    print()


def show_usage_patterns():
    """Show common usage patterns."""
    
    print("=== Common Usage Patterns ===\n")
    
    patterns = [
        {
            "scenario": "Standard OpenAI embeddings",
            "code": "chunk.set_embedding_vector(openai_1536_vector, 'openai', 'text-embedding-3-small')",
            "result": "Uses 'embedding' column for fastest search"
        },
        {
            "scenario": "Multiple embedding models",
            "code": "# Different models can coexist\nchunk1.set_embedding_vector(openai_vector, 'openai', 'text-embedding-3-small')\nchunk2.set_embedding_vector(st_vector, 'sentence-transformers', 'all-MiniLM-L6-v2')",
            "result": "System automatically chooses optimal search strategy"
        },
        {
            "scenario": "Searching with exact dimensions",
            "code": "results = await pipeline.search_documents(query, prefer_exact_match=True)",
            "result": "Prefers exact dimensional matches when available"
        },
        {
            "scenario": "Searching with normalization",
            "code": "results = await pipeline.search_documents(query, prefer_exact_match=False)",
            "result": "Uses computed_embedding for consistent results"
        }
    ]
    
    for pattern in patterns:
        print(f"Scenario: {pattern['scenario']}")
        print(f"Code: {pattern['code']}")
        print(f"Result: {pattern['result']}")
        print()


if __name__ == "__main__":
    demonstrate_hybrid_usage()
    show_database_benefits()
    show_migration_info()
    show_usage_patterns()