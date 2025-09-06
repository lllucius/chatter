# API Module Conversion Summary Table

This table provides a quick reference for the dependency injection conversion requirements for each API module in the chatter system.

## Conversion Overview

| Module | Current Pattern | Services Used | Complexity | Est. Hours | Priority |
|--------|----------------|---------------|------------|------------|----------|
| `ab_testing.py` | Direct Instantiation | ABTestManager | Medium | 4-6 | Medium |
| `agents.py` | Import Singleton | agent_manager | Low-Medium | 2-3 | Low |
| `analytics.py` | Direct Instantiation | AnalyticsService | Medium | 4-6 | Medium |
| `auth.py` | Direct Instantiation | AuthService | High | 8-12 | High |
| `chat.py` | Direct Instantiation | ChatService, LLMService, Resource Handlers | High | 10-15 | High |
| `data_management.py` | Import Singleton | data_manager | Low-Medium | 2-3 | Low |
| `dependencies.py` | Utilities Only | None | None | 0 | None |
| `documents.py` | Direct Instantiation | DocumentService | Medium-High | 6-8 | Medium |
| `events.py` | Import Singleton | sse_service | Low-Medium | 2-3 | Low |
| `health.py` | Direct DB Access | None | Low | 1 | Low |
| `jobs.py` | Import Singleton | job_queue | Low-Medium | 2-3 | Low |
| `model_registry.py` | Direct Instantiation | ModelRegistryService | Medium | 4-6 | Medium |
| `plugins.py` | Import Singleton | plugin_manager | Low-Medium | 2-3 | Low |
| `profiles.py` | Direct Instantiation | ProfileService | Medium | 4-6 | Medium |
| `prompts.py` | Direct Instantiation | PromptService | Medium | 4-6 | Medium |
| `resources.py` | Handler Classes | ChatService (injected) | Low | 1-2 | Low |
| `toolserver.py` | Direct Instantiation | ToolServerService, ToolAccessService | Medium | 4-6 | Medium |

## Pattern Distribution

### Direct Instantiation (67%)
**Modules:** ab_testing, analytics, auth, chat, documents, model_registry, profiles, prompts, toolserver

**Current Pattern:**
```python
async def get_service(session: AsyncSession = Depends(get_session_generator)) -> ServiceClass:
    return ServiceClass(session)
```

**After Conversion:**
```python  
async def get_service(session: AsyncSession = Depends(get_session_generator)) -> ServiceClass:
    from chatter.core.dependencies import get_service_name
    service = get_service_name()
    service.set_session(session)
    return service
```

### Import Singleton (22%)
**Modules:** agents, data_management, events, jobs, plugins

**Current Pattern:**
```python
async def get_service() -> ServiceClass:
    from chatter.services.module import service_instance
    return service_instance
```

**After Conversion:**
```python
async def get_service() -> ServiceClass:
    from chatter.core.dependencies import get_service_name
    return get_service_name()
```

### No Service Dependencies (11%)
**Modules:** dependencies, health, resources

These modules require minimal or no changes.

## Service Registration Requirements

### New Services to Register

```python
def register_api_services() -> None:
    """Register all API service lazy loaders."""
    
    # Direct instantiation services (need new lazy loaders)
    container.register_lazy_loader("ab_test_manager", _lazy_import_ab_test_manager)
    container.register_lazy_loader("analytics_service", _lazy_import_analytics_service) 
    container.register_lazy_loader("auth_service", _lazy_import_auth_service)
    container.register_lazy_loader("chat_service", _lazy_import_chat_service)
    container.register_lazy_loader("llm_service", _lazy_import_llm_service)
    container.register_lazy_loader("document_service", _lazy_import_document_service)
    container.register_lazy_loader("profile_service", _lazy_import_profile_service)
    container.register_lazy_loader("prompt_service", _lazy_import_prompt_service)
    container.register_lazy_loader("tool_server_service", _lazy_import_tool_server_service)
    container.register_lazy_loader("tool_access_service", _lazy_import_tool_access_service)
    
    # Singleton services (route through DI container)
    container.register_lazy_loader("agent_manager", _lazy_import_agent_manager)
    container.register_lazy_loader("data_manager", _lazy_import_data_manager)
    container.register_lazy_loader("sse_service", _lazy_import_sse_service)
    container.register_lazy_loader("job_queue", _lazy_import_job_queue) 
    container.register_lazy_loader("plugin_manager", _lazy_import_plugin_manager)
```

