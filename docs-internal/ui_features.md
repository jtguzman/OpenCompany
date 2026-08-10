# UI Features Reference

Parameter system, node rename, UI state persistence, Normal/Dev mode, Console Panel, per-workflow workspace dir, workflow naming (Wave 14), execution system, event-driven deployment, WebSocket hooks, conditional parameter display. Moved verbatim out of CLAUDE.md.

## Key Features

### Parameter System
- **Universal Renderer**: Supports both INodeProperties and NodeParameter interfaces
- **Type-Specific Controls**: String, number, boolean, select, slider, file, array types
- **Drag-and-Drop**: Map outputs from connected nodes to parameters
- **Validation**: Required field checking and type constraints
- **Conditional Display**: Dynamic parameter visibility using displayOptions.show pattern
  - Implemented in `MiddleSection.tsx` with `shouldShowParameter()` function
  - Supports array-based conditions (e.g., `messageType: ['text']`)
  - Filters parameters before rendering based on other parameter values

### Node Rename System (n8n-style)
Three methods for renaming nodes, following n8n UX patterns:
- **F2 Keyboard Shortcut**: Press F2 with a node selected to enter rename mode
- **Double-click on Label**: Click the node label twice to edit inline
- **Right-click Context Menu**: "Rename" option in the context menu

#### Architecture
```
Global State (useAppStore)          Node Components
├── renamingNodeId: string | null   ├── SquareNode.tsx
├── setRenamingNodeId()             ├── TriggerNode.tsx
        ↓                           └── StartNode.tsx
   Coordinates which node               ↓
   is currently being renamed       Local State:
                                    ├── isRenaming: boolean
                                    ├── editLabel: string
                                    └── inputRef: HTMLInputElement
```

#### Implementation Files
- **`client/src/store/useAppStore.ts`** - Global rename state (`renamingNodeId`, `setRenamingNodeId`)
- **`client/src/components/ui/NodeContextMenu.tsx`** - Right-click menu with Rename, Copy, Delete
- **`client/src/Dashboard.tsx`** - Context menu handler, F2 keyboard handler
- **`client/src/components/SquareNode.tsx`** - Inline rename for square nodes (Android, WhatsApp)
- **`client/src/components/TriggerNode.tsx`** - Inline rename for trigger nodes
- **`client/src/components/StartNode.tsx`** - Inline rename with label support (was hardcoded "Start")

#### Key Pattern (shared by all node components)
```typescript
// Sync with global renaming state
useEffect(() => {
  if (renamingNodeId === id) {
    setIsRenaming(true);
    setEditLabel(data?.label || definition?.displayName || type || '');
  } else {
    setIsRenaming(false);
  }
}, [renamingNodeId, id, data?.label, definition?.displayName, type]);

// Handle save - only save if changed and non-empty
const handleSaveRename = useCallback(() => {
  const newLabel = editLabel.trim();
  if (newLabel && newLabel !== originalLabel) {
    updateNodeData(id, { ...data, label: newLabel });
  }
  setIsRenaming(false);
  setRenamingNodeId(null);
}, [...]);
```

#### NodeContextMenu Features
- Rename (F2), Copy (Ctrl+C), Delete (Del) with keyboard shortcuts shown
- Uses existing `useCopyPaste.copySelectedNodes()` for Copy
- Uses existing `onNodesDelete` for Delete
- Keyboard navigation (Arrow keys, Enter)
- Click outside to close
- Dracula-themed styling

### UI State Persistence
The application persists UI state to localStorage for a consistent user experience across sessions:

#### Persisted Settings
| Setting | Storage Key | Default | Location |
|---------|-------------|---------|----------|
| Sidebar visibility | `ui_sidebar_visible` | `true` | `useAppStore.ts` |
| Component palette visibility | `ui_component_palette_visible` | `true` | `useAppStore.ts` |
| Pro mode | `ui_pro_mode` | `false` | `useAppStore.ts` |
| Collapsed palette sections | `component_palette_collapsed_sections` | All collapsed | `useComponentPalette.ts` |

#### Implementation Pattern
```typescript
// In useAppStore.ts
const STORAGE_KEYS = {
  sidebarVisible: 'ui_sidebar_visible',
  componentPaletteVisible: 'ui_component_palette_visible',
};

const loadBooleanFromStorage = (key: string, defaultValue: boolean): boolean => {
  try {
    const saved = localStorage.getItem(key);
    if (saved !== null) return saved === 'true';
  } catch { /* Ignore storage errors */ }
  return defaultValue;
};

// Initial state loads from localStorage
sidebarVisible: loadBooleanFromStorage(STORAGE_KEYS.sidebarVisible, true),

// Toggle functions save to localStorage
toggleSidebar: () => {
  set((state) => {
    const newValue = !state.sidebarVisible;
    saveBooleanToStorage(STORAGE_KEYS.sidebarVisible, newValue);
    return { sidebarVisible: newValue };
  });
},
```

