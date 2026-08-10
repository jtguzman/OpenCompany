# Real-time Status WebSocket System

StatusBroadcaster, `/ws/status` endpoint, WebSocketContext, Android status broadcasting, message-type catalogue. Moved verbatim out of CLAUDE.md. See also status_broadcaster.md.

## Real-time Status WebSocket System

### Overview
The frontend and Python backend communicate via WebSocket for real-time status updates. This replaces API polling with push-based updates for Android connection status, node execution status, and variable changes.

### Architecture
```
React Frontend (WebSocketContext.tsx) <--WebSocket--> Python Backend (status_broadcaster.py)
         |                                                    |
         v                                                    v
   SquareNode.tsx                                   websocket_client.py
   (uses androidStatus)                             (broadcasts Android status)
```

### Backend Implementation

#### Status Broadcaster (`server/services/status_broadcaster.py`)
Central service for managing WebSocket connections and broadcasting status updates:

```python
class StatusBroadcaster:
    def __init__(self):
        self._connections: Set[WebSocket] = set()
        self._status: Dict[str, Any] = {
            "android": {"connected": False, "device_id": None, "connected_devices": [], "connection_type": None},
            "nodes": {},
            "variables": {},
            "workflow": {"executing": False, "current_node": None}
        }

    async def connect(self, websocket: WebSocket): ...
    async def disconnect(self, websocket: WebSocket): ...
    async def update_android_status(self, connected, device_id, connected_devices, connection_type): ...
    async def update_node_status(self, node_id, status, data): ...
    async def update_variable(self, name, value): ...
    async def update_workflow_status(self, executing, current_node, progress): ...
```

Key methods:
- `connect()` - Accepts WebSocket, adds to connection set, sends initial status
- `update_android_status()` - Updates Android status and broadcasts to all clients
- `update_node_status()` - Updates individual node status with data/output
- `update_variable()` - Updates single variable value
- `_broadcast()` - Sends message to all connected clients

#### WebSocket Router (`server/routers/websocket.py`)
FastAPI WebSocket endpoint:

```python
@router.websocket("/ws/status")
async def websocket_status_endpoint(websocket: WebSocket):
    broadcaster = get_status_broadcaster()
    await broadcaster.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            elif data.get("type") == "get_status":
                await websocket.send_json({"type": "full_status", "data": broadcaster.get_status()})
    except WebSocketDisconnect:
        await broadcaster.disconnect(websocket)
```

### Frontend Implementation

#### WebSocket Context (`client/src/contexts/WebSocketContext.tsx`)
React context providing WebSocket connection and status state:

```typescript
export interface AndroidStatus {
  connected: boolean;
  device_id: string | null;
  connected_devices: string[];
  connection_type: string | null;
}

export const WebSocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [androidStatus, setAndroidStatus] = useState<AndroidStatus>(defaultAndroidStatus);
  const [nodeStatuses, setNodeStatuses] = useState<Record<string, NodeStatus>>({});
  const [variables, setVariables] = useState<Record<string, any>>({});
  // WebSocket connection with auto-reconnect
};

// Hooks for consuming status
export const useWebSocket = (): WebSocketContextValue => { ... }
export const useAndroidStatus = (): AndroidStatus => { ... }
export const useNodeStatus = (nodeId: string): NodeStatus => { ... }
```

Features:
- Auto-connect on mount
- Auto-reconnect after 3 seconds on disconnect
- Ping every 30 seconds to keep connection alive
- Message type handlers for all status update types

#### Usage in Components (`client/src/components/SquareNode.tsx`)
```typescript
const { androidStatus } = useWebSocket();
// Android service nodes use 'paired' status (device must be paired to execute)
const isAndroidConnected = isAndroidNode && androidStatus.paired;
```

### Android Status Broadcasting
The Android relay client (`server/services/android/client.py`) broadcasts status changes via dedicated functions in `broadcaster.py`:

```python
# When device pairs successfully
await broadcast_connected(device_id, device_name)

# When device unpairs (relay may still be connected)
await broadcast_device_disconnected(
    relay_connected=self.is_connected(),
    qr_data=self.qr_data,
    session_token=self.session_token
)

# When relay WebSocket closes unexpectedly
await broadcast_relay_disconnected()
```

**Key distinction:**
- `broadcast_device_disconnected()` - Device unpaired, relay still connected (can re-pair via QR)
- `broadcast_relay_disconnected()` - Full disconnection, need to reconnect

### Real Device Detection
Fixed issue where Android status remained green after device disconnect:

**Problem**: Base name `android_system_services` remained in connected devices set after real device `android_system_services_1764708352672` left.

**Solution**: Added methods to distinguish real devices (with timestamp suffix) from base names:

```python
def _get_discovered_devices(self) -> list:
    """Get list of actual discovered devices (with timestamp suffix)."""
    discovered = []
    for device_id in self._connected_android_devices:
        parts = device_id.rsplit('_', 1)
        if len(parts) == 2 and parts[1].isdigit():
            discovered.append(device_id)
    return discovered

def has_real_android_devices(self) -> bool:
    """Check if there are any real (discovered) Android devices connected."""
    return len(self._get_discovered_devices()) > 0
```

Updated `client_left` and presence handlers use `has_real_android_devices()` instead of checking total device count.

### WebSocket Message Types

> Live count = `len(MESSAGE_HANDLERS) + len(get_ws_handlers())` (core dict in `server/routers/websocket.py` + plugin-registered handlers). The catalogue below is illustrative, not exhaustive or hand-maintained.

