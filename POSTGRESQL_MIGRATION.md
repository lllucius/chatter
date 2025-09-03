# PostgreSQL Migration: From pytest-postgresql to Real PostgreSQL

This document outlines the migration from using embedded pytest-postgresql to a real PostgreSQL server for testing.

## Changes Made

### 1. Dependencies Updated

**Removed:**
- `pytest-postgresql>=7.0.0` from dev dependencies in `pyproject.toml`

**Benefits:**
- Smaller dependency footprint
- No need to manage embedded PostgreSQL instances
- Better performance with real PostgreSQL optimizations

### 2. Test Configuration Refactored

**File:** `tests/conftest.py`

**Changes:**
- Removed `pytest_postgresql.factories` import
- Replaced `postgresql_proc` and `postgresql_session` fixtures
- Updated `db_engine` fixture to connect to real PostgreSQL using `settings.test_database_url`
- Changed fixture scope from `session` to `function` to prevent asyncio loop conflicts
- Simplified transaction handling for test isolation

**Before:**
```python
from pytest_postgresql import factories

postgresql_proc = factories.postgresql_proc(
    port=None,
    unixsocketdir="/tmp",
)

@pytest.fixture(scope="session") 
async def db_engine(postgresql_proc, postgresql_session):
    # Complex embedded PostgreSQL setup
    pg_host = postgresql_proc.host
    pg_port = postgresql_proc.port
    # ...
```

**After:**
```python
@pytest.fixture(scope="function") 
async def db_engine():
    # Simple connection to real PostgreSQL
    from chatter.config import settings
    db_url = settings.test_database_url
    engine = create_async_engine(db_url, ...)
    # ...
```

### 3. PostgreSQL Server Setup

**Required Setup:**
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib postgresql-client postgresql-16-pgvector

# Create test database and user
sudo -u postgres psql -c "CREATE USER test_user WITH PASSWORD 'test_password';"
sudo -u postgres psql -c "CREATE DATABASE chatter_test OWNER test_user;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE chatter_test TO test_user;"
sudo -u postgres psql -c "ALTER USER test_user CREATEDB;"

# Enable pgvector extension
sudo -u postgres psql -d chatter_test -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### 4. Configuration

**Environment Variables:**
- `DATABASE_URL`: Points to real PostgreSQL for testing
- `TEST_DATABASE_URL`: `postgresql+asyncpg://test_user:test_password@localhost:5432/chatter_test`

## Benefits of the Migration

### 1. Real Database Features
- **Full PostgreSQL functionality**: All PostgreSQL features, extensions, and optimizations
- **pgvector extension**: Native support for vector operations
- **Performance**: Real database performance characteristics
- **Constraints**: Actual database constraints and foreign key validation

### 2. Simplified Dependencies
- **Fewer packages**: No need for pytest-postgresql and its dependencies
- **Reduced complexity**: No embedded database management
- **Standard setup**: Uses the same PostgreSQL as production

### 3. Better Test Reliability
- **Consistent environment**: Same database engine as production
- **No embedded database issues**: No port conflicts or startup failures
- **Predictable behavior**: Standard PostgreSQL behavior

### 4. Performance Improvements
- **Faster startup**: No need to start embedded PostgreSQL instances
- **Connection pooling**: Better connection management
- **Parallel testing**: Better support for parallel test execution

## Test Isolation

Tests maintain isolation through:
- **Transaction rollback**: Each test runs in a transaction that's rolled back
- **Function-scoped fixtures**: Fresh database connections per test
- **Schema recreation**: Database schema is created fresh for each test

## Verification

Tests can be verified with:
```bash
# Run PostgreSQL functionality tests
pytest tests/test_postgresql_functionality.py -v

# Verify database setup
python scripts/verify_test_db.py

# Test database connection
psql postgresql://test_user:test_password@localhost:5432/chatter_test -c "SELECT version();"
```

## Migration Impact

### Positive
- ✅ Real PostgreSQL features and performance
- ✅ Simplified dependency management
- ✅ Better test reliability
- ✅ Production parity

### Requirements
- ⚠️ PostgreSQL server must be installed and running
- ⚠️ Test database must be set up manually
- ⚠️ CI/CD environments need PostgreSQL service

## Troubleshooting

### Common Issues

1. **Connection errors**: Ensure PostgreSQL is running and test database exists
2. **Permission errors**: Verify test_user has proper privileges
3. **Extension errors**: Install postgresql-16-pgvector for vector support

### Verification Commands

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection
psql postgresql://test_user:test_password@localhost:5432/chatter_test -c "SELECT 1;"

# Run verification script
python scripts/verify_test_db.py
```

This migration provides a more robust, performant, and production-like testing environment while simplifying the dependency chain.