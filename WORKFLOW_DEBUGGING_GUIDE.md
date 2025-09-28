# Workflow Execution Results and Debugging Guide

This guide explains how to get workflow execution results and use the debugging features in the Chatter workflow system.

## Getting Workflow Execution Results

### 1. Basic Execution Results

When you execute a workflow, you get a `WorkflowExecutionResponse` that includes:

```json
{
  "id": "execution-ulid-here",
  "definition_id": "workflow-definition-id",
  "owner_id": "user-id",
  "status": "completed|failed|running|pending",
  "started_at": "2024-01-01T12:00:00Z",
  "completed_at": "2024-01-01T12:00:30Z",
  "execution_time_ms": 30000,
  "input_data": {"message": "Hello, world!"},
  "output_data": {
    "response": "AI response here",
    "conversation_id": "conv-ulid",
    "metadata": {}
  },
  "error_message": null,
  "tokens_used": 150,
  "cost": 0.0025,
  "execution_log": [...],  // Detailed logs if debug mode enabled
  "debug_info": {...},     // Debug information if debug mode enabled
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:30Z"
}
```

### 2. API Endpoints for Execution Results

#### List All Executions for a Workflow
```http
GET /api/v1/workflows/definitions/{workflow_id}/executions
```

#### Get Detailed Execution Information
```http
GET /api/v1/workflows/definitions/{workflow_id}/executions/{execution_id}
```
Returns comprehensive execution details including debug information when available.

#### Get Execution Logs Only  
```http
GET /api/v1/workflows/definitions/{workflow_id}/executions/{execution_id}/logs?log_level=DEBUG&limit=1000
```
Returns structured execution logs with optional filtering by log level.

### 3. Using the Python SDK

```python
from chatter_sdk import WorkflowsApi, Configuration

# Configure the SDK
config = Configuration(host="http://localhost:8000")
workflows_api = WorkflowsApi(config)

# Execute a workflow with debug mode
execution_request = {
    "definition_id": "your-workflow-id",
    "input_data": {"message": "Hello, world!"},
    "debug_mode": True  # Enable debug mode
}

# Execute
result = workflows_api.execute_workflow_api_v1_workflows_definitions_workflow_id_execute(
    workflow_id="your-workflow-id",
    data=execution_request
)

# Get detailed execution information
detailed_result = workflows_api.get_workflow_execution_details_api_v1_workflows_definitions_workflow_id_executions_execution_id(
    workflow_id="your-workflow-id", 
    execution_id=result.id
)

# Get execution logs
logs = workflows_api.get_workflow_execution_logs_api_v1_workflows_definitions_workflow_id_executions_execution_id_logs(
    workflow_id="your-workflow-id",
    execution_id=result.id,
    log_level="DEBUG"
)
```

### 4. Using the TypeScript SDK

```typescript
import { WorkflowsApi } from '@chatter/sdk';

const workflowsApi = new WorkflowsApi();

// Execute with debug mode
const result = await workflowsApi.executeWorkflowApiV1WorkflowsDefinitionsWorkflowIdExecute(
  'your-workflow-id',
  {
    input_data: { message: 'Hello, world!' },
    debug_mode: true  // Enable debug mode
  }
);

// Get detailed execution information  
const detailedResult = await workflowsApi.getWorkflowExecutionDetailsApiV1WorkflowsDefinitionsWorkflowIdExecutionsExecutionId(
  'your-workflow-id',
  result.id
);

// Get execution logs
const logs = await workflowsApi.getWorkflowExecutionLogsApiV1WorkflowsDefinitionsWorkflowIdExecutionsExecutionIdLogs(
  'your-workflow-id', 
  result.id,
  'DEBUG',  // log level
  1000      // limit
);
```

## Debug Mode and Debugging Information

### 1. Enabling Debug Mode

Debug mode can be enabled in several ways:

#### Via API Request
```json
{
  "definition_id": "workflow-id",
  "input_data": {"message": "Hello"},
  "debug_mode": true
}
```

#### Via Frontend UI
In the workflow editor, when executing a workflow:
1. Click "Execute" on your workflow
2. In the execution dialog, toggle "Enable Debug Mode"
3. Click "Execute Workflow"

### 2. What Debug Information is Captured

When debug mode is enabled, the system captures:

#### Execution Logs
Structured log entries with:
- **Timestamp**: When the log entry was created
- **Level**: DEBUG, INFO, WARN, ERROR
- **Message**: Human-readable log message
- **Node ID**: Which workflow node generated the log (if applicable)
- **Step Name**: Name of the execution step
- **Data**: Additional structured data
- **Execution Time**: Time taken for the step

#### Debug Information Object
Comprehensive debugging data including:
- **Workflow Structure**: Nodes and edges in the executed workflow
- **Execution Path**: Actual path taken through the workflow nodes
- **Node Executions**: Details of each node's execution
- **Variable States**: Variable values throughout execution
- **Performance Metrics**: Timing and resource usage data
- **LLM Interactions**: API calls to language models
- **Tool Calls**: External tool executions

### 3. Example Debug Information

