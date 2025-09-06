# Example Implementation: Converting auth.py to DI Container

This document provides a detailed example of how to convert the `auth.py` API module to use the dependency injection container, serving as a template for other conversions.

## Current Implementation

### Before: Direct Service Instantiation

```python
# chatter/api/auth.py (current)
from sqlalchemy.ext.asyncio import AsyncSession
from chatter.core.auth import AuthService
from chatter.utils.database import get_session_generator

async def get_auth_service(
    session: AsyncSession = Depends(get_session_generator),
) -> AuthService:
    """Get authentication service instance.

    Args:
        session: Database session

    Returns:
        AuthService instance
    """
    return AuthService(session)

@router.post("/login")
async def login(
    user_data: UserLogin,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """User login endpoint."""
    return await auth_service.login(user_data, get_client_ip(request))
```

### Before: Service Implementation

```python
# chatter/core/auth.py (current)
from sqlalchemy.ext.asyncio import AsyncSession

class AuthService:
    """Authentication service."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def login(self, user_data: UserLogin, client_ip: str) -> TokenResponse:
        """Authenticate user and return token."""
        # Implementation using self.session
        pass
```

## Step-by-Step Conversion

### Step 1: Update Core Dependencies System

Add the auth service to the dependency injection container:

```python
# chatter/core/dependencies.py
# Add to register_lazy_loaders() function:

def register_lazy_loaders() -> None:
    """Register all lazy loaders to avoid circular imports."""
    
    # Existing registrations...
    container.register_lazy_loader("builtin_tools", lambda: _lazy_import_builtin_tools())
    # ... other existing services
    
    # Add auth service registration
    container.register_lazy_loader("auth_service", lambda: _lazy_import_auth_service())

def _lazy_import_auth_service():
    """Lazy import of AuthService to avoid circular imports."""
    from chatter.core.auth import AuthService
    return AuthService()  # Note: No session in constructor

def get_auth_service():
    """Get auth service with dependency injection."""
    return container.get_lazy("auth_service")
```

### Step 2: Update Service Implementation

Modify the service to support dependency injection patterns:

```python
# chatter/core/auth.py (after conversion)
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import contextmanager
from typing import Optional

class AuthService:
    """Authentication service with DI support."""
    
    def __init__(self):
        """Initialize auth service without session."""
        self._session: Optional[AsyncSession] = None
    
    def set_session(self, session: AsyncSession) -> None:
        """Set the database session for this request."""
        self._session = session
    
    @property
    def session(self) -> AsyncSession:
        """Get the current database session."""
        if self._session is None:
            raise RuntimeError("Database session not set. Call set_session() first.")
        return self._session
    
    @contextmanager
    def with_session(self, session: AsyncSession):
        """Context manager for temporary session usage."""
        old_session = self._session
        self._session = session
        try:
            yield self
        finally:
            self._session = old_session
    
    async def login(self, user_data: UserLogin, client_ip: str) -> TokenResponse:
        """Authenticate user and return token."""
        # Implementation using self.session (property)
        user = await self.session.execute(...)
        # ... rest of implementation
```

### Step 3: Update API Module

Convert the API module to use the DI container:

```python
# chatter/api/auth.py (after conversion)
from sqlalchemy.ext.asyncio import AsyncSession
from chatter.core.dependencies import get_auth_service
from chatter.core.auth import AuthService
from chatter.utils.database import get_session_generator

async def get_auth_service_with_session(
    session: AsyncSession = Depends(get_session_generator),
) -> AuthService:
    """Get authentication service instance with session.

    Args:
        session: Database session

    Returns:
        AuthService instance configured with session
    """
    service = get_auth_service()  # Get from DI container
    service.set_session(session)  # Configure with request session
    return service

@router.post("/login")
async def login(
    user_data: UserLogin,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service_with_session),
) -> TokenResponse:
    """User login endpoint."""
    return await auth_service.login(user_data, get_client_ip(request))
```

### Step 4: Update Tests

Modify tests to work with the new DI pattern:

```python
# tests/test_auth.py (before)
import pytest
from chatter.core.auth import AuthService

@pytest.fixture
async def auth_service(db_session):
    """Create auth service for testing."""
    return AuthService(db_session)

async def test_login(auth_service, mock_user):
    """Test user login."""
    result = await auth_service.login(mock_user, "127.0.0.1")
    assert result.access_token
```

