# Android Services Guide

Service node authoring, relay client, connection-vs-pairing two-state model, real device detection. Moved verbatim out of CLAUDE.md.

## Android Services Development Guide

### Architecture
Android services use a factory pattern with `createAndroidServiceNode()` for consistent node structure:
- **SquareNode Component**: Visual representation with configuration status indicators
- **Dynamic Actions**: Load available actions from backend via `loadOptionsMethod`
- **ADB Integration**: All services communicate with Android devices via ADB commands
- **Parameter System**: Flexible JSON parameters for service-specific configuration

### Adding New Android Services

**Wave 11+**: Android service nodes are authored as backend plugins
under `server/nodes/android/<service>.py`. Each plugin subclasses the
shared `AndroidServiceBase` (see `server/nodes/android/_base.py`), which
handles ADB dispatch via `SERVICE_ID_MAP`. See the
[Android Services Development Guide](./plugin_system.md#android).

Adding a new Android service:

1. **Create the plugin** at `server/nodes/android/<service_name>.py`
   subclassing `AndroidServiceBase` — the base handles `service_id`
   routing, argument translation, and broadcast status updates.
2. **Register the service id** in `SERVICE_ID_MAP` on
   `server/nodes/android/_base.py` (camelCase node type → snake_case
   service id).
3. **Implement the execution path** in the plugin's `execute` method;
   shared ADB infrastructure lives in `AndroidService`.

### Key Files
- **Shared base**: `server/nodes/android/_base.py` — `AndroidServiceBase`, `SERVICE_ID_MAP`, `execute_android_service_tool`
- **Backend Router**: `server/routers/android.py` - API endpoints for Android operations
- **Workflow Handler**: `server/services/workflow.py` - Execution logic for all nodes
- **Execution Service**: `src/services/executionService.ts` - Routes Android nodes to Python backend

### Requirements
- **Device Connection**: Configure Android connection via Credentials Modal (Android panel)
- **Permissions**: Android app must have necessary permissions for services

### Android Device Connection
Android device connection is configured via the **Credentials Modal** (Android panel), not via workflow nodes.

**Connection Types:**
1. **Remote Relay** (recommended): Connect to Android device via relay server (QR code pairing)
2. **Local ADB**: Connect via USB with ADB port forwarding

**WebSocket Handlers** (`server/routers/websocket.py`):
- `android_relay_connect` - Connect to relay server, get QR code for pairing
- `android_relay_disconnect` - Disconnect from relay server
- `android_relay_reconnect` - Reconnect to relay server

### Android Relay Client
Located in `server/services/android/`:

**Key Components:**
- `client.py` - RelayWebSocketClient manages persistent connection
- `broadcaster.py` - Status broadcast functions (connected, paired, disconnected)
- `manager.py` - Global client instance management
- `protocol.py` - JSON-RPC 2.0 message handling

**Message Filtering:**
```python
async def receive_message(self, timeout: float = 10.0):
    """Receive response message, skipping non-response types"""
    skip_types = {'presence', 'pong', 'ping', 'connected'}

    while True:
        data = await asyncio.wait_for(self._message_queue.get(), timeout)
        msg_type = data.get('type', '')

        if msg_type in skip_types:
            continue  # Skip and wait for next message

        return data  # Return actual response
```

**Performance Benefits:**
- Initial connection: ~0.18s (WebSocket handshake + registration)
- Reused connection: ~0.0003s (600x faster)
- Background tasks maintain connection health
- Message queue decouples receiving from service execution

### Android Relay Connection vs Device Pairing

The Android relay system uses a **two-state model** for connection status:

| State | Description | Frontend Indicator |
|-------|-------------|-------------------|
| `connected` | WebSocket connection to relay server is active | N/A (not shown directly) |
| `paired` | Android device has scanned QR and is paired via relay | Green/Red status dot |

**Key Concepts:**
- **Relay Connection**: The WebSocket connection to `wss://relay.opencompany.sh/ws` - can be active without a device
- **Device Pairing**: An Android device scans the QR code and pairs - required for service execution
- **Android service nodes require pairing**, not just relay connection, to execute

**Status Broadcasting Architecture:**
```
server/services/android/
├── client.py        # RelayWebSocketClient - manages WebSocket connection
├── broadcaster.py   # Status broadcast functions
├── manager.py       # Global client instance management
└── protocol.py      # JSON-RPC 2.0 message handling
```

**Broadcast Functions** (`server/services/android/broadcaster.py`):
```python
# Device connected and paired
await broadcast_connected(device_id, device_name)

# Device disconnected but relay still connected (for re-pairing)
await broadcast_device_disconnected(
    relay_connected=True,
    qr_data=qr_data,
    session_token=session_token
)

# Relay connection fully closed
await broadcast_relay_disconnected()

# QR code available for pairing
await broadcast_qr_code(qr_data, session_token)
```

**Frontend Status Indicator** (`client/src/components/SquareNode.tsx`):
```typescript
// Android nodes use 'paired' status, not 'connected'
const isAndroidConnected = isAndroidNode && androidStatus.paired;
```

**Status Flow:**
1. User clicks "Connect" → Relay WebSocket connects → `connected=true, paired=false`
2. QR code displayed → User scans with Android app → `connected=true, paired=true`
3. Android app disconnects → `connected=true, paired=false` (can re-pair)
4. Relay WebSocket closes → `connected=false, paired=false`

**WebSocket Context Interface** (`client/src/contexts/WebSocketContext.tsx`):
```typescript
export interface AndroidStatus {
  connected: boolean;      // Relay WebSocket connected
  paired: boolean;         // Android device paired
  device_id: string | null;
  device_name: string | null;
  connected_devices: string[];
  connection_type: string | null;
  qr_data: string | null;
  session_token: string | null;
}
```
