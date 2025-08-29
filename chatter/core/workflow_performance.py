"""Performance optimization utilities for workflows including caching and lazy loading."""

import asyncio
import hashlib
import json
import time
from functools import lru_cache
from typing import Any, Dict, List, Optional, Set, Tuple
from weakref import WeakValueDictionary

# Simple logger fallback
import logging
logger = logging.getLogger(__name__)


class WorkflowCache:
    """LRU cache for compiled workflows to avoid repeated compilation."""
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        """Initialize workflow cache.
        
        Args:
            max_size: Maximum number of workflows to cache
            ttl_seconds: Time-to-live for cached workflows in seconds
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.access_times: Dict[str, float] = {}
        self.hit_count = 0
        self.miss_count = 0
    
    def _generate_cache_key(
        self, 
        provider_name: str, 
        workflow_type: str, 
        config: Dict[str, Any]
    ) -> str:
        """Generate a cache key for workflow configuration.
        
        Args:
            provider_name: Name of the LLM provider
            workflow_type: Type of workflow
            config: Workflow configuration
            
        Returns:
            Cache key string
        """
        # Create a deterministic hash of the configuration
        config_str = json.dumps(config, sort_keys=True, default=str)
        combined = f"{provider_name}:{workflow_type}:{config_str}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def get(
        self, 
        provider_name: str, 
        workflow_type: str, 
        config: Dict[str, Any]
    ) -> Optional[Any]:
        """Get a cached workflow if available and not expired.
        
        Args:
            provider_name: Name of the LLM provider
            workflow_type: Type of workflow
            config: Workflow configuration
            
        Returns:
            Cached workflow or None if not found/expired
        """
        cache_key = self._generate_cache_key(provider_name, workflow_type, config)
        current_time = time.time()
        
        if cache_key in self.cache:
            workflow, cached_time = self.cache[cache_key]
            
            # Check if cache entry is still valid
            if current_time - cached_time < self.ttl_seconds:
                self.access_times[cache_key] = current_time
                self.hit_count += 1
                
                logger.debug(
                    "Workflow cache hit",
                    provider=provider_name,
                    workflow_type=workflow_type,
                    cache_key=cache_key[:8]
                )
                
                return workflow
            else:
                # Remove expired entry
                del self.cache[cache_key]
                if cache_key in self.access_times:
                    del self.access_times[cache_key]
        
        self.miss_count += 1
        
        logger.debug(
            "Workflow cache miss",
            provider=provider_name,
            workflow_type=workflow_type,
            cache_key=cache_key[:8]
        )
        
        return None
    
    def put(
        self, 
        provider_name: str, 
        workflow_type: str, 
        config: Dict[str, Any], 
        workflow: Any
    ) -> None:
        """Cache a compiled workflow.
        
        Args:
            provider_name: Name of the LLM provider
            workflow_type: Type of workflow
            config: Workflow configuration
            workflow: Compiled workflow to cache
        """
        cache_key = self._generate_cache_key(provider_name, workflow_type, config)
        current_time = time.time()
        
        # Check if we need to evict old entries
        if len(self.cache) >= self.max_size:
            self._evict_oldest()
        
        self.cache[cache_key] = (workflow, current_time)
        self.access_times[cache_key] = current_time
        
        logger.debug(
            "Workflow cached",
            provider=provider_name,
            workflow_type=workflow_type,
            cache_key=cache_key[:8]
        )
    
    def _evict_oldest(self) -> None:
        """Evict the least recently used cache entry."""
        if not self.access_times:
            return
        
        # Find the oldest accessed item
        oldest_key = min(self.access_times.keys(), 
                        key=lambda k: self.access_times[k])
        
        # Remove from both caches
        if oldest_key in self.cache:
            del self.cache[oldest_key]
        del self.access_times[oldest_key]
        
        logger.debug("Evicted oldest workflow from cache", cache_key=oldest_key[:8])
    
    def clear(self) -> None:
        """Clear all cached workflows."""
        self.cache.clear()
        self.access_times.clear()
        self.hit_count = 0
        self.miss_count = 0
        logger.info("Workflow cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        total_requests = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total_requests if total_requests > 0 else 0.0
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": hit_rate,
            "ttl_seconds": self.ttl_seconds
        }


class LazyToolLoader:
    """Lazy loading system for tools to improve performance."""
    
    def __init__(self):
        """Initialize lazy tool loader."""
        self.tool_registry: Dict[str, Any] = {}
        self.loaded_tools: WeakValueDictionary = WeakValueDictionary()
        self.load_stats: Dict[str, int] = {}
        self.total_loads = 0
    
    def register_tool(self, tool_name: str, tool_factory: callable) -> None:
        """Register a tool factory for lazy loading.
        
        Args:
            tool_name: Name of the tool
            tool_factory: Factory function that returns the tool instance
        """
        self.tool_registry[tool_name] = tool_factory
        logger.debug("Tool registered for lazy loading", tool_name=tool_name)
    
    async def get_tool(self, tool_name: str) -> Optional[Any]:
        """Get a tool, loading it lazily if needed.
        
        Args:
            tool_name: Name of the tool to get
            
        Returns:
            Tool instance or None if not found
        """
        # Check if already loaded
        if tool_name in self.loaded_tools:
            return self.loaded_tools[tool_name]
        
        # Check if registered
        if tool_name not in self.tool_registry:
            logger.warning("Tool not registered", tool_name=tool_name)
            return None
        
        try:
            # Load the tool
            tool_factory = self.tool_registry[tool_name]
            
            if asyncio.iscoroutinefunction(tool_factory):
                tool = await tool_factory()
            else:
                tool = tool_factory()
            
            # Cache the loaded tool
            self.loaded_tools[tool_name] = tool
            
            # Update statistics
            self.load_stats[tool_name] = self.load_stats.get(tool_name, 0) + 1
            self.total_loads += 1
            
            logger.debug("Tool loaded lazily", tool_name=tool_name)
            return tool
            
        except Exception as e:
            logger.error("Failed to load tool", tool_name=tool_name, error=str(e))
            return None
    
    async def get_tools(self, tool_names: List[str]) -> List[Any]:
        """Get multiple tools, loading them lazily.
        
        Args:
            tool_names: List of tool names to get
            
        Returns:
            List of tool instances (may contain None for failed loads)
        """
        tasks = [self.get_tool(name) for name in tool_names]
        tools = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and None values
        valid_tools = [tool for tool in tools 
                      if tool is not None and not isinstance(tool, Exception)]
        
        return valid_tools
    
    def get_required_tools(self, workflow_config: Dict[str, Any]) -> Set[str]:
        """Determine which tools are required for a workflow configuration.
        
        Args:
            workflow_config: Workflow configuration
            
        Returns:
            Set of required tool names
        """
        required_tools = set()
        
        # Basic heuristics for determining required tools
        workflow_type = workflow_config.get("mode", "plain")
        
        if workflow_type in ("tools", "full"):
            # For tool-enabled workflows, we might need various tools
            # This is a simplified example - in practice, this would be more sophisticated
            if workflow_config.get("enable_file_operations"):
                required_tools.add("file_manager")
            
            if workflow_config.get("enable_web_search"):
                required_tools.add("web_search")
            
            if workflow_config.get("enable_calculator"):
                required_tools.add("calculator")
        
        return required_tools
    
    def preload_tools(self, tool_names: List[str]) -> None:
        """Preload specific tools synchronously.
        
        Args:
            tool_names: List of tool names to preload
        """
        for tool_name in tool_names:
            if tool_name in self.tool_registry and tool_name not in self.loaded_tools:
                try:
                    tool_factory = self.tool_registry[tool_name]
                    # Only preload non-async tools
                    if not asyncio.iscoroutinefunction(tool_factory):
                        tool = tool_factory()
                        self.loaded_tools[tool_name] = tool
                        self.load_stats[tool_name] = self.load_stats.get(tool_name, 0) + 1
                        self.total_loads += 1
                        logger.debug("Tool preloaded", tool_name=tool_name)
                except Exception as e:
                    logger.error("Failed to preload tool", tool_name=tool_name, error=str(e))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get lazy loading statistics.
        
        Returns:
            Dictionary with loading statistics
        """
        return {
            "registered_tools": len(self.tool_registry),
            "loaded_tools": len(self.loaded_tools),
            "total_loads": self.total_loads,
            "load_stats": dict(self.load_stats)
        }


