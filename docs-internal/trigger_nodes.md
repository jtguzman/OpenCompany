# Event-Driven Trigger Node System

Event waiter, filter builders, WhatsApp Receive, Task Trigger, adding new trigger types, polling triggers, design decisions. Moved verbatim out of CLAUDE.md. See also event_waiter_system.md.

## Event-Driven Trigger Node System

### Overview
Trigger nodes wait for external events (WhatsApp messages, webhooks, etc.) using Python's asyncio.Future. The backend handles all event waiting logic with the frontend displaying waiting state and providing cancel functionality.

### Architecture
```
User clicks "Run" on Trigger Node
       ↓
Frontend sends execute_node via WebSocket
       ↓
Python backend detects trigger node type (event_waiter.is_trigger_node)
       ↓
Backend registers asyncio.Future waiter with filter
       ↓
Backend broadcasts "waiting" status to frontend
       ↓
External service sends event (e.g., whatsapp_message_received)
       ↓
event_waiter.dispatch() resolves matching waiters
       ↓
Backend returns execution result with event data as output
       ↓
Frontend displays result in output panel
```

### Backend Implementation

#### Event Waiter Service (`server/services/event_waiter.py`)
Generic event waiting using standard asyncio primitives:

```python
@dataclass
class TriggerConfig:
    node_type: str
    event_type: str  # e.g., 'whatsapp_message_received'
    display_name: str

TRIGGER_REGISTRY: Dict[str, TriggerConfig] = {
    'whatsappReceive': TriggerConfig('whatsappReceive', 'whatsapp_message_received', 'WhatsApp Message'),
    'webhookTrigger': TriggerConfig('webhookTrigger', 'webhook_received', 'Webhook Request'),
    'chatTrigger': TriggerConfig('chatTrigger', 'chat_message_received', 'Chat Message'),
    'taskTrigger': TriggerConfig('taskTrigger', 'task_completed', 'Task Completed'),
    'telegramReceive': TriggerConfig('telegramReceive', 'telegram_message_received', 'Telegram Message'),
    # Future: 'emailTrigger', 'mqttTrigger', etc.
}

@dataclass
class Waiter:
    id: str
    node_id: str
    node_type: str
    event_type: str
    filter_fn: Callable[[Dict], bool]
    future: asyncio.Future

# Key functions:
def register(node_type: str, node_id: str, params: Dict) -> Waiter
def dispatch(event_type: str, data: Dict) -> int  # Returns count resolved
def cancel(waiter_id: str) -> bool
def cancel_for_node(node_id: str) -> int
def get_active_waiters() -> List[Dict]
```

#### Trigger Node Execution (`server/services/workflow.py`)
```python
async def _execute_trigger_node(self, node_id: str, node_type: str, parameters: Dict) -> Dict:
    config = event_waiter.get_trigger_config(node_type)
    waiter = event_waiter.register(node_type, node_id, parameters)

    # Broadcast waiting status
    await broadcaster.update_node_status(node_id, "waiting", {
        "message": f"Waiting for {config.display_name}...",
        "waiter_id": waiter.id
    })

    # Wait indefinitely (user cancels via cancel_event_wait)
    event_data = await waiter.future
    return {"success": True, "result": event_data, ...}
```

#### Filter Builders
Each trigger type has a filter builder that creates a function to match events:

```python
def build_whatsapp_filter(params: Dict) -> Callable[[Dict], bool]:
    """Build filter for WhatsApp messages based on node parameters."""
    msg_type = params.get('messageTypeFilter', 'all')
    sender_filter = params.get('filter', 'all')  # all, any_contact, contact, group, keywords
    forwarded_filter = params.get('forwardedFilter', 'all')  # all, only_forwarded, ignore_forwarded
    # ... builds closure that checks message fields
```

**Sender Filter Options:**
- `all` - Accept all messages (groups and contacts)
- `any_contact` - Accept only non-group messages (individual chats)
- `contact` - Accept from specific phone number
- `group` - Accept from specific group (optionally filter by sender)
- `keywords` - Accept messages containing specific keywords

### WebSocket Handlers

#### Cancel Event Wait (`server/routers/websocket.py`)
```python
@ws_handler()
async def handle_cancel_event_wait(data: Dict[str, Any], websocket: WebSocket):
    """Cancel by waiter_id or node_id."""
    if waiter_id := data.get("waiter_id"):
        success = event_waiter.cancel(waiter_id)
    elif node_id := data.get("node_id"):
        count = event_waiter.cancel_for_node(node_id)
    return {"success": success, ...}

@ws_handler()
async def handle_get_active_waiters(data: Dict[str, Any], websocket: WebSocket):
    """Get list of active waiters for debugging/UI."""
    return {"waiters": event_waiter.get_active_waiters()}
```

### WhatsApp Receive Node

#### Node Definition (plugin: `server/nodes/whatsapp/whatsapp_receive.py`; pre-Wave-11 frontend shape shown below for historical reference)
```typescript
whatsappReceive: {
  displayName: 'WhatsApp Receive',
  name: 'whatsappReceive',
  icon: WHATSAPP_RECEIVE_ICON,  // Bell with notification dot
  group: ['whatsapp', 'trigger'],
  outputs: [{
    name: 'main',
    displayName: 'Message',
    type: 'main',
    description: 'message_id, sender, chat_id, message_type, text, timestamp, is_group, is_from_me, push_name, group_info'
  }],
  properties: [
    // Message Type Filter: all, text, image, video, audio, document, location, contact
    // Sender Filter: all, contact (specific phone), group (specific group), keywords
    // Ignore Own Messages: boolean (default true)
    // Include Media Data: boolean (default false)
  ]
}
```

