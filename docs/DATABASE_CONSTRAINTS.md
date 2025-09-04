# Database Model Constraints Reference

This document provides a comprehensive overview of all database constraints implemented across the Chatter application models.

## Overview

The database models implement **120 check constraints** across **19 models** to ensure data integrity, enforce business rules, and prevent invalid states. All constraints follow a consistent naming pattern: `check_<field>_<validation_type>`.

## Constraint Categories

### 1. Positive Value Constraints
Ensure numeric fields that represent counts, sizes, or limits are positive:
- `check_*_positive` - Values must be > 0
- `check_*_non_negative` - Values must be >= 0

### 2. Range Constraints
Validate values are within acceptable business ranges:
- `check_temperature_range` - 0.0 to 2.0 (LLM temperature)
- `check_top_p_range` - 0.0 to 1.0 (sampling parameter)
- `check_rating_range` - 0.0 to 5.0 (user ratings)
- `check_success_rate_range` - 0.0 to 1.0 (percentage values)

### 3. Non-Empty String Constraints
Ensure required text fields are not empty:
- `check_*_not_empty` - String fields cannot be empty ('')

### 4. Logical Relationship Constraints
Enforce business logic between related fields:
- `check_end_char_greater_than_start` - End position > start position
- `check_effective_dimensions_lte_base` - Reduced dimensions <= original dimensions
- `check_min_length_less_than_max` - Minimum < maximum length

## Model-by-Model Constraint Details

### User Model (5 constraints)
```sql
check_daily_message_limit_positive     -- daily_message_limit > 0
check_monthly_message_limit_positive   -- monthly_message_limit > 0  
check_max_file_size_positive          -- max_file_size_mb > 0
check_email_format                    -- Valid email regex pattern
check_username_format                 -- Valid username regex pattern
```

### Conversation Model (9 constraints)
```sql
check_temperature_range               -- temperature: 0.0-2.0
check_max_tokens_positive            -- max_tokens > 0
check_context_window_positive        -- context_window > 0
check_retrieval_limit_positive       -- retrieval_limit > 0
check_retrieval_score_threshold_range -- retrieval_score_threshold: 0.0-1.0
check_message_count_non_negative     -- message_count >= 0
check_total_tokens_non_negative      -- total_tokens >= 0
check_total_cost_non_negative        -- total_cost >= 0.0
check_title_not_empty                -- title != ''
```

### Message Model (8 constraints)
```sql
check_prompt_tokens_non_negative      -- prompt_tokens >= 0
check_completion_tokens_non_negative  -- completion_tokens >= 0
check_total_tokens_non_negative       -- total_tokens >= 0
check_response_time_non_negative      -- response_time_ms >= 0
check_cost_non_negative               -- cost >= 0.0
check_retry_count_non_negative        -- retry_count >= 0
check_sequence_number_non_negative    -- sequence_number >= 0
check_content_not_empty               -- content != ''
```

### Document Model (7 constraints)
```sql
check_file_size_positive              -- file_size > 0
check_chunk_size_positive             -- chunk_size > 0
check_chunk_overlap_non_negative      -- chunk_overlap >= 0
check_chunk_count_non_negative        -- chunk_count >= 0
check_version_positive                -- version > 0
check_view_count_non_negative         -- view_count >= 0
check_search_count_non_negative       -- search_count >= 0
```

### DocumentChunk Model (6 constraints)
```sql
check_chunk_index_non_negative        -- chunk_index >= 0
check_start_char_non_negative         -- start_char >= 0
check_end_char_positive               -- end_char > 0
check_end_char_greater_than_start     -- end_char > start_char
check_token_count_positive            -- token_count > 0
check_content_not_empty               -- content != ''
```

