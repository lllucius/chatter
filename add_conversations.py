#!/usr/bin/env python3
"""Script to add 20 test conversations to the database."""

import asyncio
import random
from datetime import datetime, timedelta

from chatter.models.conversation import (
    Conversation,
    ConversationStatus,
    Message,
    MessageRole,
)
from chatter.utils.database import DatabaseManager


async def add_test_conversations():
    """Add 20 test conversations to the database."""

    # Sample conversation topics and messages
    conversation_topics = [
        "Python Programming Help",
        "Machine Learning Fundamentals",
        "Database Design Questions",
        "Web Development Best Practices",
        "API Design Discussion",
        "Data Science Project",
        "Code Review Session",
        "System Architecture Planning",
        "Performance Optimization",
        "Security Best Practices",
        "Frontend Framework Comparison",
        "DevOps and Deployment",
        "Testing Strategies",
        "Algorithm Discussion",
        "Career Advice",
        "Project Planning",
        "Technical Documentation",
        "Code Debugging Session",
        "Software Design Patterns",
        "Technology Trends",
    ]

    sample_user_messages = [
        "Hello! I need help with this problem.",
        "Can you explain how this works?",
        "I'm having trouble understanding this concept.",
        "What's the best approach for this task?",
        "Could you review my code?",
        "I'm getting an error, can you help?",
        "What are your thoughts on this implementation?",
        "How would you solve this differently?",
        "Can you walk me through the process?",
        "I need some guidance on this project.",
    ]

    sample_assistant_messages = [
        "I'd be happy to help you with that! Let me break it down step by step.",
        "That's a great question. Here's how you can approach this problem.",
        "I can see the issue here. Let me explain what's happening.",
        "There are several ways to handle this. Here's what I recommend.",
        "Looking at your code, I can suggest some improvements.",
        "This error typically occurs when... Here's how to fix it.",
        "Your implementation looks good! Here are a few suggestions.",
        "I would approach this differently. Let me show you why.",
        "Sure! Let me walk you through this process.",
        "I can definitely guide you through this. Let's start with...",
    ]

    async with DatabaseManager() as session:
        # Get all users to assign conversations to
        from sqlalchemy import text

        users = await session.execute(
            text("SELECT id FROM users ORDER BY created_at LIMIT 4")
        )
        user_ids = [row[0] for row in users.fetchall()]

        if not user_ids:
            print("No users found! Please run seeding first.")
            return

        print(
            f"Found {len(user_ids)} users to create conversations for"
        )

        conversations_created = 0

        for i in range(20):
            # Pick a random user and topic
            user_id = random.choice(user_ids)
            topic = conversation_topics[i]

            # Create conversation
            conversation = Conversation(
                user_id=user_id,
                title=topic,
                description=f"Test conversation about {topic.lower()}",
                status=ConversationStatus.ACTIVE,
                llm_provider="openai",
                llm_model="gpt-4",
                temperature=0.7,
                max_tokens=2048,
                context_window=4096,
                memory_enabled=True,
                enable_retrieval=False,
                message_count=2,  # Will have 2 messages
                created_at=datetime.utcnow()
                - timedelta(days=random.randint(0, 30)),
                last_message_at=datetime.utcnow()
                - timedelta(hours=random.randint(1, 48)),
            )

            session.add(conversation)
            await session.flush()  # Get the conversation ID

            # Add user message
            user_message = Message(
                conversation_id=conversation.id,
                role=MessageRole.USER,
                content=random.choice(sample_user_messages),
                sequence_number=1,
                created_at=conversation.created_at,
            )
            session.add(user_message)

            # Add assistant message
            assistant_message = Message(
                conversation_id=conversation.id,
                role=MessageRole.ASSISTANT,
                content=random.choice(sample_assistant_messages),
                sequence_number=2,
                total_tokens=random.randint(50, 200),
                prompt_tokens=random.randint(20, 50),
                completion_tokens=random.randint(30, 150),
                model_used="gpt-4",
                provider_used="openai",
                created_at=conversation.created_at
                + timedelta(seconds=random.randint(1, 30)),
            )
            session.add(assistant_message)

            conversations_created += 1

        await session.commit()
        print(
            f"✅ Successfully created {conversations_created} test conversations!"
        )


if __name__ == "__main__":
    asyncio.run(add_test_conversations())
