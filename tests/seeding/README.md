# Database Seeding System Tests

This directory contains tests for the comprehensive database seeding system.

## Running Tests

### Prerequisites
- PostgreSQL database configured
- Environment variables set (DATABASE_URL, etc.)
- Dependencies installed: `pip install -e .`

### Test Commands

```bash
# Run basic seeding test
pytest tests/test_seeding_basic.py -v

# Run configuration tests
pytest tests/test_seeding_config.py -v

# Run CLI tests
pytest tests/test_seeding_cli.py -v

# Run all seeding tests
pytest tests/ -k seeding -v
```

### Manual Testing

```bash
# Test CLI modes
python scripts/seed_database.py modes

# Test status (requires database)
python scripts/seed_database.py status

# Test development seeding (requires database)
python scripts/seed_database.py seed --mode development --force
```

## Test Coverage

The seeding tests cover:

- ✅ Configuration loading from YAML
- ✅ All seeding modes (minimal, development, demo, testing, production)
- ✅ Entity creation (users, profiles, prompts, conversations, documents)
- ✅ CLI interface functionality
- ✅ Error handling and edge cases
- ✅ Skip existing data functionality
- ✅ Force mode operations

## Test Data

Tests use the same configuration system as the main seeding:
- `seed_data.yaml` - Main configuration
- Test-specific overrides for predictable results
- Isolated test database recommended

## Notes

- Tests require a real PostgreSQL database (SQLite not supported due to model constraints)
- Use a separate test database to avoid conflicts
- Some tests may take time due to database operations
- CLI tests verify command structure and help output