### Normal/Dev Mode Toggle
The toolbar includes a mode toggle that filters the Component Palette for different user experience levels:

| Mode | Description | Visible Categories |
|------|-------------|-------------------|
| **Normal** (default) | Simplified view for AI-focused workflows | AI Agents, AI Models, AI Skills, AI Abilities, AI Tools |
| **Dev** | Full access to all node types | All categories |

#### Implementation
- **State**: `proMode` boolean in `useAppStore.ts` with localStorage persistence (internal name unchanged for compatibility)
- **Toggle UI**: Segmented control in toolbar with "Normal" and "Dev" labels
- **Filtering**: `ComponentPalette.tsx` filters by `SIMPLE_MODE_CATEGORIES = ['agent', 'model', 'skill', 'tool']`
- **Category Merging**: WhatsApp and social nodes are merged into "Social Media Platforms" category via `SOCIAL_CATEGORIES = ['whatsapp', 'social']`

```typescript
// In ComponentPalette.tsx
const SIMPLE_MODE_CATEGORIES = ['agent', 'model', 'skill', 'tool'];
const SOCIAL_CATEGORIES = ['whatsapp', 'social'];

// Filter nodes based on mode
if (!proMode) {  // proMode=false means Normal mode
  const categoryKey = (definition.group?.[0] || '').toLowerCase();
  if (!SIMPLE_MODE_CATEGORIES.includes(categoryKey)) {
    return false;
  }
}

// Merge whatsapp and social categories
if (SOCIAL_CATEGORIES.includes(categoryKey.toLowerCase())) {
  categoryKey = 'social';
}
```

### Console Panel
The Console Panel provides a resizable bottom panel with three sections: Chat (AI conversation), Console (node execution logs), and Terminal (planned).

#### Features
- **Resizable**: Drag handle at top to resize, persisted to localStorage
- **Three Tabs**: Chat, Console, Terminal (placeholder)
- **Chat Section**: Send messages to Chat Trigger nodes, view conversation history
- **Console Section**: View and filter node execution logs

#### Node Selector Dropdowns
When multiple chatTrigger or console nodes exist in the workflow, dropdowns appear to select which node to target:

| Selector | Location | Behavior |
|----------|----------|----------|
| Chat Trigger | Chat section header | Select which chatTrigger node receives messages. "All" broadcasts to all triggers |
| Console | Console section controls | Filter logs to show only output from selected console node |

**Implementation** (`client/src/components/ui/ConsolePanel.tsx`):
```typescript
// Node type constants for filtering
const CHAT_TRIGGER_TYPES = ['chatTrigger'];
const CONSOLE_NODE_TYPES = ['console'];

// Filter workflow nodes
const chatTriggerNodes = useMemo(() =>
  nodes.filter(n => CHAT_TRIGGER_TYPES.includes(n.type || '')),
  [nodes]
);
const consoleNodes = useMemo(() =>
  nodes.filter(n => CONSOLE_NODE_TYPES.includes(n.type || '')),
  [nodes]
);

// State for selected nodes
const [selectedChatTriggerId, setSelectedChatTriggerId] = useState<string>('');
const [selectedConsoleId, setSelectedConsoleId] = useState<string>('');
```

#### Chat Message Persistence
Chat messages are persisted to SQLite database and survive server restarts.

**Database Model** (`server/models/database.py`):
```python
class ChatMessage(SQLModel, table=True):
    __tablename__ = "chat_messages"
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(default="default", index=True, max_length=255)
    role: str = Field(max_length=20)  # 'user' or 'assistant'
    message: str = Field(max_length=50000)
    created_at: datetime
```

**WebSocket Handlers** (`server/routers/websocket.py`):
| Handler | Description |
|---------|-------------|
| `send_chat_message` | Send message to chat, optionally targeting specific node via `node_id` |
| `get_chat_messages` | Retrieve chat history for session |
| `clear_chat_messages` | Clear all messages for session |

**Database Methods** (`server/core/database.py`):
- `add_chat_message(session_id, role, message)` - Add message to database
- `get_chat_messages(session_id, limit)` - Get messages with pagination
- `clear_chat_messages(session_id)` - Delete all messages for session

