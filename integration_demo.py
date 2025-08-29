"""Integration example showing how to use the dynamic embedding system.

This demonstrates the complete workflow from document processing to
similarity search using multiple embedding providers with different dimensions.
"""

import asyncio
from datetime import datetime
from typing import Any


class MockEmbeddingProvider:
    """Mock embedding provider for demonstration."""

    def __init__(self, name: str, dimensions: int):
        self.name = name
        self.dimensions = dimensions

    async def aembed_query(self, text: str) -> list[float]:
        """Generate a mock embedding for a query."""
        await asyncio.sleep(0.1)  # Simulate API call
        # Generate a simple mock embedding based on text hash
        hash_val = hash(text) % 1000000
        base_value = hash_val / 1000000.0
        return [base_value + (i * 0.001) for i in range(self.dimensions)]

    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        """Generate mock embeddings for multiple documents."""
        embeddings = []
        for text in texts:
            embedding = await self.aembed_query(text)
            embeddings.append(embedding)
        return embeddings


class EnhancedEmbeddingService:
    """Enhanced embedding service supporting multiple providers."""

    def __init__(self):
        self.providers = {
            "openai": MockEmbeddingProvider("openai", 1536),
            "anthropic": MockEmbeddingProvider("anthropic", 768),
            "cohere": MockEmbeddingProvider("cohere", 1024),
            "mistral": MockEmbeddingProvider("mistral", 4096),
        }

    async def generate_embedding(
        self,
        text: str,
        provider_name: str
    ) -> tuple[list[float], dict[str, Any]]:
        """Generate embedding with usage info."""
        if provider_name not in self.providers:
            raise ValueError(f"Provider {provider_name} not available")

        provider = self.providers[provider_name]
        start_time = datetime.now()

        embedding = await provider.aembed_query(text)

        usage_info = {
            "provider": provider_name,
            "text_length": len(text),
            "embedding_dimensions": len(embedding),
            "response_time_ms": int((datetime.now() - start_time).total_seconds() * 1000),
        }

        return embedding, usage_info

    def get_provider_info(self, provider_name: str) -> dict[str, Any]:
        """Get provider information."""
        if provider_name not in self.providers:
            return {}

        provider = self.providers[provider_name]
        return {
            "name": provider_name,
            "available": True,
            "dimensions": provider.dimensions,
        }

    def list_available_providers(self) -> list[str]:
        """List all available providers."""
        return list(self.providers.keys())


class MockDocumentChunk:
    """Mock document chunk for demonstration."""

    def __init__(self, chunk_id: str, document_id: str, content: str):
        self.id = chunk_id
        self.document_id = document_id
        self.content = content
        self.embedding_models: list[str] = []
        self.primary_embedding_model: str | None = None
        self.embedding_provider: str | None = None
        self.embedding_created_at: datetime | None = None
        self.extra_metadata: dict[str, Any] = {}

    def add_embedding_model(self, model_name: str, set_as_primary: bool = False):
        """Add an embedding model to the list."""
        if model_name not in self.embedding_models:
            self.embedding_models.append(model_name)

        if set_as_primary or not self.primary_embedding_model:
            self.primary_embedding_model = model_name
            self.embedding_provider = model_name.split("_")[0]
            self.embedding_created_at = datetime.now()


