# Observability Skill

You have access to observability tools that let you query VictoriaLogs and VictoriaTraces.

## Available Tools

### Log Tools (VictoriaLogs)

- **logs_search(query, limit)**: Search logs using LogsQL
  - `query`: LogsQL query string (e.g., "level:error", "_stream:{service=\"backend\"}", "db_query AND error")
  - `limit`: Max entries to return (default 100)
  - Use this when user asks about errors, warnings, or specific events

- **logs_error_count(service, hours)**: Count errors per service
  - `service`: Service name or "*" for all (default "*")
  - `hours`: Time window in hours (default 1)
  - Use this when user asks "any errors?" or "how many errors?"

### Trace Tools (VictoriaTraces)

- **traces_list(service, limit)**: List recent traces for a service
  - `service`: Service name (default "backend")
  - `limit`: Max traces to return (default 10)
  - Use this to see recent request flows

- **traces_get(trace_id)**: Fetch full trace details
  - `trace_id`: The trace ID to fetch
  - Use this when you find a trace ID in logs and need full context

## When to Use

1. **User asks about errors**: "Any errors?", "What failed?", "Show me errors"
   - First call `logs_error_count(service="*", hours=1)` to get overview
   - Then call `logs_search(query="level:error", limit=10)` to see details

2. **User asks about a specific service**: "Is backend working?"
   - Call `logs_search(query="_stream:{service=\"backend\"} AND level:error", limit=10)`
   - Call `traces_list(service="backend", limit=5)` to see recent traces

3. **User asks about a request flow**: "What happened to my request?"
   - Call `traces_list(service="backend", limit=5)` to find recent traces
   - If you find a relevant trace, call `traces_get(trace_id=...)` for details

4. **Debugging a failure**: "Why did this fail?"
   - Search for errors: `logs_search(query="level:error", limit=20)`
   - Look for trace IDs in error logs
   - Fetch the trace: `traces_get(trace_id=...)`

## Response Style

- Summarize findings concisely — don't dump raw JSON
- Highlight the key issue (e.g., "Found 5 errors in backend in the last hour")
- If you find a trace ID, mention it and offer to fetch details
- If no errors found, say so clearly (e.g., "No errors found in the last hour")

## Example LogsQL Queries

- All errors: `level:error`
- Backend errors: `level:error AND service="backend"`
- Database errors: `db_query AND error`
- Specific time: `level:error AND _time > now()-1h`
- By stream: `_stream:{service="backend"}`