#### Console Log Persistence
Console logs are persisted to SQLite database and loaded on page refresh.

**WebSocket Handlers**:
| Handler | Description |
|---------|-------------|
| `get_console_logs` | Retrieve console logs from database (limit: 100) |
| `clear_console_logs` | Clear all console logs from database |

**Database Methods** (`server/core/database.py`):
- `add_console_log(log_data)` - Add console log to database
- `get_console_logs(limit)` - Get console logs
- `clear_console_logs()` - Delete all console logs

#### Key Files
| File | Description |
|------|-------------|
| `client/src/components/ui/ConsolePanel.tsx` | Main panel component with chat/console/terminal tabs |
| `server/models/database.py` | ChatMessage and ConsoleLog SQLModel definitions |
| `server/core/database.py` | Chat message and console log CRUD methods |
| `server/routers/websocket.py` | WebSocket handlers for chat and console operations |

### Per-Workflow Workspace Directory
Each workflow execution gets a persistent workspace directory where nodes save output files and agents such as Coding Agent access them through connected filesystem tools.

**Directory**: `~/.opencompany/workspaces/<workflow_slug>/` (Wave 14 — keyed by the human-readable slug, not the UUID; see "Workflow naming" below).

**Configuration** (`server/core/config.py`):
```python
workspace_base_dir: str = Field(default="workspaces", env="WORKSPACE_BASE_DIR")  # resolved under DATA_DIR -> ~/.opencompany/workspaces/
```

**How it works:**
- `workflow.py` creates the workspace dir and injects `workspace_dir` into the execution context. The dir name is the `workflow_slug` resolved from the DB (falls back to `"default"` for one-off Runs without a saved row).
- `fileDownloader` saves to `{workspace_dir}/downloads/` by default
- Code executors (Python/JS/TS) receive `workspace_dir` in their execution namespace
- The `fileRead`, `fileModify`, `fsSearch`, `shell` and `gallery` nodes use the native `WorkspaceBackend` rooted at `workspace_dir`; Coding Agent can invoke the first four when they are connected as tools. **`gallery` is deliberately `usable_as_tool = False`** — it carries destructive operations, and `fsSearch` + `fileModify` already cover what an agent needs, so shipping an editor panel must not hand every agent a delete tool as a side effect
- `WorkspaceBackend` resolves and validates paths beneath that root, rejects traversal and symlink escapes, and uses per-path locks plus atomic replacement for writes
- Rename follows the workflow: when the user renames a workflow, `save_workflow` recomputes the slug and `os.rename`s the workspace dir to match (existing files preserved).

**Key Files:**
| File | Description |
|------|-------------|
| `server/core/config.py` | `workspace_base_dir` setting |
| `server/services/workflow.py` | `_get_workspace_dir()`, injects into context |
| `server/nodes/document/file_downloader/` | `fileDownloader` saves to the workspace |
| `server/nodes/code/` | `workspace_dir` available in Python/JS/TS executors |
| `server/nodes/filesystem/_backend.py` | Native contained workspace filesystem implementation |

### Workflow Naming (Wave 14)
The workflow record carries three identity fields with strict separation:

| Field | Carrier | Stable? | Surfaces |
|---|---|---|---|
| `Workflow.id` | opaque 32-hex UUID (`uuid.uuid4().hex`) | yes — never changes on rename | FK target (`Execution.workflow_id`), `EventWorkflowId` Search Attribute in Temporal Visibility, legacy `WorkflowEvent.workflow_id` compatibility field, `log_context(workflow_id=...)`, Redis cache keys, `DeploymentManager._deployments` dict key, frontend `useAppStore.currentWorkflow.id` |
| `Workflow.name` | free-form display ("AI Assistant") | mutable | sidebar, parameter panel, exported JSON |
| `Workflow.slug` | `<Sanitized_Name>_<N>` (`AI_Assistant_1`) | mutable, recomputed on rename | `~/.opencompany/workspaces/<slug>/`, Temporal workflow IDs (visible in Temporal Web UI), cron Schedule IDs, export filenames |

Single source of truth: [`server/services/workflow_naming.py`](../server/services/workflow_naming.py) — `slugify_name` (via `python-slugify` for Unicode transliteration, emoji strip, case preservation, length cap), `next_available_slug(name, database, *, exclude_id=None)` (fill-gap counter; pass `exclude_id=workflow_id` on rename so the row doesn't bump itself), `new_workflow_id()` (bare hex UUID), `node_label_slug(node)` (sandbox-safe stdlib slug from `node.data.label` or `node.type`, used inside Temporal `@workflow.defn` modules where `python-slugify` can't import safely).

