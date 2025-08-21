# Chatter CLI Management Commands

This document describes the comprehensive CLI management interface for the Chatter platform.

## Overview

The Chatter CLI now provides full management capabilities for all aspects of the platform:

- **Profiles** - LLM profile management
- **Conversations** - Chat conversation management  
- **Documents** - Document upload and search
- **Authentication** - User and API key management
- **Analytics** - Platform metrics and usage stats
- **Prompts** - Prompt template management (requires API implementation)

## Authentication

Most management commands require authentication. You can authenticate in several ways:

### 1. Login Command
```bash
chatter auth login --email user@example.com
# Will prompt for password and save token to .env file
```

### 2. Environment Variable
```bash
export CHATTER_ACCESS_TOKEN=your_token_here
```

### 3. .env File
```
CHATTER_ACCESS_TOKEN=your_token_here
CHATTER_BASE_URL=http://localhost:8000
```

## Command Reference

### Profiles Management

List all LLM profiles:
```bash
chatter profiles list
chatter profiles list --provider openai --limit 10
chatter profiles list --type custom --public
```

Show profile details:
```bash
chatter profiles show <profile_id>
```

Create new profile:
```bash
# Interactive mode
chatter profiles create --interactive

# Command line mode
chatter profiles create \
  --name "Technical Assistant" \
  --description "Specialized for code help" \
  --provider openai \
  --model gpt-4 \
  --temperature 0.3 \
  --max-tokens 2048 \
  --system-prompt "You are a helpful technical assistant"
```

Delete profile:
```bash
chatter profiles delete <profile_id>
chatter profiles delete <profile_id> --force  # Skip confirmation
```

### Conversations Management

List conversations:
```bash
chatter conversations list
chatter conversations list --limit 50 --offset 100
```

Show conversation details:
```bash
chatter conversations show <conversation_id>
chatter conversations show <conversation_id> --no-messages  # Without message content
chatter conversations show <conversation_id> --limit 5      # Show last 5 messages
```

Export conversations:
```bash
chatter conversations export <conversation_id>
chatter conversations export <conversation_id> --format json --output backup.json
chatter conversations export <conversation_id> --format md --output conversation.md
chatter conversations export <conversation_id> --format txt
```

Delete conversations:
```bash
chatter conversations delete <conversation_id>
chatter conversations delete <conversation_id> --force
```

### Documents Management

List documents:
```bash
chatter documents list
chatter documents list --type pdf --limit 20
```

Upload documents:
```bash
chatter documents upload /path/to/document.pdf
chatter documents upload /path/to/file.txt \
  --title "Important Document" \
  --description "User manual for XYZ" \
  --tags "manual,help,documentation"
```

Show document details:
```bash
chatter documents show <document_id>
```

Search documents:
```bash
chatter documents search "machine learning algorithms"
chatter documents search "installation guide" --limit 5 --threshold 0.8
```

Delete documents:
```bash
chatter documents delete <document_id>
chatter documents delete <document_id> --force
```

### Authentication Management

User registration:
```bash
chatter auth register --email user@example.com --name "John Doe"
```

Login:
```bash
chatter auth login --email user@example.com
chatter auth login --email user@example.com --password mypass --no-save
```

Show current user:
```bash
chatter auth whoami
```

Logout:
```bash
chatter auth logout
```

API key management:
```bash
# Create API key
chatter auth create-api-key --name "Production API" --expires 365

# List API keys
chatter auth list-api-keys

# Delete API key
chatter auth delete-api-key <key_id>
```

### Analytics

Dashboard overview:
```bash
chatter analytics dashboard
```

Usage metrics:
```bash
chatter analytics usage
chatter analytics usage --days 30  # Last 30 days
```

Performance metrics:
```bash
chatter analytics performance
```

### Prompts Management

**Note:** ✅ Prompts API is now fully implemented and functional!

List prompts:
```bash
chatter prompts list
chatter prompts list --category technical --limit 10
chatter prompts list --type template --public
```

