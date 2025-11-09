# Chat Streaming Refactor

## Overview
This document captures the changes required to deliver streaming chat responses across the ideation workflow. The refactor replaces the single-block assistant reply with server-sent events (SSE) so that participants can see model output as it is generated while preserving compatibility for non-stream clients.

## Backend (`backend/routes/chat.py`)
- Added support for detecting streaming-capable clients via the `Accept: text/event-stream` header or the `?stream=true` query flag.
- Persisted the user message before invoking the model to keep the database in sync when the stream begins.
- Introduced an SSE generator that yields `token`, `end`, and `error` payloads while buffering the accumulated assistant text for eventual storage.
- Preserved JSON responses for non-streaming requests and tightened error logging for unexpected failures.

### Stream Event Payloads
- `{"type": "token", "delta": "text"}` – incremental chunks to append in the UI.
- `{"type": "end", "content": "full message", "message_id": int, "timestamp": iso8601}` – emitted once the assistant reply is committed to the database.
- `{"type": "error", "error": "message"}` – emitted if the stream aborts; the connection closes immediately after.

## Frontend (`frontend/js/api.js`, `frontend/ideation.html`)
- Upgraded the API client to request SSE responses, parse event chunks, and surface deltas through an `onToken` callback while maintaining the legacy JSON path.
- Updated the ideation chat workflow to insert a placeholder assistant bubble, update it as tokens arrive, and stamp metadata when the stream completes.
- Added defensive handling for missing sessions and streaming failures so the participant still receives actionable feedback.

## Usage Notes
1. Clients expecting streaming should set the `Accept` header to `text/event-stream` when posting to `/api/chat`.
2. Non-stream clients continue to receive the prior JSON structure without modification.
3. Streaming consumers must handle the three event types above and treat connection closure without an `end` event as an error.

## Recommended Tests
- Post a chat message from the ideation UI and observe incremental assistant output.
- Terminate a request mid-stream to confirm UI recovery and server rollback.
- Trigger a reset/end-session flow to ensure streaming changes do not affect ancillary routes.
- Verify database records contain both the user and assistant messages after a completed stream.
