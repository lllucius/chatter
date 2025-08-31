#!/usr/bin/env python3
"""
Verification script to check if the missing columns issue is fixed.
Run this after applying the migration to verify the fix.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def verify_fix():
    """Verify that the missing columns issue has been fixed."""
    
    try:
        # Try to import and initialize the tool server service
        from chatter.services.toolserver import ToolServerService
        from chatter.utils.database import get_session
        from chatter.models.toolserver import ServerStatus
        
        print("✓ Successfully imported ToolServerService")
        
        # Try to create a session and list servers (this would fail before the fix)
        async with get_session() as session:
            service = ToolServerService(session)
            
            # This is the operation that was failing
            servers = await service.list_servers(status=ServerStatus.ENABLED)
            print(f"✓ Successfully listed tool servers: {len(servers)} enabled servers found")
            
            # Try to list all servers too
            all_servers = await service.list_servers()
            print(f"✓ Successfully listed all tool servers: {len(all_servers)} total servers found")
            
        print("\n🎉 Migration fix verification successful!")
        print("The missing column error should be resolved.")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed.")
        return False
        
    except Exception as e:
        if "does not exist" in str(e) and "command" in str(e):
            print(f"❌ The missing column error still exists: {e}")
            print("The migration may not have been applied yet.")
            print("Run: alembic upgrade head")
            return False
        else:
            print(f"❌ Unexpected error: {e}")
            print("This may be due to database connection issues or other configuration problems.")
            return False
    
    return True

if __name__ == "__main__":
    # Check if we're in the right directory
    if not Path("chatter").exists():
        print("❌ This script must be run from the project root directory")
        sys.exit(1)
    
    # Set up environment if .env exists
    env_file = Path(".env")
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv()
    
    # Run the verification
    success = asyncio.run(verify_fix())
    sys.exit(0 if success else 1)