Create prompts:
```bash
# Interactive mode
chatter prompts create --interactive

# Command line mode
chatter prompts create \
  --name "Code Review" \
  --content "Review this code for: {criteria}. Code: {code}" \
  --description "Technical code review prompt" \
  --category technical \
  --tags "code,review,quality"
```

Show prompt details:
```bash
chatter prompts show <prompt_id>
```

Test prompts:
```bash
chatter prompts test <prompt_id> --variables '{"criteria": "security", "code": "def login(user, pass): ..."}'
chatter prompts test <prompt_id> --validate-only
```

Clone prompts:
```bash
chatter prompts clone <prompt_id> --name "My Code Review" --description "Customized version"
```

Delete prompts:
```bash
chatter prompts delete <prompt_id>
chatter prompts delete <prompt_id> --force  # Skip confirmation
```

## Configuration

### Environment Variables

- `CHATTER_ACCESS_TOKEN` - Authentication token
- `CHATTER_BASE_URL` - API base URL (default: http://localhost:8000)

### Configuration Commands

Show current configuration:
```bash
chatter config show
chatter config show database  # Show specific section
```

Test configuration:
```bash
chatter config test
```

## Error Handling

The CLI provides comprehensive error handling:

- **Authentication errors** - Clear messages about login requirements
- **Network errors** - Helpful hints about server status
- **API errors** - Detailed error messages from the server
- **Validation errors** - Input validation with helpful suggestions

## Interactive Features

Many commands support interactive modes:

```bash
chatter profiles create --interactive
# Prompts for all required fields with helpful defaults

chatter auth register
# Prompts for password securely without command line exposure
```

## Output Formats

The CLI uses rich console output with:
- **Tables** for listing data
- **Panels** for detailed information
- **Progress indicators** for long operations
- **Color coding** for different types of information

## Examples

### Complete Workflow Example

```bash
# 1. Register and login
chatter auth register --email admin@example.com
chatter auth login --email admin@example.com

# 2. Create a custom profile
chatter profiles create \
  --name "Research Assistant" \
  --provider openai \
  --model gpt-4 \
  --temperature 0.2 \
  --system-prompt "You are a research assistant specializing in academic papers"

# 3. Upload some documents
chatter documents upload research_paper.pdf \
  --title "AI Research Paper" \
  --tags "ai,research,paper"

# 4. View analytics
chatter analytics dashboard
chatter analytics usage --days 7

# 5. Export conversation data
chatter conversations list
chatter conversations export <conv_id> --format md --output research_chat.md
```

### Bulk Operations

```bash
# List and process multiple items
for doc_id in $(chatter documents list --limit 100 | grep "processing" | awk '{print $1}'); do
  chatter documents show $doc_id
done
```

## Integration with SDK

The CLI commands use the same API endpoints as the Python SDK, ensuring consistency. You can use both interchangeably:

```python
# Python SDK
from chatter_sdk import ChatterClient
client = ChatterClient(access_token="your_token")
profiles = await client.profiles.list()
```

```bash
# CLI equivalent
chatter profiles list
```

## Troubleshooting

### Common Issues

1. **Module not found errors**
   ```bash
   pip install typer rich httpx  # Install dependencies
   ```

2. **Authentication errors**
   ```bash
   chatter auth login --email your@email.com
   ```

3. **Connection errors**
   ```bash
   chatter health check  # Verify server is running
   ```

4. **API endpoint not found**
   - Some features require newer API versions
   - Check server version: `chatter version`

### Debug Mode

Set environment variable for verbose output:
```bash
export CHATTER_DEBUG=true
chatter profiles list
```

## Contributing

To add new CLI commands:

1. Create new command group in `chatter/cli.py`
2. Use the `APIClient` class for HTTP requests
3. Follow existing patterns for error handling
4. Add comprehensive help text and examples
5. Test with both success and error scenarios

Example pattern:
```python
@app.command("new-feature")
def new_feature_command():
    """Help text for the command."""
    async def _impl():
        api_client = get_api_client()
        try:
            response = await api_client.request("GET", "/new-endpoint")
            # Process response and display results
        finally:
            await api_client.close()
    
    asyncio.run(_impl())
```