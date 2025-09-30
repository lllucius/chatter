"""Enhanced memory management system with adaptive windows and caching.

This module provides improved memory management capabilities including
adaptive memory windows, memory prioritization, summary caching, and
multiple fallback strategies.
"""

from __future__ import annotations

import hashlib
import time
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from chatter.core.workflow_node_factory import WorkflowNodeContext
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class MemoryConfig:
    """Configuration for memory management behavior."""

    def __init__(
        self,
        base_window_size: int = 10,
        max_window_size: int = 50,
        min_window_size: int = 4,
        adaptive_mode: bool = True,
        prioritize_recent: bool = True,
        cache_summaries: bool = True,
        cache_ttl_seconds: int = 3600,  # 1 hour
        summary_strategy: str = "intelligent",  # "simple", "intelligent", "structured"
        fallback_strategy: str = "truncation",  # "truncation", "compression", "skip"
        complexity_threshold: float = 0.7,  # When to expand window
    ):
        self.base_window_size = base_window_size
        self.max_window_size = max_window_size
        self.min_window_size = min_window_size
        self.adaptive_mode = adaptive_mode
        self.prioritize_recent = prioritize_recent
        self.cache_summaries = cache_summaries
        self.cache_ttl_seconds = cache_ttl_seconds
        self.summary_strategy = summary_strategy
        self.fallback_strategy = fallback_strategy
        self.complexity_threshold = complexity_threshold


class MessageImportanceScorer:
    """Scores message importance for memory prioritization."""

    def __init__(self):
        self.importance_indicators = {
            # High importance indicators
            "questions": [
                "?",
                "what",
                "how",
                "why",
                "when",
                "where",
                "who",
            ],
            "decisions": [
                "decide",
                "choose",
                "select",
                "pick",
                "prefer",
                "recommend",
            ],
            "problems": [
                "error",
                "issue",
                "problem",
                "bug",
                "fail",
                "wrong",
            ],
            "instructions": [
                "please",
                "can you",
                "could you",
                "would you",
                "help me",
            ],
            "facts": [
                "is",
                "are",
                "was",
                "were",
                "fact",
                "truth",
                "actually",
            ],
            # Medium importance indicators
            "clarifications": [
                "clarify",
                "explain",
                "meaning",
                "understand",
            ],
            "examples": [
                "example",
                "instance",
                "sample",
                "demonstration",
            ],
            "confirmations": ["yes", "no", "correct", "right", "wrong"],
            # Low importance indicators
            "greetings": [
                "hello",
                "hi",
                "hey",
                "good morning",
                "good afternoon",
            ],
            "thanks": ["thank", "thanks", "appreciate", "grateful"],
            "casual": ["okay", "ok", "sure", "fine", "alright"],
        }

    def score_message(self, message: BaseMessage) -> float:
        """Score a message's importance from 0.0 to 1.0."""
        if not hasattr(message, "content") or not message.content:
            return 0.1

        content = message.content.lower()
        score = 0.5  # Base score

        # Check for high importance indicators
        for indicator in self.importance_indicators["questions"]:
            if indicator in content:
                score += 0.2

        for indicator in self.importance_indicators["decisions"]:
            if indicator in content:
                score += 0.15

        for indicator in self.importance_indicators["problems"]:
            if indicator in content:
                score += 0.15

        for indicator in self.importance_indicators["instructions"]:
            if indicator in content:
                score += 0.1

        # Check for medium importance indicators
        for indicator in self.importance_indicators["clarifications"]:
            if indicator in content:
                score += 0.05

        # Check for low importance indicators (reduce score)
        for indicator in self.importance_indicators["greetings"]:
            if indicator in content:
                score -= 0.1

        for indicator in self.importance_indicators["casual"]:
            if indicator in content:
                score -= 0.05

        # Bonus for length (longer messages often more important)
        if len(content) > 100:
            score += 0.1
        elif len(content) < 20:
            score -= 0.1

        # Bonus for AI messages with detailed responses
        if isinstance(message, AIMessage) and len(content) > 200:
            score += 0.1

        return max(0.0, min(1.0, score))  # Clamp to [0, 1]


