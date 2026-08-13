# Backend Service Map

Directory tree of `server/`, the optional Polyglot integration, and the Node.js code-executor sidecar. Moved verbatim out of CLAUDE.md.

### Backend Service Architecture (n8n-inspired)
The workflow backend follows modular architecture patterns from n8n, Temporal, and Conductor:

```
server/services/
├── workflow.py              # Facade (~460 lines) - thin coordinator
├── node_executor.py         # Single node execution with registry pattern
├── parameter_resolver.py    # Template variable resolution
├── agent_team.py            # AgentTeamService for multi-agent coordination
├── model_registry.py        # ModelRegistryService - model constraints from OpenRouter + llm_defaults
├── pricing.py               # LLM and API cost calculation (loads config/pricing.json)
├── markdown_formatter.py    # GFM markdown to platform-specific formatting (Telegram HTML, WhatsApp, plain)
├── ws_handler_registry.py   # Plugin-owned WS commands self-register here (Wave 11.H)
├── browser_service.py       # BrowserService singleton wrapping agent-browser CLI
├── himalaya_service.py      # HimalayaService CLI wrapper for IMAP/SMTP (any email provider)
├── email_service.py         # EmailService orchestrator (credential resolution, provider presets)
├── todo_service.py          # TodoService singleton for writeTodos tool (JSON per-session state)
├── media/                   # Media transport — vendor-neutral, kind-agnostic (see media_transport.md)
│   ├── refs.py              # FileRef (base; FileKind = file|audio|image|video|document)
│   │                        # + AudioRef(FileRef), the probed-container narrowing.
│   │                        # A reference, never bytes; extra="forbid" makes that structural.
│   │                        # kind="audio" ASSERTS inspect_audio ran — never guess it.
│   ├── preview.py           # Single owner of the inline-vs-attachment rule (serves_inline /
│   │                        # preview_kind). TWO consumers: routers/workspace.py picks the
│   │                        # Content-Disposition, the gallery listing sets each row's
│   │                        # `preview`. One function, so the panel can never offer a preview
│   │                        # the route refuses to serve inline.
│   ├── workspace.py         # write_audio / resolve_media / read_media_bytes / coerce_file_param
│   ├── inspect.py           # tinytag -> wave -> PCM arithmetic; NEVER raises
│   └── limits.py            # every size constant, each annotated with what it defends against
├── provider_registry.py     # Generic ProviderSpec + ProviderRegistry + lazy exception refs.
│                            # Shared by services/llm and nodes/speech (which owns two, one per
│                            # direction). Registration must never import a provider SDK.
├── memory/                  # Native Markdown/JSONL/runtime/vector-store helpers
├── memory_store.py          # In-memory conversation sessions using native Message values
├── skill_prompt.py          # Skill system prompt builder (injects SKILL.md for personality skills)
├── text.py                  # TextService (text generation nodes)
├── chat_client.py           # JSON-RPC 2.0 WebSocket client for chat backend
│                            # (Claude Code CLI wrapper + isolated OAuth moved to
│                            #  nodes/agent/claude_code_agent/_oauth.py — CLAUDE_CONFIG_DIR=<DATA_DIR>/claude/)
├── tracked_http.py          # HTTPX event hooks for automatic API cost tracking
├── whatsapp_service.py      # WhatsApp RPC proxy helpers (used by nodes/whatsapp/*, not an APIRouter)
├── handlers/                # Cross-cutting orchestration only (Wave 11: 16 → 4 files, 12.8K → 1.1K LOC)
│   ├── tools.py             # AI-tool dispatch + agent delegation (~821 LOC)
│   ├── triggers.py          # Generic event-trigger handler
│   ├── todo.py              # writeTodos execution shim (used by every agent)
│   └── __init__.py          # Docstring only (google_auth.py retired into nodes/google/_auth_helper.py)
├── llm/                     # Native LLM provider SDKs for chat and every new agent execution
│   ├── __init__.py          # Public API exports
│   ├── protocol.py          # ThinkingConfig, Message, LLMResponse, LLMProvider Protocol
│   ├── config.py            # ProviderConfig, resolve_max_tokens, resolve_temperature
│   ├── registry.py          # ProviderSpec + register_provider — sdk_exception_refs are LAZY "module:Class" strings resolved via pkgutil.resolve_name at except/read time; NEVER import an SDK at registration (locked by tests/llm/test_lazy_sdk_imports.py)
│   ├── unifier.py           # ChatUnifier facade — routes chat/fetch_models, translates typed SDK errors → NodeUserError, applies incompatible_models filter
│   ├── vertex.py            # Vertex / Agent-Platform key handling
│   ├── messages.py          # filter_empty_messages, is_valid_message_content
│   └── providers/           # Per-provider implementations (+ _compat.py for the 8 OpenAI-compatible providers)
│       ├── anthropic.py     # AnthropicProvider (anthropic SDK)
│       ├── openai.py        # OpenAIProvider (openai SDK)
│       ├── gemini.py        # GeminiProvider (google-genai SDK)
│       └── openrouter.py    # OpenRouterProvider (extends OpenAIProvider)
├── proxy/                   # Residential proxy provider management
│   ├── __init__.py          # Exports get_proxy_service, ProxyService
│   ├── service.py           # ProxyService singleton - provider selection, URL generation
│   ├── providers.py         # TemplateProxyProvider - JSON url_template formatting
│   └── models.py            # ProxyProvider, RoutingRule, SessionType enums
├── deployment/              # Event-driven deployment lifecycle
│   ├── __init__.py
│   ├── state.py             # DeploymentState, TriggerInfo dataclasses
│   ├── triggers.py          # TriggerManager (cron, event triggers)
│   └── manager.py           # DeploymentManager (deploy, cancel, status)
├── execution/               # Parallel workflow orchestration
│   ├── models.py            # ExecutionContext, TaskStatus
│   ├── executor.py          # WorkflowExecutor with decide pattern
│   ├── cache.py             # Cache persistence (Redis/SQLite)
│   └── recovery.py          # Crash recovery
└── temporal/                # Distributed workflow execution (optional)
    ├── __init__.py          # Exports TemporalExecutor, TemporalClientWrapper
    ├── workflow.py          # MachinaWorkflow orchestrator
    ├── activities.py        # Class-based activities with connection pooling
    ├── worker.py            # TemporalWorkerManager + run_standalone_worker()
    ├── executor.py          # TemporalExecutor interface
    ├── client.py            # Temporal client wrapper
    └── ws_client.py         # WebSocket connection pool

server/core/
├── container.py             # Dependency injection container
├── database.py              # SQLite database with cache CRUD methods
├── cache.py                 # CacheService with Redis/SQLite/Memory fallback
├── config.py                # Application configuration
├── logging.py               # Logging configuration
├── paths.py                 # SSOT for on-disk locations (generic helpers only): opencompany_root()/data_path()/workspaces_dir()/workspace_dir()/daemons_dir() + packages_dir()/package_dir(name) all under ~/.opencompany/ (= DATA_DIR); packages/ holds the single shared npm tree + stripe/ + temporal/ binary subdirs; example_workflows_dir() = <repo>/.opencompany/workflows/ (shipped seeds, NOT under DATA_DIR). Plugin-specific subpaths composed inline at the call site, never added here.
├── env_defaults.py          # Env accessor backed by .env.template/.env (the SSOT for port numbers; used by entry points that bypass the CLI env push)
├── encryption.py            # Fernet encryption with PBKDF2 key derivation
├── credentials_database.py  # Async SQLite for encrypted API keys and OAuth tokens
└── credential_backends.py   # Multi-backend abstraction (Fernet, Keyring, AWS)

server/models/
├── cache.py                 # CacheEntry SQLModel for SQLite cache
├── auth.py                  # User model with bcrypt
└── database.py              # ConversationMessage, NodeParameter, ToolSchema, ChatMessage, TokenUsageMetric, APIUsageMetric, CompactionEvent, SessionTokenState, UserSettings, ProviderDefaults, AgentTeam, TeamMember, TeamTask, AgentMessage tables

server/config/
├── llm_defaults.json        # Per-provider defaults (model, base_url, max_output_tokens, context_length, temperature_range, reasoning_models, thinking_type, ...) AND a top-level `agent` block (recursion_limit, default_temperature, compaction.ratio) that drives the agent loop and CompactionService — no env-var defaults; this is the source of truth.
├── model_registry.json      # Cached model data from OpenRouter (auto-refreshed)
├── pricing.json             # LLM and API pricing config
├── google_apis.json         # Google Workspace API endpoints, scopes, OAuth callback paths
├── email_providers.json     # IMAP/SMTP provider presets (Gmail, Outlook, Yahoo, iCloud, ProtonMail, Fastmail, custom)
├── speech_defaults.json     # Per-provider TTS/STT capabilities, per-direction, with per-model overrides
                             # ({"whisper-1": [...], "_default": [...]} resolved exact -> longest-prefix ->
                             # _default). Drives the provider dropdowns, voice/model loaders and validation.
                             # Boolean flags default PERMISSIVE so a missing declaration never silently
                             # disables a working feature. Read by nodes/speech/_config.py.
└── translate_defaults.json  # Same shape, three capability blocks per provider (translate /
                             # transliterate / detect). Both files are resolved by the shared
                             # services/plugin/capabilities.CapabilityConfig.

server/nodejs/                   # Persistent Node.js server for JS/TS execution
├── package.json                 # Dependencies: express, tsx
├── tsconfig.json                # TypeScript config (ES2024)
├── src/
│   └── index.ts                 # Express server (/execute, /health, /packages/*)
└── user-packages/               # User-installed npm packages
```

