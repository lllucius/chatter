# SQLAlchemy Connection Leak Fix

## Problem Statement
SQLAlchemy was generating garbage collector warnings about non-checked-in connections:

```
The garbage collector is trying to clean up non-checked-in connection <AdaptedConnection <asyncpg.connection.Connection object at 0x7e609e091b80>>, which will be terminated. Please ensure that SQLAlchemy pooled connections are returned to the pool explicitly, either by calling ``close()`` or by using appropriate context managers to manage their lifecycle.
```

## Root Cause Analysis
The issue was caused by three methods in `chatter/utils/database.py` that violated async context manager patterns:

1. **`_attempt_connection()`** - This method created a connection inside an `async with engine.begin() as conn:` context manager but returned the connection outside the context scope
2. **`get_connection_with_retry()`** - Called `_attempt_connection()` and returned its result
3. **`get_connection_with_timeout()`** - Also called `_attempt_connection()` and returned its result

### The Problem Pattern
```python
async def _attempt_connection(self):
    """Attempt to establish a database connection."""
    engine = self.engine
    async with engine.begin() as conn:
        return conn  # ❌ BAD: Returning connection outside context manager
```

When a connection is returned outside its context manager scope, SQLAlchemy's connection pool tracking gets confused. The connection is checked out from the pool but never properly returned, leading to connection leaks that the garbage collector eventually has to clean up.

## Solution
**Removed the problematic methods entirely** since they were:
1. Not used anywhere in the codebase
2. Fundamentally flawed in their approach
3. Not following proper async context manager patterns

## Changes Made

### Files Modified
- `chatter/utils/database.py` - Removed three problematic methods
- `tests/test_connection_leak_fix.py` - Added comprehensive test to verify fix

### Methods Removed
- `DatabaseManager._attempt_connection()`
- `DatabaseManager.get_connection_with_retry()`  
- `DatabaseManager.get_connection_with_timeout()`

### Verification
- ✅ No existing code used these methods
- ✅ Core DatabaseManager functionality preserved
- ✅ All async context manager patterns remain intact
- ✅ Connection pool management now follows proper SQLAlchemy patterns

## Proper Connection Usage Patterns

For anyone needing database connections in the future, use these patterns:

### For Sessions (Recommended)
```python
async with DatabaseManager() as session:
    # Use session here
    result = await session.execute(query)
```

### For Raw Connections
```python
engine = get_engine()
async with engine.begin() as conn:
    # Use connection here
    result = await conn.execute(query)
# Connection automatically returned to pool when exiting context
```

### For Session Makers
```python
session_maker = get_session_maker()
async with session_maker() as session:
    # Use session here
    result = await session.execute(query)
```

## Testing
Added `tests/test_connection_leak_fix.py` which verifies:
- Problematic methods are completely removed
- Core functionality remains intact
- Async context manager patterns are preserved

## Expected Outcome
The SQLAlchemy garbage collector warnings should no longer appear since connections are now properly managed within their context scopes and returned to the pool appropriately.