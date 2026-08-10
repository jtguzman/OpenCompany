# Backend API Endpoints & Dev Scripts

Android routes, remote-Android WebSocket, webhook router, workspace router, workflow services, frontend-backend WebSocket, dev scripts, and the concurrently process-management fix. Moved verbatim out of CLAUDE.md.

### Python Backend (FastAPI)
- **Port**: `PYTHON_BACKEND_PORT` (defaults in `.env.template`)
- **Base URL**: `http://localhost:${PYTHON_BACKEND_PORT}`
- **Main File**: `server/main.py`

### API Endpoints
#### Android Services (`server/routers/android.py`)
- `GET /api/android/devices` - List connected Android devices via ADB with model and state info
- `POST /api/android/port-forward` - Setup ADB port forwarding for device communication
- `POST /api/android/{service_id}/{action}` - Execute Android service actions with parameters
- `GET /api/android/health` - Android service health check

#### Remote Android WebSocket
- **WebSocket**: Configurable via environment variable - Persistent WebSocket connection for remote Android devices
- **Health Check**: `{relay-url}/ws-health` - WebSocket proxy health status
- **Stats**: `{relay-url}/ws-stats` - Active connection statistics
- **Implementation**: `server/services/websocket_client.py` - Persistent WebSocket client with background tasks
  - Background message receiver continuously queues incoming messages
  - Keepalive loop sends ping every 25 seconds to maintain connection
  - Message queue (asyncio.Queue) for async message handling
  - Connection reuse across multiple API requests
  - Message filtering to skip non-response messages (presence, pong, ping)

#### Webhook Router (`server/routers/webhook.py`)
- `ANY /webhook/{path}` - Dynamic webhook endpoint for incoming HTTP requests (GET, POST, PUT, DELETE, PATCH)
- Dispatches `webhook_received` event via `broadcaster.send_custom_event()` to trigger waiting webhookTrigger nodes
- Returns immediate 200 OK response (responseNode mode planned for future)
- `GET /webhook/` - Webhook endpoint info and usage documentation

#### Workspace Router (`server/routers/workspace.py`)
- `GET /api/workspace/{workflow_id}/files/{path:path}` - Serve a file from a workflow's workspace.
  Range/seeking comes free from Starlette's `FileResponse` (`206` / `Content-Range` / `If-Range` /
  `416`) — do NOT wrap it in a `StreamingResponse`. Containment via `resolve_within`; 404 never 403
  (a distinct status would confirm what exists outside the workspace). **The `Content-Disposition`
  is not decided here** — it comes from `services.media.preview.serves_inline`, which the gallery
  listing also reads (via `preview_kind`) so the panel never offers a preview the route refuses to
  serve. Only `audio/ image/ video/` render inline; `NEVER_INLINE` is `{image/svg+xml, text/html,
  text/xml, application/xhtml+xml}`, because nodes can write arbitrary files into a workspace and
  inline markup from the app origin is stored XSS.
- **Listing is a WebSocket command, not an HTTP route.** `list_workspace_files` (owned by the
  gallery plugin) is the listing channel; these HTTP routes stay the *content* channel. The
  consumer is the parameter panel, which already holds an authenticated socket with request
  correlation — a second HTTP listing surface would mean a second auth path and a second error
  envelope for no gain.
- `POST /api/workspace/{workflow_id}/uploads` - Streamed multipart upload (the first in the repo on
  either side of the wire). Chunked read with a running total — `Content-Length` is never trusted —
  413 past `MEDIA_MAX_UPLOAD_BYTES`. Returns an `AudioRef`, which `coerce_file_param` accepts.
- **The URL carries `workflow_id`; the directory is named by `Workflow.slug`.** The router owns that
  lookup because it needs the database, while `services.media` stays synchronous. See
  [Media Transport](./media_transport.md).

#### Workflow Services (`server/services/workflow.py`)
- Node execution dispatches every registered plugin via the `BaseNode` registry (one self-contained folder per node under `server/nodes/<group>/`; live total via `len(services.node_registry.NODE_METADATA)` — do not hardcode it, and note a bare `__init__.py` glob overcounts by also matching the group packages)
- Parameter resolution and template variable substitution
- Result formatting and error handling

#### Frontend-Backend WebSocket (`server/routers/websocket.py`)
- **WebSocket Endpoint**: `/ws/status` - Real-time status updates between React and Python
- **REST Endpoint**: `GET /ws/info` - WebSocket connection info and current status
- **Message Types**:
  - `android_status` - Android device connection status updates
  - `node_status` - Individual node execution status
  - `node_output` - Node execution output data
  - `variable_update` - Single variable value change
  - `variables_update` - Batch variable updates
  - `workflow_status` - Workflow execution progress
  - `ping/pong` - Keep-alive messages

### Development Scripts
- `stop.bat` / `stop.sh` - Stops all development servers with duplicate Python process detection and verification
- `restart.bat` / `restart.sh` - Restarts all services cleanly
- `start.bat` / `start.sh` - Starts frontend and backend servers

### Concurrently Process Management Fix
**Problem**: Starting external services (WhatsApp, etc.) after the dev server would kill the frontend client.
- Root cause: `--kill-others` flag in concurrently npm script
- When uvicorn reloads (exit code 1), concurrently kills all processes including frontend

**Fix Applied**:
1. Removed `--kill-others` from `npm run dev` in package.json
2. Added named colored output: `-n client,python -c blue,green`
3. Added uvicorn reload controls: `--reload-dir .` and `--reload-exclude` patterns

**Result**: Frontend and backend run independently, uvicorn reloads don't cascade
