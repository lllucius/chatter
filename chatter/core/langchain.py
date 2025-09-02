"""LangChain integration and orchestration."""

from typing import Any

from langchain_community.callbacks import get_openai_callback
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnablePassthrough

from chatter.config import settings
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class LangChainOrchestrator:
    """Central orchestrator for LangChain operations."""

    def __init__(self) -> None:
        """Initialize the orchestrator."""
        self.setup_tracing()

    def setup_tracing(self) -> None:
        """Setup LangSmith tracing if enabled."""
        if settings.langchain_tracing_v2:
            import os

            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            if settings.langchain_api_key:
                os.environ["LANGCHAIN_API_KEY"] = (
                    settings.langchain_api_key
                )
            if settings.langchain_project:
                os.environ["LANGCHAIN_PROJECT"] = (
                    settings.langchain_project
                )
            if settings.langchain_endpoint:
                os.environ["LANGCHAIN_ENDPOINT"] = (
                    settings.langchain_endpoint
                )
            logger.info(
                "LangSmith tracing enabled",
                project=settings.langchain_project,
            )

    def create_chat_chain(
        self,
        llm: BaseChatModel,
        system_message: str | None = None,
        include_history: bool = True,
    ) -> Runnable:
        """Create a basic chat chain with optional system message and history."""
        messages = []

        if system_message:
            messages.append(("system", system_message))

        if include_history:
            messages.append(("placeholder", "{chat_history}"))

        messages.append(("human", "{input}"))

        prompt = ChatPromptTemplate.from_messages(messages)
        chain = prompt | llm | StrOutputParser()

        return chain

    def create_rag_chain(
        self,
        llm: BaseChatModel,
        retriever: Any,
        system_message: str | None = None,
    ) -> Runnable:
        """Create a RAG (Retrieval-Augmented Generation) chain."""
        if not system_message:
            system_message = (
                "You are an assistant for question-answering tasks. "
                "Use the following pieces of retrieved context to answer "
                "the question. If you don't know the answer, say that you "
                "don't know. Use three sentences maximum and keep the "
                "answer concise.\n\n{context}"
            )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_message),
                ("human", "{input}"),
            ]
        )

        def format_docs(docs: list[Any]) -> str:
            """Format retrieved documents for RAG context."""
            return "\n\n".join(doc.page_content for doc in docs)

        rag_chain = (
            {
                "context": retriever | format_docs,
                "input": RunnablePassthrough(),
            }
            | prompt
            | llm
            | StrOutputParser()
        )

        return rag_chain

    def create_conversational_rag_chain(
        self,
        llm: BaseChatModel,
        retriever: Any,
        system_message: str | None = None,
    ) -> Runnable:
        """Create a conversational RAG chain with chat history."""
        if not system_message:
            system_message = (
                "Given a chat history and the latest user question "
                "which might reference context in the chat history, "
                "formulate a standalone question which can be understood "
                "without the chat history. Do NOT answer the question, "
                "just reformulate it if needed and otherwise return it as is."
            )

        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_message),
                ("placeholder", "{chat_history}"),
                ("human", "{input}"),
            ]
        )

        contextualize_q_chain = (
            contextualize_q_prompt | llm | StrOutputParser()
        )

        qa_system_prompt = (
            "You are an assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer "
            "the question. If you don't know the answer, say that you "
            "don't know. Use three sentences maximum and keep the "
            "answer concise.\n\n{context}"
        )

        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", qa_system_prompt),
                ("placeholder", "{chat_history}"),
                ("human", "{input}"),
            ]
        )

        def format_docs(docs: list[Any]) -> str:
            """Format retrieved documents for context."""
            return "\n\n".join(doc.page_content for doc in docs)

        def contextualized_question(input: dict[str, Any]) -> Any:
            """Generate contextualized question from chat history."""
            if input.get("chat_history"):
                return contextualize_q_chain
            else:
                return input["input"]

        rag_chain = (
            RunnablePassthrough.assign(
                context=contextualized_question
                | retriever
                | format_docs
            )
            | qa_prompt
            | llm
            | StrOutputParser()
        )

        return rag_chain

    async def run_chain_with_callback(
        self,
        chain: Runnable,
        inputs: dict[str, Any],
        provider_name: str = "unknown",
    ) -> dict[str, Any]:
        """Run a chain with callback tracking for token usage."""
        result = {"response": "", "usage": {}}

        try:
            if provider_name.lower() == "openai":
                with get_openai_callback() as cb:
                    response = await chain.ainvoke(inputs)
                    result["response"] = response
                    result["usage"] = {
                        "total_tokens": cb.total_tokens,
                        "prompt_tokens": cb.prompt_tokens,
                        "completion_tokens": cb.completion_tokens,
                        "total_cost": cb.total_cost,
                    }
            else:
                response = await chain.ainvoke(inputs)
                result["response"] = response
                result["usage"] = {"provider": provider_name}

        except Exception as e:
            logger.error(
                "Chain execution failed",
                error=str(e),
                provider=provider_name,
            )
            raise

        return result

    def convert_messages_to_langchain(
        self, messages: list[dict[str, Any]]
    ) -> list[BaseMessage]:
        """Convert API messages to LangChain message format."""
        langchain_messages = []

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                langchain_messages.append(
                    SystemMessage(content=content)
                )
            elif role == "assistant":
                langchain_messages.append(AIMessage(content=content))
            else:  # user or any other role
                langchain_messages.append(HumanMessage(content=content))

        return langchain_messages

    def format_chat_history(
        self, messages: list[BaseMessage]
    ) -> list[BaseMessage]:
        """Format chat history for use in prompts."""
        # Filter out system messages from history
        return [
            msg
            for msg in messages
            if not isinstance(msg, SystemMessage)
        ]


# Global orchestrator instance
orchestrator = LangChainOrchestrator()