```python
# tests/test_auth.py (after conversion)
import pytest
from chatter.core.dependencies import get_auth_service
from chatter.core.auth import AuthService

@pytest.fixture
async def auth_service(db_session):
    """Create auth service for testing."""
    service = get_auth_service()
    service.set_session(db_session)
    return service

# Alternative: Mock the entire service
@pytest.fixture
async def mock_auth_service():
    """Create mock auth service for testing."""
    from unittest.mock import AsyncMock
    mock_service = AsyncMock(spec=AuthService)
    # Configure mock behaviors
    return mock_service

async def test_login(auth_service, mock_user):
    """Test user login."""
    result = await auth_service.login(mock_user, "127.0.0.1")
    assert result.access_token

# Test with context manager pattern
async def test_login_with_context(db_session, mock_user):
    """Test login with context manager pattern."""
    service = get_auth_service()
    with service.with_session(db_session):
        result = await service.login(mock_user, "127.0.0.1")
        assert result.access_token
```

## Alternative Implementation Patterns

### Pattern A: Factory Function

If services need complex initialization:

```python
# chatter/core/dependencies.py
def _lazy_import_auth_service():
    """Lazy import with factory pattern."""
    from chatter.core.auth import AuthService, AuthConfig
    
    # Load configuration
    config = AuthConfig.from_settings()
    
    # Create and configure service
    service = AuthService()
    service.configure(config)
    return service
```

### Pattern B: Service with Session Factory

For more complex session management:

```python
# chatter/core/auth.py
class AuthService:
    """Auth service with session factory."""
    
    def __init__(self, session_factory: Optional[Callable] = None):
        self._session_factory = session_factory or get_session_generator
        self._session_cache = {}
    
    async def get_session(self) -> AsyncSession:
        """Get session for current request/context."""
        # Implement session management logic
        pass
```

### Pattern C: Async Context Manager

For services requiring async initialization:

```python
# chatter/core/auth.py
class AuthService:
    """Auth service with async context support."""
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()
        
    async def initialize(self):
        """Initialize service resources."""
        pass
    
    async def cleanup(self):
        """Clean up service resources."""  
        pass
```

## Testing Strategies

### Strategy 1: Service Injection

```python
# tests/conftest.py
@pytest.fixture
async def mock_auth_service():
    """Mock auth service for testing."""
    from unittest.mock import AsyncMock
    from chatter.core.dependencies import container
    
    mock_service = AsyncMock(spec=AuthService)
    # Configure mock behaviors
    mock_service.login.return_value = MockTokenResponse()
    
    # Replace in DI container for test duration
    container.register_singleton(AuthService, mock_service)
    yield mock_service
    container.clear()  # Clean up after test
```

### Strategy 2: Real Service with Test Database

```python
# tests/conftest.py
@pytest.fixture
async def auth_service_with_db(test_db_session):
    """Real auth service with test database."""
    from chatter.core.dependencies import get_auth_service
    
    service = get_auth_service()
    service.set_session(test_db_session)
    yield service
    # Session cleanup handled by test_db_session fixture
```

### Strategy 3: Integration Testing

```python
# tests/test_auth_integration.py
async def test_login_endpoint(client, test_user):
    """Test login endpoint with DI."""
    response = await client.post(
        "/auth/login",
        json={"username": test_user.username, "password": "password"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
```

## Migration Checklist

### Pre-conversion
- [ ] Identify all usages of AuthService
- [ ] Review current test patterns  
- [ ] Plan session management approach
- [ ] Create backup of current implementation

### Core Changes
- [ ] Add lazy loader to dependencies.py
- [ ] Add helper function to dependencies.py
- [ ] Update AuthService class for DI compatibility
- [ ] Test service in isolation

### API Changes  
- [ ] Update dependency function in auth.py
- [ ] Update all endpoint functions
- [ ] Test API endpoints work correctly
- [ ] Verify no breaking changes

### Testing Updates
- [ ] Update test fixtures
- [ ] Update unit tests
- [ ] Update integration tests
- [ ] Add DI-specific test cases

### Validation
- [ ] Run full test suite
- [ ] Manual testing of auth flows
- [ ] Performance testing
- [ ] Security validation

## Benefits Achieved

### Testability
- Easy to inject mock auth services
- Better isolation of auth logic
- Simplified test setup/teardown

### Flexibility  
- Can swap auth implementations
- Centralized auth configuration
- Better separation of concerns

### Consistency
- Uniform service access patterns
- Consistent error handling
- Standardized service lifecycle

## Potential Issues

### Session Management
**Issue:** Database sessions are request-scoped but service is singleton
**Solution:** Use session injection pattern or context managers

### Service State
**Issue:** Service may accumulate state across requests  
**Solution:** Ensure services are stateless or properly reset

### Error Handling  
**Issue:** Errors in DI container setup may be harder to debug
**Solution:** Add comprehensive logging and error messages

### Performance
**Issue:** Additional indirection through DI container
**Solution:** Benchmark and optimize if necessary (usually negligible)

---

*This example demonstrates the complete conversion process for the auth.py module and can be used as a template for converting other API modules.*