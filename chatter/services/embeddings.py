"""Embedding generation service."""

import hashlib
import time
from typing import Any
import numpy as np

from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings

try:
    from langchain_anthropic import AnthropicEmbeddings

    ANTHROPIC_EMBEDDINGS_AVAILABLE = True
except ImportError:
    AnthropicEmbeddings = None
    ANTHROPIC_EMBEDDINGS_AVAILABLE = False

try:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings

    GOOGLE_AVAILABLE = True
except ImportError:
    GoogleGenerativeAIEmbeddings = None
    GOOGLE_AVAILABLE = False

try:
    from langchain_cohere import CohereEmbeddings

    COHERE_AVAILABLE = True
except ImportError:
    CohereEmbeddings = None
    COHERE_AVAILABLE = False

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False

from chatter.config import get_settings
from chatter.core.dynamic_embeddings import get_model_dimensions
from chatter.utils.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class DimensionalReductionEmbeddings(Embeddings):
    """Embedding wrapper that supports optional dimensional reduction."""
    
    def __init__(
        self,
        base_embeddings: Embeddings,
        target_dim: int,
        strategy: str = "truncate",
        reducer_path: str | None = None,
        normalize: bool = True,
    ):
        """Initialize dimensional reduction wrapper.
        
        Args:
            base_embeddings: Base embedding provider
            target_dim: Target dimension after reduction
            strategy: "truncate" for simple truncation, "reducer" for fitted reducer
            reducer_path: Path to joblib reducer file (required for "reducer" strategy)
            normalize: Whether to L2-normalize vectors after reduction
        """
        self.base = base_embeddings
        self.target_dim = target_dim
        self.strategy = strategy
        self.normalize = normalize
        self.reducer = None
        
        if strategy == "reducer":
            if not reducer_path:
                raise ValueError("reducer_path required for 'reducer' strategy")
            if not JOBLIB_AVAILABLE:
                raise ImportError("joblib required for dimensional reduction")
            
            try:
                self.reducer = joblib.load(reducer_path)
                logger.info(
                    "Loaded dimensional reducer",
                    reducer_path=reducer_path,
                    target_dim=target_dim
                )
            except Exception as e:
                logger.error(
                    "Failed to load dimensional reducer",
                    reducer_path=reducer_path,
                    error=str(e)
                )
                raise
    
    def _reduce_vector(self, vector: list[float]) -> list[float]:
        """Apply dimensional reduction to a single vector."""
        if self.strategy == "truncate":
            # Simple truncation to target dimension
            reduced = vector[:self.target_dim]
            # Pad with zeros if vector is shorter than target
            if len(reduced) < self.target_dim:
                reduced.extend([0.0] * (self.target_dim - len(reduced)))
        elif self.strategy == "reducer":
            # Use fitted reducer (PCA/SVD)
            if self.reducer is None:
                raise RuntimeError("Reducer not loaded")
            
            vector_array = np.array(vector).reshape(1, -1)
            reduced_array = self.reducer.transform(vector_array)[0]
            reduced = reduced_array.tolist()
        else:
            raise ValueError(f"Unknown reduction strategy: {self.strategy}")
        
        # L2 normalize if requested
        if self.normalize:
            norm = np.linalg.norm(reduced)
            if norm > 0:
                reduced = (np.array(reduced) / norm).tolist()
        
        return reduced
    
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed documents and apply dimensional reduction."""
        base_embeddings = self.base.embed_documents(texts)
        return [self._reduce_vector(embedding) for embedding in base_embeddings]
    
    def embed_query(self, text: str) -> list[float]:
        """Embed query and apply dimensional reduction."""
        base_embedding = self.base.embed_query(text)
        return self._reduce_vector(base_embedding)


class EmbeddingService:
    """Service for generating text embeddings."""

    def __init__(self) -> None:
        """Initialize embedding service."""
        self._providers: dict[str, Embeddings] = {}
        self._initialize_providers()

    def _initialize_providers(self) -> None:
        """Initialize available embedding providers."""
        # OpenAI
        if settings.openai_api_key:
            try:
                base_provider = OpenAIEmbeddings(
                    api_key=settings.openai_api_key,
                    base_url=settings.openai_base_url,
                    model=settings.openai_embedding_model,
                    chunk_size=settings.openai_embedding_chunk_size,
                )
                
                # Apply dimensional reduction if enabled
                if settings.embedding_reduction_enabled:
                    self._providers["openai"] = DimensionalReductionEmbeddings(
                        base_embeddings=base_provider,
                        target_dim=settings.embedding_reduction_target_dim,
                        strategy=settings.embedding_reduction_strategy,
                        reducer_path=settings.embedding_reducer_path,
                        normalize=settings.embedding_reduction_normalize,
                    )
                    logger.info(
                        "OpenAI embedding provider initialized with dimensional reduction",
                        model=settings.openai_embedding_model,
                        target_dim=settings.embedding_reduction_target_dim,
                        strategy=settings.embedding_reduction_strategy,
                    )
                else:
                    self._providers["openai"] = base_provider
                    logger.info(
                        "OpenAI embedding provider initialized",
                        model=settings.openai_embedding_model,
                    )
            except Exception as e:
                logger.warning(
                    "Failed to initialize OpenAI embedding provider",
                    error=str(e),
                )

        # Anthropic (if available)
        if (
            settings.anthropic_api_key
            and ANTHROPIC_EMBEDDINGS_AVAILABLE
        ):
            try:
                # Note: Anthropic doesn't have dedicated embedding models in langchain_anthropic yet
                # This is a placeholder for when they become available
                pass
            except Exception as e:
                logger.warning(
                    "Failed to initialize Anthropic embedding provider",
                    error=str(e),
                )

        # Google Generative AI
        if settings.google_api_key and GOOGLE_AVAILABLE:
            try:
                base_provider = GoogleGenerativeAIEmbeddings(
                    model=settings.google_embedding_model,
                    google_api_key=settings.google_api_key,
                )
                
                # Apply dimensional reduction if enabled
                if settings.embedding_reduction_enabled:
                    self._providers["google"] = DimensionalReductionEmbeddings(
                        base_embeddings=base_provider,
                        target_dim=settings.embedding_reduction_target_dim,
                        strategy=settings.embedding_reduction_strategy,
                        reducer_path=settings.embedding_reducer_path,
                        normalize=settings.embedding_reduction_normalize,
                    )
                    logger.info(
                        "Google Generative AI embedding provider initialized with dimensional reduction",
                        model=settings.google_embedding_model,
                        target_dim=settings.embedding_reduction_target_dim,
                    )
                else:
                    self._providers["google"] = base_provider
                    logger.info(
                        "Google Generative AI embedding provider initialized",
                        model=settings.google_embedding_model,
                    )
            except Exception as e:
                logger.warning(
                    "Failed to initialize Google Generative AI embedding provider",
                    error=str(e),
                )

        # Cohere
        if settings.cohere_api_key and COHERE_AVAILABLE:
            try:
                base_provider = CohereEmbeddings(
                    model=settings.cohere_embedding_model,
                    cohere_api_key=settings.cohere_api_key,
                )
                
                # Apply dimensional reduction if enabled
                if settings.embedding_reduction_enabled:
                    self._providers["cohere"] = DimensionalReductionEmbeddings(
                        base_embeddings=base_provider,
                        target_dim=settings.embedding_reduction_target_dim,
                        strategy=settings.embedding_reduction_strategy,
                        reducer_path=settings.embedding_reducer_path,
                        normalize=settings.embedding_reduction_normalize,
                    )
                    logger.info(
                        "Cohere embedding provider initialized with dimensional reduction",
                        model=settings.cohere_embedding_model,
                        target_dim=settings.embedding_reduction_target_dim,
                    )
                else:
                    self._providers["cohere"] = base_provider
                    logger.info(
                        "Cohere embedding provider initialized",
                        model=settings.cohere_embedding_model,
                    )
            except Exception as e:
                logger.warning(
                    "Failed to initialize Cohere embedding provider",
                    error=str(e),
                )

        if not self._providers:
            logger.warning("No embedding providers available")

    def get_provider(self, provider_name: str) -> Embeddings | None:
        """Get embedding provider by name.

        Args:
            provider_name: Name of the provider

        Returns:
            Embedding provider or None if not available
        """
        return self._providers.get(provider_name)

    def get_default_provider(self) -> Embeddings | None:
        """Get default embedding provider.

        Returns:
            Default embedding provider or None if none available
        """
        if not self._providers:
            return None

        # Try to get the configured default provider
        default_provider = settings.default_embedding_provider
        if default_provider in self._providers:
            return self._providers[default_provider]

        # Fall back to first available provider
        return next(iter(self._providers.values()))

    def list_available_providers(self) -> list[str]:
        """List available embedding providers.

        Returns:
            List of provider names
        """
        return list(self._providers.keys())

    def get_provider_info(self, provider_name: str) -> dict[str, Any]:
        """Get information about an embedding provider.

        Args:
            provider_name: Name of the provider

        Returns:
            Provider information
        """
        provider = self._providers.get(provider_name)
        if not provider:
            return {}

        info = {
            "name": provider_name,
            "available": True,
            "class": provider.__class__.__name__,
        }

        # Add provider-specific information
        if provider_name == "openai":
            info.update(
                {
                    "model": settings.openai_embedding_model,
                    "dimensions": get_model_dimensions("openai"),
                    "chunk_size": settings.openai_embedding_chunk_size,
                }
            )
        elif provider_name == "anthropic":
            info.update(
                {
                    "model": getattr(settings, "anthropic_embedding_model", "claude-3-sonnet"),
                    "dimensions": get_model_dimensions("anthropic"),
                }
            )
        elif provider_name == "google":
            info.update(
                {
                    "model": settings.google_embedding_model,
                    "dimensions": get_model_dimensions("google"),
                }
            )
        elif provider_name == "cohere":
            info.update(
                {
                    "model": settings.cohere_embedding_model,
                    "dimensions": get_model_dimensions("cohere"),
                }
            )

        return info

    def get_all_provider_info(self) -> dict[str, dict[str, Any]]:
        """Get information for all available providers.
        
        Returns:
            Dictionary mapping provider names to their info
        """
        all_info = {}
        for provider_name in self._providers.keys():
            all_info[provider_name] = self.get_provider_info(provider_name)
        return all_info

    async def generate_embedding(
        self, text: str, provider_name: str | None = None
    ) -> tuple[list[float], dict[str, Any]]:
        """Generate embedding for text.

        Args:
            text: Text to embed
            provider_name: Specific provider to use (optional)

        Returns:
            Tuple of (embedding vector, usage info)

        Raises:
            EmbeddingError: If embedding generation fails
        """
        start_time = time.time()

        # Get provider
        if provider_name:
            provider = self.get_provider(provider_name)
            if not provider:
                raise EmbeddingError(
                    f"Provider '{provider_name}' not available"
                ) from None
        else:
            provider = self.get_default_provider()
            if not provider:
                raise EmbeddingError(
                    "No embedding providers available"
                ) from None
            provider_name = self._get_provider_name(provider)

        try:
            # Generate embedding
            embedding = await provider.aembed_query(text)

            # Calculate usage info
            usage_info = {
                "provider": provider_name,
                "model": self._get_model_name(provider_name),
                "text_length": len(text),
                "embedding_dimensions": len(embedding),
                "response_time_ms": int(
                    (time.time() - start_time) * 1000
                ),
                "text_hash": hashlib.sha256(text.encode()).hexdigest(),
            }

            logger.debug(
                "Embedding generated",
                provider=provider_name,
                text_length=len(text),
                dimensions=len(embedding),
                response_time_ms=usage_info["response_time_ms"],
            )

            return embedding, usage_info

        except Exception as e:
            logger.error(
                "Failed to generate embedding",
                provider=provider_name,
                text_length=len(text),
                error=str(e),
            )
            raise EmbeddingError(
                f"Failed to generate embedding: {str(e)}"
            ) from e

    async def generate_embeddings(
        self,
        texts: list[str],
        provider_name: str | None = None,
        batch_size: int = 100,
    ) -> tuple[list[list[float]], dict[str, Any]]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed
            provider_name: Specific provider to use (optional)
            batch_size: Batch size for processing

        Returns:
            Tuple of (embedding vectors list, usage info)

        Raises:
            EmbeddingError: If embedding generation fails
        """
        start_time = time.time()

        # Get provider
        if provider_name:
            provider = self.get_provider(provider_name)
            if not provider:
                raise EmbeddingError(
                    f"Provider '{provider_name}' not available"
                ) from None
        else:
            provider = self.get_default_provider()
            if not provider:
                raise EmbeddingError(
                    "No embedding providers available"
                ) from None
            provider_name = self._get_provider_name(provider)

        try:
            # Process in batches
            all_embeddings = []
            total_chars = 0

            for i in range(0, len(texts), batch_size):
                batch = texts[i : i + batch_size]
                batch_embeddings = await provider.aembed_documents(
                    batch
                )
                all_embeddings.extend(batch_embeddings)
                total_chars += sum(len(text) for text in batch)

            # Calculate usage info
            usage_info = {
                "provider": provider_name,
                "model": self._get_model_name(provider_name),
                "text_count": len(texts),
                "total_characters": total_chars,
                "embedding_dimensions": len(all_embeddings[0])
                if all_embeddings
                else 0,
                "response_time_ms": int(
                    (time.time() - start_time) * 1000
                ),
                "batch_size": batch_size,
            }

            logger.info(
                "Embeddings generated",
                provider=provider_name,
                text_count=len(texts),
                total_characters=total_chars,
                dimensions=usage_info["embedding_dimensions"],
                response_time_ms=usage_info["response_time_ms"],
            )

            return all_embeddings, usage_info

        except Exception as e:
            logger.error(
                "Failed to generate embeddings",
                provider=provider_name,
                text_count=len(texts),
                error=str(e),
            )
            raise EmbeddingError(
                f"Failed to generate embeddings: {str(e)}"
            ) from e

    def _get_provider_name(self, provider: Embeddings) -> str:
        """Get provider name from provider instance."""
        if isinstance(provider, OpenAIEmbeddings):
            return "openai"
        elif (
            GOOGLE_AVAILABLE
            and GoogleGenerativeAIEmbeddings
            and isinstance(provider, GoogleGenerativeAIEmbeddings)
        ):
            return "google"
        elif (
            COHERE_AVAILABLE
            and CohereEmbeddings
            and isinstance(provider, CohereEmbeddings)
        ):
            return "cohere"
        else:
            return "unknown"

    def _get_model_name(self, provider_name: str) -> str:
        """Get model name for provider."""
        if provider_name == "openai":
            return settings.openai_embedding_model
        elif provider_name == "google":
            return settings.google_embedding_model
        elif provider_name == "cohere":
            return settings.cohere_embedding_model
        else:
            return "unknown"


class EmbeddingError(Exception):
    """Embedding generation error."""

    pass
