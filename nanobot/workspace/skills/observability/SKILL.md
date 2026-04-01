# Observability Skill

This skill enables the agent to query logs and traces using MCP tools to investigate errors and system behavior.

## Capabilities

The agent can:
- Search logs with LogsQL queries
- Count errors per service over time windows
- List recent traces for services
- Fetch detailed trace hierarchies with timing information

## Usage Guidelines

### When to Use Observability

Use these tools when:
- User asks about errors, failures, or system health
- User mentions specific services (backend, auth, etc.)
- User asks "what happened" after a request
- User wants to investigate performance issues

### Tool Workflow

1. **Start with error count** - Use `logs_error_count` to see if there are errors
2. **Search logs** - Use `logs_search` to find specific error patterns
3. **Find trace IDs** - Extract trace IDs from log entries
4. **Fetch traces** - Use `traces_get` to see complete request flow
5. **List traces** - Use `traces_list` to see recent activity for a service

### Example Queries

**Check for recent errors:**

### Response Format

When reporting observability findings:
1. Start with summary (e.g., "Found 5 errors in the last hour")
2. List errors by service
3. Provide sample error messages
4. If trace IDs found, offer to fetch detailed traces
5. Keep responses concise - don't dump raw JSON

### LogsQL Query Patterns

Common queries:
- `level:error` - All errors
- `service:backend AND level:error` - Backend errors only
- `_time: now-1h AND level:error` - Errors in last hour
- `event:db_query AND error:*` - Database query errors
- `*connection*` - Any logs containing "connection"

## MCP Tools Available

- `logs_search` - Query logs with LogsQL
- `logs_error_count` - Count errors by service
- `traces_list` - List recent traces for a service
- `traces_get` - Fetch detailed trace by ID
