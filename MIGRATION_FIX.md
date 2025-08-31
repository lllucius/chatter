# Fix for Missing Column Error

This migration fixes the error:
```
column tool_servers.command does not exist
```

## Problem

The database schema was out of sync with the SQLAlchemy model. The `tool_servers` table was missing columns that the `ToolServer` model expects:

- `command` (String, nullable)
- `args` (JSON, nullable)  
- `env` (JSON, nullable)

## Solution

A new migration `002_add_missing_columns.py` has been created that:

1. Checks if each column exists before adding it
2. Only adds missing columns to avoid conflicts
3. Uses PostgreSQL-compatible column definitions matching the model

## Running the Migration

To apply this migration:

```bash
# Run the migration
alembic upgrade head

# Or run just this specific migration
alembic upgrade 002_add_missing_columns
```

## Verification

After running the migration, the health check and scheduler services should work without the column error.

You can verify the columns were added by checking the database:

```sql
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'tool_servers' 
AND column_name IN ('command', 'args', 'env');
```

## Rollback

If needed, you can rollback this migration:

```bash
alembic downgrade remote_tool_servers
```

This will remove the added columns.