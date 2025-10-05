# API Tests Overview

This document explains the comprehensive API test suite for Chatter's REST endpoints.

## API Test Coverage

### Core API Endpoints Tested

1. **Authentication API** (`test_auth_unit.py`, `test_auth_integration.py`)
   - User registration and login workflows
   - Token management and validation
   - Password operations
   - API key management and authentication
   - API keys can be used directly for authentication without requiring JWT tokens

2. **Documents API** (`test_documents_unit.py`, `test_documents_integration.py`)
   - Document upload and processing
   - Document search and retrieval
   - CRUD operations and metadata management
   - Document chunks and reprocessing

3. **Conversations API** (`test_conversations_*.py`)  
   - Conversation creation and management
   - Message handling and streaming
   - Chat workflows and context management

4. **Workflows API** (`test_workflow_*.py`)
   - LangGraph workflow execution
   - Workflow definition management
   - Template-based workflow creation
   - Validation and error handling

5. **Analytics API** (`test_analytics_unit.py`, `test_analytics_integration.py`)
   - Usage metrics and statistics
   - Performance analytics
   - Dashboard data aggregation

6. **Data Management API** (`test_data_management_unit.py`, `test_data_management_integration.py`)
   - Data export and backup operations
   - Bulk operations and cleanup
   - Storage statistics and management

7. **Advanced Features**
   - **Agents API**: AI agent management and execution
   - **A/B Testing API**: Experiment creation and results tracking
   - **Events API**: Event system and notifications  
   - **Plugins API**: Plugin installation and management
   - **Jobs API**: Background job scheduling and monitoring
   - **Model Registry API**: LLM and embedding model management

## Running API Tests

### Prerequisites
- PostgreSQL database with test configuration
- All dependencies installed: `pip install -e ".[dev]"`

### Test Commands

```bash
# Run all API tests
pytest tests/ -v

# Run specific API test suites
pytest tests/test_documents_*.py -v
pytest tests/test_auth_*.py -v  
pytest tests/test_workflows_*.py -v

# Run by test type
pytest -m unit -v           # Unit tests only
pytest -m integration -v    # Integration tests only
pytest -m "not slow" -v     # Exclude slow tests

# Run with coverage
pytest --cov=chatter tests/ --cov-report=html
```

### Test Categories

- **Unit Tests**: Fast, isolated endpoint testing
- **Integration Tests**: Full workflow and database testing
- **Contract Tests**: API specification compliance
- **Performance Tests**: Load and response time testing

## Test Statistics

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

### Additional Test Suites
- **Authentication Tests**: 15+ tests covering registration, login, tokens
- **Workflow Tests**: 20+ tests for LangGraph execution and management
- **Analytics Tests**: 12+ tests for metrics and dashboard functionality
- **Integration Tests**: Cross-system workflow testing

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