### Polyglot Server Integration (Optional)
OpenCompany can optionally integrate with the sibling **polyglot-server** repo (a plugin-registry microservice exposing REST + MCP + WebSocket). NOTE: the OpenCompany-side client/handler (`polyglot_client.py`, `handlers/polyglot.py`) are not currently present in the tree — this is a possible future integration, not wired. See [Polyglot Server](../../polyglot-server/ARCHITECTURE.md).

### Node.js Code Executor
Persistent Node.js server for JavaScript/TypeScript code execution, replacing subprocess spawning per execution. **Plugin-owned (July 2026):** the sidecar is supervised by `nodes/code/_runtime.py` (`NodeJSExecutorRuntime`, same `BaseProcessSupervisor` pattern as WhatsApp/Temporal) and spawns on demand from `acquire_client()` on the first JS/TS node execution — in every run mode, with no CLI service wiring. Client + config are plugin-owned too (`nodes/code/_client.py`, `NODEJS_EXECUTOR_*` env vars; core `Settings` carries no executor fields).

**Architecture:**
```
┌─────────────────────────────────────────────────────────────┐
│           Python Backend (PYTHON_BACKEND_PORT)               │
│  ┌────────────────┐     HTTP/JSON      ┌──────────────────┐ │
│  │ NodeJSClient   │◄──────────────────►│  Node.js Server  │ │
│  │ (aiohttp)      │ NODEJS_EXECUTOR_PORT │ (Express + tsx)│ │
│  └────────────────┘                    └──────────────────┘ │
│         ▲                                                    │
│         │                                                    │
│  ┌──────┴─────────┐                                         │
│  │ nodes/code/    │                                         │
│  │ plugins        │                                         │
│  └────────────────┘                                         │
└─────────────────────────────────────────────────────────────┘
```