#### Output Schema (plugin-owned, `server/nodes/whatsapp/whatsapp_receive.py`)
Runtime output shapes are fetched lazily by InputSection per the Wave 3 source-of-truth decision. WhatsApp's schemas live in the plugin folder (the node's `Output` Pydantic classes — `WhatsAppGroupInfo` / `WhatsAppReceiveOutput` / `WhatsAppSendOutput` / `WhatsAppDbOutput`) and self-register from `nodes/whatsapp/__init__.py` via `register_output_schema(...)` — same pattern as telegram; `services/node_output_schemas.py` carries no whatsapp code.
Served via `GET /api/schemas/nodes/whatsappReceive.json` + `get_node_output_schema` WS handler. See [docs-internal/schema_source_of_truth_rfc.md](./schema_source_of_truth_rfc.md).

### Task Trigger Node

The Task Trigger node fires when a delegated child agent completes its task (success or error). This enables parent agents to react to child completion via workflow nodes.

#### Node Definition (plugin: `server/nodes/trigger/task_trigger.py`; pre-Wave-11 frontend shape shown below for historical reference)
```typescript
taskTrigger: {
  displayName: 'Task Completed',
  name: 'taskTrigger',
  icon: '📨',
  group: ['trigger', 'workflow'],
  outputs: [{
    name: 'main',
    displayName: 'Output',
    type: 'main',
    description: 'task_id, status, agent_name, result/error, parent_node_id'
  }],
  properties: [
    // Task ID Filter: Optional specific task ID to watch
    // Agent Name Filter: Optional partial match on agent name
    // Status Filter: all, completed, error
    // Parent Node ID: Optional filter by parent agent node
  ]
}
```

#### Output Schema (`client/src/components/parameterPanel/InputSection.tsx`)
```typescript
taskTrigger: {
  task_id: 'string',
  status: 'string',      // 'completed' or 'error'
  agent_name: 'string',
  agent_node_id: 'string',
  parent_node_id: 'string',
  result: 'string',      // Present when status='completed'
  error: 'string',       // Present when status='error'
  workflow_id: 'string',
}
```

#### Event Dispatch (`server/services/handlers/tools.py`)
The `task_completed` event is dispatched when a delegated child agent finishes:
```python
# On success:
await broadcaster.send_custom_event('task_completed', {
    'task_id': task_id,
    'status': 'completed',
    'agent_name': agent_label,
    'agent_node_id': node_id,
    'parent_node_id': config.get('parent_node_id', ''),
    'result': result.get('result', {}).get('response', ...),
    'workflow_id': workflow_id,
})

# On error:
await broadcaster.send_custom_event('task_completed', {
    'task_id': task_id,
    'status': 'error',
    'agent_name': agent_label,
    'agent_node_id': node_id,
    'parent_node_id': config.get('parent_node_id', ''),
    'error': str(e),
    'workflow_id': workflow_id,
})
```

### Adding New Trigger Types

1. **Add to Registry** in `server/services/event_waiter.py`:
   ```python
   TRIGGER_REGISTRY['emailTrigger'] = TriggerConfig('emailTrigger', 'email_received', 'Email')
   ```

2. **Add Filter Builder**:
   ```python
   def build_email_filter(params: Dict) -> Callable[[Dict], bool]:
       # Build filter based on node parameters
   FILTER_BUILDERS['emailTrigger'] = build_email_filter
   ```

3. **Add the plugin** at `server/nodes/<category>/<trigger_name>.py`:
   - Define the `NodeSpec` (inputs / outputs / uiHints) as a subclass
     or dataclass per the plugin system
   - Implement the trigger-handler `execute` method

4. **Add Output Schema** in `InputSection.tsx`:
   ```typescript
   email: { from: 'string', subject: 'string', body: 'string', ... }
   ```

5. **Dispatch Events** from external service:
   ```python
   from services import event_waiter
   event_waiter.dispatch('email_received', email_data)
   ```

### Polling Triggers (Gmail, Twitter)

Some triggers require active API polling instead of waiting for externally dispatched events. These use `setup_polling_trigger` in `TriggerManager` instead of `setup_event_trigger`.

**Architecture:**
```
setup_polling_trigger() → broadcasts "waiting" status
       ↓
   poller task: runs poll_coroutine(queue, is_running_fn)
       ↓                    ↓
   polls API at interval → enqueues new items to asyncio.Queue
       ↓
   processor task: reads queue → calls on_event → spawns execution run
```

**Key differences from event triggers:**
- Event triggers: `event_waiter.register()` + `wait_for_event()` (push-based)
- Polling triggers: Custom poll coroutine + `asyncio.Queue` (pull-based)

**Routing** (`server/services/deployment/manager.py`):
```python
if node_type in POLLING_TRIGGER_TYPES:  # gmailReceive, twitterReceive
    poll_coroutine = self._create_poll_coroutine(node_type, node_id, params)
    await trigger_manager.setup_polling_trigger(...)
```

**Constants** (`server/constants.py`):
- `POLLING_TRIGGER_TYPES`: `frozenset(['gmailReceive', 'twitterReceive'])`
- These are also in `WORKFLOW_TRIGGER_TYPES` for trigger node detection

### Key Design Decisions

- **No Timeout**: Trigger nodes wait indefinitely; users cancel via Cancel button
- **Backend-First**: All event waiting logic in Python backend, minimal frontend changes
- **Generic Architecture**: Same execution flow for all trigger types via registry
- **Filter Functions**: Each trigger type builds its own filter from node parameters
- **asyncio.Future**: Simpler than asyncio.Event for single-value resolution
- **Polling triggers**: Use asyncio.Queue + dedicated poll coroutine for APIs without push support