**Temporal workflow ID convention** — uniform `<workflow_slug>-<node_label>` shape across every workflow type. The Temporal Web UI's "Workflow Type" column already distinguishes the kind (TriggerListenerWorkflow / PollingTriggerWorkflow / CronTriggerWorkflow / AgentWorkflow / MachinaWorkflow), so no middle `-trigger-` / `-agent-` tag in the id.

| Surface | Format | Example |
|---|---|---|
| Trigger listener (push/poll) | `<slug>-<trigger_label>` | `AI_Assistant_1-chatTrigger` (or `AI_Assistant_1-Customer_Inbox` after F2 rename) |
| Per-firing run (child of listener) | `<slug>-<trigger_label>-<event_id>` | `AI_Assistant_1-chatTrigger-evt-abc` |
| Cron Schedule | `<slug>-<trigger_label>` | `AI_Assistant_1-cronScheduler` |
| Cron firing (per-tick child) | `<slug>-<trigger_label>-<ScheduledStartTime>` | `AI_Assistant_1-cronScheduler-2026-05-27T12:00:00Z` |
| Agent child workflow | `<root_temporal_workflow_id>-agent-<node_id>` | `AI_Assistant_1-Chat_Trigger-<event>-agent-1:aiAgent:1`. Uses the IMMUTABLE node id and does carry a middle `-agent-` tag, unlike every other row. The label-derived `<slug>-<agent_label>` form survives only for histories recorded before the `machina-agent-child-id-v2` patch. |
| Direct MachinaWorkflow exec | `<slug>-<uuid8>` | `AI_Assistant_1-a1b2c3d4` |
| Per-node activity (inside MachinaWorkflow) | `activity_id = <node_id>` | `chatTrigger-1779...-47c2f5` |

`node_label` is `node.data.label` (the F2-renamed canvas label) when set, falling back to `node.type` (`chatTrigger` / `telegramReceive` / `aiAgent` / etc.). Computed once at deploy time via `node_label_slug(node)` and passed into Temporal workflows as `trigger_label` (in `listener_data` for the trigger path) or read directly from the node dict (in `MachinaWorkflow.run` for the agent path). Stable `TriggerNodeId` / `EventWorkflowId` Search Attributes still use the immutable node_id / UUID so admin queries don't break across rename.

**Rename path** — there is NO dedicated rename endpoint. The frontend's auto-save chain (`TopToolbar` inline edit → `updateWorkflow({name})` → debounced save → REST `POST /api/database/workflows` → `services.workflow_storage.handlers.handle_save_workflow`) IS the rename path. When `name` changes between saves, the handler (1) allocates a fresh slug via `next_available_slug`, (2) `database.rename_workflow` updates name + slug atomically (id UUID stays put), (3) renames the on-disk workspace dir via `Path.rename()`, (4) broadcasts a CloudEvents `workflow.renamed` envelope (`broadcaster.broadcast_workflow_lifecycle("renamed", workflow_id=..., name=..., slug=..., old_slug=...)`) so other tabs invalidate their workflows query.

**Invariants** (locked by `tests/services/test_workflow_naming.py` + `test_workflow_rename.py` — 42 tests):
- First creation always gets `_1` suffix (no bare-base slugs).
- Fill-gap: deleted `AI_Assistant_2` slot is reused on next "AI Assistant" creation.
- Renaming `AI Assistant` → `AI Assistant!` (same slug base) keeps `_1` via `exclude_id` (no self-bump).
- UNIQUE constraint on `slug` is the final collision guard; `IntegrityError` indicates a race the caller should retry.
- Non-ASCII names transliterate via `text-unidecode` ("日本語" → "Ri_Ben_Yu"); fall back to `Workflow_N` only when slug is empty after sanitize.
- No backfill migration — the slug column is required on every save. Existing DBs must be rebuilt.

### Execution System
- **Supported Components**: AI models, location services, Android automation, WhatsApp messaging, HTTP requests, webhooks
- **Android Integration**: ADB-based device control with 17 service nodes across monitoring, apps, automation, sensors, and media
- **Result Display**: Formatted output panel with success/error states
- **Performance Metrics**: Execution time and status tracking
- **Error Handling**: Comprehensive error reporting and logging
- **Dynamic Options**: Load options from backend (e.g., Android device list, service actions)
- **Continuous Scheduling**: Temporal/Conductor pattern using `asyncio.wait(FIRST_COMPLETED)` - dependent nodes start immediately when their specific dependency completes
- **Event-Driven Deployment**: n8n-style architecture where triggers spawn independent concurrent execution runs (no iteration loop)