class SummaryCache:
    """Cache for conversation summaries with TTL support."""

    def __init__(self, ttl_seconds: int = 3600):
        self.cache: dict[str, dict[str, Any]] = {}
        self.ttl_seconds = ttl_seconds

    def _generate_key(self, messages: list[BaseMessage]) -> str:
        """Generate a cache key from messages."""
        # Create a hash of message contents for caching
        content_hash = hashlib.md5(usedforsecurity=False)
        for msg in messages:
            content_hash.update(
                f"{type(msg).__name__}:{getattr(msg, 'content', '')}".encode()
            )
        return content_hash.hexdigest()

    def get_summary(self, messages: list[BaseMessage]) -> str | None:
        """Get cached summary if available and not expired."""
        key = self._generate_key(messages)

        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry["timestamp"] < self.ttl_seconds:
                logger.debug(f"Cache hit for summary key: {key[:8]}...")
                return entry["summary"]
            else:
                # Expired entry
                del self.cache[key]
                logger.debug(
                    f"Cache expired for summary key: {key[:8]}..."
                )

        return None

    def store_summary(
        self, messages: list[BaseMessage], summary: str
    ) -> None:
        """Store summary in cache."""
        key = self._generate_key(messages)
        self.cache[key] = {
            "summary": summary,
            "timestamp": time.time(),
            "message_count": len(messages),
        }
        logger.debug(
            f"Cached summary for key: {key[:8]}... ({len(messages)} messages)"
        )

    def clear_expired(self) -> int:
        """Clear expired entries and return count of removed entries."""
        current_time = time.time()
        expired_keys = [
            key
            for key, entry in self.cache.items()
            if current_time - entry["timestamp"] >= self.ttl_seconds
        ]

        for key in expired_keys:
            del self.cache[key]

        if expired_keys:
            logger.debug(
                f"Cleared {len(expired_keys)} expired summary cache entries"
            )

        return len(expired_keys)

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return {
            "total_entries": len(self.cache),
            "cache_size_bytes": sum(
                len(str(entry)) for entry in self.cache.values()
            ),
            "oldest_entry_age": min(
                (
                    time.time() - entry["timestamp"]
                    for entry in self.cache.values()
                ),
                default=0,
            ),
        }


