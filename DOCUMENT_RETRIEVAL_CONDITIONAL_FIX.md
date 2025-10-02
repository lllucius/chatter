# Document Retrieval Conditional Fix

## Problem Statement

In the Chat page and all workflow executions, if the Document Retrieval toggle is off or if it's on and no documents are selected, the workflow still searches the document vectors. This is inefficient and incorrect behavior.

## Root Cause

The code was checking only `chat_request.enable_retrieval` to determine whether to create a retriever and perform vector searches. This meant that even when no documents were selected (`document_ids` is `None` or empty list), the system would still attempt to create a retriever and search all documents.

## Solution

Modified the conditional logic in all workflow execution paths to check **both** conditions:
1. `chat_request.enable_retrieval` is `True`
2. `chat_request.document_ids` is not `None` and not empty

### Changed Code Locations

All changes were made in `chatter/services/workflow_execution.py`:

1. **Line 403** - `_execute_with_universal_template` method
2. **Line 783** - `_execute_with_dynamic_workflow` method  
3. **Line 1186** - `_execute_streaming_with_universal_template` method
4. **Line 1578** - `_execute_streaming_with_dynamic_workflow` method

### Before

```python
if chat_request.enable_retrieval:
    try:
        from chatter.core.vector_store import get_vector_store_retriever
        
        retriever = await get_vector_store_retriever(
            user_id=user_id,
            document_ids=chat_request.document_ids,
        )
        logger.info("Loaded retriever from vector store", ...)
    except Exception as e:
        logger.warning(f"Could not load retriever from vector store: {e}")
        retriever = None
```

### After

```python
if chat_request.enable_retrieval and chat_request.document_ids:
    try:
        from chatter.core.vector_store import get_vector_store_retriever
        
        retriever = await get_vector_store_retriever(
            user_id=user_id,
            document_ids=chat_request.document_ids,
        )
        logger.info("Loaded retriever from vector store", ...)
    except Exception as e:
        logger.warning(f"Could not load retriever from vector store: {e}")
        retriever = None
elif chat_request.enable_retrieval and not chat_request.document_ids:
    logger.info(
        "Document retrieval is enabled but no documents selected, skipping retrieval"
    )
```

## Benefits

1. **Performance**: No unnecessary vector searches when no documents are selected
2. **Correctness**: System behavior now matches user expectations and UI state
3. **Clarity**: Added informational logging when retrieval is skipped
4. **Consistency**: All workflow execution paths (dynamic, universal template, streaming) now have the same logic

## Test Coverage

Added comprehensive test suite in `tests/test_document_retrieval_conditional.py` covering:

1. **test_retrieval_skipped_when_no_document_ids**: Validates that retrieval is skipped when `enable_retrieval=True` but `document_ids` is `None` or empty list
2. **test_retrieval_enabled_with_document_ids**: Validates that retrieval is enabled when both `enable_retrieval=True` and `document_ids` contains values
3. **test_retrieval_disabled**: Validates that retrieval is disabled when `enable_retrieval=False` regardless of `document_ids` value

All tests pass successfully.

## Workflow Execution Paths Covered

- ✅ Universal template execution (non-streaming)
- ✅ Dynamic workflow execution (non-streaming)
- ✅ Universal template streaming execution
- ✅ Dynamic workflow streaming execution

## Implementation Details

The fix uses Python's truthiness checking where:
- `None` evaluates to `False`
- Empty list `[]` evaluates to `False`
- Non-empty list `["doc1"]` evaluates to `True`

This means `if chat_request.enable_retrieval and chat_request.document_ids:` will only pass when:
- `enable_retrieval` is `True` AND
- `document_ids` is not `None` AND  
- `document_ids` is not an empty list

## No Breaking Changes

This is a pure bug fix with no breaking changes:
- The API schema remains unchanged
- Existing behavior when documents ARE selected remains the same
- Only changes behavior for the problematic case (retrieval enabled but no documents selected)
