# Running the New API Tests

This document explains how to run the newly added tests for the documents and data_management APIs.

## Test Files Added

1. **tests/test_documents_unit.py** - Unit tests for documents API endpoints
2. **tests/test_documents_integration.py** - Integration tests for documents workflows  
3. **tests/test_data_management_unit.py** - Unit tests for data management API endpoints
4. **tests/test_data_management_integration.py** - Integration tests for data management workflows

## Running the Tests

### With Full Dependencies (Recommended)

If you have all the project dependencies installed:

```bash
# Install the project in development mode
pip install -e .

# Run all new API tests
pytest tests/test_documents_unit.py tests/test_documents_integration.py tests/test_data_management_unit.py tests/test_data_management_integration.py -v

# Run just the unit tests
pytest tests/test_documents_unit.py tests/test_data_management_unit.py -v -m unit

# Run just the integration tests  
pytest tests/test_documents_integration.py tests/test_data_management_integration.py -v -m integration
```

### With Minimal Dependencies (For Testing)

If you want to run tests without the full application dependencies, you can use a simplified approach:

```bash
# Install minimal test dependencies
pip install pytest pytest-asyncio fastapi httpx

# Run tests with basic coverage
pytest tests/test_documents_unit.py tests/test_data_management_unit.py -v
```

## Test Coverage

### Documents API Tests (18 tests total)
**Unit Tests (10 tests):**
- Upload document endpoint validation
- List documents endpoint
- Search documents endpoint  
- Get document endpoint
- Update document endpoint
- Delete document endpoint
- Get document chunks endpoint
- Process document endpoint
- Document stats endpoint
- Download document endpoint

**Integration Tests (8 tests):**
- Document upload workflow
- List and search workflow
- CRUD operations workflow
- Document chunks workflow  
- Document processing workflow
- Document stats workflow
- Document download workflow
- Permission and access control workflow

### Data Management API Tests (17 tests total)
**Unit Tests (8 tests):**
- Export data endpoint
- Create backup endpoint
- List backups endpoint
- Restore data endpoint
- Storage stats endpoint
- Bulk delete documents endpoint
- Bulk delete conversations endpoint
- Bulk delete prompts endpoint

**Integration Tests (9 tests):**
- Export data workflow
- Backup creation and listing workflow
- Restore workflow
- Storage stats workflow
- Bulk delete documents workflow
- Bulk delete conversations workflow
- Bulk delete prompts workflow
- Permission and access control workflow
- Cross-API data consistency testing

## Test Features

- **Authentication Testing**: Verifies 401 responses for unauthenticated requests
- **Validation Testing**: Checks 422 responses for invalid data
- **Endpoint Existence**: Confirms all API endpoints are properly registered
- **Response Structure**: Validates response format and required fields
- **Permission Control**: Tests access control and user isolation
- **Error Handling**: Verifies graceful handling of various error conditions
- **Cross-API Testing**: Ensures consistency between related APIs

## Test Patterns Used

The tests follow the established patterns in the repository:

- Use of `@pytest.mark.unit` and `@pytest.mark.integration` markers
- Consistent use of fixtures from `conftest.py` (client, auth_headers, db_session)
- Proper async/await patterns for FastAPI testing
- Descriptive test names and docstrings
- Test isolation and cleanup
- Appropriate assertions for different scenarios

## Expected Behavior

The tests are designed to be resilient and handle various application states:

- **Tests pass** when the full application is properly configured
- **Tests provide meaningful feedback** when services are not fully initialized
- **Tests verify API contract** regardless of backend implementation status
- **Tests can run independently** without requiring complex setup

This approach ensures the tests provide value both during development and in CI/CD pipelines.