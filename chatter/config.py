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

    host: str = Field(
        default="0.0.0.0",  # nosec B104 - configurable, use 127.0.0.1 for production
        description="Server host - use 127.0.0.1 for local development, 0.0.0.0 for containers",
    )
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
        ...,
        description="Database URL (required, no default for security)",
    )
    test_database_url: str = Field(
        default="postgresql+asyncpg://test_user:test_password@localhost:5432/chatter_test",
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
    # UNIFIED CACHING SETTINGS
    # =============================================================================

    # Global cache control
    cache_disabled: bool = Field(
        default=False,
        description="Completely disable all caching operations",
    )

    # Cache backend configuration
    cache_backend: str = Field(
        default="multi_tier",
        description="Cache backend: 'memory', 'redis', or 'multi_tier'",
    )

    # Redis connection settings
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis URL for caching",
    )
    test_redis_url: str = Field(
        default="redis://localhost:6379/1", description="Test Redis URL"
    )
    redis_connect_timeout: int = Field(
        default=5, description="Redis connection timeout in seconds"
    )
    redis_connect_retries: int = Field(
        default=3, description="Redis connection retry attempts"
    )

    # Cache sizing and behavior
    cache_max_size: int = Field(
        default=1000, description="Maximum entries in cache"
    )
    cache_l1_size_ratio: float = Field(
        default=0.1,
        description="L1 cache size as ratio of total size (for multi-tier)",
    )
    cache_eviction_policy: str = Field(
        default="lru",
        description="Cache eviction policy: 'lru', 'ttl', or 'random'",
    )

    # TTL configuration - simplified hierarchy
    cache_ttl_default: int = Field(
        default=3600, description="Default cache TTL (1 hour)"
    )
    cache_ttl_short: int = Field(
        default=300, description="Short-lived cache TTL (5 minutes)"
    )
    cache_ttl_long: int = Field(
        default=7200, description="Long-lived cache TTL (2 hours)"
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
    # Backwards compatibility for existing code
    @property
    def cache_enabled(self) -> bool:
        """Backwards compatibility - inverse of cache_disabled."""
        return not self.cache_disabled

    @property
    def cache_disable_all(self) -> bool:
        """Backwards compatibility - same as cache_disabled."""
        return self.cache_disabled

    @property
    def cache_ttl(self) -> int:
        """Backwards compatibility - same as cache_ttl_default."""
        return self.cache_ttl_default

    @property
    def cache_max_memory_size(self) -> int:
        """Backwards compatibility - same as cache_max_size."""
        return self.cache_max_size

    # =============================================================================
    # UNIFIED RATE LIMITING SETTINGS
    # =============================================================================

    # Global rate limiting defaults
    rate_limit_requests: int = Field(
        default=100,
        description="Default rate limit requests per window",
    )
    rate_limit_window: int = Field(
        default=60, description="Default rate limit window in seconds"
    )

    # Cache integration for rate limiting
    rate_limit_use_cache: bool = Field(
        default=True,
        description="Use cache backend for distributed rate limiting",
    )

    # Endpoint-specific rate limits
    rate_limit_auth_requests: int = Field(
        default=10, description="Auth endpoint requests per window"
    )
    rate_limit_auth_window: int = Field(
        default=300,
        description="Auth endpoint window in seconds (5 minutes)",
    )

    rate_limit_analytics_requests: int = Field(
        default=20, description="Analytics endpoint requests per window"
    )
    rate_limit_analytics_window: int = Field(
        default=60, description="Analytics endpoint window in seconds"
    )

    rate_limit_model_write_requests: int = Field(
        default=30,
        description="Model registry write requests per window",
    )
    rate_limit_model_write_window: int = Field(
        default=60, description="Model registry write window in seconds"
    )

    rate_limit_model_read_requests: int = Field(
        default=200,
        description="Model registry read requests per window",
    )
    rate_limit_model_read_window: int = Field(
        default=60, description="Model registry read window in seconds"
    )

    # Tool access rate limiting (preserves existing behavior)
    rate_limit_tool_hourly: int = Field(
        default=100, description="Tool access requests per hour"
    )
    rate_limit_tool_daily: int = Field(
        default=1000, description="Tool access requests per day"
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
    # SERVER-SENT EVENTS (SSE) SETTINGS
    # =============================================================================

    sse_keepalive_timeout: int = Field(
        default=30, description="SSE keepalive timeout in seconds"
    )
    sse_max_connections_per_user: int = Field(
        default=10, description="Maximum SSE connections per user"
    )
    sse_max_total_connections: int = Field(
        default=1000, description="Maximum total SSE connections"
    )
    sse_connection_cleanup_interval: int = Field(
        default=300,
        description="SSE connection cleanup interval in seconds",
    )
    sse_inactive_timeout: int = Field(
        default=3600,
        description="SSE connection inactive timeout in seconds",
    )
    sse_queue_maxsize: int = Field(
        default=100,
        description="Maximum size of SSE event queue per connection",
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
    # WORKFLOW EXECUTION SETTINGS
    # =============================================================================

    # Workflow timeouts
    workflow_execution_timeout: int = Field(
        default=300, description="Workflow execution timeout in seconds"
    )
    workflow_step_timeout: int = Field(
        default=60,
        description="Individual workflow step timeout in seconds",
    )
    workflow_streaming_timeout: int = Field(
        default=600, description="Workflow streaming timeout in seconds"
    )

    # Resource limits
    workflow_max_tokens: int = Field(
        default=100000,
        description="Maximum tokens per workflow execution",
    )
    workflow_max_memory_mb: int = Field(
        default=1024,
        description="Maximum memory usage per workflow in MB",
    )
    workflow_max_concurrent: int = Field(
        default=10, description="Maximum concurrent workflows per user"
    )

    # Token streaming settings
    streaming_chunk_size: int = Field(
        default=1, description="Number of tokens per streaming chunk"
    )
    streaming_heartbeat_interval: float = Field(
        default=30.0,
        description="Streaming heartbeat interval in seconds",
    )
    streaming_buffer_size: int = Field(
        default=4096, description="Streaming buffer size"
    )

    # Circuit breaker settings for workflow reliability
    workflow_failure_threshold: int = Field(
        default=5,
        description="Failure threshold for workflow circuit breaker",
    )
    workflow_circuit_breaker_timeout: int = Field(
        default=60, description="Circuit breaker timeout in seconds"
    )

    # =============================================================================
    # ENCRYPTION SETTINGS
    # =============================================================================

    chatter_encryption_key: str | None = Field(
        default=None,
        description="Primary encryption key (base64 encoded)",
    )
    chatter_secret_password: str = Field(
        default="default-dev-password",
        description="Fallback password for key derivation (dev only)",
    )
    chatter_secret_salt: str = Field(
        default="default-dev-salt",
        description="Fallback salt for key derivation (dev only)",
    )

    # =============================================================================
    # CLI SETTINGS
    # =============================================================================

    chatter_api_base_url: str = Field(
        default="http://localhost:8000", description="CLI API base URL"
    )
    chatter_access_token: str | None = Field(
        default=None, description="CLI access token"
    )

    # =============================================================================
    # LLM PROVIDER API KEYS
    # =============================================================================

    openai_api_key: str | None = Field(
        default=None, description="OpenAI API key"
    )
    anthropic_api_key: str | None = Field(
        default=None, description="Anthropic API key"
    )

    # =============================================================================
    # MCP TOOL API KEYS
    # =============================================================================

    brave_api_key: str | None = Field(
        default=None, description="Brave Search API key for MCP tools"
    )

    # =============================================================================
    # TESTING SETTINGS
    # =============================================================================

    skip_slow_tests: bool = Field(
        default=False, description="Skip slow tests"
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

    @model_validator(mode="after")
    def validate_configuration(self) -> "Settings":
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

    @field_validator("database_url")
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
    def effective_rate_limit_auth_requests(self) -> int:
        """Get auth rate limit requests, more lenient in testing."""
        return (
            1000 if self.is_testing else self.rate_limit_auth_requests
        )

    @property
    def effective_rate_limit_auth_window(self) -> int:
        """Get auth rate limit window, more lenient in testing."""
        return 60 if self.is_testing else self.rate_limit_auth_window

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
                "0.0.0.0",  # nosec B104 - intentional for development/testing
                "testserver",  # Add testserver for pytest TestClient
                f"localhost:{self.port}",
                f"127.0.0.1:{self.port}",
                f"0.0.0.0:{self.port}",  # nosec B104 - intentional for development/testing
            ]

            # Combine and deduplicate
            all_hosts = list(set(base_hosts + dev_patterns))
            return all_hosts
        else:
            # Production: use configured hosts as-is for security
            return base_hosts


# Global settings instance cache
_settings_instance: Settings | None = None


def get_settings() -> Settings:
    """Get settings instance using singleton pattern."""
    global _settings_instance
    if _settings_instance is None:
        try:
            _settings_instance = Settings()  # type: ignore[call-arg]
        except Exception as e:
            # If database_url is not available, we can't create settings
            # This is expected in some contexts like testing or CLI tools
            raise RuntimeError(
                "Settings initialization failed. Ensure DATABASE_URL environment variable is set."
            ) from e
    return _settings_instance


# Module-level settings that will be lazily initialized
class _SettingsProxy:
    """Proxy to provide backward compatibility for module-level settings access."""
    
    def __getattr__(self, name: str) -> Any:
        return getattr(get_settings(), name)


settings = _SettingsProxy()