### Profile Model (11 constraints)
```sql
check_temperature_range               -- temperature: 0.0-2.0
check_top_p_range                     -- top_p: 0.0-1.0
check_top_k_positive                  -- top_k > 0
check_max_tokens_positive             -- max_tokens > 0
check_context_window_positive         -- context_window > 0
check_retrieval_limit_positive        -- retrieval_limit > 0
check_retrieval_score_threshold_range -- retrieval_score_threshold: 0.0-1.0
check_usage_count_non_negative        -- usage_count >= 0
check_total_tokens_used_non_negative  -- total_tokens_used >= 0
check_total_cost_non_negative         -- total_cost >= 0.0
check_name_not_empty                  -- name != ''
```

### Prompt Model (13 constraints)
```sql
check_max_length_positive             -- max_length > 0
check_min_length_non_negative         -- min_length >= 0
check_min_length_less_than_max        -- min_length < max_length
check_version_positive                -- version > 0
check_rating_range                    -- rating: 0.0-5.0
check_rating_count_non_negative       -- rating_count >= 0
check_usage_count_non_negative        -- usage_count >= 0
check_total_tokens_used_non_negative  -- total_tokens_used >= 0
check_total_cost_non_negative         -- total_cost >= 0.0
check_success_rate_range              -- success_rate: 0.0-1.0
check_avg_response_time_ms_positive   -- avg_response_time_ms > 0
check_content_not_empty               -- content != ''
check_name_not_empty                  -- name != ''
```

### Provider Model (2 constraints)
```sql
check_name_not_empty                  -- name != ''
check_display_name_not_empty          -- display_name != ''
```

### ModelDef Model (8 constraints)
```sql
check_max_tokens_positive             -- max_tokens > 0
check_context_length_positive         -- context_length > 0
check_dimensions_positive             -- dimensions > 0
check_chunk_size_positive             -- chunk_size > 0
check_max_batch_size_positive         -- max_batch_size > 0
check_name_not_empty                  -- name != ''
check_display_name_not_empty          -- display_name != ''
check_model_name_not_empty            -- model_name != ''
```

### EmbeddingSpace Model (6 constraints)
```sql
check_base_dimensions_positive        -- base_dimensions > 0
check_effective_dimensions_positive   -- effective_dimensions > 0
check_effective_dimensions_lte_base   -- effective_dimensions <= base_dimensions
check_name_not_empty                  -- name != ''
check_display_name_not_empty          -- display_name != ''
check_table_name_not_empty            -- table_name != ''
```

### Analytics Models (28 constraints total)

#### ConversationStats (11 constraints)
All message and token counts >= 0, cost >= 0.0

#### DocumentStats (6 constraints)  
All view, search, retrieval counts >= 0

#### PromptStats (6 constraints)
All usage and token counts >= 0, cost >= 0.0

#### ProfileStats (5 constraints)
All conversation and message counts >= 0, cost >= 0.0

### ToolServer Models (15 constraints total)

#### ToolServer (5 constraints)
Name validation, positive timeout and failure limits

#### ServerTool (5 constraints)
Name validation, non-negative call/error counts  

#### ToolUsage (2 constraints)
Name validation, non-negative response time

#### ToolPermission (3 constraints)
Positive rate limits, non-negative usage count

#### RoleToolAccess (2 constraints)
Positive default rate limits

## Testing

All constraints are validated through comprehensive test suites:
- `tests/test_database_model_integrity.py` - 18 test cases covering all models
- 100% pass rate ensuring all constraints are properly defined
- Tests verify constraint names, presence, and logical consistency

## Benefits

1. **Data Integrity**: Prevents invalid states at the database level
2. **Business Logic Enforcement**: Ensures values stay within business-acceptable ranges
3. **Early Error Detection**: Catches invalid data before it propagates through the system
4. **Clear Documentation**: Constraint names self-document business rules
5. **Database Performance**: Database-level validation is faster than application-level

## Maintenance

When adding new fields to models:
1. Consider if the field needs validation constraints
2. Follow the naming pattern: `check_<field>_<validation_type>`
3. Add corresponding test cases to verify the constraint
4. Update this documentation with new constraints

## Migration Notes

These constraints will be enforced during database migrations. Ensure existing data complies with the constraint rules before applying migrations with these constraints.