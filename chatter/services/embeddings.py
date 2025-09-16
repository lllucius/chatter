"""Embedding generation service."""

import hashlib
import time
from typing import Any
import asyncio

import numpy as np
from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings
from pydantic import SecretStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

try:
    ANTHROPIC_EMBEDDINGS_AVAILABLE = True
except ImportError:
    ANTHROPIC_EMBEDDINGS_AVAILABLE = False

try:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings

    GOOGLE_AVAILABLE = True
except ImportError:
    GoogleGenerativeAIEmbeddings = None
    GOOGLE_AVAILABLE = False

try:
    import cohere
    from langchain_cohere import CohereEmbeddings

    COHERE_AVAILABLE = True
except ImportError:
    CohereEmbeddings = None
    cohere = None
    COHERE_AVAILABLE = False

try:
    import joblib

    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False

from chatter.config import get_settings, settings
from chatter.core.model_registry import ModelRegistryService
from chatter.models.registry import ModelType, ProviderType
from chatter.models.document import DocumentChunk
from chatter.utils.database import get_session_maker
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class SafeOpenAIEmbeddings(OpenAIEmbeddings):
    """OpenAI embeddings wrapper that handles response format inconsistencies.

    This wrapper addresses the issue where OpenAI API responses sometimes
    don't have the expected 'data' attribute structure that LangChain expects.
    """

    async def aembed_documents(
        self, texts: list[str], chunk_size: int | None = None, **kwargs
    ) -> list[list[float]]:
        """Safely embed documents with proper response format handling."""
        try:
            return await super().aembed_documents(
                texts, chunk_size, **kwargs
            )
        except (AttributeError, KeyError, TypeError) as e:
            # Check if this is the specific response format error
            if (
                "model_dump" in str(e)
                or "data" in str(e)
                or "'list' object" in str(e)
            ):
                logger.warning(
                    "OpenAI response format issue detected, attempting manual processing",
                    error=str(e),
                    text_count=len(texts),
                )
                return await self._safe_embed_documents_fallback(
                    texts, chunk_size, **kwargs
                )
            else:
                # Re-raise other errors
                raise

    async def aembed_query(self, text: str, **kwargs) -> list[float]:
        """Safely embed query with proper response format handling."""
        try:
            return await super().aembed_query(text, **kwargs)
        except (AttributeError, KeyError, TypeError) as e:
            if (
                "model_dump" in str(e)
                or "data" in str(e)
                or "'list' object" in str(e)
            ):
                logger.warning(
                    "OpenAI response format issue detected for query, attempting manual processing",
                    error=str(e),
                )
                result = await self._safe_embed_documents_fallback(
                    [text], None, **kwargs
                )
                return result[0] if result else []
            else:
                raise

    async def _safe_embed_documents_fallback(
        self, texts: list[str], chunk_size: int | None = None, **kwargs
    ) -> list[list[float]]:
        """Fallback method that manually handles OpenAI API responses."""
        chunk_size_ = chunk_size or self.chunk_size
        client_kwargs = {**self._invocation_params, **kwargs}

        embeddings: list[list[float]] = []

        for i in range(0, len(texts), chunk_size_):
            batch = texts[i : i + chunk_size_]
            try:
                response = await self.async_client.create(
                    input=batch, **client_kwargs
                )

                # Handle different response formats
                if isinstance(response, list):
                    # Response is already a list of embedding objects
                    logger.debug(
                        "OpenAI response is already a list format"
                    )
                    batch_embeddings = []
                    for r in response:
                        if isinstance(r, dict) and "embedding" in r:
                            batch_embeddings.append(r["embedding"])
                        elif hasattr(r, "embedding"):
                            batch_embeddings.append(r.embedding)
                        else:
                            logger.error(
                                "Invalid embedding object in list response",
                                object_type=type(r),
                                object_keys=(
                                    list(r.keys())
                                    if isinstance(r, dict)
                                    else "N/A"
                                ),
                            )
                            raise ValueError(
                                f"Invalid embedding object in response: {type(r)}"
                            )
                    embeddings.extend(batch_embeddings)
                else:
                    # Try to access .data attribute safely
                    try:
                        data = response.data
                        if data:
                            # Standard OpenAI response format with .data attribute
                            logger.debug("OpenAI response has .data attribute")
                            batch_embeddings = []
                            for r in data:
                                if hasattr(r, "embedding"):
                                    batch_embeddings.append(r.embedding)
                                elif isinstance(r, dict) and "embedding" in r:
                                    batch_embeddings.append(r["embedding"])
                                else:
                                    logger.error(
                                        "Invalid embedding object in .data response",
                                        object_type=type(r),
                                    )
                                    raise ValueError(
                                        f"Invalid embedding object in response.data: {type(r)}"
                                    )
                            embeddings.extend(batch_embeddings)
                        else:
                            # .data exists but is empty/falsy, try other paths
                            raise AttributeError("Empty .data attribute")
                    except AttributeError:
                        # No .data attribute or .data access failed, try dict access
                        if isinstance(response, dict) and "data" in response:
                            # Dict format response
                            logger.debug(
                                "OpenAI response is dict with 'data' key"
                            )
                            batch_embeddings = []
                            for r in response["data"]:
                                if isinstance(r, dict) and "embedding" in r:
                                    batch_embeddings.append(r["embedding"])
                                elif hasattr(r, "embedding"):
                                    batch_embeddings.append(r.embedding)
                                else:
                                    logger.error(
                                        "Invalid embedding object in dict response",
                                        object_type=type(r),
                                        object_keys=(
                                            list(r.keys())
                                            if isinstance(r, dict)
                                            else "N/A"
                                        ),
                                    )
                                    raise ValueError(
                                        f"Invalid embedding object in response['data']: {type(r)}"
                                    )
                            embeddings.extend(batch_embeddings)
                        elif hasattr(response, "model_dump"):
                            # Pydantic model, convert to dict
                            logger.debug("OpenAI response is Pydantic model")
                            response_dict = response.model_dump()
                            if "data" in response_dict:
                                batch_embeddings = []
                                for r in response_dict["data"]:
                                    if isinstance(r, dict) and "embedding" in r:
                                        batch_embeddings.append(r["embedding"])
                                    elif hasattr(r, "embedding"):
                                        batch_embeddings.append(r.embedding)
                                    else:
                                        logger.error(
                                            "Invalid embedding object in model_dump response",
                                            object_type=type(r),
                                            object_keys=(
                                                list(r.keys())
                                                if isinstance(r, dict)
                                                else "N/A"
                                            ),
                                        )
                                        raise ValueError(
                                            f"Invalid embedding object in model_dump['data']: {type(r)}"
                                        )
                                embeddings.extend(batch_embeddings)
                            else:
                                logger.error(
                                    "Unexpected OpenAI response format after model_dump",
                                    response_keys=list(response_dict.keys()),
                                )
                                raise ValueError(
                                    f"Unexpected OpenAI response format: {type(response)}"
                                )
                        else:
                            logger.error(
                                "Unhandled OpenAI response format",
                                response_type=type(response),
                            )
                            raise ValueError(
                                f"Unhandled OpenAI response format: {type(response)}"
                            )


            except Exception as e:
                logger.error(
                    "Failed to process OpenAI embedding batch",
                    batch_size=len(batch),
                    error=str(e),
                )
                raise

        logger.debug(
            "Successfully processed embeddings using fallback method",
            total_texts=len(texts),
            total_embeddings=len(embeddings),
        )

        return embeddings


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
                raise ValueError(
                    "reducer_path required for 'reducer' strategy"
                )
            if not JOBLIB_AVAILABLE:
                raise ImportError(
                    "joblib required for dimensional reduction"
                )

            try:
                self.reducer = joblib.load(reducer_path)
                logger.info(
                    "Loaded dimensional reducer",
                    reducer_path=reducer_path,
                    target_dim=target_dim,
                )
            except Exception as e:
                logger.error(
                    "Failed to load dimensional reducer",
                    reducer_path=reducer_path,
                    error=str(e),
                )
                raise

    def _reduce_vector(self, vector: list[float]) -> list[float]:
        """Apply dimensional reduction to a single vector."""
        if self.strategy == "truncate":
            # Simple truncation to target dimension
            reduced = vector[: self.target_dim]
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
            raise ValueError(
                f"Unknown reduction strategy: {self.strategy}"
            )

        # L2 normalize if requested
        if self.normalize:
            norm = np.linalg.norm(reduced)
            if norm > 0:
                reduced = (np.array(reduced) / norm).tolist()

        return reduced

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed documents and apply dimensional reduction."""
        base_embeddings = self.base.embed_documents(texts)
        return [
            self._reduce_vector(embedding)
            for embedding in base_embeddings
        ]

    def embed_query(self, text: str) -> list[float]:
        """Embed query and apply dimensional reduction."""
        base_embedding = self.base.embed_query(text)
        return self._reduce_vector(base_embedding)

    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        """Async embed documents and apply dimensional reduction."""
        base_embeddings = await self.base.aembed_documents(texts)
        return [
            self._reduce_vector(embedding)
            for embedding in base_embeddings
        ]

    async def aembed_query(self, text: str) -> list[float]:
        """Async embed query and apply dimensional reduction."""
        base_embedding = await self.base.aembed_query(text)
        return self._reduce_vector(base_embedding)


class EmbeddingService:
    """Service for generating text embeddings."""

    def __init__(self, session: AsyncSession | None = None) -> None:
        """Initialize embedding service."""
        self._session = session
        self._providers: dict[str, Embeddings] = {}
        # We'll load providers dynamically as needed

    async def _get_session(self) -> AsyncSession:
        """Get database session."""
        if self._session:
            return self._session
        session_maker = get_session_maker()
        return session_maker()

    async def _create_embedding_provider_instance(
        self, provider, model_def
    ) -> Embeddings | None:
        """Create an embedding provider instance based on registry data."""
        try:
            if provider.provider_type == ProviderType.OPENAI:
                # Get API key from settings
                try:
                    current_settings = get_settings()
                    api_key = current_settings.openai_api_key
                except Exception:
                    api_key = None

                if provider.api_key_required and not api_key:
                    logger.warning(
                        f"API key required for provider {provider.name} but not found in settings"
                    )
                    return None

                config = model_def.default_config or {}
                base_provider = SafeOpenAIEmbeddings(
                    api_key=SecretStr(api_key) if api_key else None,
                    base_url=provider.base_url,
                    model=model_def.model_name,
                    chunk_size=model_def.chunk_size
                    or config.get("chunk_size", 1000),
                )

                # Apply dimensional reduction if configured for this model
                if settings.embedding_reduction_enabled:
                    return DimensionalReductionEmbeddings(
                        base_embeddings=base_provider,
                        target_dim=settings.embedding_reduction_target_dim,
                        strategy=settings.embedding_reduction_strategy,
                        reducer_path=settings.embedding_reducer_path,
                        normalize=settings.embedding_reduction_normalize,
                    )
                else:
                    return base_provider

            elif (
                provider.provider_type == ProviderType.GOOGLE
                and GOOGLE_AVAILABLE
            ):
                # Get API key from settings (Google uses a different field name)
                try:
                    current_settings = get_settings()
                    # For now, we don't have a google_api_key field in settings
                    # This would need to be added to the Settings class
                    api_key = None  # TODO: Add google_api_key to Settings class
                except Exception:
                    api_key = None

                if provider.api_key_required and not api_key:
                    logger.warning(
                        f"No API key found for provider {provider.name} in settings (google_api_key field needed)"
                    )
                    return None

                return GoogleGenerativeAIEmbeddings(
                    google_api_key=api_key,
                    model=model_def.model_name,
                )

            elif (
                provider.provider_type == ProviderType.COHERE
                and COHERE_AVAILABLE
            ):
                # Get API key from settings (Cohere uses a different field name)
                try:
                    current_settings = get_settings()
                    # For now, we don't have a cohere_api_key field in settings
                    # This would need to be added to the Settings class
                    api_key = None  # TODO: Add cohere_api_key to Settings class
                except Exception:
                    api_key = None

                if provider.api_key_required and not api_key:
                    logger.warning(
                        f"No API key found for provider {provider.name} in settings (cohere_api_key field needed)"
                    )
                    return None

                return CohereEmbeddings(
                    cohere_api_key=(
                        SecretStr(api_key) if api_key else None
                    ),
                    model=model_def.model_name,
                    client=(
                        cohere.Client(api_key)
                        if cohere and api_key
                        else None
                    ),
                    async_client=(
                        cohere.AsyncClient(api_key)
                        if cohere and api_key
                        else None
                    ),
                )

            else:
                logger.warning(
                    f"Unsupported embedding provider type: {provider.provider_type}"
                )
                return None

        except Exception as e:
            logger.error(
                f"Failed to create embedding provider instance for {provider.name}: {e}"
            )
            return None

    def _initialize_providers(self) -> None:
        """Initialize available embedding providers.

        Note: Providers are now loaded dynamically from model registry.
        """
        logger.info(
            "Embedding providers will be loaded dynamically from model registry"
        )

    async def get_provider(
        self, provider_name: str
    ) -> Embeddings | None:
        """Get embedding provider by name.

        Args:
            provider_name: Name of the provider

        Returns:
            Embedding provider or None if not available
        """
        # Check if we already have this provider cached
        if provider_name in self._providers:
            return self._providers[provider_name]

        # Load from registry
        session = await self._get_session()
        registry = ModelRegistryService(session)

        # Get provider by name
        provider = await registry.get_provider_by_name(provider_name)
        if not provider or not provider.is_active:
            logger.warning(
                f"Provider '{provider_name}' not found or inactive"
            )
            return None

        # Get default embedding model for this provider
        models, _ = await registry.list_models(
            provider.id, ModelType.EMBEDDING
        )
        default_model = None
        for model in models:
            if model.is_default and model.is_active:
                default_model = model
                break

        if not default_model:
            # Get first active model if no default
            for model in models:
                if model.is_active:
                    default_model = model
                    break

        if not default_model:
            logger.warning(
                f"No active embedding model found for provider '{provider_name}'"
            )
            return None

        # Create provider instance
        instance = await self._create_embedding_provider_instance(
            provider, default_model
        )
        if not instance:
            logger.warning(
                f"Failed to create instance for provider '{provider_name}'"
            )
            return None

        # Cache the instance
        self._providers[provider_name] = instance
        logger.info(
            f"Initialized embedding provider: {provider_name} with model: {default_model.model_name}"
        )

        return instance

    async def get_default_provider(self) -> Embeddings | None:
        """Get default embedding provider.

        Returns:
            Default embedding provider or None if not available
        """
        session = await self._get_session()
        registry = ModelRegistryService(session)

        # Get default provider for embeddings
        provider = await registry.get_default_provider(
            ModelType.EMBEDDING
        )
        if not provider:
            logger.warning("No default embedding provider configured")
            return None

        return await self.get_provider(provider.name)

    async def list_available_providers(self) -> list[str]:
        """List available embedding providers.

        Returns:
            List of provider names
        """
        session = await self._get_session()
        registry = ModelRegistryService(session)

        providers, _ = await registry.list_providers()
        active_providers = [p.name for p in providers if p.is_active]

        return active_providers

    async def get_provider_info(
        self, provider_name: str
    ) -> dict[str, Any]:
        """Get information about an embedding provider.

        Args:
            provider_name: Name of the provider

        Returns:
            Provider information
        """
        session = await self._get_session()
        registry = ModelRegistryService(session)

        provider = await registry.get_provider_by_name(provider_name)
        if not provider:
            return {}

        # Get models for this provider
        models, _ = await registry.list_models(
            provider.id, ModelType.EMBEDDING
        )
        active_models = [m for m in models if m.is_active]

        return {
            "name": provider.name,
            "display_name": provider.display_name,
            "provider_type": provider.provider_type,
            "description": provider.description,
            "is_active": provider.is_active,
            "is_default": provider.is_default,
            "models": [
                {
                    "name": m.name,
                    "model_name": m.model_name,
                    "display_name": m.display_name,
                    "is_default": m.is_default,
                    "dimensions": m.dimensions,
                    "chunk_size": m.chunk_size,
                    "supports_batch": m.supports_batch,
                    "max_batch_size": m.max_batch_size,
                }
                for m in active_models
            ],
        }

    async def get_all_provider_info(self) -> dict[str, dict[str, Any]]:
        """Get information for all available providers.

        Returns:
            Dictionary mapping provider names to their info
        """
        providers = await self.list_available_providers()
        all_info = {}
        for provider_name in providers:
            all_info[provider_name] = await self.get_provider_info(
                provider_name
            )
        return all_info

    async def invalidate_provider_cache(
        self, provider_name: str | None = None
    ) -> None:
        """Invalidate cached embedding provider instances.

        This should be called when providers or models are updated/deleted
        to ensure the cache doesn't serve stale data.

        Args:
            provider_name: Specific provider to invalidate, or None to invalidate all
        """
        if provider_name:
            # Invalidate specific provider
            if provider_name in self._providers:
                del self._providers[provider_name]
                logger.debug(
                    "Invalidated embedding provider cache",
                    provider_name=provider_name,
                )
        else:
            # Invalidate all cached providers
            if self._providers:
                provider_count = len(self._providers)
                self._providers.clear()
                logger.info(
                    "Invalidated all embedding provider caches",
                    provider_count=provider_count,
                )

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
            provider = await self.get_provider(provider_name)
            if not provider:
                raise EmbeddingError(
                    f"Provider '{provider_name}' not available"
                ) from None
        else:
            provider = await self.get_default_provider()
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
            provider = await self.get_provider(provider_name)
            if not provider:
                raise EmbeddingError(
                    f"Provider '{provider_name}' not available"
                ) from None
        else:
            provider = await self.get_default_provider()
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
                "embedding_dimensions": (
                    len(all_embeddings[0]) if all_embeddings else 0
                ),
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
        if isinstance(
            provider, (OpenAIEmbeddings, SafeOpenAIEmbeddings)
        ):
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
        # For now, return generic model names since specific model settings
        # are managed through the model registry, not global settings
        if provider_name == "openai":
            return "text-embedding-ada-002"  # Default OpenAI embedding model
        elif provider_name == "google":
            return "embedding-001"  # Default Google embedding model
        elif provider_name == "cohere":
            return (
                "embed-english-v2.0"  # Default Cohere embedding model
            )
        else:
            return "unknown"

    # Vector storage and search methods for consolidation
    async def store_embedding(
        self,
        chunk_id: str,
        embedding: list[float],
        provider_name: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Store embedding for a document chunk using hybrid vector storage.
        
        This method consolidates functionality from DynamicVectorStoreService.
        
        Args:
            chunk_id: Document chunk ID
            embedding: Embedding vector
            provider_name: Provider name (optional, uses default if not provided)
            metadata: Additional metadata
            
        Returns:
            True if successful
        """
        try:
            # Get the chunk
            result = await self._session.execute(
                select(DocumentChunk).where(DocumentChunk.id == chunk_id)
            )
            chunk = result.scalar_one_or_none()
            
            if not chunk:
                logger.error("Chunk not found", chunk_id=chunk_id)
                return False
            
            # Use hybrid vector storage approach from document_chunks table
            chunk.set_embedding_vector(
                vector=embedding,
                provider=provider_name,
                model=metadata.get("model") if metadata else None,
            )
            
            await self._session.commit()
            await self._session.refresh(chunk)
            
            logger.debug(
                "Stored embedding using hybrid vector system",
                chunk_id=chunk_id,
                provider=provider_name,
                dimensions=len(embedding),
            )
            
            return True
            
        except Exception as e:
            await self._session.rollback()
            logger.error(
                "Failed to store embedding",
                chunk_id=chunk_id,
                error=str(e),
            )
            return False

    async def similarity_search(
        self,
        query_embedding: list[float],
        provider_name: str | None = None,
        limit: int = 10,
        score_threshold: float = 0.5,
        document_ids: list[str] | None = None,
    ) -> list[tuple[DocumentChunk, float]]:
        """Perform similarity search using hybrid vector storage.
        
        This method consolidates functionality from DynamicVectorStoreService.
        
        Args:
            query_embedding: Query vector
            provider_name: Provider name for filtering (optional)
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            document_ids: Filter by document IDs (optional)
            
        Returns:
            List of (chunk, similarity_score) tuples
        """
        try:
            # Use the hybrid vector search helper from document chunks
            from chatter.models.document import HybridVectorSearchHelper
            
            # Get session for the helper
            session = await self._get_session()
            helper = HybridVectorSearchHelper(session)
            
            # Perform hybrid search
            results = await helper.hybrid_search(
                query_vector=query_embedding,
                limit=limit,
                document_ids=document_ids,
                provider_filter=provider_name,
            )
            
            # Filter by score threshold
            filtered_results = [
                (chunk, score) for chunk, score in results
                if score >= score_threshold
            ]
            
            logger.debug(
                "Similarity search completed",
                results_count=len(filtered_results),
                limit=limit,
                score_threshold=score_threshold,
            )
            
            return filtered_results
            
        except Exception as e:
            logger.error(
                "Similarity search failed",
                error=str(e),
                query_dimensions=len(query_embedding),
            )
            return []

    async def get_embedding_stats(self) -> dict[str, Any]:
        """Get statistics about stored embeddings.
        
        Simplified version consolidating functionality from DynamicVectorStoreService.
        
        Returns:
            Dictionary with embedding statistics
        """
        try:
            from sqlalchemy import func
            
            stats: dict[str, Any] = {
                "total_chunks": 0,
                "embedded_chunks": 0,
                "vector_store_type": "hybrid",
            }
            
            # Total chunks
            total_result = await self._session.execute(
                select(func.count(DocumentChunk.id))
            )
            stats["total_chunks"] = int(total_result.scalar() or 0)
            
            # Chunks with embeddings (using hybrid vector fields)
            embedded_result = await self._session.execute(
                select(func.count(DocumentChunk.id)).where(
                    DocumentChunk.raw_embedding.is_not(None)
                )
            )
            stats["embedded_chunks"] = int(embedded_result.scalar() or 0)
            
            logger.debug(
                "Generated embedding statistics",
                total_chunks=stats["total_chunks"],
                embedded_chunks=stats["embedded_chunks"],
            )
            
            return stats
            
        except Exception as e:
            logger.error("Failed to get embedding stats", error=str(e))
            return {
                "total_chunks": 0,
                "embedded_chunks": 0,
                "vector_store_type": "hybrid",
                "error": str(e),
            }


class EmbeddingError(Exception):
    """Embedding generation error."""

    pass