### Event-Driven Deployment Architecture (n8n Pattern)
The deployment system follows modern workflow engine patterns from n8n, Temporal, and Conductor:

```
deploy_workflow() -> Sets up triggers, returns immediately
                 |
                 +-> cronScheduler fires -> spawns ExecutionRun 1
                 +-> cronScheduler fires -> spawns ExecutionRun 2 (concurrent)
                 +-> whatsappReceive fires -> spawns ExecutionRun 3 (concurrent)
                 +-> webhookTrigger fires -> spawns ExecutionRun 4 (concurrent)
```

**Key Concepts:**
- **Workflow Template**: The deployed workflow is a template stored in memory
- **Execution Run**: Each trigger event spawns an independent, isolated run
- **Concurrent Runs**: Multiple runs execute simultaneously without interference
- **No Iteration Loop**: Purely event-driven, not polling or sequential iterations
- **Pre-Executed Triggers**: The firing trigger is marked complete before downstream execution. All other trigger nodes in the run are also marked `_pre_executed` with `{not_triggered: True}` to prevent them from blocking as event waiters

**Implementation Files:**
- `server/services/workflow.py`: Thin facade (~460 lines) delegating to specialized modules
- `server/services/node_executor.py`: Single node execution with registry-based dispatch
- `server/services/parameter_resolver.py`: Template variable resolution (`{{node.field}}`)
- `server/services/deployment/manager.py`: Deployment lifecycle, spawn runs, cancel
- `server/services/deployment/triggers.py`: Cron and event trigger management
- `server/services/deployment/state.py`: DeploymentState, TriggerInfo dataclasses
- `server/services/execution/models.py`: `ExecutionContext.create()` with `_pre_executed` support
- `server/services/execution/executor.py`: Continuous scheduling with `asyncio.wait(FIRST_COMPLETED)`

## WebSocket Hooks

### useWhatsApp (`client/src/hooks/useWhatsApp.ts`)
Hook for WhatsApp operations via WebSocket:
```typescript
const { getStatus, getQRCode, sendMessage, startConnection, isLoading, connectionStatus } = useWhatsApp();
```

### Node execution (`client/src/services/executionService.ts`)
`ExecutionService.executeNodeViaWebSocket()` is the live path, called from
[`ParameterPanel.tsx`](../client/src/ParameterPanel.tsx). It delegates to the
context's `executeNode`, which sizes its request budget from the node's own
`uiHints.executionTimeoutMs` rather than any local list of "slow" node types.
(A `useExecution` hook once wrapped this; it was unreachable and was deleted.)

### useApiKeys (`client/src/hooks/useApiKeys.ts`)
Hook for API key management via WebSocket:
```typescript
const { validateApiKey, getStoredKey, saveApiKey, deleteApiKey } = useApiKeys();
```

### useAndroidOperations (`client/src/hooks/useAndroidOperations.ts`)
Hook for Android device operations via WebSocket:
```typescript
const { getDevices, executeAction, setupDevice, isConnected, deviceStatus } = useAndroidOperations();
```

### useParameterPanel (`client/src/hooks/useParameterPanel.ts`)
Hook for parameter management via WebSocket:
```typescript
const { parameters, saveParameters, loadParameters, isDirty } = useParameterPanel(nodeId);
```

### Conditional Parameter Display Implementation
Located in `client/src/components/parameterPanel/MiddleSection.tsx`:

```typescript
const shouldShowParameter = (param: INodeProperties, allParameters: Record<string, any>): boolean => {
  if (!param.displayOptions?.show) {
    return true;
  }

  const showConditions = param.displayOptions.show;

  for (const [paramName, allowedValues] of Object.entries(showConditions)) {
    const currentValue = allParameters[paramName];

    if (Array.isArray(allowedValues)) {
      if (!allowedValues.includes(currentValue)) {
        return false;
      }
    } else {
      if (currentValue !== allowedValues) {
        return false;
      }
    }
  }

  return true;
};
```

This function:
- Checks if parameter has displayOptions.show configuration
- Evaluates all show conditions against current parameter values
- Returns false if any condition fails (parameter hidden)
- Returns true if all conditions pass (parameter visible)
- Applied before rendering: `.filter(param => shouldShowParameter(param, parameters))`
