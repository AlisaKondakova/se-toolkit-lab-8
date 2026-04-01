import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import Optional
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

class ObservabilityServer:
    def __init__(self):
        self.victorialogs_url = "http://localhost:9428"
        self.victoriatraces_url = "http://localhost:10428"
        self.server = Server("observability-server")

    async def logs_search(self, query: str, hours_back: int = 1, limit: int = 50) -> str:
        """Search logs with LogsQL query"""
        time_filter = f"_time: now-{hours_back}h"
        full_query = f"{time_filter} AND ({query})" if query else time_filter
        
        async with aiohttp.ClientSession() as session:
            params = {
                "query": full_query,
                "limit": limit
            }
            async with session.get(f"{self.victorialogs_url}/select/logsql/query", params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return self._format_logs(data)
                return f"Error querying logs: {resp.status}"

    async def logs_error_count(self, hours_back: int = 1) -> str:
        """Count errors per service"""
        time_filter = f"_time: now-{hours_back}h"
        query = f"{time_filter} AND level:error"
        
        async with aiohttp.ClientSession() as session:
            params = {"query": query}
            async with session.get(f"{self.victorialogs_url}/select/logsql/query", params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    errors_by_service = {}
                    for log in data.get("results", []):
                        service = log.get("service", "unknown")
                        errors_by_service[service] = errors_by_service.get(service, 0) + 1
                    
                    result = f"Error counts in last {hours_back} hour(s):\n"
                    for service, count in errors_by_service.items():
                        result += f"  - {service}: {count} errors\n"
                    if not errors_by_service:
                        result += "  No errors found\n"
                    return result
                return f"Error querying logs: {resp.status}"

    async def traces_list(self, service: str, limit: int = 20) -> str:
        """List recent traces for a service"""
        async with aiohttp.ClientSession() as session:
            params = {"service": service, "limit": limit}
            async with session.get(f"{self.victoriatraces_url}/jaeger/api/traces", params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    traces = data.get("data", [])
                    if not traces:
                        return f"No traces found for service '{service}'"
                    
                    result = f"Recent traces for '{service}':\n"
                    for trace in traces[:10]:
                        trace_id = trace.get("traceID", "unknown")
                        spans = trace.get("spans", [])
                        duration = self._calculate_duration(spans)
                        error = self._has_error(spans)
                        status = "❌ ERROR" if error else "✅ OK"
                        result += f"  - {trace_id}: {status} - {duration}ms\n"
                    return result
                return f"Error querying traces: {resp.status}"

    async def traces_get(self, trace_id: str) -> str:
        """Fetch a specific trace by ID"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.victoriatraces_url}/jaeger/api/traces/{trace_id}") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    traces = data.get("data", [])
                    if not traces:
                        return f"Trace '{trace_id}' not found"
                    
                    trace = traces[0]
                    spans = trace.get("spans", [])
                    
                    result = f"Trace: {trace_id}\n"
                    result += "Span hierarchy:\n"
                    
                    span_map = {s["spanID"]: s for s in spans}
                    root_spans = [s for s in spans if not s.get("references")]
                    
                    for root in root_spans:
                        result += self._format_span_hierarchy(root, span_map, 0)
                    
                    if self._has_error(spans):
                        result += "\n⚠️ Error detected in trace!\n"
                        errors = [s for s in spans if self._span_has_error(s)]
                        for error_span in errors[:3]:
                            error_msg = "unknown error"
                            for tag in error_span.get("tags", []):
                                if tag.get("key") == "error.message":
                                    error_msg = tag.get("value")
                                    break
                            result += f"  - {error_span['operationName']}: {error_msg}\n"
                    
                    return result
                return f"Error fetching trace: {resp.status}"

    def _format_logs(self, data: dict) -> str:
        """Format log entries nicely"""
        results = data.get("results", [])
        if not results:
            return "No logs found"
        
        output = f"Found {len(results)} log entries:\n\n"
        for log in results[:20]:
            timestamp = log.get("_time", "unknown")
            level = log.get("level", "info").upper()
            service = log.get("service", "unknown")
            event = log.get("event", "")
            message = log.get("message", "")
            
            output += f"[{timestamp}] {level} [{service}] {event} - {message}\n"
            if log.get("error"):
                output += f"  Error: {log['error']}\n"
        return output

    def _calculate_duration(self, spans: list) -> int:
        """Calculate total trace duration in ms"""
        if not spans:
            return 0
        min_start = min(s.get("startTime", 0) for s in spans)
        max_end = max(s.get("startTime", 0) + s.get("duration", 0) for s in spans)
        return (max_end - min_start) // 1000

    def _has_error(self, spans: list) -> bool:
        """Check if any span has an error"""
        return any(self._span_has_error(s) for s in spans)

    def _span_has_error(self, span: dict) -> bool:
        """Check if a span has error tags"""
        tags = span.get("tags", [])
        for tag in tags:
            if tag.get("key") == "error" and tag.get("value") is True:
                return True
            if tag.get("key") == "error.message":
                return True
        return False

    def _format_span_hierarchy(self, span: dict, span_map: dict, indent: int) -> str:
        """Recursively format spans with indentation"""
        indent_str = "  " * indent
        operation = span.get("operationName", "unknown")
        duration = span.get("duration", 0) // 1000
        error = self._span_has_error(span)
        status = "❌" if error else "✓"
        
        output = f"{indent_str}{status} {operation} - {duration}ms\n"
        
        child_spans = [s for s in span_map.values() 
                      if any(ref.get("spanID") == span["spanID"] 
                            for ref in s.get("references", []))]
        
        for child in child_spans:
            output += self._format_span_hierarchy(child, span_map, indent + 1)
        
        return output

    async def setup_handlers(self):
        """Setup MCP tool handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            return [
                types.Tool(
                    name="logs_search",
                    description="Search logs with LogsQL query",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "LogsQL query (e.g., 'level:error AND service:backend')"},
                            "hours_back": {"type": "integer", "description": "Hours to look back", "default": 1},
                            "limit": {"type": "integer", "description": "Max results", "default": 50}
                        }
                    }
                ),
                types.Tool(
                    name="logs_error_count",
                    description="Count errors per service over time",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "hours_back": {"type": "integer", "description": "Hours to look back", "default": 1}
                        }
                    }
                ),
                types.Tool(
                    name="traces_list",
                    description="List recent traces for a service",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "service": {"type": "string", "description": "Service name (e.g., 'backend')"},
                            "limit": {"type": "integer", "description": "Max traces", "default": 20}
                        },
                        "required": ["service"]
                    }
                ),
                types.Tool(
                    name="traces_get",
                    description="Get detailed trace by ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "trace_id": {"type": "string", "description": "Trace ID"}
                        },
                        "required": ["trace_id"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: dict | None
        ) -> list[types.TextContent]:
            if name == "logs_search":
                query = arguments.get("query", "")
                hours_back = arguments.get("hours_back", 1)
                limit = arguments.get("limit", 50)
                result = await self.logs_search(query, hours_back, limit)
                return [types.TextContent(type="text", text=result)]
            
            elif name == "logs_error_count":
                hours_back = arguments.get("hours_back", 1)
                result = await self.logs_error_count(hours_back)
                return [types.TextContent(type="text", text=result)]
            
            elif name == "traces_list":
                service = arguments.get("service")
                limit = arguments.get("limit", 20)
                result = await self.traces_list(service, limit)
                return [types.TextContent(type="text", text=result)]
            
            elif name == "traces_get":
                trace_id = arguments.get("trace_id")
                result = await self.traces_get(trace_id)
                return [types.TextContent(type="text", text=result)]
            
            else:
                raise ValueError(f"Unknown tool: {name}")

    async def run(self):
        """Run the MCP server"""
        await self.setup_handlers()
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="observability-server",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

async def main():
    server = ObservabilityServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