#### Request/Response Messages (Client -> Server -> Client)
| Category | Message Types |
|----------|--------------|
| **Status/Ping** | `ping`, `get_status`, `get_android_status`, `get_node_status`, `get_variable` |
| **Node Parameters** | `get_node_parameters`, `get_all_node_parameters`, `save_node_parameters`, `delete_node_parameters` |
| **Tool Schemas** | `get_tool_schema`, `save_tool_schema`, `delete_tool_schema`, `get_all_tool_schemas` |
| **Node Execution** | `execute_node`, `execute_workflow`, `cancel_execution`, `get_node_output`, `clear_node_output` |
| **Triggers/Events** | `cancel_event_wait`, `get_active_waiters` |
| **Dead Letter Queue** | `get_dlq_entries`, `get_dlq_entry`, `get_dlq_stats`, `replay_dlq_entry`, `remove_dlq_entry`, `purge_dlq` |
| **Deployment** | `deploy_workflow`, `cancel_deployment`, `get_deployment_status`, `get_workflow_lock`, `update_deployment_settings` |
| **AI Operations** | `execute_ai_node`, `get_ai_models` |
| **API Keys** | `validate_api_key`, `get_stored_api_key`, `save_api_key`, `delete_api_key` |
| **Claude OAuth** | `claude_oauth_login`, `claude_oauth_status` |
| **Twitter OAuth** | `twitter_oauth_login`, `twitter_oauth_status`, `twitter_logout` |
| **Google OAuth** | `google_oauth_login`, `google_oauth_status`, `google_logout` |
| **AI Proxy** | `test_ai_proxy` |
| **Android** | `get_android_devices`, `execute_android_action`, `android_relay_connect`, `android_relay_disconnect`, `android_relay_reconnect` |
| **Maps** | `validate_maps_key` |
| **Apify** | `validate_apify_key` |
| **WhatsApp** | `whatsapp_status`, `whatsapp_connected_phone`, `whatsapp_qr`, `whatsapp_send`, `whatsapp_start`, `whatsapp_restart`, `whatsapp_groups`, `whatsapp_group_info`, `whatsapp_chat_history`, `whatsapp_newsletters`, `whatsapp_rate_limit_get`, `whatsapp_rate_limit_set`, `whatsapp_rate_limit_stats`, `whatsapp_rate_limit_unpause`, `whatsapp_mark_read`, `whatsapp_typing`, `whatsapp_presence`, `whatsapp_stop`, `whatsapp_diagnostics` |
| **Telegram** | `telegram_connect`, `telegram_disconnect`, `telegram_status`, `telegram_send`, `telegram_reconnect`, `telegram_get_me`, `telegram_get_chat` |
| **Workflow Storage** | `save_workflow`, `get_workflow`, `get_all_workflows`, `delete_workflow` |
| **Chat Messages** | `send_chat_message`, `get_chat_messages`, `clear_chat_messages`, `save_chat_message`, `get_chat_sessions` |
| **Console/Terminal** | `get_console_logs`, `clear_console_logs`, `get_terminal_logs`, `clear_terminal_logs` |
| **User Skills** | `get_user_skills`, `get_user_skill`, `create_user_skill`, `update_user_skill`, `delete_user_skill` |
| **Built-in Skills** | `get_skill_content`, `save_skill_content`, `scan_skill_folder`, `list_skill_folders` |
| **Memory/Skill Reset** | `clear_memory`, `reset_skill` |
| **User Settings** | `get_user_settings`, `save_user_settings` |
| **Provider Defaults** | `get_provider_defaults`, `save_provider_defaults` |
| **Pricing** | `get_pricing_config`, `save_pricing_config` |
| **Usage/Compaction** | `get_api_usage_summary`, `get_compaction_stats`, `configure_compaction`, `get_provider_usage_summary` |
| **Agent Teams** | `create_team`, `get_team`, `get_team_status`, `dissolve_team`, `add_team_task`, `claim_team_task`, `complete_team_task`, `get_team_tasks`, `send_team_message`, `get_team_messages` |
| **Model Registry** | `get_model_constraints`, `refresh_model_registry` |

#### Broadcast Messages (Server -> All Clients)
| Message Type | Description |
|--------------|-------------|
| `android_status` | Android device connection update |
| `node_status` | Node execution status change |
| `node_output` | Node execution output data |
| `agent_progress` | CloudEvents v1.0 envelope (type=`com.opencompany.agent.progress`) — per-step agent-loop iteration count, drives the live "N / max" badge on AI Agent canvas nodes |
| `agent_capability` | CloudEvents v1.0 envelope (`com.opencompany.agent.(skill|tool).*`) — exact-agent capability lifecycle with deterministic Temporal IDs, `(source,id)` deduplication, sanitized data, and an optional exact target node |
| `deployment_snapshot` | CloudEvents v1.0 envelope (type=`workflow.deployment.snapshot`) — pushed once per WS connect from `broadcaster._send_deployment_snapshot`; lets the FE reconcile stale `deploymentStatus.isRunning=true` after a backend restart wiped `DeploymentManager._deployments`. Empty list is meaningful (forces reset). |
| `variable_update` | Single variable value change |
| `workflow_status` | Workflow execution progress |
| `api_key_status` | API key validation status |
| `node_parameters_updated` | Node parameters changed by another client |

#### Status Messages
| Message Type | Direction | Description |
|--------------|-----------|-------------|
| `initial_status` | Server -> Client | Full status on connect |
| `full_status` | Server -> Client | Full status response |
| `pong` | Server -> Client | Keep-alive response |
| `error` | Server -> Client | Error response with code and message |