**Files:**
```
server/nodejs/
├── package.json              # Dependencies: express, tsx
├── tsconfig.json             # TypeScript config (ES2024)
├── src/
│   └── index.ts              # Express server with /execute, /health, /packages/*
└── user-packages/            # User npm packages directory
    └── package.json

server/services/

server/nodes/code/                # Executor plugins (javascript_executor, typescript_executor)
```

**Endpoints:**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check with Node.js version |
| `/execute` | POST | Execute JS/TS code with input_data and timeout |
| `/packages/install` | POST | Install npm packages to user-packages |
| `/packages` | GET | List installed packages |

**Environment Variables:**
| Variable | Default | Description |
|----------|---------|-------------|
| `NODEJS_EXECUTOR_URL` | `http://localhost:${NODEJS_EXECUTOR_PORT}` | Server URL for Python client |
| `NODEJS_EXECUTOR_TIMEOUT` | `30` | Request timeout in seconds |
| `NODEJS_EXECUTOR_PORT` | see `.env.template` | Server port |
| `NODEJS_EXECUTOR_HOST` | `localhost` | Server host |
| `NODEJS_EXECUTOR_BODY_LIMIT` | `10mb` | Max request body size |

**Key Modules:**

| Module | Responsibility | Pattern |
|--------|---------------|---------|
| `workflow.py` | Facade delegating to specialized modules | Facade Pattern |
| `node_executor.py` | Execute single node via handler registry | Registry + functools.partial |
| `parameter_resolver.py` | Resolve `{{node.field}}` templates | Compiled regex |
| `deployment/manager.py` | Deploy/cancel workflows, spawn runs | n8n Deployment |
| `deployment/triggers.py` | Setup cron/event triggers | Event-driven |
| `deployment/state.py` | Immutable state dataclasses | Dataclass |
| `temporal/executor.py` | Temporal-based distributed execution | Per-node Activities |
| `temporal/workflow.py` | Pure orchestrator (no business logic) | FIRST_COMPLETED |
| `temporal/worker.py` | Worker lifecycle + horizontal scaling | Connection Pooling |

**NodeExecutor Registry Pattern:**
```python
class NodeExecutor:
    def _build_handler_registry(self) -> Dict[str, Callable]:
        return {
            'start': handle_start,
            'aiAgent': _dispatch_plugin_node,  # Wave 11: routes via BaseNode.execute()
            # ... registry-based dispatch instead of if-else chains
        }
```
