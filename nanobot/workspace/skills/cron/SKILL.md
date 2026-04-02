---
name: cron
description: Manage scheduled jobs and periodic tasks
always: true
---

# Cron Skill

Use the built-in `cron` tool to create, list, and remove scheduled jobs.

## Available Tools

- `cron_create` — Create a new scheduled job
- `cron_list` — List all scheduled jobs
- `cron_remove` — Remove a scheduled job

## When to Use

When the user asks for a **recurring** or **periodic** task:
- "Create a health check that runs every 2 minutes"
- "Schedule a daily report"
- "Run this every hour"

Use `cron_create` with:
- `schedule`: cron expression (e.g., "*/2 * * * *" for every 2 minutes)
- `message`: what the job should do
- `chat_id`: the chat session where results should be posted

## Cron Expressions

- `*/2 * * * *` — Every 2 minutes
- `*/15 * * * *` — Every 15 minutes
- `0 * * * *` — Every hour at minute 0
- `0 0 * * *` — Every day at midnight
- `0 9 * * 1-5` — Every weekday at 9 AM

## Example Flow

**User:** "Create a health check for this chat that runs every 2 minutes"

**You:**
1. Call `cron_create` with:
   - schedule: "*/2 * * * *"
   - message: "Check for backend errors in the last 2 minutes and post a summary"
   - chat_id: [current chat session ID]

2. Confirm: "Created health check job running every 2 minutes"

**User:** "List scheduled jobs"

**You:**
1. Call `cron_list`
2. Display results in a table format

**User:** "Remove the health check job"

**You:**
1. Call `cron_remove` with the job ID
2. Confirm removal

## Important Notes

- Jobs are tied to the chat session they were created in
- If the chat session ends, jobs for that session stop running
- Use short intervals (2 minutes) only for testing
- For production, use 15+ minute intervals
