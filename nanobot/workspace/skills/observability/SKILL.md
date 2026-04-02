---
name: observability
description: Use observability MCP tools to investigate system health and errors
always: true
---

# Observability Skill

Use observability MCP tools to investigate system health, errors, and failures.

## Available Tools

- `logs_search` — Search logs using LogsQL query. Returns matching log entries.
- `logs_error_count` — Count errors for a service over a time window.
- `traces_list` — List recent traces for a service.
- `traces_get` — Fetch a specific trace by ID.

## Strategy

### When the user asks "What went wrong?" or "Check system health":
1. **Start with `logs_error_count`** to see if there are recent errors
   - Use a narrow time window like "10m" for recent issues
   - Focus on the LMS backend service: "Learning Management Service"
2. **Use `logs_search`** to inspect error details
   - Query: `_time:10m service.name:"Learning Management Service" severity:ERROR`
   - Look for the `trace_id` field in error logs
   - Note the error message and exception type
3. **If you find a trace_id, use `traces_get`** to inspect the full trace
   - This shows the complete request flow and where it failed
   - Identify which span failed and what operation was being performed
4. **Summarize findings as one coherent investigation**
   - Don't dump raw JSON
   - Explain what went wrong in plain language
   - Cite both log evidence AND trace evidence
   - Mention the affected service, root failing operation, and error type
   - Note any discrepancy between what logs show vs what HTTP response was returned
### When the user asks about errors or system health:

1. **Start with `logs_error_count`** to see if there are recent errors
   - Use a narrow time window like "10m" or "1h" for recent issues
   - Focus on the LMS backend service: "Learning Management Service"

2. **If errors exist, use `logs_search`** to inspect them
   - Query: `_time:10m service.name:"Learning Management Service" severity:ERROR`
   - Look for the `trace_id` field in error logs

3. **If you find a trace_id, use `traces_get`** to inspect the full trace
   - This shows the complete request flow and where it failed

4. **Summarize findings concisely**
   - Don't dump raw JSON
   - Explain what went wrong in plain language
   - Mention the affected service, error type, and timeframe

### When the user asks about traces:

1. Use `traces_list` to find recent traces for the service
2. Use `traces_get` to fetch details of a specific trace
3. Explain the span hierarchy and timing

### Example queries:

- **Count recent errors:** `logs_error_count(service="Learning Management Service", time_range="10m")`
- **Search error logs:** `logs_search(query='_time:10m service.name:"Learning Management Service" severity:ERROR')`
- **Get trace details:** `traces_get(trace_id="abc123...")`

### Response style:

- Lead with the answer: "Yes, there are X errors in the last 10 minutes" or "No errors found"
- If errors exist, summarize the root cause
- If you found a trace, explain what it shows
- Keep it brief — 2-4 sentences unless the user asks for more detail
