# Comprehensive Database Seeding Guide

This document describes the full database seeding system implemented for the Chatter platform.

## Overview

The seeding system provides comprehensive data population capabilities for different use cases:

- **Minimal**: Essential data only (admin user, basic defaults)
- **Development**: Developer-friendly data with sample users and content
- **Demo**: Full demonstration data with rich sample content
- **Testing**: Predictable data for automated testing
- **Production**: Production-ready minimal data set

## Quick Start

### Using the CLI Script

```bash
# Show available seeding modes
python scripts/seed_database.py modes

# Check database status
python scripts/seed_database.py status

# Seed with development data (recommended for development)
python scripts/seed_database.py seed --mode development

# Seed with minimal data for production
python scripts/seed_database.py seed --mode production --force

# Initialize database schema first, then seed
python scripts/seed_database.py seed --mode development --init
```

### Using Python API

```python
from chatter.utils.seeding import seed_database, SeedingMode

# Seed development data
results = await seed_database(mode=SeedingMode.DEVELOPMENT)
print(f"Created {results['created']['users']} users")

# Seed minimal data for production
results = await seed_database(
    mode=SeedingMode.PRODUCTION,
    force=True,
    skip_existing=False
)
```

## Seeding Modes

### Minimal Mode
Creates only essential data:
- Admin user with secure random password
- Basic OpenAI provider and models (GPT-4, text-embedding-3-large)
- Default embedding space
- 3 basic chat profiles (Analytical, Creative, Conversational)
- 3 basic prompt templates

**Use case**: Production deployments, CI/CD pipelines

### Development Mode
Includes minimal data plus:
- 3 development users (developer, tester, demo) with known passwords
- Sample conversations with realistic dialog
- Sample documents (welcome guide, API documentation)
- Additional development-friendly content

**Use case**: Local development, staging environments

### Demo Mode
Includes development data plus:
- Additional specialized chat profiles
- More comprehensive prompt template library
- Multiple embedding spaces for different use cases
- Rich sample content for demonstrations

**Use case**: Product demonstrations, customer previews

### Testing Mode
Creates predictable test data:
- Test users with consistent credentials (testuser1/testpass1, etc.)
- Minimal but complete data for all entity types
- Designed for automated testing scenarios

**Use case**: Automated testing, CI/CD test suites

### Production Mode
Same as minimal mode but with production-specific optimizations:
- Only essential data
- Secure defaults
- Optimized for production deployment

**Use case**: Production deployments

## Data Created

### Users
- **Admin User**: `admin@admin.net` with secure random password (logged to console)
- **Development Users**: Known credentials for development (dev123!, test123!, demo123!)
- **Test Users**: Predictable credentials for testing

### Chat Profiles
1. **Deterministic/Factual Mode**: Low temperature (0.1) for factual responses
2. **Creative Writing Mode**: High temperature (0.9) for creative content
3. **Balanced Mode**: Medium temperature (0.7) for general use
4. *(Demo mode adds more specialized profiles)*

### Prompt Templates
1. **Instruction Task Template**: General task completion
2. **Code Review Template**: Code analysis and feedback
3. **Document Summary Template**: Document summarization
4. *(Demo mode adds more specialized templates)*

### Model Registry
- **OpenAI Provider**: Configured and activated
- **GPT-4 Model**: Primary LLM model with optimal settings
- **Text-Embedding-3-Large**: Embedding model with 3072 dimensions
- **Default Embedding Space**: Ready-to-use vector store

### Sample Content (Development/Demo)
- **Welcome Conversation**: Introduction to platform capabilities
- **Documentation**: Welcome guide and API documentation
- **Sample Documents**: Processed and ready for search

## CLI Reference

### Commands

#### `seed`
Seed the database with sample data.

**Options:**
- `--mode, -m`: Seeding mode (minimal, development, demo, testing, production)
- `--force, -f`: Force seeding even if database has existing users
- `--skip-existing/--overwrite`: Skip or overwrite existing data
- `--init, -i`: Initialize database schema first

