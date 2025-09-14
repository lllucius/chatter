"""
Comprehensive example demonstrating the hybrid vector search system.

This example shows how the system automatically handles different embedding dimensions
and chooses the optimal column for fast pgvector search.
"""

from chatter.models.document import (
    DocumentChunk, 
    HybridVectorSearchHelper,
    normalize_embedding_to_fixed_dim
)
from datetime import datetime


def demonstrate_hybrid_vector_search():
    """Demonstrate the hybrid vector search functionality."""
    
    print("=== Hybrid Vector Search Demonstration ===\n")
    
    # 1. Create sample document chunks with different embedding dimensions
    print("1. Creating sample document chunks with different embedding dimensions:")
    
    chunk1 = DocumentChunk(
        document_id="doc1",
        content="This is a chunk about machine learning.",
        chunk_index=0,
        content_hash="hash1"
    )
    
    chunk2 = DocumentChunk(
        document_id="doc2", 
        content="This chunk discusses artificial intelligence.",
        chunk_index=0,
        content_hash="hash2"
    )
    
    chunk3 = DocumentChunk(
        document_id="doc3",
        content="Natural language processing techniques.",
        chunk_index=0,
        content_hash="hash3"
    )
    
    # Set different embedding dimensions
    # OpenAI text-embedding-3-small (1536 dimensions)
    embedding_1536 = [0.1 + i * 0.001 for i in range(1536)]
    chunk1.set_embedding_vector(embedding_1536, "openai", "text-embedding-3-small")
    
    # Smaller embedding (768 dimensions) 
    embedding_768 = [0.2 + i * 0.001 for i in range(768)]
    chunk2.set_embedding_vector(embedding_768, "sentence-transformers", "all-MiniLM-L6-v2")
    
    # Larger embedding (2048 dimensions)
    embedding_2048 = [0.3 + i * 0.001 for i in range(2048)]
    chunk3.set_embedding_vector(embedding_2048, "custom", "large-model")
    
    print(f"Chunk 1: {len(embedding_1536)} dimensions (OpenAI)")
    print(f"Chunk 2: {len(embedding_768)} dimensions (Sentence Transformers)")  
    print(f"Chunk 3: {len(embedding_2048)} dimensions (Custom Large)")
    print()
    
    # 2. Demonstrate automatic normalization
    print("2. Automatic normalization to 1536 dimensions:")
    print(f"Original 768-dim → 1536-dim: padding with {1536-768} zeros")
    print(f"Original 2048-dim → 1536-dim: truncating {2048-1536} values")
    print()
    
    # 3. Demonstrate column selection logic
    print("3. Hybrid search column selection:")
    helper = HybridVectorSearchHelper()
    
    # Query with 1536 dimensions (exact match)
    query_1536 = [0.5] * 1536
    column = helper.choose_search_column(query_1536)
    print(f"Query (1536-dim) → Use '{column}' column (optimized pgvector)")
    
    # Query with 768 dimensions (prefer exact match)
    query_768 = [0.5] * 768
    column = helper.choose_search_column(query_768, prefer_exact_match=True)
    print(f"Query (768-dim, exact) → Use '{column}' column (exact match)")
    
    # Query with 768 dimensions (computed match)
    column = helper.choose_search_column(query_768, prefer_exact_match=False)
    print(f"Query (768-dim, computed) → Use '{column}' column (normalized)")
    
    # Query with 512 dimensions (no exact match available)
    query_512 = [0.5] * 512
    column = helper.choose_search_column(query_512, prefer_exact_match=True)
    print(f"Query (512-dim) → Use '{column}' column (fallback)")
    print()
    
    # 4. Demonstrate query vector preparation
    print("4. Query vector preparation for different columns:")
    
    # Prepare for embedding column (normalize to 1536)
    prepared = helper.prepare_query_vector(query_768, 'embedding')
    print(f"768-dim query for 'embedding' → {len(prepared)}-dim (padded)")
    
    # Prepare for raw_embedding column (keep original)
    prepared = helper.prepare_query_vector(query_768, 'raw_embedding')
    print(f"768-dim query for 'raw_embedding' → {len(prepared)}-dim (original)")
    
    # Prepare for computed_embedding column (normalize to 1536)
    query_2048_demo = [0.5] * 2048
    prepared = helper.prepare_query_vector(query_2048_demo, 'computed_embedding')
    print(f"2048-dim query for 'computed_embedding' → {len(prepared)}-dim (truncated)")
    print()
    
    # 5. Show the database structure benefits
    print("5. Database structure and indexing:")
    print("├── embedding (Vector(1536))        - Fast HNSW index for 1536-dim")
    print("├── raw_embedding (JSON)            - Flexible storage for any dimension")
    print("├── computed_embedding (Vector(1536)) - Normalized with HNSW index")
    print("└── raw_dim (Integer)               - Filter by original dimension")
    print()
    
    # 6. Demonstrate search scenarios
    print("6. Search scenarios and automatic column selection:")
    scenarios = [
        (1536, "Standard OpenAI embedding", "embedding", "Direct optimized search"),
        (768, "Sentence Transformers", "raw_embedding", "Exact dimension match"),
        (512, "Custom small model", "computed_embedding", "Normalized search"),
        (3072, "Large custom model", "computed_embedding", "Truncated search"),
    ]
    
    for dim, model, expected_column, description in scenarios:
        query = [0.5] * dim
        column = helper.choose_search_column(query, prefer_exact_match=True)
        print(f"• {model} ({dim}-dim) → '{column}' ({description})")
    
    print()
    print("=== Key Benefits ===")
    print("✓ Automatic column selection based on query vector size")
    print("✓ Fast pgvector indexes for both 1536-dim and computed embeddings")  
    print("✓ Flexible storage for any embedding dimension in raw_embedding")
    print("✓ Dimension filtering with raw_dim for exact matches")
    print("✓ No Python-side vector math - fully uses Postgres + pgvector")
    print("✓ Event listeners ensure automatic normalization and consistency")


if __name__ == "__main__":
    demonstrate_hybrid_vector_search()