# Backend Architecture Integration Map

## System Components Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    CHATTER BACKEND ARCHITECTURE                  │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Frontend   │  │   REST API   │  │  Workflows   │  │   Database   │
│   (React)    │◄─┤  Endpoints   │◄─┤  Execution   │◄─┤ (PostgreSQL) │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
                         │                   │
                         │                   │
                  ┌──────▼───────┐    ┌─────▼──────┐
                  │ Monitoring   │    │   Events   │
                  │   Service    │    │   System   │
                  └──────────────┘    └────────────┘
                         │                   │
                         └──────┬────────────┘
                                │
                        ┌───────▼────────┐
                        │   Analytics    │
                        │    Service     │
                        └────────────────┘
```

## Current Integration Status

### ✅ Working Integrations

```
┌─────────────┐
│   Auth API  │ ─────► MonitoringService ✅ (Security Events)
└─────────────┘        └─► EventSystem ✅ (Audit Logs)

┌─────────────┐
│  Streaming  │ ─────► MonitoringService ✅ (Workflow Metrics)
└─────────────┘

┌─────────────┐
│  Analytics  │ ─────► Database ✅ (Queries)
└─────────────┘
```

### ❌ Broken/Missing Integrations

```
┌──────────────────┐
│ Workflow         │
│ Execution        │ ──X──► MonitoringService ❌ (Should track)
│ Service          │ ──X──► EventSystem ❌ (Should emit events)
└──────────────────┘ ──X──► Analytics ❌ (Should push metrics)
        │
        │
        ▼
┌──────────────────┐
│ Message Records  │ ──X──► Token Stats ❌ (Fields empty)
│ (Database)       │
└──────────────────┘
```

## Data Flow: Token Statistics

### ❌ Current Broken Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         TOKEN DATA FLOW (BROKEN)                     │
└─────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │ LLM Provider │ (OpenAI, Anthropic, etc.)
    └──────┬───────┘
           │
           │ Returns: {
           │   content: "...",
           │   usage_metadata: {
           │     prompt_tokens: 150,
           │     completion_tokens: 200,
           │     total_tokens: 350
           │   }
           │ }
           ▼
    ┌──────────────┐
    │  LLM Service │ ✅ Extracts usage_metadata
    └──────┬───────┘    (in some code paths)
           │
           │ (Direct workflows use LLM service ✅)
           │ (LangGraph workflows bypass this ❌)
           ▼
    ┌──────────────┐
    │  ModelNode   │ ❌❌❌ ROOT CAUSE ❌❌❌
    │  .execute()  │ 
    └──────┬───────┘ Receives response with usage_metadata
           │         but only returns {"messages": [response]}
           │         DROPS the usage_metadata completely!
           ▼
    ┌──────────────┐
    │  LangGraph   │ ❌ Gets result without token data
    │ run_workflow │
    └──────┬───────┘ result = { "messages": [...] }
           │         No tokens_used key!
           ▼
    ┌──────────────┐
    │  Workflow    │ ❌ result.get("tokens_used", 0) → 0
    │  Execution   │
    └──────┬───────┘ Calls: tokens_used=result.get("tokens_used", 0)
           │
           ▼
    ┌──────────────┐
    │   Message    │ ❌ Created without token fields
    │   Creation   │
    └──────┬───────┘ Message(
           │           prompt_tokens=None,  ❌
           │           completion_tokens=None,  ❌
           │           cost=None  ❌
           │         )
           ▼
    ┌──────────────┐
    │   Database   │ ❌ Stored with NULL token fields
    └──────────────┘
```

### ✅ Expected Correct Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                      TOKEN DATA FLOW (SHOULD BE)                     │
└─────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │ LLM Provider │
    └──────┬───────┘
           │ Returns usage_metadata
           ▼
    ┌──────────────┐
    │  ModelNode   │ ✅ FIX: Extract usage_metadata
    │  .execute()  │
    └──────┬───────┘ return {
           │           "messages": [response],
           │           "usage_metadata": {
           │             prompt_tokens: 150,
           │             completion_tokens: 200
           │           }
           │         }
           ▼
    ┌──────────────┐
    │  LangGraph   │ ✅ FIX: Aggregate tokens from nodes
    │ run_workflow │
    └──────┬───────┘ result = {
           │           "messages": [...],
           │           "tokens_used": 350,
           │           "cost": 0.0052
           │         }
           ▼
    ┌──────────────┐
    │  Workflow    │ ✅ Has token data!
    │  Execution   │
    └──────┬───────┘ tokens = result["tokens_used"]
           │         cost = result["cost"]
           ▼
    ┌──────────────┐
    │   Message    │ ✅ Created WITH token fields
    │   Creation   │
    └──────┬───────┘ Message(
           │           prompt_tokens=150,  ✅
           │           completion_tokens=200,  ✅
           │           cost=0.0052  ✅
           │         )
           ▼
    ┌──────────────┐
    │   Database   │ ✅ Stored with complete data
    └──────────────┘
```

## Integration Points: Monitoring Service

### ❌ Current (Not Integrated)

```
┌────────────────────────────────────────────────────────────┐
│              WORKFLOW EXECUTION (Current)                   │
└────────────────────────────────────────────────────────────┘

execute_chat_workflow()
    │
    ├─► Get/Create Conversation
    │
    ├─► Execute Workflow
    │   └─► (Uses PerformanceMonitor for debug logs only)
    │
    ├─► Save Message
    │
    └─► Return

                    MonitoringService ← (not called)
                    WorkflowMetrics ← (not created)
