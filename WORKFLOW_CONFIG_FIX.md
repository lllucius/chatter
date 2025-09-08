# Fix for Missing workflow_config Column Error

This document explains the fix for the error:
```
column conversations.workflow_config does not exist
```

## Problem

The error occurs when the application tries to query the `conversations` table and access the `workflow_config` column, but this column doesn't exist in the database schema. This typically happens when:

1. The database was created before the `workflow_config` field was added to the model
2. A migration to add the column was never run
3. The database schema is out of sync with the application models

## Root Cause

The `Conversation` model in `chatter/models/conversation.py` includes a `workflow_config` field:

```python
workflow_config: Mapped[dict[str, Any] | None] = mapped_column(
    JSON, nullable=True
)
```

But the database table is missing this column, causing the SQL query to fail.

## Solution

### For Production Users (Recommended)

If you have an existing database with conversations, run the migration to add the missing column:

```bash
alembic upgrade head
```

This will apply the migration `ef29b1af6dfe_add_workflow_config_column_to_.py` which safely adds the `workflow_config` column to your existing `conversations` table.

### For New Installations

For new installations, the migrations will create all tables with the correct schema including the `workflow_config` column.

### Manual Fix (If needed)

If you prefer to add the column manually:

```sql
ALTER TABLE conversations ADD COLUMN workflow_config JSON;
```

## Migration Details

The migration (`ef29b1af6dfe_add_workflow_config_column_to_.py`) includes error handling to:

1. Attempt to add the `workflow_config` column to the `conversations` table
2. Gracefully handle the case where the table doesn't exist (for new installations)
3. Skip the operation if it fails (to avoid breaking existing setups)

## Verification

After applying the fix, you can verify it worked by:

1. Checking that the column exists:
   ```sql
   \d conversations  -- PostgreSQL
   PRAGMA table_info(conversations);  -- SQLite
   ```

2. Running a test query:
   ```sql
   SELECT id, title, workflow_config FROM conversations LIMIT 1;
   ```

3. The API endpoint `/api/v1/chat/conversations` should now work without errors.

## Files Changed

- `alembic/versions/ef29b1af6dfe_add_workflow_config_column_to_.py` - Migration to add missing column
- Added error handling to prevent migration failures on systems without the conversations table

This fix resolves the immediate error while maintaining compatibility with different database states.