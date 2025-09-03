# Test Suite Foundation - Usage Examples

This document demonstrates how to use the implemented test suite foundation.

## Running Tests

### Prerequisites

**PostgreSQL Database Required**: The test suite uses a real PostgreSQL database for testing to ensure compatibility with production PostgreSQL features including pgvector extension.

#### PostgreSQL Setup

1. **Install PostgreSQL** (if not already installed):
   ```bash
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib postgresql-client
   
   # macOS with Homebrew
   brew install postgresql
   
   # Start PostgreSQL service
   sudo systemctl start postgresql  # Linux
   brew services start postgresql   # macOS
   ```

2. **Create test database and user**:
   ```bash
   # Connect as postgres user
   sudo -u postgres psql
   
   # Create test user and database
   CREATE USER test_user WITH PASSWORD 'test_password';
   CREATE DATABASE chatter_test OWNER test_user;
   GRANT ALL PRIVILEGES ON DATABASE chatter_test TO test_user;
   
   # Enable pgvector extension (optional, for vector store tests)
   \c chatter_test
   CREATE EXTENSION IF NOT EXISTS vector;
   
   \q
   ```

3. **Verify connection**:
   ```bash
   # Test connection manually
   psql postgresql://test_user:test_password@localhost:5432/chatter_test -c "SELECT 1;"
   
   # Or use the verification script
   python scripts/verify_test_db.py
   ```

### Basic Test Execution
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_auth_unit.py

# Run specific test class
pytest tests/test_auth_unit.py::TestAuthUnitTests

# Run specific test method
pytest tests/test_auth_unit.py::TestAuthUnitTests::test_user_registration
```

### Test Categories
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run both unit and integration tests
pytest -m "unit or integration"

# Exclude slow tests
pytest -m "not slow"
```

### Coverage Reports
```bash
# Run tests with coverage
pytest --cov=chatter

# Generate HTML coverage report
pytest --cov=chatter --cov-report=html

# Open coverage report
open htmlcov/index.html
```

## Test Structure

### Key Fixtures Available

1. **Database Fixtures**
   - `db_engine` - Function-scoped PostgreSQL engine
   - `db_session` - Test-scoped session with rollback
   - `db_setup` - Database schema setup

2. **Application Fixtures**
   - `app` - FastAPI app with test overrides
   - `client` - Async HTTP client for API testing

3. **Authentication Fixtures**
   - `auth_headers` - Pre-authenticated user headers
   - `test_user_data` - Valid user registration data
   - `test_login_data` - Valid login credentials

### Example Test Usage

```python
import pytest
from httpx import AsyncClient

class TestMyAPI:
    @pytest.mark.unit
    async def test_endpoint(self, client: AsyncClient):
        response = await client.get("/api/v1/endpoint")
        assert response.status_code == 200
    
    @pytest.mark.integration
    async def test_protected_endpoint(self, client: AsyncClient, auth_headers: dict):
        response = await client.get("/api/v1/protected", headers=auth_headers)
        assert response.status_code == 200
    
    async def test_database_operation(self, db_session):
        # Database operations here are automatically rolled back
        # after the test completes
        pass
```

## Database Testing

The test suite uses a real PostgreSQL database for testing, not mocks. This ensures:

- **Real database constraints** are tested
- **SQL queries** work correctly
- **Transaction behavior** is validated
- **Performance characteristics** are realistic

Each test runs in its own transaction that is rolled back after completion, ensuring test isolation.

## Authentication Testing

Comprehensive auth test coverage includes:

### Unit Tests
- User registration validation
- Login with username/email
- Token generation and validation
- Password hashing and verification
- API key management
- Error handling

### Integration Tests
- Complete registration → login workflows
- Token refresh workflows
- Profile update with database persistence
- Password change with verification
- Multi-user isolation
- Database constraint validation

## Extending the Test Suite

To add tests for new API modules:

1. Create new test files following the naming convention: `test_<module>_unit.py` and `test_<module>_integration.py`
2. Use the existing fixtures from `conftest.py`
3. Add appropriate pytest markers (`@pytest.mark.unit`, `@pytest.mark.integration`)
4. Follow the established patterns for API testing

Example:
```python
# tests/test_documents_unit.py
import pytest
from httpx import AsyncClient

class TestDocumentsUnit:
    @pytest.mark.unit
    async def test_document_upload(self, client: AsyncClient, auth_headers: dict):
        # Test document upload endpoint
        pass
        
# tests/test_documents_integration.py  
class TestDocumentsIntegration:
    @pytest.mark.integration
    async def test_document_processing_workflow(self, client: AsyncClient, auth_headers: dict, db_session):
        # Test complete document processing workflow
        pass
```

## Benefits of This Foundation

1. **Fast Tests** - Transaction rollback is much faster than database recreation
2. **Real Database** - Tests actual PostgreSQL behavior, not mocks
3. **Isolated Tests** - Each test starts with a clean state
4. **Async Support** - Fully compatible with FastAPI's async patterns
5. **Comprehensive Coverage** - Both unit and integration testing patterns
6. **Easy Extension** - Simple to add new test modules following established patterns