#!/usr/bin/env python3
"""
Example demonstrating the transaction fix pattern.

This shows how the fix prevents PostgreSQL transaction abort errors
by properly handling exceptions and rolling back transactions.
"""

async def example_fixed_method(session):
    """Example of proper transaction handling."""
    try:
        # Perform database operations
        await session.execute("some sql")
        user = User(...)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
        
    except Exception as e:
        # CRITICAL: Roll back the transaction on any error
        await session.rollback()
        logger.error(f"Operation failed: {e}")
        raise  # Re-raise after rollback


async def example_broken_method(session):
    """Example of what was causing the transaction abort error."""
    # Check for existing data
    existing = await session.execute("SELECT * FROM users WHERE username = 'admin'")
    
    # Create new user
    user = User(...)
    session.add(user)
    await session.commit()  # This might fail due to constraint violation
    
    # If commit() fails above, transaction is now ABORTED
    # Any subsequent SQL commands will fail with "transaction is aborted"
    await session.refresh(user)  # This would fail!
    return user


# The fix ensures that if any operation fails, we:
# 1. Roll back the transaction immediately
# 2. Log the error for debugging  
# 3. Re-raise the exception for proper error handling
# 4. Leave the session in a clean state for subsequent operations