**Examples:**
```bash
# Development seeding
python scripts/seed_database.py seed --mode development

# Force production seeding
python scripts/seed_database.py seed --mode production --force

# Initialize and seed
python scripts/seed_database.py seed --mode demo --init
```

#### `status`
Check database status and entity counts.

```bash
python scripts/seed_database.py status
```

#### `clear`
**DANGEROUS**: Clear all data from database.

```bash
python scripts/seed_database.py clear --confirm
```

#### `modes`
List available seeding modes and descriptions.

```bash
python scripts/seed_database.py modes
```

## API Reference

### Core Functions

#### `seed_database(mode, force, skip_existing)`
Main seeding function.

**Parameters:**
- `mode`: SeedingMode enum value
- `force`: Boolean, seed even if database has users
- `skip_existing`: Boolean, skip existing entities

**Returns:**
Dictionary with seeding results:
```python
{
    "mode": "development",
    "created": {
        "users": 4,
        "profiles": 3,
        "prompts": 3,
        "conversations": 1,
        "documents": 2
    },
    "skipped": {},
    "errors": []
}
```

#### `DatabaseSeeder` Class
Context manager for advanced seeding operations.

```python
async with DatabaseSeeder() as seeder:
    results = await seeder.seed_database(SeedingMode.DEMO)
    admin = await seeder._create_admin_user()
```

### Security Considerations

1. **Admin Password**: Automatically generated secure random password, logged once
2. **Development Passwords**: Simple passwords for development convenience only
3. **Production Mode**: Uses only secure defaults, no development conveniences
4. **API Keys**: Not seeded - must be configured separately

## Integration

### CI/CD Integration

```yaml
# Example GitHub Actions step
- name: Seed test database
  run: |
    python scripts/seed_database.py seed --mode testing --init --force
```

### Docker Integration

```dockerfile
# Initialize and seed on container start
RUN python scripts/seed_database.py seed --mode production --init
```

### Development Setup

```bash
# One-time development setup
python scripts/seed_database.py seed --mode development --init
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check DATABASE_URL environment variable
   - Ensure database server is running
   - Verify credentials and permissions

2. **Tables Don't Exist**
   - Run with `--init` flag to create schema first
   - Check database migration status

3. **Seeding Skipped**
   - Database not empty, use `--force` to override
   - Check existing user count with `status` command

4. **Permission Errors**
   - Ensure database user has CREATE/INSERT permissions
   - Check file system permissions for SQLite databases

### Logging

Enable debug logging for detailed seeding information:

```bash
export LOG_LEVEL=DEBUG
python scripts/seed_database.py seed --mode development
```

## Best Practices

1. **Development**: Use development mode with known credentials
2. **Testing**: Use testing mode for consistent test data
3. **Production**: Use production mode and change admin password immediately
4. **Staging**: Use demo mode for realistic staging environment
5. **CI/CD**: Use testing mode with `--force` for clean test runs

## Extending the System

### Adding New Seeding Modes

1. Add new mode to `SeedingMode` enum
2. Implement mode handler in `DatabaseSeeder._seed_*_data()`
3. Update CLI help text and documentation

### Adding New Entity Types

1. Create seeding method in `DatabaseSeeder`
2. Call from appropriate mode handlers
3. Update result tracking

### Custom Seed Data

Extend the seeding system by:
1. Creating custom data files (JSON/YAML)
2. Implementing custom seeding methods
3. Adding CLI options for custom data sources

## Migration from Legacy Systems

If migrating from existing seeding systems:

1. **Backup existing data** before running seeding
2. **Audit current data** to determine appropriate mode
3. **Test seeding** in development environment first
4. **Use `--force` carefully** in production environments

The comprehensive seeding system replaces ad-hoc initialization scripts with a robust, tested, and documented solution for all database initialization needs.