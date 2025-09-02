"""Configuration management for Chatter application."""

# Using pydantic v2
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PYDANTIC_V2 = True


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # =============================================================================
    # APPLICATION SETTINGS
    # =============================================================================

    app_name: str = Field(
        default="Chatter API", description="Application name"
    )
    app_description: str = Field(
        default="Advanced AI Chatbot Backend API Platform",
        description="Application description",
    )
    app_version: str = Field(
        default="0.1.0", description="Application version"
    )
    environment: str = Field(
        default="development", description="Environment"
    )
    debug: bool = Field(default=False, description="Debug mode")

    # =============================================================================
    # SERVER SETTINGS
    # =============================================================================

    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    workers: int = Field(
        default=1, description="Number of worker processes"
    )
    reload: bool = Field(
        default=False, description="Auto-reload on code changes"
    )

    # =============================================================================
    # API SETTINGS
    # =============================================================================

    api_title: str = Field(
        default="Chatter API", description="API title"
    )
    api_description: str = Field(
        default="Advanced AI Chatbot Backend API Platform",
        description="API description",
    )
    api_version: str = Field(default="0.1.0", description="API version")
    api_prefix: str = Field(default="/api/v1", description="API prefix")
    api_base_url: str = Field(
        default="http://localhost:8000",
        description="API base URL for problem type URIs",
    )

    # CORS settings
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="CORS allowed origins",
    )
    cors_allow_credentials: bool = Field(
        default=True, description="CORS allow credentials"
    )
    cors_allow_methods: list[str] = Field(
        default=["*"], description="CORS allowed methods"
    )
    cors_allow_headers: list[str] = Field(
        default=["*"], description="CORS allowed headers"
    )

    # Security
    trusted_hosts: str | list[str] = Field(
        default=["localhost", "127.0.0.1"], description="Trusted hosts"
    )
    force_https: bool = Field(
        default=False, description="Force HTTPS redirect"
    )
    security_headers_enabled: bool = Field(
        default=True, description="Enable security headers"
    )

    # =============================================================================
    # DATABASE SETTINGS
    # =============================================================================
    # DATABASE SETTINGS
    # =============================================================================

    database_url: str = Field(
        description="Database URL (required, no default for security)",
    )
    test_database_url: str = Field(
        default="postgresql+asyncpg://test_user:test_pass@localhost:5432/chatter_test",
        description="Test database URL",
    )

    # Connection pool settings
    db_pool_size: int = Field(
        default=20, description="Database connection pool size"
    )
    db_max_overflow: int = Field(
        default=30, description="Database max overflow connections"
    )
    db_pool_pre_ping: bool = Field(
        default=True, description="Database pool pre-ping"
    )

    # =============================================================================
    # REDIS CACHE SETTINGS
    # =============================================================================

    # Enable/disable Redis caching - if disabled, operations silently fail gracefully
    cache_enabled: bool = Field(
        default=True, description="Enable Redis caching (optional)"
    )
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis URL for caching",
    )
    test_redis_url: str = Field(
        default="redis://localhost:6379/1", description="Test Redis URL"
    )
    cache_ttl: int = Field(
        default=3600, description="Default cache TTL in seconds"
    )
    # Connection timeout for Redis operations
    redis_connect_timeout: int = Field(
        default=5, description="Redis connection timeout in seconds"
    )
    # Retry attempts for Redis connection
    redis_connect_retries: int = Field(
        default=3, description="Redis connection retry attempts"
    )
    db_pool_recycle: int = Field(
        default=3600, description="Database pool recycle time"
    )

    # =============================================================================
    # VECTOR STORE SETTINGS
    # =============================================================================

    vector_store_type: str = Field(
        default="pgvector", description="Vector store type"
    )

    # PGVector settings
    pgvector_collection_name: str = Field(
        default="chatter_embeddings",
        description="PGVector collection name",
    )
    pgvector_embedding_dimension: int = Field(
        default=3072, description="PGVector embedding dimension"
    )

    # Embedding settings
    embedding_batch_size: int = Field(
        default=10, description="Embedding batch size"
    )

    # =============================================================================
    # EMBEDDING DIMENSIONAL REDUCTION SETTINGS
    # =============================================================================

    # Enable dimensional reduction for embeddings
    embedding_reduction_enabled: bool = Field(
        default=False,
        description="Enable dimensional reduction for embeddings",
    )

    # Target dimension after reduction
    embedding_reduction_target_dim: int = Field(
        default=1536, description="Target dimensions after reduction"
    )

    # Reduction strategy: "reducer" (PCA/SVD) or "truncate" (simple truncation)
    embedding_reduction_strategy: str = Field(
        default="truncate", description="Dimensional reduction strategy"
    )

    # Path to fitted reducer (joblib file)
    embedding_reducer_path: str | None = Field(
        default=None, description="Path to fitted dimensional reducer"
    )

    # Whether to L2-normalize vectors after reduction
    embedding_reduction_normalize: bool = Field(
        default=True,
        description="Normalize vectors after dimensional reduction",
    )

    # =============================================================================
    # AUTHENTICATION & SECURITY
    # =============================================================================

    secret_key: str = Field(
        default="your_super_secret_key_here_change_this_in_production",
        description="JWT secret key",
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30, description="Access token expiration minutes"
    )
    refresh_token_expire_days: int = Field(
        default=7, description="Refresh token expiration days"
    )
    bcrypt_rounds: int = Field(default=12, description="Bcrypt rounds")

    # =============================================================================
    # REDIS SETTINGS
    # =============================================================================
    redis_max_connections: int = Field(
        default=20, description="Redis max connections"
    )
    redis_socket_timeout: int = Field(
        default=5, description="Redis socket timeout"
    )
    redis_socket_connect_timeout: int = Field(
        default=5, description="Redis socket connect timeout"
    )

    # Cache TTL settings
    cache_ttl_short: int = Field(
        default=300, description="Short cache TTL"
    )
    cache_ttl_medium: int = Field(
        default=1800, description="Medium cache TTL"
    )
    cache_ttl_long: int = Field(
        default=3600, description="Long cache TTL"
    )

    # =============================================================================
    # RATE LIMITING
    # =============================================================================

    rate_limit_requests: int = Field(
        default=100, description="Rate limit requests per window"
    )
    rate_limit_window: int = Field(
        default=60, description="Rate limit window in seconds"
    )

    # =============================================================================
    # FILE UPLOAD SETTINGS
    # =============================================================================

    max_file_size: int = Field(
        default=50485760, description="Max file size in bytes (50MB)"
    )
    allowed_file_types: list[str] = Field(
        default=["pdf", "txt", "doc", "docx", "md", "html"],
        description="Allowed file types",
    )
    document_storage_path: str = Field(
        default="./data/documents", description="Document storage path"
    )

    # =============================================================================
    # LOGGING SETTINGS
    # =============================================================================

    log_level: str = Field(default="INFO", description="Log level")
    log_json: bool = Field(
        default=False, description="Use JSON logging"
    )
    log_file: str | None = Field(
        default=None, description="Log file path"
    )
    debug_http_requests: bool = Field(
        default=False, description="Debug HTTP requests"
    )
    debug_database_queries: bool = Field(
        default=False, description="Debug database queries"
    )
    debug_llm_interactions: bool = Field(
        default=False, description="Debug LLM interactions"
    )

    # =============================================================================
    # MONITORING & METRICS
    # =============================================================================

    metrics_path: str = Field(
        default="/metrics", description="Metrics endpoint path"
    )
    enable_health_checks: bool = Field(
        default=True, description="Enable health checks"
    )
    health_check_interval: int = Field(
        default=30, description="Health check interval"
    )

    # =============================================================================
    # DOCUMENT PROCESSING
    # =============================================================================

    chunk_size: int = Field(
        default=1000, description="Document chunk size"
    )
    chunk_overlap: int = Field(
        default=200, description="Document chunk overlap"
    )
    max_chunks_per_document: int = Field(
        default=1000, description="Max chunks per document"
    )
    enable_background_processing: bool = Field(
        default=True, description="Enable background processing"
    )
    background_worker_concurrency: int = Field(
        default=4, description="Background worker concurrency"
    )

    # =============================================================================
    # LANGCHAIN/LANGGRAPH SETTINGS
    # =============================================================================

    # LangSmith
    langchain_tracing_v2: bool = Field(
        default=False, description="Enable LangSmith tracing"
    )
    langchain_endpoint: str = Field(
        default="https://api.smith.langchain.com",
        description="LangChain endpoint",
    )
    langchain_api_key: str | None = Field(
        default=None, description="LangChain API key"
    )
    langchain_project: str = Field(
        default="chatter", description="LangChain project"
    )

    # LangGraph
    langgraph_checkpoint_store: str = Field(
        default="postgres", description="LangGraph checkpoint store"
    )
    langgraph_max_iterations: int = Field(
        default=50, description="LangGraph max iterations"
    )
    langgraph_recursion_limit: int = Field(
        default=100, description="LangGraph recursion limit"
    )

    # =============================================================================
    # MCP SETTINGS
    # =============================================================================

    mcp_enabled: bool = Field(default=True, description="Enable MCP")
    mcp_servers: list[str] = Field(
        default=["filesystem", "browser", "calculator"],
        description="MCP servers",
    )
    mcp_tool_timeout: int = Field(
        default=30, description="MCP tool timeout"
    )

    # =============================================================================
    # TESTING SETTINGS
    # =============================================================================

    skip_slow_tests: bool = Field(
        default=False, description="Skip slow tests"
    )
    chatter_access_token: str | None = Field(
        default=None, description="CLI access token"
    )

    # -----------------------------------------------------------------------------
    # Pydantic Settings Config
    # -----------------------------------------------------------------------------
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @model_validator(mode='after')
    def validate_configuration(self) -> 'Settings':
        """Validate configuration for security and production readiness."""
        # In v2, 'self' is the instance
        database_url = self.database_url
        is_production = self.is_production
        debug = self.debug
        secret_key = self.secret_key

        # Validate database URL is provided
        if not database_url:
            raise ValueError(
                "DATABASE_URL must be provided - no default database credentials allowed for security"
            )

        # Validate production settings
        if is_production:
            if debug:
                raise ValueError(
                    "Debug mode must be disabled in production"
                )

            # Validate secret key strength in production
            if (
                secret_key == "your-secret-key-here"
                or len(secret_key) < 32
            ):
                raise ValueError(
                    "SECRET_KEY must be a strong secret (32+ characters) in production"
                )

        return self

    @field_validator('database_url')
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL format."""
        if not v:
            raise ValueError("Database URL is required")

        # Prevent default/weak credentials
        weak_patterns = [
            "chatter:chatter_password",
            "user:password",
            "postgres:postgres",
            "root:root",
        ]
        for pattern in weak_patterns:
            if pattern in v:
                raise ValueError(
                    f"Default/weak database credentials detected: {pattern}. "
                    "Please use strong, unique credentials."
                )

        return v

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

    @property
    def trusted_hosts_for_env(self) -> list[str]:
        """Get trusted hosts configuration for current environment.

        In development/testing: More permissive to include common development patterns
        In production: Use the configured trusted_hosts as-is for security
        """
        base_hosts = (
            self.trusted_hosts
            if isinstance(self.trusted_hosts, list)
            else [self.trusted_hosts]
        )

        if self.is_development or self.is_testing:
            # Add common development patterns if not already present
            dev_patterns = [
                "localhost",
                "127.0.0.1",
                "0.0.0.0",
                "testserver",  # Add testserver for pytest TestClient
                f"localhost:{self.port}",
                f"127.0.0.1:{self.port}",
                f"0.0.0.0:{self.port}",
            ]

            # Combine and deduplicate
            all_hosts = list(set(base_hosts + dev_patterns))
            return all_hosts
        else:
            # Production: use configured hosts as-is for security
            return base_hosts


# Create module-level settings instance
settings = Settings()


# Global settings instance cache
_settings_instance: Settings | None = None


def get_settings() -> Settings:
    """Get settings instance using singleton pattern."""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = settings
    return _settings_instance
