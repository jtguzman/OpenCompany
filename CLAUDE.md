# OpenCompany - Claude Documentation

## Project Overview
This is a React Flow-based workflow automation platform implementing n8n-inspired architectural patterns. The project has undergone a comprehensive refactoring to implement modern INodeProperties interface system with full TypeScript compliance and code cleanup.

## Documentation Reference

**Always refer to these documentation files for detailed guides.** The compact list below is the index; **[Documentation Index](./docs-internal/documentation_index.md)** carries the full annotated table (one paragraph of load-bearing detail per document) and is the place to look before opening any of them.

**Architecture & contracts**
- [Schema Source of Truth RFC](./docs-internal/schema_source_of_truth_rfc.md) — backend is SSOT for node schemas / visuals / handlers / icons
- [Plugin System (Wave 11)](./docs-internal/plugin_system.md) — `BaseNode` / `ActionNode` / `TriggerNode` / `ToolNode`, `@Operation`, Routing DSL, self-contained plugin folders, the seven generic registries
- [Nodes Cookbook](./server/nodes/README.md) — 5-minute recipe, folder map, shared helpers, contract invariants, pitfalls
- [Node Creation Guide](./docs-internal/node_creation.md) — decision tree for action / trigger / tool / dual-purpose / specialized-agent nodes
- [Workflow Schema](./docs-internal/workflow-schema.md) · [Execution Engine Design](./docs-internal/DESIGN.md) · [Execution Roadmap](./docs-internal/ROADMAP.md)
- [Workflow Ops Protocol](./docs-internal/workflow_ops_protocol.md) — backend-driven canvas mutations
- [Event Framework](./docs-internal/event_framework.md) · [Event Waiter System](./docs-internal/event_waiter_system.md)
- [Node Allowlist](./docs-internal/node_allowlist.md) — single-config UI visibility
- [Polyglot Server](../polyglot-server/ARCHITECTURE.md) — optional plugin-registry microservice

**Frontend**
- [Frontend Architecture](./docs-internal/frontend_architecture.md) — React 19 + Vite + Tailwind v4 + shadcn/Radix + RHF/zod + TanStack Query + Zustand; tokens, primitives, forms, `uiHints` catalogue
- [Theme System](./docs-internal/theme_system.md) — 12-way theme system, six token tiers, `--node-color` contract, sound system. Read before adding a theme or a canvas-node component
- [Design System Bundle](./docs-internal/design-system/IMPLEMENTATION.md) — vendored canonical token/component reference
- [UI Migration Plan](./docs-internal/ui_migration_plan.md) — antd → shadcn migration plan + completion log
- [Node Parameter Panel](./docs-internal/node_panels.md) · [Credentials Panel](./docs-internal/credentials_panel.md)
- [Frontend Performance Architecture](./docs-internal/frontend_performance.md) · [Frontend Key Files](./docs-internal/frontend_key_files.md) · [UI Features](./docs-internal/ui_features.md)

**Agents, models, memory**
- [Agent Architecture](./docs-internal/agent_architecture.md) · [Agent Delegation](./docs-internal/agent_delegation.md) · [Agent Teams](./docs-internal/agent_teams.md)
- [AI Agent Tool System](./docs-internal/agent_tool_system.md) · [Tool Building Pipeline](./docs-internal/tool_building_pipeline.md)
- [Native LLM SDK](./docs-internal/native_llm_sdk.md) — protocol-based providers, 13 providers, `supports_model_listing`
- [Memory Compaction](./docs-internal/memory_compaction.md) · [Memory Lifecycle](./docs-internal/memory_lifecycle.md) (**stale — pre-RFC-0002**)
- [RLM Service](./docs-internal/rlm_service.md) · [Autonomous Agent Creation](./docs-internal/autonomous_agent_creation.md)
- [Skill Creation Guide](./server/skills/GUIDE.md)
- [Claude Code Agent](./docs-internal/claude_code_agent.md) — hub; then [CLI Agent Framework](./docs-internal/cli_agent_framework.md), [Interactive Mode](./docs-internal/claude_code_interactive_mode.md), [Canonical Patterns RFC](./docs-internal/cli_agent_canonical_patterns_rfc.md)
- Claude Code snapshots: [CLI Reference](./docs-internal/claude_code_cli_reference.md) · [Env Vars](./docs-internal/claude_code_env_vars_reference.md) · [Permission Modes](./docs-internal/claude_code_permission_modes_reference.md) · [Headless / Print Mode](./docs-internal/claude_code_headless_reference.md) · [Skills](./docs-internal/claude_code_skills_reference.md)

**Execution & Temporal**
- [Temporal Architecture](./docs-internal/TEMPORAL_ARCHITECTURE.md) — activities, dispatch matrix, worker pools, all `.env` tunables
- [Temporal Workflow Control](./docs-internal/temporal-workflow-control.md) — recovery policies, canvas editability, `can_edit`
- [Temporal Cleanup & Resilience Plan (Waves 15-18)](./docs-internal/TEMPORAL_CLEANUP_AND_RESILIENCE_PLAN.md) · [Temporal Execution Engine RFC](./docs-internal/temporal-execution-engine-rfc.md)
- [Temporal Operational Contract](./docs-internal/temporal_operational_contract.md) — months-long durability invariants + tracing ownership
- [Trigger Nodes](./docs-internal/trigger_nodes.md) · [Real-time Status WebSocket](./docs-internal/realtime_status_websocket.md) · [Status Broadcaster](./docs-internal/status_broadcaster.md)

