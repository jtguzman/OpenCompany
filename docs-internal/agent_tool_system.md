# AI Agent Tool System (detail)

Tool discovery/execution flow, implemented tools, direct Android service tools, tool schemas, web search implementation. Moved verbatim out of CLAUDE.md.

## AI Agent Tool System

### Overview
Tool nodes provide capabilities that AI Agents can invoke during reasoning. Each tool node connects to the AI Agent's `input-tools` handle and defines a schema for the LLM to understand how to call it.

### Architecture
```
Tool Node (calculatorTool) → (tool output) → AI Agent (input-tools handle)
                                                    ↓
                                            AIService builds AgentToolSpec values
                                                    ↓
                                            run_native_agent_loop sends ToolDef schemas
                                                    ↓
                                            LLM selects zero or more tool calls
                                                    ↓
                                            Tool executor runs handlers
                                                    ↓
                                            Native tool results return to LLM
```

### Tool Execution Flow
1. **Tool Discovery**: AI Agent scans edges for nodes connected to `input-tools` handle
2. **Schema Building**: `_build_tool_from_node()` in `ai.py` combines the Pydantic validation model with an inlined JSON schema in an `AgentToolSpec` / `ToolDef`
3. **Provider Compilation**: `run_native_agent_loop` passes provider-neutral `ToolDef` values through `ChatUnifier`; each native provider compiles the schema it supports
4. **LLM Decision**: LLM decides when to call tools based on user query
5. **Status Broadcast**: `executing_tool` status broadcast with tool_name for UI animation
6. **Tool Execution**: `execute_tool()` in `tools.py` dispatches to appropriate handler
7. **Result Return**: Native tool-result messages are appended for continued reasoning

### Key Files
| File | Description |
|------|-------------|
| `server/services/handlers/tools.py` | Tool execution handlers |
| `server/services/ai.py` | `_build_tool_from_node()` / `_get_tool_schema()` - provider-neutral tool specs and Pydantic validation |
| `server/services/agent_runtime.py` | `AgentToolSpec` and the shared native agent loop |
| `server/services/plugin/edge_walker.py` | `collect_agent_connections` — tool/skill/memory discovery from edges |

### Adding a new tool or specialized agent (Wave 11)

**Single source of truth: [`server/nodes/README.md`](../server/nodes/README.md)** (5-minute recipe) and [`docs-internal/plugin_system.md`](./plugin_system.md) (full reference). The pre-Wave-11 `toolNodes.ts` / `specializedAgentNodes.ts` / `AGENT_CONFIGS` files do not exist — the canonical authoring shape is one Python file.

The whole workflow:

```python
# server/nodes/tool/<plugin>/__init__.py     ← for a tool
# server/nodes/agent/<plugin>/__init__.py    ← for a specialized agent
class MyTool(ToolNode):              # or SpecializedAgentBase for an agent
    type = "myTool"
    display_name = "My Tool"
    group = ("tool", "ai")
    component_kind = "tool"          # or "agent"
    Params = MyParams                # Pydantic — feeds UI + AI tool schema
    Output = MyOutput
    @Operation("run")
    async def run(self, ctx, params): ...
```

`BaseNode.__init_subclass__` registers the class into `_NODE_CLASS_REGISTRY` (first), then into `NODE_METADATA`, `_DIRECT_MODELS`, `NODE_OUTPUT_SCHEMAS`, and `_HANDLER_REGISTRY` on import. The class-registry-first order matters: `_metadata_dict` calls `get_plugin_icon_path(cls.type)` which goes through `get_node_class()`. NodeSpec emits at `GET /api/schemas/nodes/<type>/spec.json`. The frontend auto-discovers via `useNodeSpec` + `componentKind` dispatch (see "Spec-driven component design" above). Icon goes in `<plugin>/icon.svg` (or `visuals.json` for emoji / library brand); color goes in `<plugin>/meta.json` (or `visuals.json` legacy fallback).

