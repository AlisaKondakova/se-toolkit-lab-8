"""Stdio MCP server exposing VictoriaLogs and VictoriaTraces as tools."""

from __future__ import annotations

import asyncio
import json
import os
from collections.abc import Sequence
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from pydantic import BaseModel, Field

server = Server("observability")

# VictoriaLogs and VictoriaTraces URLs
VICTORIALOGS_URL = os.environ.get("VICTORIALOGS_URL", "http://victorialogs:9428")
VICTORIATRACES_URL = os.environ.get("VICTORIATRACES_URL", "http://victoriatraces:8428")


# ---------------------------------------------------------------------------
# Input models
# ---------------------------------------------------------------------------


class LogsSearchInput(BaseModel):
    query: str = Field(description="LogsQL query string")
    limit: int = Field(default=100, ge=1, le=1000)


class LogsErrorCountInput(BaseModel):
    service: str = Field(default="*")
    hours: int = Field(default=1, ge=1, le=24)


class TracesListInput(BaseModel):
    service: str = Field(default="backend")
    limit: int = Field(default=10, ge=1, le=100)


class TracesGetInput(BaseModel):
    trace_id: str = Field(description="Trace ID to fetch")


# ---------------------------------------------------------------------------
# Tool handlers
# ---------------------------------------------------------------------------


async def handle_logs_search(args: LogsSearchInput) -> list[TextContent]:
    """Search logs in VictoriaLogs using LogsQL."""
    url = f"{VICTORIALOGS_URL}/select/logsql/query"
    params = {"query": args.query, "limit": args.limit}
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            lines = resp.text.strip().split("\n")
            results = []
            for line in lines:
                if line.strip():
                    try:
                        results.append(json.loads(line))
                    except json.JSONDecodeError:
                        results.append({"raw": line})
            return [TextContent(type="text", text=json.dumps(results, indent=2))]
    except httpx.HTTPError as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}, indent=2))]


async def handle_logs_error_count(args: LogsErrorCountInput) -> list[TextContent]:
    """Count errors per service over a time window."""
    if args.service == "*":
        query = "level:error"
    else:
        query = f'level:error AND service="{args.service}"'
    
    url = f"{VICTORIALOGS_URL}/select/logsql/query"
    params = {"query": query, "limit": 10000}
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            lines = resp.text.strip().split("\n")
            count = len([l for l in lines if l.strip()])
            result = {"service": args.service, "hours": args.hours, "error_count": count}
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
    except httpx.HTTPError as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}, indent=2))]


async def handle_traces_list(args: TracesListInput) -> list[TextContent]:
    """List recent traces for a service from VictoriaTraces."""
    url = f"{VICTORIATRACES_URL}/jaeger/api/traces"
    params = {"service": args.service, "limit": args.limit}
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            traces = data.get("data", [])
            result = [
                {
                    "trace_id": t.get("traceID"),
                    "spans": len(t.get("spans", [])),
                    "start_time": t.get("startTime"),
                    "duration_us": t.get("duration"),
                }
                for t in traces
            ]
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
    except httpx.HTTPError as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}, indent=2))]


async def handle_traces_get(args: TracesGetInput) -> list[TextContent]:
    """Fetch full details of a specific trace by ID."""
    url = f"{VICTORIATRACES_URL}/jaeger/api/traces/{args.trace_id}"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            traces = data.get("data", [])
            if traces:
                return [TextContent(type="text", text=json.dumps(traces[0], indent=2))]
            return [TextContent(type="text", text=json.dumps({"error": "Trace not found"}))]
    except httpx.HTTPError as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}, indent=2))]


# ---------------------------------------------------------------------------
# Tool registration
# ---------------------------------------------------------------------------


_TOOLS = {
    "logs_search": (LogsSearchInput, handle_logs_search, Tool(
        name="logs_search",
        description="Search logs in VictoriaLogs using LogsQL. Use for finding errors, warnings, or specific events.",
        inputSchema=LogsSearchInput.model_json_schema(),
    )),
    "logs_error_count": (LogsErrorCountInput, handle_logs_error_count, Tool(
        name="logs_error_count",
        description="Count errors per service over a time window. Use for 'any errors?' type questions.",
        inputSchema=LogsErrorCountInput.model_json_schema(),
    )),
    "traces_list": (TracesListInput, handle_traces_list, Tool(
        name="traces_list",
        description="List recent traces for a service from VictoriaTraces. Shows trace summaries.",
        inputSchema=TracesListInput.model_json_schema(),
    )),
    "traces_get": (TracesGetInput, handle_traces_get, Tool(
        name="traces_get",
        description="Fetch full details of a specific trace by ID. Use to see complete span hierarchy.",
        inputSchema=TracesGetInput.model_json_schema(),
    )),
}


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [entry[2] for entry in _TOOLS.values()]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    entry = _TOOLS.get(name)
    if entry is None:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    model_cls, handler, _ = entry
    try:
        args = model_cls.model_validate(arguments or {})
        return await handler(args)
    except Exception as exc:
        return [TextContent(type="text", text=f"Error: {type(exc).__name__}: {exc}")]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


async def run() -> None:
    async with stdio_server() as (read_stream, write_stream):
        init_options = server.create_initialization_options()
        await server.run(read_stream, write_stream, init_options)


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