class EnhancedMemoryManager:
    """Enhanced memory manager with adaptive windows and intelligent summarization."""

    def __init__(self, config: MemoryConfig | None = None):
        self.config = config or MemoryConfig()
        self.importance_scorer = MessageImportanceScorer()
        self.summary_cache = SummaryCache(self.config.cache_ttl_seconds)

    async def manage_memory(
        self,
        context: WorkflowNodeContext,
        llm: BaseChatModel | None = None,
    ) -> dict[str, Any]:
        """Enhanced memory management with adaptive window sizing."""
        messages = list(context["messages"])

        if not messages:
            return {}

        # Determine optimal window size
        window_size = self._determine_window_size(context, messages)

        if len(messages) <= window_size:
            logger.debug(
                f"Messages ({len(messages)}) within window size ({window_size}), no management needed"
            )
            return {}

        # Split messages
        if self.config.prioritize_recent:
            recent_messages, older_messages = self._split_by_importance(
                messages, window_size
            )
        else:
            recent_messages = messages[-window_size:]
            older_messages = messages[:-window_size]

        # Create or get cached summary
        summary = await self._create_or_get_summary(
            older_messages, context, llm
        )

        if summary:
            return {
                "messages": recent_messages,
                "conversation_summary": summary,
                "metadata": {
                    **context.get("metadata", {}),
                    "memory_management": {
                        "window_size_used": window_size,
                        "messages_summarized": len(older_messages),
                        "messages_kept": len(recent_messages),
                        "summary_strategy": self.config.summary_strategy,
                        "adaptive_mode": self.config.adaptive_mode,
                        "summary_cached": self._was_summary_cached(
                            older_messages
                        ),
                    },
                },
            }
        else:
            # Fallback strategy
            return await self._apply_fallback_strategy(
                recent_messages, older_messages, context
            )

    def _determine_window_size(
        self, context: WorkflowNodeContext, messages: list[BaseMessage]
    ) -> int:
        """Determine optimal window size based on context and complexity."""
        if not self.config.adaptive_mode:
            return self.config.base_window_size

        # Start with base window size
        window_size = self.config.base_window_size

        # Analyze conversation complexity
        complexity_score = self._analyze_conversation_complexity(
            messages, context
        )

        if complexity_score > self.config.complexity_threshold:
            # High complexity - expand window
            expansion_factor = 1 + (
                complexity_score - self.config.complexity_threshold
            )
            window_size = int(window_size * expansion_factor)
            logger.debug(
                f"High complexity ({complexity_score:.2f}), expanding window to {window_size}"
            )
        elif complexity_score < 0.3:
            # Low complexity - can shrink window
            window_size = max(
                self.config.min_window_size, int(window_size * 0.8)
            )
            logger.debug(
                f"Low complexity ({complexity_score:.2f}), shrinking window to {window_size}"
            )

        # Apply bounds
        window_size = max(
            self.config.min_window_size,
            min(self.config.max_window_size, window_size),
        )

        return window_size

    def _analyze_conversation_complexity(
        self, messages: list[BaseMessage], context: WorkflowNodeContext
    ) -> float:
        """Analyze conversation complexity to determine memory needs."""
        if len(messages) < 5:
            return 0.3  # Low complexity for short conversations

        complexity_factors = []

        # Factor 1: Tool usage indicates complexity
        tool_count = context.get("tool_call_count", 0)
        tool_complexity = min(1.0, tool_count / 5.0)  # Normalize to 0-1
        complexity_factors.append(tool_complexity)

        # Factor 2: Message length variance (complex conversations have varied lengths)
        message_lengths = [
            len(getattr(msg, "content", "")) for msg in messages[-10:]
        ]
        if message_lengths:
            length_variance = max(message_lengths) - min(
                message_lengths
            )
            length_complexity = min(
                1.0, length_variance / 500.0
            )  # Normalize
            complexity_factors.append(length_complexity)

        # Factor 3: Question frequency (more questions = more complex)
        recent_messages = messages[-10:]
        question_count = sum(
            1
            for msg in recent_messages
            if "?" in getattr(msg, "content", "")
        )
        question_complexity = min(1.0, question_count / 5.0)
        complexity_factors.append(question_complexity)

        # Factor 4: Technical terms or jargon
        technical_indicators = [
            "api",
            "function",
            "code",
            "algorithm",
            "parameter",
            "configuration",
            "implementation",
        ]
        recent_content = " ".join(
            getattr(msg, "content", "") for msg in recent_messages
        ).lower()
        tech_count = sum(
            1 for term in technical_indicators if term in recent_content
        )
        tech_complexity = min(1.0, tech_count / 3.0)
        complexity_factors.append(tech_complexity)

        # Factor 5: Error states increase complexity
        error_state = context.get("error_state", {})
        error_complexity = min(1.0, len(error_state) / 3.0)
        complexity_factors.append(error_complexity)

        # Calculate weighted average
        weights = [
            0.3,
            0.2,
            0.2,
            0.2,
            0.1,
        ]  # Tool usage gets highest weight
        complexity_score = sum(
            factor * weight
            for factor, weight in zip(
                complexity_factors, weights, strict=False
            )
        )

        return complexity_score

    def _split_by_importance(
        self, messages: list[BaseMessage], window_size: int
    ) -> tuple[list[BaseMessage], list[BaseMessage]]:
        """Split messages by importance, keeping most important recent messages."""
        if len(messages) <= window_size:
            return messages, []

        # Score all messages
        [
            (i, msg, self.importance_scorer.score_message(msg))
            for i, msg in enumerate(messages)
        ]

        # Always keep the most recent messages (they're usually most relevant)
        guaranteed_recent = min(window_size // 2, len(messages) // 4)
        recent_guaranteed = messages[-guaranteed_recent:]
        remaining_messages = (
            messages[:-guaranteed_recent]
            if guaranteed_recent > 0
            else messages
        )

        # Score remaining messages and select by importance
        remaining_scored = [
            (i, msg, self.importance_scorer.score_message(msg))
            for i, msg in enumerate(remaining_messages)
        ]

        # Sort by importance score (descending)
        remaining_scored.sort(key=lambda x: x[2], reverse=True)

        # Take top N by importance
        slots_remaining = window_size - len(recent_guaranteed)
        selected_important = remaining_scored[:slots_remaining]

        # Combine and sort by original order
        selected_messages = []
        selected_indices = {i for i, _, _ in selected_important}

        for i, msg in enumerate(remaining_messages):
            if i in selected_indices:
                selected_messages.append(msg)

        selected_messages.extend(recent_guaranteed)

        # Everything else goes to older messages
        older_messages = []
        selected_set = {id(msg) for msg in selected_messages}
        for msg in messages:
            if id(msg) not in selected_set:
                older_messages.append(msg)

        logger.debug(
            f"Split by importance: {len(selected_messages)} kept, {len(older_messages)} to summarize"
        )
        return selected_messages, older_messages

    async def _create_or_get_summary(
        self,
        messages: list[BaseMessage],
        context: WorkflowNodeContext,
        llm: BaseChatModel | None = None,
    ) -> str | None:
        """Create or retrieve cached summary."""
        if not messages:
            return None

        # Check cache first
        if self.config.cache_summaries:
            cached_summary = self.summary_cache.get_summary(messages)
            if cached_summary:
                return cached_summary

        # Create new summary
        if llm:
            try:
                summary = await self._create_summary(messages, llm)

                # Cache the summary
                if self.config.cache_summaries and summary:
                    self.summary_cache.store_summary(messages, summary)

                return summary
            except Exception as e:
                logger.error(f"Summary creation failed: {e}")
                return None
        else:
            logger.warning("No LLM provided for summarization")
            return None

    async def _create_summary(
        self, messages: list[BaseMessage], llm: BaseChatModel
    ) -> str:
        """Create summary using specified strategy."""
        if self.config.summary_strategy == "simple":
            return await self._create_simple_summary(messages, llm)
        elif self.config.summary_strategy == "intelligent":
            return await self._create_intelligent_summary(messages, llm)
        elif self.config.summary_strategy == "structured":
            return await self._create_structured_summary(messages, llm)
        else:
            return await self._create_simple_summary(messages, llm)

    async def _create_simple_summary(
        self, messages: list[BaseMessage], llm: BaseChatModel
    ) -> str:
        """Create a simple conversation summary."""
        summary_prompt = (
            "Create a concise summary of this conversation. "
            "Focus on key facts, decisions, and context that would be useful for continuing the conversation. "
            "Format: 'Summary: [key points]'\n\n"
        )

        for msg in messages:
            role = (
                "Human"
                if isinstance(msg, HumanMessage)
                else "Assistant"
            )
            content = getattr(msg, "content", "")
            summary_prompt += f"{role}: {content[:200]}...\n"  # Truncate long messages

        summary_prompt += "\nProvide a factual summary:"

        response = await llm.ainvoke(
            [HumanMessage(content=summary_prompt)]
        )
        summary = getattr(response, "content", str(response)).strip()

        if not summary.lower().startswith("summary:"):
            summary = f"Summary: {summary}"

        return summary

    async def _create_intelligent_summary(
        self, messages: list[BaseMessage], llm: BaseChatModel
    ) -> str:
        """Create an intelligent summary that prioritizes important information."""
        # Score messages by importance
        scored_messages = [
            (msg, self.importance_scorer.score_message(msg))
            for msg in messages
        ]

        # Sort by importance and take top messages for detailed summary
        scored_messages.sort(key=lambda x: x[1], reverse=True)
        important_messages = [
            msg for msg, score in scored_messages[:10]
        ]  # Top 10 important

        summary_prompt = (
            "Create an intelligent summary of this conversation, focusing on the most important exchanges. "
            "Prioritize: decisions made, problems discussed, facts established, and key questions asked. "
            "Format: 'Context: [important facts and decisions] | Discussion: [key topics] | Status: [current state]'\n\n"
            "Important exchanges:\n"
        )

        for msg in important_messages:
            role = (
                "Human"
                if isinstance(msg, HumanMessage)
                else "Assistant"
            )
            content = getattr(msg, "content", "")
            summary_prompt += f"{role}: {content[:150]}...\n"

        summary_prompt += "\nProvide an intelligent summary:"

        response = await llm.ainvoke(
            [HumanMessage(content=summary_prompt)]
        )
        summary = getattr(response, "content", str(response)).strip()

        if not any(
            summary.lower().startswith(prefix)
            for prefix in ["context:", "summary:", "discussion:"]
        ):
            summary = f"Context: {summary}"

        return summary

    async def _create_structured_summary(
        self, messages: list[BaseMessage], llm: BaseChatModel
    ) -> str:
        """Create a structured summary with categories."""
        summary_prompt = (
            "Create a structured summary of this conversation using the following format:\n"
            "FACTS: [Key facts and information established]\n"
            "DECISIONS: [Decisions made or preferences expressed]\n"
            "QUESTIONS: [Important questions asked]\n"
            "ACTIONS: [Actions taken or tools used]\n"
            "CONTEXT: [Background context for next interaction]\n\n"
            "Conversation to summarize:\n"
        )

        for msg in messages:
            role = (
                "Human"
                if isinstance(msg, HumanMessage)
                else "Assistant"
            )
            content = getattr(msg, "content", "")
            summary_prompt += f"{role}: {content[:200]}...\n"

        summary_prompt += "\nProvide a structured summary:"

        response = await llm.ainvoke(
            [HumanMessage(content=summary_prompt)]
        )
        summary = getattr(response, "content", str(response)).strip()

        return summary

    async def _apply_fallback_strategy(
        self,
        recent_messages: list[BaseMessage],
        older_messages: list[BaseMessage],
        context: WorkflowNodeContext,
    ) -> dict[str, Any]:
        """Apply fallback strategy when summarization fails."""
        if self.config.fallback_strategy == "truncation":
            logger.info(
                f"Using truncation fallback: keeping {len(recent_messages)} recent messages"
            )
            return {
                "messages": recent_messages,
                "metadata": {
                    **context.get("metadata", {}),
                    "memory_fallback": "truncation",
                    "truncated_messages": len(older_messages),
                },
            }
        elif self.config.fallback_strategy == "compression":
            # Simple compression: keep every nth message from older messages
            compression_ratio = 3  # Keep every 3rd message
            compressed_older = older_messages[::compression_ratio]

            logger.info(
                f"Using compression fallback: compressed {len(older_messages)} to {len(compressed_older)}"
            )
            return {
                "messages": compressed_older + recent_messages,
                "metadata": {
                    **context.get("metadata", {}),
                    "memory_fallback": "compression",
                    "compression_ratio": compression_ratio,
                    "compressed_messages": len(older_messages)
                    - len(compressed_older),
                },
            }
        elif self.config.fallback_strategy == "skip":
            # Skip memory management this round
            logger.warning(
                "Skipping memory management due to summarization failure"
            )
            return {
                "metadata": {
                    **context.get("metadata", {}),
                    "memory_fallback": "skip",
                    "memory_management_skipped": True,
                }
            }
        else:
            # Default to truncation
            return await self._apply_fallback_strategy(
                recent_messages, older_messages, context
            )

    def _was_summary_cached(self, messages: list[BaseMessage]) -> bool:
        """Check if summary was retrieved from cache (for metrics)."""
        if not self.config.cache_summaries:
            return False
        return self.summary_cache.get_summary(messages) is not None

    def get_memory_stats(self) -> dict[str, Any]:
        """Get memory management statistics."""
        cache_stats = self.summary_cache.get_cache_stats()

        return {
            "config": {
                "adaptive_mode": self.config.adaptive_mode,
                "base_window_size": self.config.base_window_size,
                "max_window_size": self.config.max_window_size,
                "summary_strategy": self.config.summary_strategy,
                "fallback_strategy": self.config.fallback_strategy,
            },
            "cache_stats": cache_stats,
        }

    def clear_cache(self) -> int:
        """Clear summary cache and return number of entries removed."""
        count = len(self.summary_cache.cache)
        self.summary_cache.cache.clear()
        logger.info(f"Cleared {count} entries from summary cache")
        return count