**Cross-cutting edits that are still required (small):**
- New specialized agent: update `AI_AGENT_TYPES` and the canonical teammate
  discovery/validation surfaces so a team lead can authorize it through
  `input-teammates`. Team leads delegate with Task Manager; `delegate_to_*`
  remains an internal/legacy dispatch identity and must not be taught as the
  model-facing team contract.
- Brand-new uiHint flag: add to `INodeUIHints` in [`client/src/types/INodeProperties.ts`](../client/src/types/INodeProperties.ts) AND to the `known` set in `test_ui_hints_only_carry_known_flags` (`server/tests/test_node_spec.py`).

**No edits needed:** any TypeScript node definition file, `_get_tool_schema()`, `AGENT_CONFIGS`, `AGENT_WITH_SKILLS_TYPES`, `aiAgentTypes`, `Dashboard.tsx`, `MiddleSection.tsx`, `InputSection.tsx`, or any of the other arrays the pre-Wave-11 docs listed.

### Tool Execution Animation
Tool nodes display execution status via the standard node status system:
- Backend broadcasts `executing` status to tool node when AI Agent calls it
- `SquareNode.tsx` uses `getNodeStatus()` from WebSocket context
- Tool nodes show cyan border and pulse animation when `isExecuting` is true
- **Minimum glow duration**: 500ms ensures fast-executing tools are visible (via `isGlowing` state)
- Dual-purpose tools (Python/JavaScript) fall back to node params when LLM returns empty args

### Implemented Tools
| Tool | Schema | Handler | Description |
|------|--------|---------|-------------|
| calculatorTool | CalculatorSchema | `_execute_calculator()` | Math operations |
| currentTimeTool | CurrentTimeSchema | `_execute_current_time()` | Date/time with timezone |
| duckduckgoSearch | DuckDuckGoSearchSchema | `_execute_duckduckgo_search()` | DuckDuckGo web search (free) |
| taskManager | `TaskManagerParams` | `_execute_task_manager()` | Intrinsic durable team assignment; returns queued through detached Temporal runner, preserves cross-run history, review, retry/reassignment, cancellation, acceptance, timestamps, elapsed time, and token usage |
| writeTodos | WriteTodosSchema | `execute_write_todos()` / `handle_write_todos()` | Structured task list planning with checklist rendering |
| braveSearch | BraveSearchSchema | `handle_brave_search()` | Brave Search API web results |
| serperSearch | SerperSearchSchema | `handle_serper_search()` | Google SERP via Serper API |
| perplexitySearch | PerplexitySearchSchema | `handle_perplexity_search()` | AI-powered search with citations |
| Android service nodes | Per-service schema | `_execute_android_service()` | Direct Android service tools (see below) |

### Direct Android Service Tools
Android service nodes (batteryMonitor, wifiAutomation, etc.) connect directly to any agent's `input-tools` handle — this is the only Android tool path (the former `androidTool` aggregator was retired; legacy graphs are migrated on load by `workflow_migrations.normalize_legacy_android_toolkit`). The `execute_tool()` function detects these via `ANDROID_SERVICE_NODE_TYPES` and routes to `_execute_android_service()`.

**Service ID Mapping** (camelCase node type -> snake_case service ID):
```python
service_id_map = {
    'batteryMonitor': 'battery',
    'networkMonitor': 'network',
    'systemInfo': 'system_info',
    'location': 'location',
    'appLauncher': 'app_launcher',
    'appList': 'app_list',
    'wifiAutomation': 'wifi_automation',
    'bluetoothAutomation': 'bluetooth_automation',
    'audioAutomation': 'audio_automation',
    'deviceStateAutomation': 'device_state',
    'screenControlAutomation': 'screen_control',
    'airplaneModeControl': 'airplane_mode',
    'motionDetection': 'motion_detection',
    'environmentalSensors': 'environmental_sensors',
    'cameraControl': 'camera_control',
    'mediaControl': 'media_control',
}
```

