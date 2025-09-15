"""Intelligent search service with personalized recommendations and semantic enhancements."""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.core.cache_factory import get_general_cache
from chatter.models.conversation import Conversation
from chatter.models.document import Document
from chatter.models.prompt import Prompt
from chatter.services.dynamic_vector_store import (
    DynamicVectorStoreService,
)
from chatter.services.embeddings import EmbeddingService
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class IntelligentSearchService:
    """Enhanced search service with personalized recommendations and semantic intelligence."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.vector_store = DynamicVectorStoreService(session)
        self.embeddings_service = EmbeddingService()
        self.cache = get_general_cache()

    async def semantic_search(
        self,
        query: str,
        user_id: str,
        search_type: str = "documents",
        limit: int = 10,
        include_recommendations: bool = True,
    ) -> dict[str, Any]:
        """Perform semantic search with personalized results and recommendations."""

        # Generate search embedding
        query_embedding = await self._get_query_embedding(query)

        # Perform base semantic search
        base_results = await self._perform_base_search(
            query, query_embedding, search_type, limit
        )

        # Get personalized context
        user_context = await self._get_user_search_context(user_id)

        # Enhance results with personalization
        enhanced_results = await self._personalize_results(
            base_results, user_context, query
        )

        # Generate intelligent recommendations
        recommendations = []
        if include_recommendations:
            recommendations = (
                await self._generate_search_recommendations(
                    query, user_id, enhanced_results
                )
            )

        return {
            "query": query,
            "results": enhanced_results,
            "recommendations": recommendations,
            "user_context": user_context,
            "search_metadata": {
                "search_type": search_type,
                "result_count": len(enhanced_results),
                "personalized": True,
                "timestamp": datetime.now(UTC).isoformat(),
            },
        }

    async def _get_query_embedding(self, query: str) -> list[float]:
        """Generate embedding for search query."""
        try:
            # Use the embeddings service to generate query embedding
            embedding = (
                await self.embeddings_service.generate_embeddings(
                    [query]
                )
            )
            return embedding[0] if embedding else []
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            return []

    async def _perform_base_search(
        self,
        query: str,
        query_embedding: list[float],
        search_type: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        """Perform base semantic search using vector store."""
        results = []

        try:
            if search_type == "documents" and query_embedding:
                # Vector similarity search for documents
                vector_results = (
                    await self.vector_store.similarity_search(
                        query_embedding=query_embedding,
                        k=limit,
                        threshold=0.7,
                    )
                )

                for chunk, score in vector_results:
                    results.append(
                        {
                            "type": "document_chunk",
                            "id": chunk.id,
                            "document_id": chunk.document_id,
                            "content": chunk.content,
                            "score": score,
                            "metadata": chunk.metadata or {},
                        }
                    )

            elif search_type == "conversations":
                # Text search for conversations
                stmt = (
                    select(Conversation)
                    .where(Conversation.title.ilike(f"%{query}%"))
                    .order_by(desc(Conversation.updated_at))
                    .limit(limit)
                )
                result = await self.session.execute(stmt)
                conversations = result.scalars().all()

                for conv in conversations:
                    results.append(
                        {
                            "type": "conversation",
                            "id": conv.id,
                            "title": conv.title,
                            "content": conv.title,  # Could include first message
                            "score": 0.8,  # Text match score
                            "metadata": {
                                "created_at": conv.created_at.isoformat(),
                                "user_id": conv.user_id,
                            },
                        }
                    )

            elif search_type == "prompts":
                # Text search for prompts
                stmt = (
                    select(Prompt)
                    .where(
                        Prompt.name.ilike(f"%{query}%")
                        | Prompt.template.ilike(f"%{query}%")
                    )
                    .order_by(desc(Prompt.updated_at))
                    .limit(limit)
                )
                result = await self.session.execute(stmt)
                prompts = result.scalars().all()

                for prompt in prompts:
                    results.append(
                        {
                            "type": "prompt",
                            "id": prompt.id,
                            "name": prompt.name,
                            "content": prompt.template,
                            "score": 0.8,
                            "metadata": {
                                "created_at": prompt.created_at.isoformat(),
                                "user_id": prompt.user_id,
                                "variables": prompt.variables or [],
                            },
                        }
                    )

        except Exception as e:
            logger.error(f"Error in base search: {e}")

        return results

    async def _get_user_search_context(
        self, user_id: str
    ) -> dict[str, Any]:
        """Get user's search context for personalization."""
        cache_key = f"search_context:{user_id}"

        # Check cache first
        cached_context = await self.cache.get(cache_key)
        if cached_context:
            return cached_context

        # Calculate fresh context
        context = {
            "user_id": user_id,
            "recent_searches": await self._get_recent_searches(user_id),
            "preferred_content_types": await self._analyze_content_preferences(
                user_id
            ),
            "collaboration_network": await self._get_collaboration_network(
                user_id
            ),
            "expertise_areas": await self._infer_expertise_areas(
                user_id
            ),
            "activity_patterns": await self._analyze_activity_patterns(
                user_id
            ),
        }

        # Cache for 1 hour
        await self.cache.set(cache_key, context, ttl=3600)
        return context

    async def _get_recent_searches(self, user_id: str) -> list[str]:
        """Get user's recent search queries."""
        # This would be implemented with a search history table
        # For now, return empty list
        return []

    async def _analyze_content_preferences(
        self, user_id: str
    ) -> dict[str, float]:
        """Analyze user's content type preferences."""
        try:
            # Count user's interactions with different content types
            doc_count = await self._count_user_documents(user_id)
            conv_count = await self._count_user_conversations(user_id)
            prompt_count = await self._count_user_prompts(user_id)

            total = doc_count + conv_count + prompt_count
            if total == 0:
                return {
                    "documents": 0.33,
                    "conversations": 0.33,
                    "prompts": 0.33,
                }

            return {
                "documents": doc_count / total,
                "conversations": conv_count / total,
                "prompts": prompt_count / total,
            }
        except Exception as e:
            logger.error(f"Error analyzing content preferences: {e}")
            return {
                "documents": 0.33,
                "conversations": 0.33,
                "prompts": 0.33,
            }

    async def _count_user_documents(self, user_id: str) -> int:
        """Count documents associated with user."""
        try:
            stmt = select(func.count(Document.id)).where(
                Document.user_id == user_id
            )
            result = await self.session.execute(stmt)
            return result.scalar() or 0
        except Exception:
            return 0

    async def _count_user_conversations(self, user_id: str) -> int:
        """Count conversations for user."""
        try:
            stmt = select(func.count(Conversation.id)).where(
                Conversation.user_id == user_id
            )
            result = await self.session.execute(stmt)
            return result.scalar() or 0
        except Exception:
            return 0

    async def _count_user_prompts(self, user_id: str) -> int:
        """Count prompts created by user."""
        try:
            stmt = select(func.count(Prompt.id)).where(
                Prompt.user_id == user_id
            )
            result = await self.session.execute(stmt)
            return result.scalar() or 0
        except Exception:
            return 0

    async def _get_collaboration_network(
        self, user_id: str
    ) -> list[str]:
        """Get users that this user frequently collaborates with."""
        # This would analyze shared documents, conversations, etc.
        # For now, return empty list
        return []

    async def _infer_expertise_areas(self, user_id: str) -> list[str]:
        """Infer user's areas of expertise from their content."""
        try:
            # Analyze user's document topics, prompt patterns, etc.
            # This would use NLP/topic modeling on user content
            # For now, return sample areas
            return [
                "technical_writing",
                "data_analysis",
                "project_management",
            ]
        except Exception as e:
            logger.error(f"Error inferring expertise areas: {e}")
            return []

    async def _analyze_activity_patterns(
        self, user_id: str
    ) -> dict[str, Any]:
        """Analyze user's activity patterns for search personalization."""
        return {
            "most_active_hours": [9, 10, 14, 15],
            "preferred_search_depth": "detailed",
            "collaboration_frequency": "moderate",
            "content_creation_rate": "high",
        }

    async def _personalize_results(
        self,
        results: list[dict[str, Any]],
        user_context: dict[str, Any],
        query: str,
    ) -> list[dict[str, Any]]:
        """Enhance search results with personalization."""
        enhanced_results = []

        for result in results:
            # Apply personalization scoring
            personalization_boost = (
                self._calculate_personalization_boost(
                    result, user_context, query
                )
            )

            # Adjust score with personalization
            original_score = result.get("score", 0.5)
            personalized_score = min(
                1.0, original_score + personalization_boost
            )

            enhanced_result = result.copy()
            enhanced_result.update(
                {
                    "personalized_score": personalized_score,
                    "personalization_boost": personalization_boost,
                    "personalization_factors": self._get_personalization_factors(
                        result, user_context
                    ),
                }
            )

            enhanced_results.append(enhanced_result)

        # Sort by personalized score
        enhanced_results.sort(
            key=lambda x: x["personalized_score"], reverse=True
        )
        return enhanced_results

    def _calculate_personalization_boost(
        self,
        result: dict[str, Any],
        user_context: dict[str, Any],
        query: str,
    ) -> float:
        """Calculate personalization boost for a search result."""
        boost = 0.0

        # Content type preference boost
        content_type = (
            result.get("type", "")
            .replace("_chunk", "")
            .replace("_", "")
        )
        if content_type in user_context.get(
            "preferred_content_types", {}
        ):
            preference_score = user_context["preferred_content_types"][
                content_type
            ]
            boost += preference_score * 0.1

        # Expertise area boost
        expertise_areas = user_context.get("expertise_areas", [])
        content = result.get("content", "").lower()
        for area in expertise_areas:
            if area.replace("_", " ") in content:
                boost += 0.05

        # Recent relevance boost
        if "metadata" in result and "created_at" in result["metadata"]:
            try:
                created_at = datetime.fromisoformat(
                    result["metadata"]["created_at"].replace(
                        "Z", "+00:00"
                    )
                )
                days_old = (datetime.now(UTC) - created_at).days
                if days_old < 7:  # Recent content gets boost
                    boost += 0.05 * (7 - days_old) / 7
            except Exception:
                pass

        # User ownership boost
        if result.get("metadata", {}).get(
            "user_id"
        ) == user_context.get("user_id"):
            boost += 0.1

        return min(0.3, boost)  # Cap boost at 0.3

    def _get_personalization_factors(
        self, result: dict[str, Any], user_context: dict[str, Any]
    ) -> list[str]:
        """Get list of personalization factors that influenced the result."""
        factors = []

        content_type = (
            result.get("type", "")
            .replace("_chunk", "")
            .replace("_", "")
        )
        if content_type in user_context.get(
            "preferred_content_types", {}
        ):
            factors.append(f"preferred_content_type:{content_type}")

        if result.get("metadata", {}).get(
            "user_id"
        ) == user_context.get("user_id"):
            factors.append("user_created")

        return factors

    async def _generate_search_recommendations(
        self, query: str, user_id: str, results: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Generate intelligent search recommendations."""
        recommendations = []

        # Query expansion recommendations
        if len(results) < 5:
            recommendations.append(
                {
                    "type": "query_expansion",
                    "title": "Try broader search terms",
                    "description": f"Search for '{query}' returned few results. Try more general terms.",
                    "suggested_queries": await self._suggest_broader_queries(
                        query
                    ),
                }
            )

        # Related content recommendations
        if results:
            recommendations.append(
                {
                    "type": "related_content",
                    "title": "Related content you might like",
                    "description": "Based on your search results and preferences",
                    "items": await self._find_related_content(
                        results, user_id
                    ),
                }
            )

        # Collaboration recommendations
        collaboration_network = await self._get_collaboration_network(
            user_id
        )
        if collaboration_network:
            recommendations.append(
                {
                    "type": "collaboration",
                    "title": "Content from your network",
                    "description": "Similar content from users you collaborate with",
                    "items": await self._find_network_content(
                        query, collaboration_network
                    ),
                }
            )

        return recommendations

    async def _suggest_broader_queries(self, query: str) -> list[str]:
        """Suggest broader query terms."""
        # Simple implementation - remove last word or suggest synonyms
        words = query.split()
        if len(words) > 1:
            return [" ".join(words[:-1])]
        return []

    async def _find_related_content(
        self, results: list[dict[str, Any]], user_id: str
    ) -> list[dict[str, Any]]:
        """Find content related to search results."""
        # This would use embeddings to find similar content
        # For now, return empty list
        return []

    async def _find_network_content(
        self, query: str, collaboration_network: list[str]
    ) -> list[dict[str, Any]]:
        """Find content from user's collaboration network."""
        # This would search content created by network users
        # For now, return empty list
        return []

    async def get_trending_content(
        self, user_id: str, limit: int = 10
    ) -> list[dict[str, Any]]:
        """Get trending content personalized for user."""
        cache_key = f"trending:{user_id}"

        # Check cache first
        cached_trending = await self.cache.get(cache_key)
        if cached_trending:
            return cached_trending

        # Calculate trending content
        trending = await self._calculate_trending_content(
            user_id, limit
        )

        # Cache for 30 minutes
        await self.cache.set(cache_key, trending, ttl=1800)
        return trending

    async def _calculate_trending_content(
        self, user_id: str, limit: int
    ) -> list[dict[str, Any]]:
        """Calculate trending content based on recent activity and user preferences."""
        # This would analyze recent access patterns, sharing, etc.
        # For now, return recent documents
        try:
            stmt = (
                select(Document)
                .order_by(desc(Document.updated_at))
                .limit(limit)
            )
            result = await self.session.execute(stmt)
            documents = result.scalars().all()

            trending = []
            for doc in documents:
                trending.append(
                    {
                        "type": "document",
                        "id": doc.id,
                        "title": doc.title,
                        "content": (
                            doc.content[:200] + "..."
                            if len(doc.content) > 200
                            else doc.content
                        ),
                        "trending_score": 0.8,
                        "metadata": {
                            "created_at": doc.created_at.isoformat(),
                            "user_id": doc.user_id,
                            "trend_reason": "recently_updated",
                        },
                    }
                )

            return trending
        except Exception as e:
            logger.error(f"Error calculating trending content: {e}")
            return []


# Global service instance
_intelligent_search_service: IntelligentSearchService | None = None


def get_intelligent_search_service(
    session: AsyncSession,
) -> IntelligentSearchService:
    """Get the intelligent search service instance."""
    global _intelligent_search_service
    if _intelligent_search_service is None:
        _intelligent_search_service = IntelligentSearchService(session)
    return _intelligent_search_service
