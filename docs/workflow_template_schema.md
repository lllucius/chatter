# Workflow Template Database Schema

This document describes the database schema for workflow templates and template specifications.

## Overview

The workflow template system uses a hybrid approach:
- **Built-in templates** remain in memory for performance and simplicity
- **Custom templates** are persisted in the database for durability and sharing
- **Template specs** store lightweight configuration data for template creation

## Tables

### workflow_templates

Stores custom workflow templates created by users.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(26) | PRIMARY KEY | ULID identifier |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Last update timestamp |
| owner_id | VARCHAR(26) | NOT NULL, FK(users.id) | Template owner |
| name | VARCHAR(255) | NOT NULL | Template name (unique per user) |
| description | TEXT | NOT NULL | Template description |
| workflow_type | ENUM | NOT NULL | Workflow type (plain, tools, rag, full) |
| category | ENUM | NOT NULL, DEFAULT 'custom' | Template category |
| default_params | JSON | NOT NULL, DEFAULT '{}' | Default workflow parameters |
| required_tools | JSON | NULL | Required tool names array |
| required_retrievers | JSON | NULL | Required retriever names array |
| base_template_id | VARCHAR(26) | NULL, FK(workflow_templates.id) | Parent template reference |
| is_builtin | BOOLEAN | NOT NULL, DEFAULT FALSE | Whether template is built-in |
| version | INTEGER | NOT NULL, DEFAULT 1 | Template version number |
| is_latest | BOOLEAN | NOT NULL, DEFAULT TRUE | Whether this is the latest version |
| changelog | TEXT | NULL | Version change log |
| is_public | BOOLEAN | NOT NULL, DEFAULT FALSE | Whether template is publicly visible |
| rating | FLOAT | NULL, CHECK (0.0 <= rating <= 5.0) | Average user rating |
| rating_count | INTEGER | NOT NULL, DEFAULT 0 | Number of ratings |
| usage_count | INTEGER | NOT NULL, DEFAULT 0 | Number of times used |
| success_rate | FLOAT | NULL, CHECK (0.0 <= success_rate <= 1.0) | Success rate percentage |
| avg_response_time_ms | INTEGER | NULL | Average response time |
| last_used_at | TIMESTAMP WITH TIME ZONE | NULL | Last usage timestamp |
| total_tokens_used | INTEGER | NOT NULL, DEFAULT 0 | Total tokens consumed |
| total_cost | FLOAT | NOT NULL, DEFAULT 0.0 | Total cost incurred |
| avg_tokens_per_use | FLOAT | NULL | Average tokens per usage |
| tags | JSON | NULL | Template tags array |
| extra_metadata | JSON | NULL | Additional metadata |
| config_hash | VARCHAR(64) | NOT NULL | Configuration hash for caching |
| estimated_complexity | INTEGER | NULL | Estimated template complexity |

#### Indexes
- `idx_workflow_templates_owner_id` on `owner_id`
- `idx_workflow_templates_name` on `name`
- `idx_workflow_templates_workflow_type` on `workflow_type`
- `idx_workflow_templates_category` on `category`
- `idx_workflow_templates_base_template_id` on `base_template_id`
- `idx_workflow_templates_is_builtin` on `is_builtin`
- `idx_workflow_templates_is_latest` on `is_latest`
- `idx_workflow_templates_is_public` on `is_public`
- `idx_workflow_templates_config_hash` on `config_hash`

### template_specs

Stores lightweight template specifications for workflow creation.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(26) | PRIMARY KEY | ULID identifier |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Last update timestamp |
| owner_id | VARCHAR(26) | NOT NULL, FK(users.id) | Spec owner |
| name | VARCHAR(255) | NOT NULL | Spec name |
| description | TEXT | NOT NULL | Spec description |
| workflow_type | ENUM | NOT NULL | Workflow type (plain, tools, rag, full) |
| default_params | JSON | NOT NULL, DEFAULT '{}' | Default parameters |
| required_tools | JSON | NULL | Required tool names array |
| required_retrievers | JSON | NULL | Required retriever names array |
| base_template_name | VARCHAR(255) | NULL | Base template name reference |
| usage_count | INTEGER | NOT NULL, DEFAULT 0 | Number of times used |
| last_used_at | TIMESTAMP WITH TIME ZONE | NULL | Last usage timestamp |
| tags | JSON | NULL | Spec tags array |
| extra_metadata | JSON | NULL | Additional metadata |

#### Indexes
- `idx_template_specs_owner_id` on `owner_id`
- `idx_template_specs_name` on `name`
- `idx_template_specs_workflow_type` on `workflow_type`
- `idx_template_specs_base_template_name` on `base_template_name`

## Enums

### WorkflowType
- `plain` - Basic conversation workflow
- `tools` - Workflow with tool integration
- `rag` - Retrieval-augmented generation workflow
- `full` - Complete workflow with tools and retrieval

### TemplateCategory
- `general` - General purpose templates
- `customer_support` - Customer service templates
- `programming` - Software development templates
- `research` - Research and analysis templates
- `data_analysis` - Data analysis templates
- `creative` - Creative writing templates
- `educational` - Learning and teaching templates
- `business` - Business process templates
- `custom` - User-defined custom templates

## Relationships

### workflow_templates
- **owner** → `users.id` (Many-to-One)
- **base_template** → `workflow_templates.id` (Self-referencing Many-to-One)
- **derived_templates** → `workflow_templates.base_template_id` (One-to-Many)

### template_specs
- **owner** → `users.id` (Many-to-One)

### users (updated)
- **workflow_templates** → `workflow_templates.owner_id` (One-to-Many)
- **template_specs** → `template_specs.owner_id` (One-to-Many)

## Usage Patterns

### Template Discovery
```sql
-- Get all public templates and user's private templates
SELECT * FROM workflow_templates 
WHERE is_public = TRUE OR owner_id = ?
ORDER BY usage_count DESC, rating DESC;
```

### Template Inheritance
```sql
-- Get template with its inheritance chain
WITH RECURSIVE template_chain AS (
  SELECT id, name, base_template_id, 0 as level
  FROM workflow_templates WHERE id = ?
  
  UNION ALL
  
  SELECT t.id, t.name, t.base_template_id, tc.level + 1
  FROM workflow_templates t
  JOIN template_chain tc ON t.id = tc.base_template_id
)
SELECT * FROM template_chain ORDER BY level;
```

### Popular Templates
```sql
-- Get most popular templates by category
SELECT category, name, usage_count, rating
FROM workflow_templates
WHERE is_public = TRUE
ORDER BY category, usage_count DESC
LIMIT 10;
```

## Migration Notes

The migration `001_workflow_templates.py` creates:
1. Enum types for `WorkflowType` and `TemplateCategory`
2. Both tables with all constraints and indexes
3. Proper foreign key relationships
4. Check constraints for data validation

To run the migration:
```bash
alembic upgrade head
```

To rollback:
```bash
alembic downgrade base
```

## Performance Considerations

1. **Hybrid Architecture**: Built-in templates cached in memory, custom templates in database
2. **Indexing**: Strategic indexes on frequently queried columns
3. **Pagination**: Use LIMIT/OFFSET for large result sets
4. **Caching**: Config hash enables efficient change detection
5. **Denormalization**: Usage statistics stored directly for performance

## Security Considerations

1. **Access Control**: Templates have owner-based access control
2. **Public Templates**: Separate flag for public visibility
3. **Input Validation**: Check constraints prevent invalid data
4. **SQL Injection**: Use parameterized queries through SQLAlchemy ORM
5. **Data Integrity**: Foreign key constraints maintain referential integrity