```

### ✅ Should Be

```
┌────────────────────────────────────────────────────────────┐
│          WORKFLOW EXECUTION (Should Be)                     │
└────────────────────────────────────────────────────────────┘

execute_chat_workflow()
    │
    ├─► monitoring = get_monitoring_service()  ✅
    │   workflow_id = monitoring.start_workflow_tracking(
    │       user_id, conversation_id, provider, model
    │   )
    │
    ├─► Execute Workflow
    │   │
    │   ├─► On tool call:
    │   │   monitoring.update_workflow_metrics(
    │   │       workflow_id, tool_calls=1
    │   │   )
    │   │
    │   └─► On LLM response:
    │       monitoring.update_workflow_metrics(
    │           workflow_id, 
    │           token_usage={provider: tokens}
    │       )
    │
    ├─► Save Message
    │
    ├─► metrics = monitoring.finish_workflow_tracking(
    │       workflow_id,
    │       user_satisfaction=None
    │   )
    │
    └─► Return

                    MonitoringService ✅ (fully integrated)
                    WorkflowMetrics ✅ (tracked & stored)
```

## Integration Points: Event System

### ❌ Current (Not Emitting)

```
┌────────────────────────────────────────────────────────────┐
│              WORKFLOW LIFECYCLE (Current)                   │
└────────────────────────────────────────────────────────────┘

Start ──────────► [no event]  ❌
    │
Progress ───────► [no event]  ❌
    │
Tool Call ──────► [no event]  ❌
    │
Complete ───────► [no event]  ❌
    │
Error ──────────► [no event]  ❌
```

### ✅ Should Be

```
┌────────────────────────────────────────────────────────────┐
│          WORKFLOW LIFECYCLE (Should Be)                     │
└────────────────────────────────────────────────────────────┘

Start ─────────► emit_event(
                   category=WORKFLOW,
                   type="workflow_started"
                 )  ✅
    │
Progress ──────► emit_event(
                   category=WORKFLOW,
                   type="model_response"
                 )  ✅
    │
Tool Call ─────► emit_event(
                   category=WORKFLOW,
                   type="tool_called"
                 )  ✅
    │
Complete ──────► emit_event(
                   category=WORKFLOW,
                   type="workflow_completed",
                   data={tokens, cost, time}
                 )  ✅
    │
Error ─────────► emit_event(
                   category=WORKFLOW,
                   type="workflow_failed",
                   priority=HIGH
                 )  ✅
```

## Database Schema Utilization

### Message Model Fields

```sql
-- ✅ DEFINED in schema but ❌ NOT POPULATED

CREATE TABLE messages (
    id VARCHAR(26) PRIMARY KEY,
    conversation_id VARCHAR(26) NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    
    -- ❌ These fields exist but are always NULL!
    prompt_tokens INTEGER,           -- ❌ NULL
    completion_tokens INTEGER,       -- ❌ NULL  
    total_tokens INTEGER,            -- ❌ NULL
    cost FLOAT,                      -- ❌ NULL
    provider_used VARCHAR(50),       -- ❌ NULL
    response_time_ms INTEGER,        -- ❌ NULL
    
    extra_metadata JSONB
);
```

### Conversation Model Fields

```sql
-- ✅ DEFINED in schema but ❌ NOT AUTO-UPDATED

CREATE TABLE conversations (
    id VARCHAR(26) PRIMARY KEY,
    user_id VARCHAR(26) NOT NULL,
    title VARCHAR(255) NOT NULL,
    
    -- ❌ These aggregates become stale!
    message_count INTEGER DEFAULT 0,      -- ❌ Not auto-incremented
    total_tokens INTEGER DEFAULT 0,       -- ❌ Not auto-summed
    total_cost FLOAT DEFAULT 0.0,         -- ❌ Not auto-summed
    
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

## Component Dependency Graph

```
┌──────────────────────────────────────────────────────────────┐
│                  COMPONENT DEPENDENCIES                       │
└──────────────────────────────────────────────────────────────┘

API Endpoints
    │
    ▼
WorkflowExecutionService ──┬──► Should use ──► MonitoringService ❌
    │                      │                        │
    │                      ├──► Should use ──► EventSystem ❌
    │                      │                        │
    │                      └──► Should use ──► Analytics ❌
    ▼
LangGraph Manager ─────────┬──► Uses ──────────► WorkflowNodes
    │                      │                           │
    │                      │                           ▼
    │                      └─────────────────► ModelNode ❌
    │                                         (drops tokens)
    ▼
Result (missing tokens) ❌
    │
    ▼
Message Creation
    │
    ▼
Database (incomplete data) ❌
```

## Quick Reference: Integration Checklist

### For Each Workflow Execution, Should Have:

- [ ] MonitoringService.start_workflow_tracking() called
- [ ] WorkflowMetrics tracking active
- [ ] Event emitted: workflow_started  
- [ ] Token usage extracted from LLM response
- [ ] MonitoringService.update_workflow_metrics() on progress
- [ ] Event emitted per major step
- [ ] Token stats saved to Message record
- [ ] Conversation aggregates updated
- [ ] MonitoringService.finish_workflow_tracking() called
- [ ] Event emitted: workflow_completed
- [ ] Analytics notified of completion

### Current Status:

- [x] None of the above ❌

---

**Conclusion**: All the infrastructure exists, but workflow execution doesn't use it!