class IntegratedWorkflowDemo:
    """Demonstration of the complete integrated workflow."""

    def __init__(self):
        self.embedding_service = EnhancedEmbeddingService()
        self.chunks: dict[str, MockDocumentChunk] = {}
        self.embeddings_storage: dict[str, dict[str, Any]] = {}

    async def process_document_chunk(
        self,
        chunk: MockDocumentChunk,
        providers: list[str]
    ) -> dict[str, Any]:
        """Process a document chunk with multiple embedding providers."""

        print(f"📄 Processing chunk: {chunk.id}")
        print(f"📝 Content: '{chunk.content[:100]}{'...' if len(chunk.content) > 100 else ''}'")
        print(f"🔧 Providers: {providers}")
        print()

        results = {}

        for provider in providers:
            try:
                print(f"  🔄 Generating {provider} embedding...")

                # Generate embedding
                embedding, usage_info = await self.embedding_service.generate_embedding(
                    chunk.content, provider
                )

                # Store in mock dynamic table
                table_name = f"{provider}_embeddings"
                if table_name not in self.embeddings_storage:
                    self.embeddings_storage[table_name] = {}

                self.embeddings_storage[table_name][chunk.id] = {
                    "document_id": chunk.document_id,
                    "chunk_id": chunk.id,
                    "embedding": embedding,
                    "content": chunk.content,
                    "metadata": usage_info,
                    "created_at": datetime.now()
                }

                # Update chunk metadata
                chunk.add_embedding_model(provider, set_as_primary=(provider == providers[0]))

                results[provider] = {
                    "success": True,
                    "dimensions": len(embedding),
                    "table": table_name,
                    "usage": usage_info
                }

                print(f"  ✅ {provider}: {len(embedding)}d → {table_name}")

            except Exception as e:
                results[provider] = {
                    "success": False,
                    "error": str(e)
                }
                print(f"  ❌ {provider}: {str(e)}")

        print(f"  📊 Chunk metadata updated: {chunk.embedding_models}")
        print(f"  🎯 Primary model: {chunk.primary_embedding_model}")
        print()

        return results

    async def similarity_search(
        self,
        query: str,
        provider: str,
        limit: int = 5
    ) -> list[dict[str, Any]]:
        """Perform similarity search using a specific provider."""

        print("🔍 Similarity search:")
        print(f"  Query: '{query}'")
        print(f"  Provider: {provider}")
        print(f"  Limit: {limit}")

        # Generate query embedding
        query_embedding, _ = await self.embedding_service.generate_embedding(query, provider)
        table_name = f"{provider}_embeddings"

        if table_name not in self.embeddings_storage:
            print(f"  ❌ No {table_name} table found")
            return []

        # Calculate similarity scores (cosine similarity)
        results = []
        for chunk_id, data in self.embeddings_storage[table_name].items():
            similarity = self._cosine_similarity(query_embedding, data["embedding"])
            results.append({
                "chunk_id": chunk_id,
                "document_id": data["document_id"],
                "content": data["content"],
                "similarity_score": similarity,
                "metadata": data["metadata"]
            })

        # Sort by similarity and limit
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        results = results[:limit]

        print(f"  📊 Found {len(results)} results in {table_name}")
        for i, result in enumerate(results, 1):
            print(f"    {i}. Score: {result['similarity_score']:.3f} - '{result['content'][:60]}...'")

        return results

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = sum(x * y for x, y in zip(a, b, strict=False))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    def get_storage_stats(self) -> dict[str, Any]:
        """Get statistics about stored embeddings."""
        stats = {
            "total_chunks": len(self.chunks),
            "embedding_tables": {},
            "total_embeddings": 0
        }

        for table_name, embeddings in self.embeddings_storage.items():
            provider = table_name.replace("_embeddings", "")
            provider_info = self.embedding_service.get_provider_info(provider)

            stats["embedding_tables"][table_name] = {
                "provider": provider,
                "dimensions": provider_info.get("dimensions", "unknown"),
                "embedding_count": len(embeddings),
                "chunks": list(embeddings.keys())
            }
            stats["total_embeddings"] += len(embeddings)

        return stats


async def run_integration_demo():
    """Run the complete integration demonstration."""

    print("=" * 80)
    print("🚀 DYNAMIC EMBEDDING SYSTEM - INTEGRATION DEMO")
    print("=" * 80)
    print()

    demo = IntegratedWorkflowDemo()

    # Sample document chunks
    chunks = [
        MockDocumentChunk(
            "chunk_001",
            "doc_001",
            "Artificial intelligence and machine learning are transforming how we process information."
        ),
        MockDocumentChunk(
            "chunk_002",
            "doc_001",
            "Vector databases enable efficient similarity search across high-dimensional embeddings."
        ),
        MockDocumentChunk(
            "chunk_003",
            "doc_002",
            "PostgreSQL with pgvector provides excellent support for vector operations and indexing."
        )
    ]

    # Store chunks
    for chunk in chunks:
        demo.chunks[chunk.id] = chunk

    # 1. Process chunks with multiple providers
    print("STEP 1: Processing document chunks with multiple embedding providers")
    print("-" * 60)

    providers = ["openai", "anthropic", "cohere"]

    for chunk in chunks:
        await demo.process_document_chunk(chunk, providers)

    # 2. Show storage statistics
    print("\nSTEP 2: Storage Statistics")
    print("-" * 40)

    stats = demo.get_storage_stats()
    print(f"📊 Total chunks processed: {stats['total_chunks']}")
    print(f"📊 Total embeddings stored: {stats['total_embeddings']}")
    print(f"📊 Embedding tables: {len(stats['embedding_tables'])}")
    print()

    for table_name, info in stats["embedding_tables"].items():
        print(f"  📋 {table_name}:")
        print(f"    Provider: {info['provider']}")
        print(f"    Dimensions: {info['dimensions']}")
        print(f"    Embeddings: {info['embedding_count']}")
        print()

    # 3. Perform similarity searches
    print("STEP 3: Similarity Search Examples")
    print("-" * 40)

    queries = [
        ("machine learning applications", "openai"),
        ("vector search techniques", "anthropic"),
        ("database optimization", "cohere"),
    ]

    for query, provider in queries:
        print()
        await demo.similarity_search(query, provider, limit=3)

    # 4. Cross-provider comparison
    print("\nSTEP 4: Cross-Provider Comparison")
    print("-" * 40)

    query = "artificial intelligence systems"
    print(f"🔍 Comparing search results for: '{query}'")
    print()

    for provider in providers:
        print(f"  📊 Results from {provider}_embeddings:")
        results = await demo.similarity_search(query, provider, limit=2)
        if not results:
            print("    No results found")
        print()

    print("=" * 80)
    print("✅ INTEGRATION DEMO COMPLETE")
    print("=" * 80)
    print()

    print("🎯 Key Achievements:")
    achievements = [
        "✅ Multiple embedding providers working simultaneously",
        "✅ Different vector dimensions properly handled",
        "✅ Automatic table creation per provider",
        "✅ Efficient similarity search per model",
        "✅ Proper metadata tracking",
        "✅ Scalable architecture for new providers"
    ]

    for achievement in achievements:
        print(f"  {achievement}")

    return demo


if __name__ == "__main__":
    # Run the complete integration demo
    demo = asyncio.run(run_integration_demo())
