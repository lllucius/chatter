# 🧪 Chatter Test Suite

This directory contains the comprehensive test suite for the Chatter AI platform. The tests are organized into different categories to ensure comprehensive coverage of all components.

## 📁 Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Pytest configuration and shared fixtures
├── test_utils.py            # Test utilities and helper functions
├── test_core_auth.py        # Core authentication module tests
├── test_core_exceptions.py  # Core exception handling tests
├── test_api_health.py       # Health API endpoint tests
└── test_integration_workflows.py  # Integration tests for workflows
```

## 🏷️ Test Categories

Tests are organized using pytest markers:

- `@pytest.mark.unit` - Unit tests for individual components
- `@pytest.mark.integration` - Integration tests for component interactions
- `@pytest.mark.e2e` - End-to-end tests (planned)
- `@pytest.mark.performance` - Performance tests (planned)
- `@pytest.mark.security` - Security tests (planned)

## 🚀 Running Tests

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Run with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=chatter --cov-report=html
```

### Run Specific Test Files
```bash
# Run health API tests
pytest tests/test_api_health.py

# Run core authentication tests
pytest tests/test_core_auth.py

# Run integration workflow tests
pytest tests/test_integration_workflows.py
```

## 🔧 Test Configuration

The test suite is configured via `pyproject.toml` with the following settings:

- **Test Discovery**: Automatically finds `test_*.py` files
- **Async Support**: Full async/await test support
- **Coverage**: Code coverage reporting enabled
- **Markers**: Custom markers for test categorization
- **Fixtures**: Shared fixtures for common test data

## 📊 Test Coverage

Current test coverage includes:

### Core Modules ✅
- ✅ Authentication (core/auth.py)
- ✅ Exception handling (core/exceptions.py)
- 🔄 Chat engine (planned)
- 🔄 Document processing (planned)
- 🔄 Vector store (planned)

### API Endpoints ✅
- ✅ Health checks (/healthz, /readyz)
- 🔄 Authentication endpoints (planned)
- 🔄 Chat endpoints (planned)
- 🔄 Document endpoints (planned)
- 🔄 Agent endpoints (planned)

### Integration Tests ✅
- ✅ Authentication workflows
- ✅ Chat and messaging workflows
- ✅ Document processing workflows
- ✅ Cache integration
- ✅ Error handling across components

## 🛠️ Test Utilities

The `test_utils.py` module provides helpful utilities:

- **Mock Factories**: Create test data for users, chats, messages, documents
- **Mock Services**: Database, Redis, LLM service mocks
- **Test Helpers**: ID generation, response validation, error assertions
- **Async Utilities**: Mock async context managers and database connections

## 📝 Writing New Tests

### Unit Test Example
```python
import pytest
from chatter.core.auth import some_function

@pytest.mark.unit
class TestSomeFeature:
    def test_basic_functionality(self):
        result = some_function("input")
        assert result == "expected_output"
```

### Integration Test Example
```python
import pytest
from tests.test_utils import MockDatabase, create_mock_user

@pytest.mark.integration
class TestSomeWorkflow:
    @pytest.mark.asyncio
    async def test_complete_workflow(self):
        mock_db = MockDatabase()
        user = create_mock_user()
        
        # Test workflow steps
        # ... test implementation
        
        assert workflow_completed
```

### Async Test Example
```python
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result is not None
```

## 🎯 Best Practices

1. **Test Isolation**: Each test should be independent
2. **Mock External Dependencies**: Use mocks for databases, APIs, services
3. **Clear Assertions**: Make test expectations explicit
4. **Descriptive Names**: Test names should describe what they test
5. **Arrange-Act-Assert**: Follow the AAA pattern
6. **Edge Cases**: Test both happy path and error conditions

## 🔮 Future Enhancements

Planned additions to the test suite:

- [ ] **Performance Tests**: Response time and load testing
- [ ] **Security Tests**: Authentication, authorization, input validation
- [ ] **End-to-End Tests**: Full user journey testing
- [ ] **Database Tests**: Migration and data integrity tests
- [ ] **Contract Tests**: API schema validation
- [ ] **Load Tests**: Concurrent user simulation

## 🐛 Debugging Tests

### Common Issues

1. **Import Errors**: Check Python path and module structure
2. **Async Issues**: Ensure proper `@pytest.mark.asyncio` usage
3. **Mock Problems**: Verify mock setup and patch targets
4. **Fixture Scope**: Check fixture scope for shared state issues

### Debugging Commands
```bash
# Run with debug output
pytest tests/ -s

# Run specific test with debugging
pytest tests/test_core_auth.py::TestAuthenticationCore::test_password_validation -s -vvv

# Show local variables on failure
pytest tests/ --tb=long -l
```

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Mock Library](https://docs.python.org/3/library/unittest.mock.html)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)