class StateCompressor:
    """Utilities for compressing conversation state to improve performance."""
    
    def __init__(self, max_messages: int = 50, summary_threshold: int = 100):
        """Initialize state compressor.
        
        Args:
            max_messages: Maximum number of messages to keep uncompressed
            summary_threshold: Threshold for triggering compression
        """
        self.max_messages = max_messages
        self.summary_threshold = summary_threshold
    
    def should_compress(self, messages: List[Any]) -> bool:
        """Check if state should be compressed.
        
        Args:
            messages: List of messages in the conversation
            
        Returns:
            True if compression is recommended
        """
        return len(messages) > self.summary_threshold
    
    def compress_conversation_state(
        self, 
        state: Dict[str, Any], 
        llm: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Compress conversation state by summarizing old messages.
        
        Args:
            state: Conversation state to compress
            llm: Language model for generating summaries (optional)
            
        Returns:
            Compressed conversation state
        """
        messages = state.get("messages", [])
        
        if not self.should_compress(messages):
            return state
        
        # Keep recent messages
        recent_messages = messages[-self.max_messages:]
        
        # Compress older messages
        older_messages = messages[:-self.max_messages]
        
        if older_messages:
            # Create a simple summary if no LLM provided
            if llm is None:
                summary = f"[Summary: {len(older_messages)} previous messages in this conversation]"
            else:
                # Generate a more detailed summary using the LLM
                # This would need to be implemented based on the specific LLM interface
                summary = f"[AI-generated summary of {len(older_messages)} messages]"
            
            # Create compressed state
            compressed_state = state.copy()
            compressed_state["messages"] = recent_messages
            compressed_state["conversation_summary"] = summary
            compressed_state["compressed_message_count"] = len(older_messages)
            
            logger.info(
                "Compressed conversation state",
                original_messages=len(messages),
                compressed_messages=len(recent_messages),
                summary_length=len(summary)
            )
            
            return compressed_state
        
        return state
    
    def estimate_state_size(self, state: Dict[str, Any]) -> int:
        """Estimate the size of conversation state in characters.
        
        Args:
            state: Conversation state
            
        Returns:
            Estimated size in characters
        """
        # Simple size estimation
        size = 0
        
        for key, value in state.items():
            if isinstance(value, str):
                size += len(value)
            elif isinstance(value, list):
                for item in value:
                    if hasattr(item, "content"):
                        size += len(str(item.content))
                    else:
                        size += len(str(item))
            else:
                size += len(str(value))
        
        return size


# Global instances for easy access
workflow_cache = WorkflowCache()
lazy_tool_loader = LazyToolLoader()
state_compressor = StateCompressor()


# Example tool registration
def register_common_tools():
    """Register common tools for lazy loading."""
    
    def create_calculator():
        """Create calculator tool."""
        # This would be replaced with actual tool creation
        class MockCalculator:
            name = "calculator"
            def invoke(self, args):
                return f"Calculator result for {args}"
        
        return MockCalculator()
    
    def create_file_manager():
        """Create file manager tool."""
        class MockFileManager:
            name = "file_manager"
            def invoke(self, args):
                return f"File operation result for {args}"
        
        return MockFileManager()
    
    async def create_web_search():
        """Create web search tool."""
        class MockWebSearch:
            name = "web_search"
            def invoke(self, args):
                return f"Web search results for {args}"
        
        return MockWebSearch()
    
    # Register tools
    lazy_tool_loader.register_tool("calculator", create_calculator)
    lazy_tool_loader.register_tool("file_manager", create_file_manager)
    lazy_tool_loader.register_tool("web_search", create_web_search)


# Register common tools on module import
register_common_tools()