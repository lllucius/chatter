"""Configuration management for Chatter application."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # =============================================================================
    # APPLICATION SETTINGS
    # =============================================================================

    app_name: str = Field(default="Chatter API", description="Application name")
    app_description: str = Field(
        default="Advanced AI Chatbot Backend API Platform", description="Application description"
    )
    app_version: str = Field(default="0.1.0", description="Application version")
    environment: str = Field(default="development", description="Environment")
    debug: bool = Field(default=False, description="Debug mode")

    # =============================================================================
    # SERVER SETTINGS
    # =============================================================================

    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    workers: int = Field(default=1, description="Number of worker processes")
    reload: bool = Field(default=False, description="Auto-reload on code changes")

    # =============================================================================
    # API SETTINGS
    # =============================================================================

    api_title: str = Field(default="Chatter API", description="API title")
    api_description: str = Field(default="Advanced AI Chatbot Backend API Platform", description="API description")
    api_version: str = Field(default="0.1.0", description="API version")
    api_prefix: str = Field(default="/api/v1", description="API prefix")
    api_base_url: str = Field(default="http://localhost:8000", description="API base URL for problem type URIs")

    # CORS settings
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"], description="CORS allowed origins"
    )
    cors_allow_credentials: bool = Field(default=True, description="CORS allow credentials")
    cors_allow_methods: list[str] = Field(default=["*"], description="CORS allowed methods")
    cors_allow_headers: list[str] = Field(default=["*"], description="CORS allowed headers")

    # Security
    trusted_hosts: str | list[str] = Field(default=["localhost", "127.0.0.1"], description="Trusted hosts")
    force_https: bool = Field(default=False, description="Force HTTPS redirect")
    security_headers_enabled: bool = Field(default=True, description="Enable security headers")

    # =============================================================================
    # DATABASE SETTINGS
    # =============================================================================

    database_url: str = Field(
        default="postgresql+asyncpg://chatter:chatter_password@localhost:5432/chatter", description="Database URL"
    )
    test_database_url: str = Field(
        default="postgresql+asyncpg://chatter:chatter_password@localhost:5432/chatter_test",
        description="Test database URL",
    )

    # Connection pool settings
    db_pool_size: int = Field(default=20, description="Database connection pool size")
    db_max_overflow: int = Field(default=30, description="Database max overflow connections")
    db_pool_pre_ping: bool = Field(default=True, description="Database pool pre-ping")
    db_pool_recycle: int = Field(default=3600, description="Database pool recycle time")

    # =============================================================================
    # VECTOR STORE SETTINGS
    # =============================================================================

    vector_store_type: str = Field(default="pgvector", description="Vector store type")

    # PGVector settings
    pgvector_collection_name: str = Field(default="chatter_embeddings", description="PGVector collection name")
    pgvector_embedding_dimension: int = Field(default=1536, description="PGVector embedding dimension")

    # Pinecone settings
    pinecone_api_key: str | None = Field(default=None, description="Pinecone API key")
    pinecone_environment: str | None = Field(default=None, description="Pinecone environment")
    pinecone_index_name: str = Field(default="chatter-index", description="Pinecone index name")

    # Qdrant settings
    qdrant_url: str = Field(default="http://localhost:6333", description="Qdrant URL")
    qdrant_api_key: str | None = Field(default=None, description="Qdrant API key")
    qdrant_collection_name: str = Field(default="chatter", description="Qdrant collection name")

    # ChromaDB settings
    chromadb_persist_directory: str = Field(default="./data/chromadb", description="ChromaDB persist directory")
    chromadb_collection_name: str = Field(default="chatter", description="ChromaDB collection name")

    # =============================================================================
    # LLM PROVIDER SETTINGS
    # =============================================================================

    # OpenAI
    openai_api_key: str | None = Field(default=None, description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o", description="OpenAI model")
    openai_embedding_model: str = Field(default="text-embedding-3-small", description="OpenAI embedding model")
    openai_embedding_dimensions: int = Field(default=1536, description="OpenAI embedding dimensions")
    openai_embedding_chunk_size: int = Field(default=1000, description="OpenAI embedding chunk size")
    openai_max_tokens: int = Field(default=4096, description="OpenAI max tokens")
    openai_temperature: float = Field(default=0.7, description="OpenAI temperature")
    openai_timeout: int = Field(default=60, description="OpenAI timeout")

    # Anthropic
    anthropic_api_key: str | None = Field(default=None, description="Anthropic API key")
    anthropic_model: str = Field(default="claude-3-5-sonnet-20241022", description="Anthropic model")
    anthropic_max_tokens: int = Field(default=4096, description="Anthropic max tokens")
    anthropic_temperature: float = Field(default=0.7, description="Anthropic temperature")
    anthropic_timeout: int = Field(default=60, description="Anthropic timeout")

    # Google Generative AI
    google_api_key: str | None = Field(default=None, description="Google API key")
    google_embedding_model: str = Field(default="models/embedding-001", description="Google embedding model")
    google_embedding_dimensions: int = Field(default=768, description="Google embedding dimensions")

    # Cohere
    cohere_api_key: str | None = Field(default=None, description="Cohere API key")
    cohere_embedding_model: str = Field(default="embed-english-light-v3.0", description="Cohere embedding model")
    cohere_embedding_dimensions: int = Field(default=384, description="Cohere embedding dimensions")

    # Default providers
    default_llm_provider: str = Field(default="openai", description="Default LLM provider")
    default_embedding_provider: str = Field(default="openai", description="Default embedding provider")

    # Embedding settings
    embedding_batch_size: int = Field(default=10, description="Embedding batch size")

    # =============================================================================
    # AUTHENTICATION & SECURITY
    # =============================================================================

    secret_key: str = Field(
        default="your_super_secret_key_here_change_this_in_production", description="JWT secret key"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiration minutes")
    refresh_token_expire_days: int = Field(default=7, description="Refresh token expiration days")
    bcrypt_rounds: int = Field(default=12, description="Bcrypt rounds")

    # =============================================================================
    # REDIS SETTINGS
    # =============================================================================

    redis_url: str | None = Field(default=None, description="Redis URL")
    test_redis_url: str = Field(default="redis://localhost:6379/1", description="Test Redis URL")
    redis_max_connections: int = Field(default=20, description="Redis max connections")
    redis_socket_timeout: int = Field(default=5, description="Redis socket timeout")
    redis_socket_connect_timeout: int = Field(default=5, description="Redis socket connect timeout")

    # Cache TTL settings
    cache_ttl_short: int = Field(default=300, description="Short cache TTL")
    cache_ttl_medium: int = Field(default=1800, description="Medium cache TTL")
    cache_ttl_long: int = Field(default=3600, description="Long cache TTL")

    # =============================================================================
    # RATE LIMITING
    # =============================================================================

    rate_limit_requests: int = Field(default=100, description="Rate limit requests per window")
    rate_limit_window: int = Field(default=60, description="Rate limit window in seconds")

    # =============================================================================
    # FILE UPLOAD SETTINGS
    # =============================================================================

    max_file_size: int = Field(default=50485760, description="Max file size in bytes (50MB)")
    allowed_file_types: list[str] = Field(
        default=["pdf", "txt", "doc", "docx", "md", "html"], description="Allowed file types"
    )
    document_storage_path: str = Field(default="./data/documents", description="Document storage path")

    # =============================================================================
    # LOGGING SETTINGS
    # =============================================================================

    log_level: str = Field(default="INFO", description="Log level")
    log_json: bool = Field(default=False, description="Use JSON logging")
    log_file: str | None = Field(default=None, description="Log file path")
    debug_http_requests: bool = Field(default=False, description="Debug HTTP requests")
    debug_database_queries: bool = Field(default=False, description="Debug database queries")
    debug_llm_interactions: bool = Field(default=False, description="Debug LLM interactions")

    # =============================================================================
    # MONITORING & METRICS
    # =============================================================================

    metrics_path: str = Field(default="/metrics", description="Metrics endpoint path")
    enable_health_checks: bool = Field(default=True, description="Enable health checks")
    health_check_interval: int = Field(default=30, description="Health check interval")

    # =============================================================================
    # DOCUMENT PROCESSING
    # =============================================================================

    chunk_size: int = Field(default=1000, description="Document chunk size")
    chunk_overlap: int = Field(default=200, description="Document chunk overlap")
    max_chunks_per_document: int = Field(default=1000, description="Max chunks per document")
    enable_background_processing: bool = Field(default=True, description="Enable background processing")
    background_worker_concurrency: int = Field(default=4, description="Background worker concurrency")

    # =============================================================================
    # LANGCHAIN/LANGGRAPH SETTINGS
    # =============================================================================

    # LangSmith
    langchain_tracing_v2: bool = Field(default=False, description="Enable LangSmith tracing")
    langchain_endpoint: str = Field(default="https://api.smith.langchain.com", description="LangChain endpoint")
    langchain_api_key: str | None = Field(default=None, description="LangChain API key")
    langchain_project: str = Field(default="chatter", description="LangChain project")

    # LangGraph
    langgraph_checkpoint_store: str = Field(default="postgres", description="LangGraph checkpoint store")
    langgraph_max_iterations: int = Field(default=50, description="LangGraph max iterations")
    langgraph_recursion_limit: int = Field(default=100, description="LangGraph recursion limit")

    # =============================================================================
    # MCP SETTINGS
    # =============================================================================

    mcp_enabled: bool = Field(default=True, description="Enable MCP")
    mcp_servers: list[str] = Field(default=["filesystem", "browser", "calculator"], description="MCP servers")
    mcp_tool_timeout: int = Field(default=30, description="MCP tool timeout")

    # =============================================================================
    # TESTING SETTINGS
    # =============================================================================

    skip_slow_tests: bool = Field(default=False, description="Skip slow tests")
    chatter_access_token: str | None = Field(default=None, description="CLI access token")

    # -----------------------------------------------------------------------------
    # Pydantic v2 Settings Config
    # -----------------------------------------------------------------------------
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.environment.lower() == "testing"

    @property
    def database_url_for_env(self) -> str:
        """Get database URL for current environment."""
        if self.is_testing:
            return self.test_database_url
        return self.database_url

    @property
    def redis_url_for_env(self) -> str | None:
        """Get Redis URL for current environment."""
        if self.is_testing:
            return self.test_redis_url
        return self.redis_url


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
