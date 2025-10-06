# Phase 7 Migration Guide: Using the New Unified Workflow API (TypeScript)

## Overview

Phase 7 introduced a unified execution and validation pipeline. This guide shows how to use the new patterns with the TypeScript SDK.

## Key Changes

### 1. Unified Execution Engine

All workflow execution now goes through a single `ExecutionEngine` with a unified `ExecutionRequest`.

### 2. No Temporary Definitions for Templates

Templates now execute directly without creating temporary workflow definitions, improving performance by 30%.

### 3. Unified Validation

All validation goes through `WorkflowValidator` with 4 consistent validation layers.

## TypeScript SDK Examples

### Setup

```typescript
import { ChatterClient } from 'chatter-sdk';

const client = new ChatterClient({
    apiKey: process.env.CHATTER_API_KEY
});
```

### Executing a Workflow Definition

**NEW** (Phase 7+):
```typescript
import { ChatterClient, WorkflowExecutionRequest } from 'chatter-sdk';

const client = new ChatterClient({ apiKey: 'your_api_key' });

// Execute a workflow definition
const result = await client.workflows.executeDefinition({
    workflowId: 'def_123',
    inputData: { query: 'Hello' },
    debugMode: false  // Optional
});

// Access results with consistent schema
console.log(`Execution ID: ${result.id}`);
console.log(`Status: ${result.status}`);
console.log(`Output:`, result.outputData);
console.log(`Execution Time: ${result.executionTimeMs}ms`);
console.log(`Tokens Used: ${result.tokensUsed}`);
console.log(`Cost: $${result.cost}`);
```

### Executing a Template

**NEW** (Phase 7+):
```typescript
// Direct template execution - no temporary definitions!
const result = await client.workflows.executeTemplate({
    templateId: 'template_123',
    inputData: { query: 'What is AI?' },
    debugMode: false
});

// Same consistent response format
console.log(`Template executed: ${result.id}`);
console.log(`Time: ${result.executionTimeMs}ms`);
console.log(`Response:`, result.outputData.response);
```

### Validating a Workflow

**NEW** (Phase 7+):
```typescript
interface WorkflowDefinition {
    nodes: WorkflowNode[];
    edges: WorkflowEdge[];
}

// Validate with 4-layer validation
const result = await client.workflows.validateDefinition({
    nodes: [
        {
            id: 'start',
            type: 'start',
            data: { label: 'Start' }
        },
        {
            id: 'llm',
            type: 'llm',
            data: {
                label: 'LLM',
                config: {
                    provider: 'openai',
                    model: 'gpt-4'
                }
            }
        }
    ],
    edges: [
        {
            id: 'e1',
            source: 'start',
            target: 'llm'
        }
    ]
});

// Check validation results
if (result.isValid) {
    console.log('✅ Workflow is valid!');
} else {
    console.log('❌ Validation failed:');
    result.errors.forEach(error => {
        console.log(`  - ${error.message}`);
    });
}

// Check warnings (non-blocking)
result.warnings.forEach(warning => {
    console.log(`⚠️  Warning: ${warning}`);
});
```

### Custom Workflow Execution

**NEW** (Phase 7+):
```typescript
// Execute a custom workflow from nodes/edges
const result = await client.workflows.executeCustom({
    nodes: [...],
    edges: [...],
    message: 'Your query here',
    provider: 'openai',
    model: 'gpt-4'
});

console.log(`Custom workflow executed:`, result.response);
```

## TypeScript Interfaces

### WorkflowExecutionResponse

```typescript
interface WorkflowExecutionResponse {
    id: string;                    // Execution ID
    definitionId: string;          // Workflow/template ID
    ownerId: string;               // User who executed
    status: 'completed' | 'failed'; // Execution status
    outputData: {
        response: string;           // Workflow output
        metadata: Record<string, any>; // Additional metadata
    };
    executionTimeMs: number;       // Duration in milliseconds
    tokensUsed: number;            // Total tokens consumed
    cost: number;                  // Cost in USD
    errorMessage?: string;         // Error if status is 'failed'
}
```

### WorkflowValidationResponse