**Services & integrations**
- [Backend Service Map](./docs-internal/backend_service_map.md) — the `server/services/` tree + Node.js code executor
- [Backend API Endpoints](./docs-internal/backend_api_endpoints.md) · [Server Documentation](./docs-internal/server-readme.md)
- [New Service Integration](./docs-internal/new_service_integration.md) · [CLI Services Integration](./docs-internal/cli_services_integration.md)
- [Media Transport](./docs-internal/media_transport.md) — files move as references, never bytes
- [Speech Provider RFC](./docs-internal/speech_provider_rfc.md) — provider-abstracted speech; [Translate / Transliterate / Detect](./docs-internal/speech_provider_rfc.md#8-what-this-pattern-should-absorb-next)
- [Browser Harness](./docs-internal/browser_harness.md) · [Proxy Service](./docs-internal/proxy_service.md) · [Email Service](./docs-internal/email_service.md) · [Pricing Service](./docs-internal/pricing_service.md) · [API Cost Tracking](./docs-internal/api_cost_tracking.md)
- CLI-managed-auth family: [Stripe](./docs-internal/stripe_service.md) · [Vercel](./docs-internal/vercel_service.md) · [GitHub](./docs-internal/github_service.md) · [Cloudflare](./docs-internal/cloudflare_service.md) · [Google Cloud](./docs-internal/gcloud_service.md) · [Sarvam AI](./docs-internal/sarvam_service.md)
- [WhatsApp Integration](./docs-internal/whatsapp_integration.md) · [Android Services](./docs-internal/android_services.md) · [Config Node Architecture](./docs-internal/config_nodes.md)
- [Process Manager](./docs-internal/process_manager.md) · [Example Workflows](./docs-internal/example_workflows.md) · [Onboarding Service](./docs-internal/onboarding.md)

**Security, auth, ops**
- [Authentication](./docs-internal/authentication.md) — read the Known Limitations section before building on it
- [Credentials Encryption](./docs-internal/credentials_encryption.md) — Fernet + PBKDF2, two credential systems, multi-backend
- [CI/CD Pipeline](./docs-internal/ci_cd.md) · [Release Build Pipeline](./docs-internal/release_build_pipeline.md) · [Performance](./docs-internal/performance.md)
- [Setup Guide](./docs-internal/SETUP.md) · [Scripts Reference](./docs-internal/SCRIPTS.md) · [Logging & Error Handling](./docs-internal/logging_and_errors.md) · [Cache System](./docs-internal/cache_system.md)
- [Known Errors & Troubleshooting](./docs-internal/errors.md)
- [Deployment (legacy reference)](./docs-internal/deployment_legacy.md) · [GCP VM Deploy Runbook](./docs-internal/gcp_vm_deploy_runbook.md)

**History & invariants**
- [Invariants & Notes](./docs-internal/invariants.md) — the long-form list of load-bearing decisions, gotchas, and "do not reintroduce" rules. Check it before re-solving anything that looks already-solved.
- [Status History](./docs-internal/status_history.md) · [Planned Features](./docs-internal/planned_features.md) · [Node Logic Flows](./docs-internal/node-logic-flows/)

## Design Principles & Standards

**CRITICAL: Always follow these principles when modifying backend execution code:**

### 0. Adding a new node — the canonical recipe (Wave 11.H)

Every plugin is a self-contained folder under `server/nodes/<group>/<plugin>/` rooted at `__init__.py`. `BaseNode.__init_subclass__` auto-registers metadata, schemas, handlers, and Temporal activity on import — zero edits anywhere else.

**Where to look:**
- [server/nodes/README.md](./server/nodes/README.md) — 5-minute walkthrough with the canonical folder template
- [docs-internal/plugin_system.md → Self-contained plugin folders](./docs-internal/plugin_system.md#self-contained-plugin-folders) — full reference, plus the **up-to-seven generic registries** plugins self-wire into (`register_ws_handlers`, `register_router`, `register_filter_builder`, `register_trigger_precheck`, `register_service_refresh`, `register_output_schema`, `register_agent_context_builder`)
- [docs-internal/node_creation.md](./docs-internal/node_creation.md) — decision tree for action / trigger / tool / dual-purpose / specialized-agent nodes
- [server/nodes/telegram/](./server/nodes/telegram/) — reference implementation of the multi-file split (`_service.py` / `_handlers.py` / `_filters.py` / `_refresh.py` / `_credentials.py` / `_events.py` / two node files)

**Wire format is the contract — not module paths.** The frontend identifies plugin commands by WebSocket message-type strings (`telegram_connect`, `telegram_status`, …). Moving handler bodies between Python files is invisible to the frontend so long as the registered keys stay the same.

**Don't** import the plugin folder from `routers/` / `services/` / another `nodes/` subfolder. **Don't** edit `event_waiter.py` / `status_broadcaster.py` / `routers/websocket.py` to add a plugin's handler / filter / refresh — register from the plugin's `__init__.py` instead.

### 1. Use Existing Patterns - No Tribal Code
- **Never add ad-hoc workarounds** - Use the established patterns documented in DESIGN.md
- **Conductor Decide Pattern** - All orchestration goes through `_workflow_decide()` loop
- **Continuous Scheduling** - Dependent nodes start immediately via `asyncio.wait(FIRST_COMPLETED)`; the layer-barrier Fork/Join helper (`_execute_parallel_nodes`) was removed
- **Prefect Task Caching** - Cache results via `hash_inputs()` and `generate_cache_key()`
- **Distributed Locking** - Use Redis SETNX pattern for concurrent access control

### 2. State Management
- **Isolated Execution Contexts** - Each workflow run has its own `ExecutionContext`
- **No Global State** - Never use module-level variables for execution state
- **Cache Persistence** - Execution state persists to Redis (production) or SQLite (local development)
- **Explicit State Machines** - Tasks follow `TaskStatus` enum, workflows follow `WorkflowStatus`

### 3. Separation of Concerns
- **Models** (`models.py`) - Pure data structures, JSON-serializable, no business logic
- **Cache** (`cache.py`) - Redis persistence abstraction only
- **Executor** (`executor.py`) - Orchestration logic, decide pattern implementation
- **Recovery** (`recovery.py`) - Heartbeat and crash recovery only
- **Conditions** (`conditions.py`) - Edge condition evaluation for runtime branching

The full `server/services/` module map (and the Node.js code-executor topology) is in **[Backend Service Map](./docs-internal/backend_service_map.md)**.

### 4. Dependency Injection
```python
# Correct: Receive dependencies via constructor
class WorkflowExecutor:
    def __init__(self, cache: ExecutionCache, node_executor: Callable):
        self.cache = cache
        self.node_executor = node_executor

# Wrong: Import and use global singletons
from services.some_service import global_instance
```

### 5. Error Handling & Logging
- **Log at appropriate levels**: DEBUG for routine operations, INFO for significant events, ERROR for failures
- **Never suppress errors silently** - Always log or propagate
- **Use structured logging** - Include context (node_id, execution_id, etc.) — bind once via `log_context(...)`; `BaseNode.execute()` already wraps plugin bodies
- **Configurable via `.env`**: `LOG_LEVEL`, `LOG_FORMAT`, `LOG_FILE` (+ rotation caps)
- **`NodeUserError` vs `Exception` contract**: `NodeUserError` → one WARN line, no traceback, structured envelope; annotated `PermissionError` → credential envelope + CloudEvents broadcast; bare `Exception` → `logger.exception` with full traceback. Reach for `NodeUserError` for any user-correctable failure; reserve `RuntimeError`/`Exception` for genuine server bugs.
- **Output contract enforcement**: the declared `Output` Pydantic model is enforced at the serialization boundary in `BaseNode._serialize_result`. Prefer returning the `Output` instance; never put raw third-party objects or pre-stringified JSON in results.

Console mode is timestamp-less by design (the supervisor prefixes `[HH:MM:SS.fff]`). Source-tag resolution, the `_LOG_SOURCE_TAGS` registry, OpenTelemetry spans, and the full config table are in **[Logging & Error Handling](./docs-internal/logging_and_errors.md)**.

### 6. Cleanup & Lifecycle
- **Use existing teardown methods** - e.g., `_teardown_all_cron_triggers()` for cron cleanup
- **Cleanup in finally blocks** - Ensure resources are released even on error
- **No orphan prevention hacks** - Trust the existing lifecycle management

### 7. Frontend Design + Theme System (strict)

**Always use the existing design and theme systems.** Tribal styling reintroduced anywhere defeats the migration. The following rules are non-negotiable for any new or edited frontend file:

1. **Compose shadcn primitives** from [client/src/components/ui/](./client/src/components/ui/) — `Button`, `Badge`, `Alert`, `AlertDialog`, `Dialog`, `DropdownMenu`, `Select`, `Popover`, `Tooltip`, `Tabs`, `Card`, `Input`, `Textarea`, `Switch`, `Checkbox`, `Slider`, `Label`, `Form`, `Collapsible`, `Accordion`, `Skeleton`, `Sonner`. **Do not hand-roll** modals, dropdowns, menus, toasts, dialogs, or buttons when a primitive exists. Add `npx shadcn@latest add <name>` if the primitive is missing.
2. **Action buttons → `<ActionButton intent="...">`** ([client/src/components/ui/action-button.tsx](./client/src/components/ui/action-button.tsx)). The `intent` prop is a semantic role (`run | stop | save | config | secret | tools`), never a palette color. Never re-introduce the `actionButtonStyle()` / hand-built colored buttons.
3. **Style with Tailwind classes**, not `style={{...}}`. Inline `style` is allowed only for genuinely dynamic values (React Flow `<Handle>` positioning, runtime-computed coordinates, dynamic per-definition `nodeColor` on canvas nodes).
4. **Use the token tier table** in [docs-internal/frontend_architecture.md](./docs-internal/frontend_architecture.md#tokens--theming):
   - Generic chrome / status → shadcn semantic tokens (`bg-card`, `text-muted-foreground`, `border-border`, `text-success`, `bg-destructive`, `text-warning`, `text-info`, `bg-accent`, etc.)
   - Node-type-themed surfaces → `--node-X` role tokens (`bg-node-agent`, `bg-node-model-soft`, `border-node-skill-border`, `text-node-trigger`, `text-node-workflow`, `bg-node-tool-soft`)
   - Toolbar / panel actions → `--action-X` semantic role tokens (`bg-action-run-soft`, `text-action-stop`, `border-action-config-border`, etc.) for icon-only buttons + dropdown items; `<ActionButton intent="...">` for the standard "soft tinted button" pill
   - **No palette names in components.** `bg-dracula-green` etc. are forbidden in non-decorative code; always go through `--action-X` or `--node-X`
5. **No opacity arithmetic at call sites.** `bg-primary/10`, `border-node-agent/30`, `${color}25` template literals are forbidden. If a unique tint is needed, add a new variant to the theme (e.g., `--node-X-soft`, `--node-X-border`) and use it by name.
6. **No theme-locked names in non-decorative code.** Avoid `bg-dracula-purple`, `text-dracula-cyan`, etc. unless the constant accent is intentional (action-button palette). Prefer the role token (`bg-node-agent`) so future themes redefine without code edits.
7. **No `useAppTheme()` in new files.** It is grandfathered for the canvas node components and `EdgeConditionEditor` only because they interpolate per-definition `nodeColor`. Every other surface uses Tailwind + the tokens above.
8. **Icons → `lucide-react`.** Inline SVGs are reserved for non-iconographic graphics (charts, decorative shapes). Replace any `<svg>...</svg>` icon you encounter while editing.
9. **Any `draggable` element that performs a function must ship a pointer-operable, non-drag control reaching the same end state through the same write path.** WCAG 2.2 SC 2.5.7 (Level AA); the sufficient technique is [G219](https://www.w3.org/WAI/WCAG22/Techniques/general/G219), the failure is [F108](https://www.w3.org/WAI/WCAG22/Techniques/failures/F108). Two traps worth stating: **keyboard support does not discharge it** — the Understanding doc is explicit that an equivalent counts only "*unless that equivalent keyboard operation also provides controls that can be clicked or tapped with a pointer*", because touchscreen users may have no keyboard. And the alternative must operate *the same function*, so extract the write into a shared helper rather than reimplementing it — see [`lib/workspaceFileAssign.ts`](./client/src/lib/workspaceFileAssign.ts), which both `ParameterRenderer.handleDrop` and `WorkspaceFilePickerDialog` call, with a test asserting the two paths produce deep-equal results.

When in doubt, read [docs-internal/frontend_architecture.md](./docs-internal/frontend_architecture.md) before introducing new patterns.

### 8. Naming Conventions (strict)

| Layer | Convention | Examples |
|---|---|---|
| Python identifier (function, variable, module, file) | `snake_case` | `get_user_settings`, `auth_service`, `node_allowlist.py` |
| JSON config key (read by Python) | `snake_case` | `enabled_nodes`, `default_llm_provider`, `compaction_ratio` |
| WebSocket message type (Python ↔ TS wire) | `snake_case` | `get_node_allowlist`, `save_user_settings`, `validate_api_key` |
| Database column / SQLModel field | `snake_case` | `created_at`, `auto_save_interval`, `examples_loaded` |
| Python class | `PascalCase` | `NodeAllowlistService`, `WorkflowExecutor` |
| TypeScript identifier | `camelCase` | `useNodeAllowlist`, `enabledNodes`, `isVisible` |
| TypeScript file (React hook) | `camelCase` starting with `use` | `useNodeAllowlist.ts`, `useWebSocket.ts` |
| Node type identifier | stored verbatim — **do not transform** | `aiAgent`, `httpRequest`, `openaiChatModel` (currently camelCase in this repo) |

**Crossing the wire**: payload keys between Python and TS are always `snake_case` (Python writes the payload). The TS hook receives `snake_case` keys and binds them to local `camelCase` variables; do not auto-transform across languages with a serializer.

Do not invent kebab-case or PascalCase variants for any of the rows above. The existing codebase is internally consistent — match it.

### 9. Cache System Architecture (n8n Pattern)

Automatic fallback with no code branching at call sites: production (Docker) `Redis → SQLite → Memory`; local development `SQLite → Memory` (`REDIS_ENABLED=false`). `CacheService` (`server/core/cache.py`) owns the fallback; `CacheEntry` (`server/models/cache.py`) is the SQLite model; CRUD + TTL cleanup live on `server/core/database.py`. Full code walkthrough in **[Cache System](./docs-internal/cache_system.md)**.

## Codebase Summary
- **Hybrid architecture**: Python (FastAPI + Pydantic plugins) + React/TypeScript frontend + Node.js subprocess for JS/TS code execution.
- **Backend NodeSpec is the single source of truth.** Plugins live in [`server/nodes/<group>/<name>.py`](./server/nodes/) and auto-register via `BaseNode.__init_subclass__`. Authoritative node count is whatever globs out of `server/nodes/**/*.py` (excluding `_*.py` helpers and `__init__.py`); folders cover agent / model / android / google / whatsapp / twitter / telegram / social / email / search / scraper / document / code / filesystem / proxy / location / chat / text / scheduler / trigger / tool / utility / workflow / skill / browser / stripe / vercel / github / cloudflare / gcloud / sarvam.
- **WebSocket-first frontend-backend communication.** Authoritative handler count is the size of the `MESSAGE_HANDLERS` dict in [`server/routers/websocket.py`](./server/routers/websocket.py) plus plugin-registered handlers via `services.ws_handler_registry`. Don't hand-maintain the count in this doc — it drifts on every plugin add.
- **Plugin-first architecture (Wave 11).** One file = one node. `services/handlers/` shrank from 12.8K → 1.1K LOC across 16 → 4 files. Live invariant total via `pytest --collect-only`.

## Frontend Performance Architecture

The frontend uses a layered cache + slice-subscription model so cold refreshes are instant and high-frequency status broadcasts do not cascade through the React tree. The rules below are canonical; the full reference (with file links and rationale) is **[Frontend Performance Architecture](./docs-internal/frontend_performance.md)**.

- **TanStack Query persistence** — only `nodeSpec` / `nodeGroups` / `pluginCatalogue` prefixes are dehydrated to localStorage (`__APP_VERSION__` buster, 24h SWR window). Any persisted prefix MUST also have matching `queryClient.setQueryDefaults` in `lib/queryClient.ts` — per-call options don't apply on hydration.
- **`useNodeSpec` is a slice subscription, not a `useQuery`.** Do not re-introduce `useQuery(['nodeSpec', type])` — N consumers would create N observers. **Critical: any cache entry consumed via `useSyncExternalStore` MUST set `gcTime: GC_TIME.FOREVER`**, or TanStack GCs it after 5 min and every consumer reads `undefined` (symptom: canvas nodes lose icons + handles after idling).
- **`nodeStatusStore`** owns per-workflow node statuses; mirror this Zustand slice pattern for any new high-frequency push state. Never put it on `WebSocketContext.value`.
- **`useAppStore` reads must be slice selectors** — `useAppStore((s) => s.x)`, never whole-store destructure (that re-renders on ANY mutation and defeats `React.memo` + `nodePropsEqual`).
- **Gate every catalogue/spec query on `isReady`, not `isOpen`.** `isReady` flips only after the parallel `Promise.allSettled` init burst settles; the send queue drains before it is set.
- **Catalogue invalidation is debounced** — always go through `invalidateCatalogue(queryClient)` (300 ms trailing edge), never direct `invalidateQueries`.
- **`React.memo` every canvas node component** with the shared `nodePropsEqual` comparator (skips drag-state props).
- **Icon + color** resolve per-plugin folder first (`<plugin>/icon.svg`, `<plugin>/meta.json`), with `visuals.json` as the emoji / library-brand / skill-reverse-map fallback. Do not declare `icon` / `color` as class attributes on a node.

## Key Files & Components

Core types, node-system entry points, assets, UI components, AI chat-model components, specialized UI, hooks & state, theme system, and the WebSocket-first surface are inventoried in **[Frontend Key Files](./docs-internal/frontend_key_files.md)**.

**Canvas mutations from the backend** — any handler that needs to add / move / delete nodes or edges returns a workflow-ops batch (`{operations: [...]}`) applied through `applyOperations` in [client/src/lib/workflowOps.ts](./client/src/lib/workflowOps.ts); builders live in [server/services/workflow_ops.py](./server/services/workflow_ops.py). Full spec: [docs-internal/workflow_ops_protocol.md](./docs-internal/workflow_ops_protocol.md).

## Implemented Node Types

> **Authoritative source: backend plugin registry.** Read the live total from `len(services.node_registry.NODE_METADATA)` — a bare `__init__.py` glob overcounts by also matching group packages. Do NOT maintain a per-node catalogue in this file; it drifts on every plugin add. The per-node "logic-flow" cards (handles / params / outputs / side-effects / edge-cases) live under [docs-internal/node-logic-flows/](./docs-internal/node-logic-flows/).

Node groups (palette categories): agent, model, skill, tool, trigger, workflow, search, google, android, whatsapp, telegram, twitter, social, email, proxy, chat, scheduler, text, code, document, location, utility, browser, scraper, filesystem, stripe, vercel, github (palette group `vcs`), cloudflare and gcloud (palette group `deployment`), speech and translate (both palette group `language` — provider-abstracted `textToSpeech` / `speechToText` and `translateText` / `transliterateText` / `detectLanguage`; `nodes/sarvam/` was retired into them, and only `sarvamChatModel` under `nodes/model/` remains vendor-named).

## Backend Services

Python FastAPI backend on `PYTHON_BACKEND_PORT` (defaults in `.env.template`), entry point `server/main.py`. The endpoint inventory (Android, remote-Android WebSocket, webhook router, workspace router, workflow services, frontend WebSocket), the development scripts, and the concurrently process-management fix are in **[Backend API Endpoints](./docs-internal/backend_api_endpoints.md)**.

### Temporal Distributed Execution

Workflows execute via Temporal for durability and horizontal scaling, gated by `TEMPORAL_ENABLED`, with per-queue activity routing production-default (Wave 16) and fallback Temporal → sequential. Full architecture, dispatch matrix, per-node + agent-loop lifecycle, worker tuning, and every `.env` tunable: **[Temporal Architecture](./docs-internal/TEMPORAL_ARCHITECTURE.md)**.

**Load-bearing operational contract — read before touching Temporal:** the months-long durability invariants (no `execution_timeout` on child starts, continue-as-new under history pressure, controllers addressed by workflow id only, `workflow.patched(...)` guards, `TEMPORAL_TERMINATE_RUNNING_ON_STARTUP=false`, recovery policies, workflow-scoped event delivery, server-owned `can_edit`) and the strict tracing-ownership rule (register `TracingInterceptor` exactly once on the shared client, never again on workers) are in **[Temporal Operational Contract](./docs-internal/temporal_operational_contract.md)**.

## Development Commands

### CLI Commands (after the global install)
```bash
company start        # Start all services (production mode)
company dev          # Start all services in dev mode (Vite HMR)
company dev --force  # ...forcing Vite to re-bundle deps (recovers "Outdated Optimize Dep"; sets VITE_FORCE -> optimizeDeps.force — the dep cache is otherwise preserved across boots)
company stop         # Stop all services
company build        # Build for production
company clean        # Clean build artifacts
company help         # Show all commands
```

### npm Scripts
```bash
# Core (thin wrappers over the Python CLI)
npm run start            # Start all services (python -m cli start)
npm run stop             # Stop all services (python -m cli stop)
npm run build            # Build for production (python -m cli build)
npm run clean            # Clean build artifacts (python -m cli clean)
npm run deploy           # Self-deploy to a cloud VM (python -m cli deploy)
```

### Cross-Platform Scripts
Service orchestration lives in the Python CLI (`company start/dev/stop/build/clean/serve/daemon/deploy/docs/version` — see `cli/`). The `scripts/` directory retains only the npm install lifecycle helpers (`install.js`, `preinstall.js`, `postinstall.js`). `company start` is single-port: uvicorn serves API + WS + built SPA on the backend port (`SERVE_STATIC_CLIENT`, default on); the retired `scripts/serve-client.js` static server and its `:3000` frontend port are gone.

See **[Scripts Reference](./docs-internal/SCRIPTS.md)** for full documentation.

## Current Status

The feature-completion checklist and the file-structure cleanup log (removed files, cleaned code) are in **[Status History](./docs-internal/status_history.md)**.

## Key Features

The parameter system, node rename system (F2 / double-click / context menu), UI state persistence, Normal/Dev mode, Console Panel (chat + console persistence), per-workflow workspace directory, Workflow Naming (Wave 14 — `id` / `name` / `slug` separation, Temporal workflow-ID convention, rename path, invariants), execution system, event-driven deployment architecture, the WebSocket hooks, and the conditional-parameter-display implementation are all in **[UI Features](./docs-internal/ui_features.md)**.

### AI Chat Model System (5-Layer Architecture)

Chat-model nodes (`openaiChatModel`, `anthropicChatModel`, ...) render through `SquareNode` from the backend NodeSpec. Direct chat and every new agent execution route through the native SDK facade (`ChatUnifier` in `services/llm/`); the 12-provider surface is 10 cloud providers plus Ollama and LM Studio. Eleven providers have standalone chat-model nodes, while xAI is selected directly from agent parameters. Model params (max output, context length, thinking type, temperature range) come from `ModelRegistryService`. The provider architecture, proxy/local-LLM routing, and the per-provider model + thinking/reasoning matrix (budget / effort / format) all live in **[Native LLM SDK](./docs-internal/native_llm_sdk.md)**. A Temporal history recorded before the native cutover carries no `llm_engine` marker and messages in a retired wire format; `agent.execute_llm_step` refuses it with a non-retryable `InvalidAgentLLMEngine` rather than misreading it, and the deployment must be Reset. The runtime output schema (`thinking` field for downstream nodes) is backend-served per [Schema Source of Truth RFC](./docs-internal/schema_source_of_truth_rfc.md).

## AI Agent Node Architecture

AI Agent (`aiAgent`) and Chat Agent / Zeenie (`chatAgent`) both use the plain-async `run_native_agent_loop` in `server/services/agent_runtime.py` and support memory / skills / tools / task input. `AIService.execute_agent()` and `execute_chat_agent()` prepare the same canonical native messages and `AgentToolSpec` values, then the loop appends each lossless assistant message before executing its tool calls, hot-rebinds the tool surface after canvas mutations, and stops when the model returns no tool calls (with `max_iterations` as a safety cap). Connection collection is `collect_agent_connections` in `server/services/plugin/edge_walker.py` (5-tuple: memory, skill, tool, input, task); the pre-Wave-11 `handle_ai_agent`/`handle_chat_agent` handlers are gone (dispatch is per-plugin `execute_op` under `server/nodes/agent/<plugin>/__init__.py`). `_run_agent_loop` remains only for replaying pre-cutover or explicitly legacy-pinned Temporal histories.

**`max_iterations` precedence (highest->lowest): per-node `parameters.max_iterations` > `UserSettings.agent_recursion_limit` > env `AGENT_RECURSION_LIMIT` (default 200) > `llm_defaults.json:agent.recursion_limit`.**

Full reference — agent loop, skill injection, tool building, input/auto-prompt fallback (message>text>content>str), handle topology, spec-driven `AIAgentNode`, durable Task Manager delegation (Temporal child workflows plus the legacy bridge), and specialized-agent routing — in [docs-internal/agent_architecture.md](./docs-internal/agent_architecture.md); low-level compatibility mechanics in [agent_delegation.md](./docs-internal/agent_delegation.md), and the authoritative team-lead contract in [agent_teams.md](./docs-internal/agent_teams.md).

## AI Agent Tool System

Tool nodes connect to an agent's `input-tools` handle and expose a schema the LLM can call. The discovery → schema-building → provider-compilation → execution → result-return flow, the tool execution animation, the implemented-tools table, the direct Android service tools, the per-service tool-schema store, the web-search implementations, and the **"adding a new tool or specialized agent"** recipe (including the small set of cross-cutting edits still required) are in **[AI Agent Tool System](./docs-internal/agent_tool_system.md)**.

## Architecture Patterns
- **Plugin-first (Wave 11).** One folder per plugin under [`server/nodes/<group>/<plugin>/`](./server/nodes/) rooted at `__init__.py`, subclassing `BaseNode` / `ActionNode` / `TriggerNode` / `ToolNode`. Auto-registers via `__init_subclass__`. See [`docs-internal/plugin_system.md`](./docs-internal/plugin_system.md).
- **Backend NodeSpec is the SSOT** for icon, colour, handles, params, output schema, uiHints, palette group. Frontend consumes via `useNodeSpec(type)` and adapts the JSON Schema → `INodeTypeDescription` shape through [`adapters/nodeSpecToDescription.ts`](./client/src/adapters/nodeSpecToDescription.ts) (legacy interface kept as a render contract; not a parallel schema system).
- **Component-driven frontend.** shadcn/ui primitives + Tailwind tokens; canvas nodes are spec-driven.
- **State management.** TanStack Query owns server-backed data; Zustand (`useAppStore`, `nodeStatusStore`) owns UI state and slice-subscribed high-frequency push state. Slice-selector reads only — never whole-store destructure (see "Frontend Performance Architecture").
- **Execution pipeline.** Temporal-distributed activities for plugin execution; `WorkflowExecutor` for parallel orchestration; per-node retry / timeout / heartbeat declared on the plugin class.

## Config Node Architecture

Config nodes (context, tools, models, skills, teammates) connect to a parent via `input-<type>` handles that are NOT `input-main`. The handle convention, the auto-derived `isConfigNode` uiHint (plugins in group `memory` or `tool` get it for free — never hand-declare it), input inheritance in the parameter panel, the filtering logic, and sub-node execution exclusion are in **[Config Node Architecture](./docs-internal/config_nodes.md)**.

## Testing & Validation
```bash
# Development server test
curl -I http://localhost:${PYTHON_BACKEND_PORT:-5678}

# TypeScript validation — the gate is TypeScript 7 (native Go) at the REPO ROOT.
pnpm run typecheck                              # root: tsc --noEmit -p client/tsconfig.json
pnpm --filter react-flow-client run typecheck   # what CI runs; delegates up to the same gate
# NOT `npx tsc --noEmit` — there is no root tsconfig.json.
# NOT client's `typecheck:tsc` — that resolves typescript@5.9.3, kept only because
# typescript-eslint's peer range excludes 6/7. It is a second opinion, not the gate.

# Build verification
npm run build
```

## Production Deployment

### Self-Deploy CLI (`company deploy`) — current path
One command provisions a login-gated OpenCompany VM on a cloud provider. Two stages: the
operator's **cloud CLI** (gcloud; aws planned) handles auth + project/region/zone resolution +
ADC verification + API enablement, then **Terraform** (`cli/terraform/gcp/`) owns all resources —
VM (new deployments use the `opencompany` resource id), firewall, artifact bucket (local `npm pack` source), service
account, and a cloud-init startup script that installs Node 22 + uv + the package and runs
`company serve` under systemd. Login gate = built-in auth (`VITE_AUTH_ENABLED=true`,
`AUTH_MODE=single`) with the owner credential generated at deploy time and seeded on first boot.
`build_app_env` (`cli/commands/deploy/_secrets.py`) also sets `DEPLOYMENT_MODE=cloud` on
deployed VMs and mints fresh `JWT_SECRET_KEY` / `SECRET_KEY` / `API_KEY_ENCRYPTION_KEY` per deploy.

```bash
company deploy up --provider gcp --owner-email you@example.com   # provision + install + print URL/creds
company deploy status                                            # URL + /health
company deploy destroy                                           # terraform destroy + clear state
```

Key files: `cli/commands/serve.py` (single-port runtime: uvicorn fronts API + WS + built SPA, plus
the node sidecar), `cli/commands/deploy/` (verbs, secrets, Terraform driver, provider CLI adapters),
`cli/terraform/gcp/` (HCL module + `startup.sh.tftpl`). Deployment state lives at
`<user-data>/deploy/opencompany/` (preserved by `company clean` — see `_OPENCOMPANY_KEEP`); only
`company deploy destroy` removes it. The deploy code is fully delinked from `company build` /
`company clean` (lazy verb stubs in `cli/cli.py`; nothing in the build pipeline imports it).
For upgrades, `_state.py` also discovers pre-rebrand `deploy/machinaos/` state
under the configured root, `~/.machina`, or `<repo>/.machina`. Such deployments
retain their durable `machinaos` cloud/systemd id; changing it would cause
Terraform replacement or strand live state. Fresh deployments use `opencompany`.
The `machina` executable remains only as a deprecated legacy alias; use `company`
for all new commands and automation.

The legacy `deploy.sh` (docker-compose images over SCP to a GCE box) was removed. The historical Docker Compose topology (4-container stack, nginx reverse proxy, compose files, env config, resource usage, commands) is preserved in **[Deployment (legacy reference)](./docs-internal/deployment_legacy.md)**.

## Authentication System

n8n-style JWT auth in HttpOnly cookies. `VITE_AUTH_ENABLED=false` bypasses login (anonymous owner, dev); when enabled, `AUTH_MODE=single` (first user = owner, registration then closed) or `multi` (open registration). Backend: `User` (bcrypt) + `UserAuthService` + `/api/auth/*` router + `AuthMiddleware` (public-path allowlist + `/webhook/` prefix). `/login` and `/register` are throttled by the in-process `core/rate_limit.py` sliding window (`AUTH_RATE_LIMIT_*`; no `slowapi` dependency — the primary runtime is a single uvicorn worker). Frontend: `AuthContext` (TanStack-Query bootstrap with full-jitter backoff, plus `useMutation` for login/register/logout) + `ProtectedRoute` + `LoginPage` (RHF + zod via the shadcn `Form` primitives); all API calls send `credentials: 'include'`, and the WebSocket refuses to connect without the cookie.

**Two context distinctions that are load-bearing, not stylistic:** `isLoading` is the bootstrap query (gates the whole app in `ProtectedRoute`) while `isSubmitting` is per-request — using the former to disable the login form disables nothing, since it has already settled by the time that form renders. And `error` means "cannot reach the server" while `submitError` is the server's own rejection text; a `setQueryData` write is a *success* value, so routing a login failure through the status cache surfaces no error at all and additionally collapses `can_register`.

**Read the Known Limitations section of [authentication.md](./docs-internal/authentication.md) before building on this.** `AUTH_MODE=multi` provides authentication but no data isolation — `request.state.user_id` is written by the middleware and read by nothing, so all users share one workflow store and one credential store. There is also no CSRF token and no token revocation (`User.is_active` is the only lever).

**Load-bearing rule:** JWT handling uses **PyJWT** (`import jwt`, HS256 with `Settings.jwt_secret_key`). Do NOT reintroduce `python-jose` — it drags in pure-Python `ecdsa` with the unpatchable Minerva timing-attack advisory (GHSA-wj6h-64fc-37mp). Full reference (models, router, middleware, config, startup retry, key files, deps) in **[Authentication](./docs-internal/authentication.md)**.

## Encrypted Credentials System

API keys and OAuth tokens live in a separate encrypted database (`credentials.db`): Fernet (AES-128-CBC + HMAC-SHA256) with the key derived via PBKDF2HMAC-SHA256 (600K iterations, OWASP-2024) from the server-scoped `API_KEY_ENCRYPTION_KEY` (`.env`) + a salt stored in `credentials.db`, initialized at startup and held for the process lifetime. Two distinct systems that never cross: API keys (`store_api_key`/`get_api_key` → `EncryptedAPIKey`) and OAuth tokens (`store_oauth_tokens`/`get_oauth_tokens` → `EncryptedOAuthToken`). Multi-backend (Fernet default / Keyring / AWS Secrets Manager) via `CREDENTIAL_BACKEND`.

**Load-bearing rule:** every credential operation MUST go through `AuthService` (`from core.container import container; container.auth_service()`); routers must NEVER touch `CredentialsDatabase` directly. Full pipeline, cache contract, backends, config, key files, and design decisions are in **[Credentials Encryption](./docs-internal/credentials_encryption.md)**.

## Example Workflows

Pre-built workflow templates auto-load on first workflow-list fetch, gated by `UserSettings.examples_loaded`. Seeds live as JSON at **`<repo>/.opencompany/workflows/`** — the only git-tracked content under `<repo>/.opencompany/`, resolved by `core.paths.example_workflows_dir()` (fixed path, NOT under `DATA_DIR`) and preserved by `company clean`. The JSON format, auto-load logic, loader service, custom-example recipe, and the `examples_loaded` migration are in **[Example Workflows](./docs-internal/example_workflows.md)**.

## Onboarding Service

Multi-step welcome wizard shown on first launch — database-backed (`UserSettings.onboarding_completed` + `onboarding_step`), skippable, resumable, replayable from Settings, and auto-skipped for existing users (migration sets `onboarding_completed=1` where `examples_loaded=1`). Built with shadcn primitives (no antd). Full step list, key files, replay flow, and how to add a step are in **[Onboarding Service](./docs-internal/onboarding.md)**.

## AI Chat Model Development Guide

A new chat-model provider is one self-contained folder under `server/nodes/model/<provider>_chat_model/` with `__init__.py` declaring a `ChatModelBase` subclass (auto-registers via `BaseNode.__init_subclass__`; the frontend renders it through `SquareNode` from the NodeSpec with zero TS changes). Credentials live in `server/nodes/model/_credentials.py`. The full recipe — native provider registration under `services/llm/providers/`, `llm_defaults.json` configuration, the `_COMPAT_PROVIDERS` entry required for OpenAI-compatible endpoints, and the per-provider implementation-file map — is in **[Native LLM SDK](./docs-internal/native_llm_sdk.md)**.

## Context and Memory (RFC-0002)

Two different things, deliberately separated. Read [RFC-0002](./RFC-0002-AGENT-CONTEXT-AND-MEMORY.md) before touching either.

**Context** is the backend-owned execution journal — what the agent actually sent and received. The `context` node (`server/nodes/context/`, `input-context` handle) is a **read-only observation surface onto it**. Load-bearing invariant, learned the hard way: *attaching a Context node must never change what the agent sends.* It once did — `context_ref` in the LLM payload selected a second implementation that rebuilt the request from the journal instead of sending `messages`, and the rebuilt transcript dropped the user's prompt, so connecting a Context node made the agent answer an empty question. There is now exactly one LLM step; `context_ref` only says *where to record*.

The journal records, it never reconstructs. `agent.execute_llm_step` writes each turn from the exact message list it hands to `ChatUnifier.chat` (`_journal_llm_turn`), immediately after the call returns. `agent.prepare_context` deliberately journals nothing — it runs before the request exists, so anything it wrote would be assembled from configuration. Journal operation ids derive from the per-firing `context_execution_id`, **not** `execution_id`: the latter is generation-scoped, so every message in a generation minted identical ids and the store's idempotency guard silently discarded every turn after the first.

A Context thread exists only under an admitted generation (`generation > 0`), which only Start assigns — manual canvas Runs journal nothing by design. Each generation gets its own thread, so conversation does not carry across a Stop/Start. Workflow Reset rotates the thread to a fresh epoch and leaves prior events as archived history; the panel's journal view is scoped to the live epoch, or a reset looks like it did nothing.

**Memory** (`simpleMemory`, plugin `server/nodes/tool/simple_memory/`) is a `ToolNode` on `input-tools` — durable facts the agent explicitly remembers, recalls, updates and forgets. It is not conversation history and has no markdown surface; `SimpleMemoryParams` declares only `reset_policy` (with `extra="ignore"`, so leftover legacy keys on migrated graphs are inert). `reset_policy` is in `server_controlled_fields`, which stops the **model** overriding it through tool arguments — it does not stop the operator editing it.

Lifecycle helpers live in `server/services/memory/`; token tracking and compaction thresholds are in **[Memory Compaction](./docs-internal/memory_compaction.md)**. **[Memory Lifecycle](./docs-internal/memory_lifecycle.md)** still documents the pre-RFC-0002 markdown model and is stale.

## Memory Compaction, Token Tracking, and Cost Calculation

Memory-connected standard agents aggregate native `Usage` across every model
turn. The in-process path calls `CompactionService.track()` after execution to
persist session metrics and can trigger `compact_context()`, which performs a
shared client-side summarization call through `ChatUnifier`. The Temporal
`AgentWorkflow` also aggregates and returns loop usage and can invoke the same
summarizer, but it does not currently persist that loop aggregate through
`CompactionService.track()`. Provider-native Anthropic/OpenAI context-management
compaction is not used by the agent runtime. Executions without connected
memory still aggregate usage inside the loop but do not create session
compaction records.

**Threshold precedence inside `CompactionService.track()` (highest-to-lowest): per-session `SessionTokenState.custom_threshold` > per-user `UserSettings.compaction_ratio` > env `COMPACTION_RATIO` (default 0.8) > `llm_defaults.json:agent.compaction.ratio`.** The Temporal agent workflow currently prepares its threshold from the model/user/env ratio without reading the per-session custom threshold, so do not promise that override on every execution path.

Full reference — the `CompactionService` API, shared client-side compaction, the 5-section summary format, DB models (`TokenUsageMetric` / `SessionTokenState` / `CompactionEvent`), WS handlers, and the broadcast events — in **[Memory Compaction](./docs-internal/memory_compaction.md)**; per-service API cost tracking is in **[Pricing Service](./docs-internal/pricing_service.md)**.

## API Cost Tracking

Centralized cost tracking for third-party API services (Twitter/X, Google Maps) with two methods — manual tracking for native-SDK services and automatic HTTPX event-hook tracking via `services/tracked_http.py`. All pricing lives in the user-editable `server/config/pricing.json`; usage rows land in `APIUsageMetric`. Details in **[API Cost Tracking](./docs-internal/api_cost_tracking.md)** and **[Pricing Service](./docs-internal/pricing_service.md)**.

## Android Services

Android service nodes are backend plugins under `server/nodes/android/<service>.py` subclassing the shared `AndroidServiceBase` (`_base.py` owns `SERVICE_ID_MAP` — camelCase node type → snake_case service id). Device connection is configured in the **Credentials Modal** (Android panel), not via workflow nodes, and uses a two-state model: `connected` (relay WebSocket) vs `paired` (device paired) — **Android service nodes require `paired`**. Adding a service, the relay client internals, broadcast functions, and the full state flow are in **[Android Services](./docs-internal/android_services.md)**.

## WhatsApp Integration

Square-design nodes with embedded QR viewing; all requests proxy through the Python backend to the WhatsApp RPC service (`WHATSAPP_RPC_PORT`). Supports individual chats, groups, and newsletter channels; all 14 WhatsApp events handled. The backend helpers, frontend component, the critical bug fixes (dependency-injection wiring, unhandled JSON parse / HTTP status errors, missing `HTTPException` re-raise), the canonical error-handling pattern, and group/sender name persistence are in **[WhatsApp Integration](./docs-internal/whatsapp_integration.md)**.

## Event-Driven Trigger Node System

Trigger nodes wait for external events using `asyncio.Future` (in-memory `event_waiter` on the canvas-Run path; deployed triggers ride the Temporal canary path). Registry-driven: `TRIGGER_REGISTRY` + per-type filter builders, no timeout (users cancel), sequential queue processing. Polling triggers (Gmail, Twitter) use a poll coroutine + `asyncio.Queue` instead. The architecture, backend implementation, WebSocket handlers, per-trigger output schemas, the "adding new trigger types" recipe, and the key design decisions are in **[Trigger Nodes](./docs-internal/trigger_nodes.md)**; see also **[Event Waiter System](./docs-internal/event_waiter_system.md)** and **[Event Framework](./docs-internal/event_framework.md)**.

## Real-time Status WebSocket System

Frontend and backend communicate over `/ws/status` for push-based Android status, node status, node output, variable changes, and workflow progress — replacing API polling. `StatusBroadcaster` owns connections and broadcasts; `WebSocketContext` owns the client side with auto-reconnect. The full message-type catalogue (request/response, broadcast, status), the Android status-broadcasting rules, and real-device detection are in **[Real-time Status WebSocket](./docs-internal/realtime_status_websocket.md)** and **[Status Broadcaster](./docs-internal/status_broadcaster.md)**.

## Planned Features

Workflow-level parallel execution (n8n-style): current limitations, the planned `ExecutionContext`-per-workflow architecture, and the frontend/backend files to modify are in **[Planned Features](./docs-internal/planned_features.md)**.

## Notes

The long-form list of load-bearing decisions, invariants, gotchas, and "do not reintroduce" rules — accumulated across every wave and covering plugin extraction, CloudEvents factories, credential broadcasts, Temporal worker tuning, media transport, reserved Params field names, supervisor Job Objects, `core.paths` ownership, logging order, code-executor error mapping, and much more — lives in **[Invariants & Notes](./docs-internal/invariants.md)**. **Read it before re-solving anything that looks already-solved**; several entries document bugs that were expensive to find and are easy to reintroduce.

Two rules that apply to every change: **never use emojis in prints**, and **no hardcoded port numbers in code or docs** (`.env.template` is the single place port numbers live; Python resolves via `core.env_defaults`).
