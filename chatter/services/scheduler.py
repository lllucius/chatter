"""Background tasks for tool server management."""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from chatter.services.toolserver import ToolServerService
from chatter.models.toolserver import ServerStatus
from chatter.utils.database import get_session_factory
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class ToolServerScheduler:
    """Background scheduler for tool server management tasks."""
    
    def __init__(self):
        """Initialize the scheduler."""
        self.running = False
        self.health_check_interval = 300  # 5 minutes
        self.auto_update_interval = 3600  # 1 hour
        self.cleanup_interval = 86400  # 24 hours
        self._tasks = []
    
    async def start(self):
        """Start the background scheduler."""
        if self.running:
            return
        
        self.running = True
        logger.info("Starting tool server scheduler")
        
        # Start background tasks
        self._tasks = [
            asyncio.create_task(self._health_check_loop()),
            asyncio.create_task(self._auto_update_loop()),
            asyncio.create_task(self._cleanup_loop()),
        ]
        
        logger.info("Tool server scheduler started")
    
    async def stop(self):
        """Stop the background scheduler."""
        if not self.running:
            return
        
        logger.info("Stopping tool server scheduler")
        self.running = False
        
        # Cancel all tasks
        for task in self._tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
        
        logger.info("Tool server scheduler stopped")
    
    async def _health_check_loop(self):
        """Periodic health check for all servers."""
        while self.running:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Health check loop error", error=str(e))
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def _auto_update_loop(self):
        """Periodic auto-update of server capabilities."""
        while self.running:
            try:
                await self._perform_auto_updates()
                await asyncio.sleep(self.auto_update_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Auto-update loop error", error=str(e))
                await asyncio.sleep(300)  # Wait 5 minutes before retrying
    
    async def _cleanup_loop(self):
        """Periodic cleanup of old usage data."""
        while self.running:
            try:
                await self._perform_cleanup()
                await asyncio.sleep(self.cleanup_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Cleanup loop error", error=str(e))
                await asyncio.sleep(3600)  # Wait 1 hour before retrying
    
    async def _perform_health_checks(self):
        """Perform health checks on all servers."""
        try:
            async_session = get_session_factory()
            async with async_session() as session:
                service = ToolServerService(session)
                
                # Get all enabled servers
                servers = await service.list_servers(status=ServerStatus.ENABLED)
                
                for server in servers:
                    try:
                        health = await service.health_check_server(server.id)
                        
                        # Handle server issues
                        if not health.is_running and server.auto_start:
                            logger.info("Auto-restarting unresponsive server", 
                                      server_id=server.id, server_name=server.name)
                            await service.start_server(server.id)
                        
                        elif not health.is_responsive:
                            logger.warning("Server not responsive", 
                                         server_id=server.id, server_name=server.name)
                            
                            # Try to restart if auto-start is enabled
                            if server.auto_start:
                                await service.restart_server(server.id)
                        
                    except Exception as e:
                        logger.error("Health check failed for server", 
                                   server_id=server.id, error=str(e))
                
                logger.debug("Health checks completed", server_count=len(servers))
                
        except Exception as e:
            logger.error("Failed to perform health checks", error=str(e))
    
    async def _perform_auto_updates(self):
        """Perform auto-updates for servers with auto_update enabled."""
        try:
            async_session = get_session_factory()
            async with async_session() as session:
                service = ToolServerService(session)
                
                # Get all servers with auto_update enabled
                servers = await service.list_servers()
                auto_update_servers = [s for s in servers if s.auto_update]
                
                for server in auto_update_servers:
                    try:
                        if server.status == ServerStatus.ENABLED:
                            logger.info("Auto-updating server capabilities", 
                                      server_id=server.id, server_name=server.name)
                            
                            # Restart server to discover new tools
                            await service.restart_server(server.id)
                            
                    except Exception as e:
                        logger.error("Auto-update failed for server", 
                                   server_id=server.id, error=str(e))
                
                logger.debug("Auto-updates completed", server_count=len(auto_update_servers))
                
        except Exception as e:
            logger.error("Failed to perform auto-updates", error=str(e))
    
    async def _perform_cleanup(self):
        """Perform cleanup of old data."""
        try:
            async_session = get_session_factory()
            async with async_session() as session:
                from chatter.models.toolserver import ToolUsage
                from sqlalchemy import delete
                
                # Delete usage records older than 90 days
                cutoff_date = datetime.now(timezone.utc) - timedelta(days=90)
                
                result = await session.execute(
                    delete(ToolUsage).where(ToolUsage.called_at < cutoff_date)
                )
                
                deleted_count = result.rowcount
                await session.commit()
                
                if deleted_count > 0:
                    logger.info("Cleaned up old usage records", deleted_count=deleted_count)
                
        except Exception as e:
            logger.error("Failed to perform cleanup", error=str(e))


# Global scheduler instance
_scheduler: Optional[ToolServerScheduler] = None


async def start_scheduler():
    """Start the global tool server scheduler."""
    global _scheduler
    
    if _scheduler is None:
        _scheduler = ToolServerScheduler()
    
    await _scheduler.start()


async def stop_scheduler():
    """Stop the global tool server scheduler."""
    global _scheduler
    
    if _scheduler is not None:
        await _scheduler.stop()


def get_scheduler() -> Optional[ToolServerScheduler]:
    """Get the global scheduler instance."""
    return _scheduler