### Helper Functions to Add

```python
# Direct instantiation services
def get_ab_test_manager(): return container.get_lazy("ab_test_manager")
def get_analytics_service(): return container.get_lazy("analytics_service")
def get_auth_service(): return container.get_lazy("auth_service")
def get_chat_service(): return container.get_lazy("chat_service") 
def get_llm_service(): return container.get_lazy("llm_service")
def get_document_service(): return container.get_lazy("document_service")
def get_profile_service(): return container.get_lazy("profile_service")
def get_prompt_service(): return container.get_lazy("prompt_service")
def get_tool_server_service(): return container.get_lazy("tool_server_service")
def get_tool_access_service(): return container.get_lazy("tool_access_service")

# Singleton services  
def get_agent_manager(): return container.get_lazy("agent_manager")
def get_data_manager(): return container.get_lazy("data_manager")
def get_sse_service(): return container.get_lazy("sse_service")
def get_job_queue(): return container.get_lazy("job_queue")
def get_plugin_manager(): return container.get_lazy("plugin_manager")
```

## Recommended Phased Approach

### Phase 1: Core Services (High Priority)
**Services:** `auth.py`, `chat.py`
**Rationale:** Security-critical and most complex, highest impact
**Timeline:** 2-3 weeks
**Hours:** 18-27 hours

### Phase 2: Document & Analytics (Medium Priority)  
**Services:** `documents.py`, `analytics.py`
**Rationale:** Moderate complexity, significant usage
**Timeline:** 1-2 weeks  
**Hours:** 10-14 hours

### Phase 3: Registry & Management (Medium Priority)
**Services:** `model_registry.py`, `prompts.py`, `profiles.py`, `toolserver.py`
**Rationale:** CRUD-heavy services, moderate complexity
**Timeline:** 2-3 weeks
**Hours:** 16-24 hours

### Phase 4: Pre-instantiated Services (Low Priority)
**Services:** `agents.py`, `data_management.py`, `events.py`, `jobs.py`, `plugins.py`
**Rationale:** Already singletons, low complexity
**Timeline:** 1 week
**Hours:** 10-15 hours

### Phase 5: Remaining Services (Low Priority)
**Services:** `ab_testing.py`, remaining utilities
**Rationale:** Low complexity or minimal dependencies
**Timeline:** 3-5 days
**Hours:** 4-8 hours

## Key Benefits by Module

| Module | Primary Benefits |
|--------|-----------------|
| `auth.py` | Easier testing with auth mocks, centralized auth config |
| `chat.py` | Complex service orchestration, better testing of chat flows |
| `documents.py` | Document processing pipeline management |  
| `analytics.py` | Analytics service configuration flexibility |
| `model_registry.py` | Model provider abstraction and testing |
| `agents.py` | Agent system plugin architecture |
| `plugins.py` | Plugin dependency management |

## Key Challenges by Module

| Module | Primary Challenges |
|--------|-------------------|
| `auth.py` | Security implications, session management |
| `chat.py` | Complex service interactions, streaming responses |
| `documents.py` | File handling, processing pipelines |
| `analytics.py` | Database session scoping, aggregation queries |
| `model_registry.py` | Provider registration and configuration |
| All Services | Database session lifecycle management |

## Testing Impact

### Test Files Affected
Each API module conversion will require updating:
- Unit tests for the API endpoints
- Integration tests using the services  
- Mock configurations for testing
- Test fixtures and setup

### Estimated Testing Effort
- **Per module:** 2-4 hours additional testing effort
- **Total:** 36-72 hours across all modules
- **Integration testing:** 15-25 hours

## Dependencies Between Services

### Service Dependency Graph
```
auth_service (foundational)
├── Used by: ALL other API modules
├── No dependencies

chat_service 
├── Depends on: auth_service, llm_service
├── Used by: resources, analytics

document_service
├── Depends on: auth_service  
├── Used by: analytics, chat

model_registry
├── Used by: chat, profiles, analytics

analytics_service
├── Depends on: All other services (for analytics)
```

### Recommended Conversion Order
1. **auth_service** (foundation for all others)
2. **llm_service** (needed by chat)  
3. **chat_service** (high complexity, many dependents)
4. **document_service** (used by others)
5. **Remaining services** (parallel conversion possible)

---

*This summary table provides a quick reference for planning the API module dependency injection conversion project.*