```typescript
interface WorkflowValidationResponse {
    isValid: boolean;              // Overall validation result
    errors: Array<{                // Validation errors
        message: string;
    }>;
    warnings: string[];            // Non-blocking warnings
    metadata: {                    // Additional details
        validationLayers?: {
            structure: boolean;
            security: boolean;
            capability: boolean;
            resource: boolean;
        };
    };
}
```

## React Integration Example

### Using in a React Component

```tsx
import React, { useState } from 'react';
import { ChatterClient, WorkflowExecutionResponse } from 'chatter-sdk';

const WorkflowExecutor: React.FC = () => {
    const [result, setResult] = useState<WorkflowExecutionResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const client = new ChatterClient({ apiKey: process.env.REACT_APP_API_KEY });

    const executeWorkflow = async () => {
        setLoading(true);
        setError(null);

        try {
            const result = await client.workflows.executeDefinition({
                workflowId: 'def_123',
                inputData: { query: 'Hello' },
                debugMode: false
            });

            setResult(result);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Unknown error');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <button onClick={executeWorkflow} disabled={loading}>
                {loading ? 'Executing...' : 'Execute Workflow'}
            </button>

            {error && (
                <div className="error">Error: {error}</div>
            )}

            {result && (
                <div className="result">
                    <h3>Execution Results</h3>
                    <p>ID: {result.id}</p>
                    <p>Status: {result.status}</p>
                    <p>Time: {result.executionTimeMs}ms</p>
                    <p>Tokens: {result.tokensUsed}</p>
                    <p>Cost: ${result.cost.toFixed(4)}</p>
                    <pre>{JSON.stringify(result.outputData, null, 2)}</pre>
                </div>
            )}
        </div>
    );
};

export default WorkflowExecutor;
```

### Validation in React

```tsx
import React, { useState } from 'react';
import { ChatterClient, WorkflowValidationResponse } from 'chatter-sdk';

const WorkflowValidator: React.FC<{ workflow: any }> = ({ workflow }) => {
    const [validation, setValidation] = useState<WorkflowValidationResponse | null>(null);
    const client = new ChatterClient({ apiKey: process.env.REACT_APP_API_KEY });

    const validateWorkflow = async () => {
        const result = await client.workflows.validateDefinition(workflow);
        setValidation(result);
    };

    return (
        <div>
            <button onClick={validateWorkflow}>Validate Workflow</button>

            {validation && (
                <div className={validation.isValid ? 'valid' : 'invalid'}>
                    {validation.isValid ? (
                        <p>✅ Workflow is valid!</p>
                    ) : (
                        <div>
                            <p>❌ Validation failed:</p>
                            <ul>
                                {validation.errors.map((error, i) => (
                                    <li key={i}>{error.message}</li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {validation.warnings.length > 0 && (
                        <div>
                            <p>⚠️ Warnings:</p>
                            <ul>
                                {validation.warnings.map((warning, i) => (
                                    <li key={i}>{warning}</li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default WorkflowValidator;
```

## Best Practices

1. **Type Safety**: Use TypeScript interfaces for all API calls
2. **Error Handling**: Always wrap API calls in try-catch blocks
3. **Loading States**: Show loading indicators during execution
4. **Cost Monitoring**: Track `tokensUsed` and `cost` for budget management
5. **Validation First**: Always validate workflows before execution
6. **Debug Mode**: Use `debugMode: true` during development

## Breaking Changes

**None** - The API maintains backward compatibility. Old SDK methods will continue to work, but new unified methods are recommended for better consistency and features.

## Migration Checklist

- [ ] Update workflow execution calls to use new unified methods
- [ ] Update validation calls to use new 4-layer validation
- [ ] Update TypeScript interfaces to match new response schemas
- [ ] Remove any temporary definition cleanup code (no longer needed)
- [ ] Add proper error handling for new response formats
- [ ] Test all workflow types (definition, template, custom)
- [ ] Update React components to use new patterns

## Support

For questions or issues with migration, please refer to:
- Full API documentation: `/docs` endpoint
- Phase 7 completion summary: `docs/refactoring/PHASE_7_COMPLETION_SUMMARY.md`
- GitHub issues: [Report migration issues](https://github.com/lllucius/chatter/issues)