### Android Toolkit Pattern (retired)
The former `androidTool` gateway node (single `android_device` tool aggregating multiple Android service nodes, n8n Sub-Node / LangChain Toolkit pattern) no longer exists. Android service nodes connect straight to `input-tools`, and sub-node exclusion keys solely on AI-agent config handles (`input-context` / `input-tools` / `input-skill` / `input-teammates`) — the `TOOLKIT_NODE_TYPES` constant was deleted along with all its usage sites. Legacy `service -> androidTool -> agent` graphs are rewritten on load by `services/workflow_migrations.normalize_legacy_android_toolkit`.

### Tool Schemas (per-service customization)
Custom LLM-visible schemas for Android service tools persist in the `tool_schemas` table and are read by the AI service at execution time. (The `ToolSchemaEditor.tsx` UI component shipped with the retired Android Toolkit node and was removed with it; the `useToolSchema` hook, WebSocket handlers, and database CRUD remain.)

#### Architecture
```
useToolSchema Hook (WebSocket CRUD)
        ↓
  Database (tool_schemas table)
        ↓
  AI Service reads schemas at execution
```

#### Key Files
| File | Description |
|------|-------------|
| `client/src/hooks/useToolSchema.ts` | WebSocket hook for schema CRUD operations |
| `server/models/database.py` | `ToolSchema` SQLModel table definition |
| `server/core/database.py` | Database CRUD methods for tool schemas |
| `server/routers/websocket.py` | WebSocket handlers for schema operations |

#### Database Model
```python
class ToolSchema(SQLModel, table=True):
    __tablename__ = "tool_schemas"
    node_id: str          # Service node ID (unique key)
    tool_name: str        # Display name (e.g., "Battery Monitor")
    tool_description: str # Description shown to LLM
    schema_config: Dict   # Schema fields and types (JSON)
    connected_services: Optional[Dict]  # Legacy field from the retired toolkit aggregation
```

#### WebSocket Messages
| Message Type | Description |
|--------------|-------------|
| `get_tool_schema` | Get schema for a node by ID |
| `save_tool_schema` | Save/update schema for a node |
| `delete_tool_schema` | Delete schema for a node |
| `get_all_tool_schemas` | Get all stored schemas |

#### Default Schema Generation
When no custom schema exists, service-specific defaults are generated:
```typescript
{
  description: `Control ${serviceName} on Android device`,
  fields: {
    action: { type: 'string', description: `Action to perform on ${serviceName}`, required: true },
    parameters: { type: 'object', description: `Parameters for the ${serviceName} action`, required: false }
  }
}
```

### Web Search Implementation

#### DuckDuckGo (duckduckgoSearch - free, no API key)
Uses `ddgs` library for web results:
```python
from ddgs import DDGS
def do_search():
    ddgs = DDGS()
    return list(ddgs.text(query, max_results=max_results))
search_results = await asyncio.get_event_loop().run_in_executor(None, do_search)
```

#### Search API Nodes (braveSearch, serperSearch, perplexitySearch)
Dedicated plugins under `server/nodes/search/` (`brave_search` / `serper_search` / `perplexity_search`) using `httpx.AsyncClient`:
- **Brave Search**: `GET https://api.search.brave.com/res/v1/web/search` with `X-Subscription-Token` header. Returns `{query, results: [{title, snippet, url}], result_count, provider}`.
- **Serper**: `POST https://google.serper.dev/search` with `X-API-KEY` header. Supports web/news/images/places search types. Returns `{query, results, result_count, search_type, provider}` with optional `knowledge_graph`.
- **Perplexity Sonar**: `POST https://api.perplexity.ai/chat/completions` with Bearer token. Returns `{query, answer (markdown), citations: [url], results: [{url}], model, provider}` with optional `images` and `related_questions`.

All handlers fetch API keys via `auth_service.get_api_key()` and track usage via `_track_search_usage()` for cost calculation.
