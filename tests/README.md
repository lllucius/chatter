# Test Configuration and Documentation

This directory contains comprehensive test suites for the Chatter platform.

## Test Categories

### 🧪 Unit Tests
```bash
# Run all unit tests with coverage
pytest -m unit --cov=chatter

# Run specific unit test file
pytest tests/test_core_auth.py -v
```

### 🔗 Integration Tests
```bash
# Run integration tests
pytest -m integration -v

# Run integration tests with timeout
pytest -m integration --timeout=300
```

### 🚀 End-to-End Tests
```bash
# Run E2E tests
pytest -m e2e -v

# Run specific E2E workflow
pytest tests/e2e/test_auth_e2e.py -v
```

### ⚡ Performance Tests
```bash
# Run performance tests
pytest -m performance -v

# Run with detailed output
pytest tests/test_performance.py -v -s
```

### 🔥 Load Tests
```bash
# Install locust first
pip install locust

# Run basic load test
locust -f tests/load/locust_scenarios.py --host=http://localhost:8000

# Run headless load test
locust -f tests/load/locust_scenarios.py --host=http://localhost:8000 \
       --users 10 --spawn-rate 2 --run-time 60s --headless
```

### 🛡️ Security Tests
```bash
# Run security tests
pytest tests/test_security_testing.py -v

# Run with security markers
pytest -k "security or auth" -v
```

### 🗄️ Database Tests
```bash
# Run database tests
pytest tests/test_database_testing.py -v

# Run migration tests
pytest -k "migration" -v
```

### 📋 Contract Tests
```bash
# Run API contract tests
pytest tests/test_contract_testing.py -v

# Test API compatibility
pytest -k "contract or api" -v
```

## Test Automation Scripts

### Main Test Automation
```bash
# Run all tests with automation script
python scripts/test_automation.py --full

# Run quick tests only
python scripts/test_automation.py --quick

# Run specific test types
python scripts/test_automation.py --unit --integration
python scripts/test_automation.py --e2e --performance
python scripts/test_automation.py --load --load-users 20 --load-duration 120

# Generate test report
python scripts/test_automation.py --report
```

### Frontend Tests
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run frontend tests
npm test

# Run with coverage
npm test -- --coverage
```

## Test Configuration

### Pytest Markers
- `unit`: Unit tests
- `integration`: Integration tests  
- `e2e`: End-to-end tests
- `performance`: Performance tests
- `load`: Load tests
- `slow`: Slow-running tests

### Running Specific Test Types
```bash
# Unit tests only
pytest -m unit

# Fast tests only (exclude slow)
pytest -m "not slow"

# Integration and E2E tests
pytest -m "integration or e2e"

# Performance and load tests
pytest -m "performance or load"
```

### Test Environment Variables
```bash
# Set test database URL
export TEST_DATABASE_URL="postgresql://test:test@localhost/test_chatter"

# Set test mode
export TESTING=true

# Disable external API calls
export MOCK_EXTERNAL_APIS=true
```

## Coverage Reporting

### Generate Coverage Reports
```bash
# HTML coverage report
pytest --cov=chatter --cov-report=html

# Terminal coverage report
pytest --cov=chatter --cov-report=term-missing

# XML coverage report (for CI/CD)
pytest --cov=chatter --cov-report=xml
```

### View Coverage
```bash
# Open HTML coverage report
open htmlcov/index.html

# Or in browser
python -m http.server 8080 -d htmlcov
```

## Load Testing

### Locust Web Interface
```bash
# Start Locust web interface
locust -f tests/load/locust_scenarios.py

# Open http://localhost:8089 to configure and run tests
```

### Load Test Scenarios
- `MixedWorkloadUser`: Realistic mix of operations
- `HeavyUser`: Resource-intensive operations  
- `ChatLoadTestUser`: Chat-focused testing
- `DocumentLoadTestUser`: Document-focused testing
- `HealthCheckLoadTestUser`: Basic health checking

### Load Test Configuration
```bash
# Test with different user counts
locust -f tests/load/locust_scenarios.py --users 50 --spawn-rate 5

# Test with specific duration
locust -f tests/load/locust_scenarios.py --run-time 300s

# Test specific scenarios
locust -f tests/load/locust_scenarios.py --users 10 --only-summary
```

## Continuous Integration

### GitHub Actions
```yaml
# Example CI configuration
- name: Run Tests
  run: |
    python scripts/test_automation.py --unit --integration
    python scripts/test_automation.py --e2e --performance
```

### Test Reports
```bash
# Generate comprehensive test report
python scripts/test_automation.py --report

# Reports will be saved in reports/ directory:
# - coverage/
# - test_report.html
# - junit.xml
# - load_test_report.html
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the package is installed in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

2. **Database Connection Issues**: Use mock sessions for unit tests:
   ```bash
   pytest -m unit  # Uses mocked database
   ```

3. **Load Test Failures**: Start the server before running load tests:
   ```bash
   # Terminal 1: Start server
   uvicorn chatter.main:app --reload
   
   # Terminal 2: Run load tests
   locust -f tests/load/locust_scenarios.py --host=http://localhost:8000
   ```

4. **E2E Test Failures**: E2E tests expect certain endpoints to exist:
   ```bash
   pytest tests/e2e/ -v  # See which endpoints are missing
   ```

### Test Data Cleanup
```bash
# Clean up test artifacts
rm -rf htmlcov/ reports/ .coverage .pytest_cache/

# Reset test database (if using real database)
python scripts/reset_test_db.py
```

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Mock External Services**: Use mocks for external APIs
3. **Test Data**: Use fixtures for consistent test data
4. **Performance**: Monitor test execution time
5. **Coverage**: Aim for 80%+ code coverage
6. **Documentation**: Document complex test scenarios

## Contributing

When adding new tests:

1. Use appropriate markers (`@pytest.mark.unit`, etc.)
2. Follow existing naming conventions
3. Add comprehensive docstrings
4. Update this documentation
5. Ensure tests are deterministic and fast