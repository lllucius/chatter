"""Table reference constants for foreign keys."""

# Table name constants to be used instead of string literals
class Tables:
    """Centralized table name references."""

    USERS = "users"
    CONVERSATIONS = "conversations"
    MESSAGES = "messages"
    DOCUMENTS = "documents"
    DOCUMENT_CHUNKS = "document_chunks"
    PROFILES = "profiles"
    PROMPTS = "prompts"
    TOOL_SERVERS = "tool_servers"
    SERVER_TOOLS = "server_tools"
    TOOL_USAGE = "tool_usage"
    CONVERSATION_STATS = "conversation_stats"
    DOCUMENT_STATS = "document_stats"
    PROMPT_STATS = "prompt_stats"
    PROFILE_STATS = "profile_stats"


class Columns:
    """Common column name references."""

    ID = "id"
    USER_ID = "user_id"
    CONVERSATION_ID = "conversation_id"
    DOCUMENT_ID = "document_id"
    PROFILE_ID = "profile_id"
    PROMPT_ID = "prompt_id"
    SERVER_ID = "server_id"
    TOOL_ID = "tool_id"


# Helper functions for creating foreign key references
def fk_user() -> str:
    """Foreign key reference to users.id."""
    return f"{Tables.USERS}.{Columns.ID}"


def fk_conversation() -> str:
    """Foreign key reference to conversations.id."""
    return f"{Tables.CONVERSATIONS}.{Columns.ID}"


def fk_document() -> str:
    """Foreign key reference to documents.id."""
    return f"{Tables.DOCUMENTS}.{Columns.ID}"


def fk_profile() -> str:
    """Foreign key reference to profiles.id."""
    return f"{Tables.PROFILES}.{Columns.ID}"


def fk_prompt() -> str:
    """Foreign key reference to prompts.id."""
    return f"{Tables.PROMPTS}.{Columns.ID}"


def fk_tool_server() -> str:
    """Foreign key reference to tool_servers.id."""
    return f"{Tables.TOOL_SERVERS}.{Columns.ID}"


def fk_server_tool() -> str:
    """Foreign key reference to server_tools.id."""
    return f"{Tables.SERVER_TOOLS}.{Columns.ID}"
