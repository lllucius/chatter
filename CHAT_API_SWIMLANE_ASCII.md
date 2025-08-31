# 🏊 Chat API Flow - ASCII Swimlane Chart

```
    CLIENT          API LAYER         SERVICE LAYER       CORE LAYER          EXTERNAL SERVICES
      |                |                   |                  |                        |
      |                |                   |                  |                        |
      | POST /chat     |                   |                  |                        |
      |--------------->|                   |                  |                        |
      |                |                   |                  |                        |
      |                | Auth Middleware   |                  |                        |
      |                |<----------------->|                  |                        |
      |                |                   |                  |                        |
      |                | Rate Limit Check  |                  |                        |
      |                |<-------+          |                  |                        |
      |                |        |          |                  |                        |
      |                | Validation        |                  |                        |
      |                |<-------+          |                  |                        |
      |                |                   |                  |                        |
      |                | get_chat_service()|                  |                        |
      |                |------------------>|                  |                        |
      |                |                   |                  |                        |
      |                |                   | get_conversation()|                       |
      |                |                   |------------------>|                       |
      |                |                   |                  |                        |
      |                |                   |                  | Database Query         |
      |                |                   |                  |----------------------->|
      |                |                   |                  |<-----------------------|
      |                |                   |<------------------|                       |
      |                |                   |                  |                        |
      |    STREAMING   |                   | add_message()    |                        |
      |    RESPONSE?   |                   |------------------>|                       |
      |                |                   |                  |                        |
      |                |                   |                  | Persist User Message   |
      |                |                   |                  |----------------------->|
      |                |                   |                  |<-----------------------|
      |                |                   |<------------------|                       |
      |                |                   |                  |                        |
      |       YES      |                   |                  |                        |
      |    +-----------|                   |                  |                        |
      |    |           |                   |                  |                        |
      |    |           |                   | chat_streaming() |                        |
      |    |           |                   |------------------>|                       |
      |    |           |                   |                  |                        |
      |    |           |                   |                  | _resolve_provider()    |
      |    |           |                   |                  |----------------------->|
      |    |           |                   |                  |<-----------------------|
      |    |           |                   |                  |                        |
      |    |           |                   |                  | convert_to_messages()  |
      |    |           |                   |                  |----+                   |
      |    |           |                   |                  |<---+                   |
      |    |           |                   |                  |                        |
      |    |           |                   |                  | LLMService.generate()  |
      |    |           |                   |                  |----------------------->|
      |    |           |                   |                  |                        | OpenAI/Anthropic
      |    |           |                   |                  |                        |------------->
      |    |           |                   |                  |                        |<-------------
      |    |           |                   |                  |<-----------------------|
      |    |           |                   |<------------------|                       |
      |    |           |                   |                  |                        |
      |    |           | StreamingResponse |                  |                        |
      |    |           |<------------------|                  |                        |
      |    |           |                   |                  |                        |
      |    | SSE Stream |                  |                  |                        |
      |<---+-----------| text/event-stream |                  |                        |
      |    |           |                   |                  |                        |
      |    |           |                   | persist_response()|                       |
      |    |           |                   |------------------>|                       |
      |    |           |                   |                  |                        |
      |    |           |                   |                  | Save Assistant Message |
      |    |           |                   |                  |----------------------->|
      |    |           |                   |                  |<-----------------------|
      |    |           |                   |<------------------|                       |
      |    |           |                   |                  |                        |
      |    | [DONE]     |                  |                  |                        |
      |<---+-----------| 
      |                |                   |                  |                        |
      |        NO      |                   |                  |                        |
      |    +-----------|                   |                  |                        |
      |    |           |                   |                  |                        |
      |    |           |                   | chat_with_workflow()                      |
      |    |           |                   |------------------>|                       |
      |    |           |                   |                  |                        |
      |    |           |                   |                  | WorkflowValidator()    |
      |    |           |                   |                  |----+                   |
      |    |           |                   |                  |<---+                   |
      |    |           |                   |                  |                        |
      |    |           |                   |                  | workflow_cache.get()   |
      |    |           |                   |                  |----+                   |
      |    |           |                   |                  |<---+                   |
      |    |           |                   |                  |                        |
      |    |           |                   |                  | create_langgraph_workflow()
      |    |           |                   |                  |----------------------->|
      |    |           |                   |                  |                        | LangGraph
      |    |           |                   |                  |                        |---------->
      |    |           |                   |                  |                        |<----------
      |    |           |                   |                  |<-----------------------|
      |    |           |                   |                  |                        |
      |    |           |                   |                  | run_workflow()         |
      |    |           |                   |                  |----------------------->|
      |    |           |                   |                  |                        | Vector Store
      |    |           |                   |                  |                        |----------->
      |    |           |                   |                  |                        |<-----------
      |    |           |                   |                  |                        | 
      |    |           |                   |                  |                        | MCP Tools
      |    |           |                   |                  |                        |---------->
      |    |           |                   |                  |                        |<----------
      |    |           |                   |                  |<-----------------------|
      |    |           |                   |<------------------|                       |
      |    |           |                   |                  |                        |
      |    |           | ChatResponse(JSON)|                  |                        |
      |    |           |<------------------|                  |                        |
      |    |           |                   |                  |                        |
      |    | JSON       |                  |                  |                        |
      |<---+-----------| application/json |                  |                        |
      |                |                   |                  |                        |

Legend:
------
CLIENT:           Frontend application, curl, Postman, etc.
API LAYER:        FastAPI routers, middleware, authentication
SERVICE LAYER:    ChatService, LLMService, business logic coordination  
CORE LAYER:       LangGraph workflows, vector operations, database models
EXTERNAL SERVICES: OpenAI, Anthropic, PostgreSQL, Vector stores, MCP tools

Flow Types:
----------
Streaming:    Real-time token-by-token response via Server-Sent Events (SSE)
Non-streaming: Single JSON response after complete processing
Workflows:    plain (basic LLM), rag (retrieval), tools (function calling), full (rag+tools)

Key Components:
--------------
- Authentication & Rate Limiting at API boundary
- Service layer orchestration with proper error handling  
- Core workflow engine with caching and validation
- External service integration with fallback handling
- Database persistence throughout the flow
```