```json
{
  "debug_info": {
    "workflow_structure": {
      "nodes": [
        {"id": "start_1", "type": "start", "config": {}},
        {"id": "llm_1", "type": "llm", "config": {"model": "gpt-4"}}
      ],
      "edges": [
        {"source": "start_1", "target": "llm_1", "type": "regular"}
      ]
    },
    "execution_path": ["start_1", "llm_1"],
    "node_executions": [
      {
        "node_id": "llm_1",
        "node_type": "llm",
        "timestamp": "2024-01-01T12:00:15Z",
        "input_data": "Hello, world!",
        "output_data": "Hello! How can I help you today?",
        "execution_time_ms": 1500,
        "status": "completed"
      }
    ],
    "variable_states": {
      "user_message": {
        "value": "Hello, world!",
        "updated_at": "2024-01-01T12:00:10Z"
      }
    },
    "performance_metrics": {
      "total_execution_time_ms": 2500,
      "nodes_executed": 2,
      "llm_calls": 1,
      "tool_calls": 0
    },
    "llm_interactions": [
      {
        "timestamp": "2024-01-01T12:00:15Z",
        "provider": "openai",
        "model": "gpt-4",
        "input_tokens": 12,
        "output_tokens": 25,
        "cost": 0.0025,
        "response_time_ms": 1500,
        "status": "completed"
      }
    ],
    "tool_calls": []
  },
  "execution_log": [
    {
      "timestamp": "2024-01-01T12:00:10Z",
      "level": "INFO",
      "message": "Started workflow execution for definition workflow-123",
      "node_id": null,
      "step_name": null,
      "data": {"execution_id": "exec-456", "user_id": "user-789"},
      "execution_time_ms": null
    },
    {
      "timestamp": "2024-01-01T12:00:15Z",
      "level": "DEBUG",
      "message": "Executing LLM node with GPT-4",
      "node_id": "llm_1",
      "step_name": "llm_execution",
      "data": {"model": "gpt-4", "temperature": 0.7},
      "execution_time_ms": 1500
    }
  ]
}
```

## Where Debug Information is Stored

### 1. Database Storage

Debug information is stored in the `workflow_executions` table:
- **execution_log**: JSON array of structured log entries
- **output_data.debug_info**: Comprehensive debug information object

### 2. Application Logs

In addition to database storage, debug information is also written to application logs:

#### Log Configuration
Debug logging is controlled by environment variables:
- `LOG_LEVEL=DEBUG` - Enable debug-level logging
- `LOG_FILE=/path/to/logfile.log` - Log to file (optional)
- `LOG_JSON=true` - Use JSON log format (optional)

#### Log Locations
- **Console**: Default output to stdout
- **File**: If `LOG_FILE` is configured
- **Structured Logging**: Uses structlog for consistent formatting

### 3. Accessing Logs

#### Via API
Use the execution logs endpoint to retrieve structured logs programmatically.

#### Via Frontend
Use the debug dialog in the workflow executions tab to view logs interactively.

#### Via Application Logs
Check application logs for additional debugging context:
```bash
# If using file logging
tail -f /var/log/chatter/app.log | grep -E "(DEBUG|workflow)"

# If using JSON logging with jq
tail -f /var/log/chatter/app.log | jq 'select(.level=="DEBUG" and .workflow_id)'
```

## Typical Debugging Information You Should See

### 1. Workflow Execution Start
```
INFO: Started workflow execution for definition simple-chat-workflow
DEBUG: Executing workflow with 3 nodes and 2 edges
DEBUG: Workflow structure - nodes: [start_1, llm_1, end_1], edges: [(start_1, llm_1), (llm_1, end_1)]
```

### 2. Node Execution Details  
```
DEBUG: Executing LLM node with GPT-4
DEBUG: Node llm_1 input: "Hello, world!"
DEBUG: LLM API call completed in 1500ms - tokens: 12 input, 25 output
DEBUG: Node llm_1 output: "Hello! How can I help you today?"
```

### 3. Variable State Changes
```
DEBUG: Variable user_message updated: "Hello, world!"
DEBUG: Variable ai_response updated: "Hello! How can I help you today!"
```

### 4. Performance Metrics
```
INFO: Workflow execution completed in 2500ms
DEBUG: Performance summary - nodes: 2, LLM calls: 1, total cost: $0.0025
```

### 5. Error Information (if applicable)
```
ERROR: Workflow execution failed: LLM API timeout
DEBUG: Error occurred in node llm_1 after 30000ms
DEBUG: Retry attempt 1 of 3 failed
```

## Troubleshooting

### 1. No Debug Information Appearing

**Check debug mode is enabled:**
- Verify `debug_mode: true` in execution request
- Check frontend debug toggle is enabled

**Check log level configuration:**
- Ensure `LOG_LEVEL=DEBUG` or `LOG_LEVEL=INFO`
- Verify debug logging is not disabled in production

### 2. Missing Execution Logs

**Verify database permissions:**
- Check user can write to workflow_executions table
- Verify JSON columns are properly configured

**Check log retention:**
- Large logs may be truncated for performance
- Check if log size limits are configured

### 3. Debug Information Not Persisting  

**Check transaction handling:**
- Ensure database transactions are committed
- Verify no rollbacks are occurring

**Verify serialization:**
- Debug objects must be JSON serializable
- Check for circular references in debug data

## Performance Considerations

### 1. Debug Mode Overhead
- Debug mode adds ~10-20% execution overhead
- Use only during development/debugging
- Consider log level filtering for production

### 2. Storage Impact
- Debug logs can be large (10KB-1MB per execution)
- Implement log rotation/cleanup policies
- Consider separate debug storage for high-volume scenarios

### 3. Query Performance
- Add indexes on execution timestamps and status
- Use pagination for large execution lists
- Consider archiving old executions

This guide should help you understand how to get workflow execution results and effectively use the debugging features in the Chatter workflow system.