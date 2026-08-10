# Status / Completed-Work Log

The historical `## Current Status` checklist and `## File Structure Cleanup` record, moved verbatim out of CLAUDE.md.

## Current Status
✅ **Plugin-first architecture (Wave 11)**: every plugin is a self-contained folder under `server/nodes/<group>/<plugin>/` rooted at `__init__.py`; backend NodeSpec is the SSOT for icon, colour, handles, params, output schema, uiHints. Frontend renders via `useNodeSpec` + `componentKind` dispatch.
✅ **WebSocket-First Architecture**: most frontend-backend RPC goes through WebSocket; live handler set lives in `MESSAGE_HANDLERS` in `server/routers/websocket.py`
✅ **Code Editor**: Python, JavaScript, and TypeScript executors with syntax-highlighted editor (react-simple-code-editor + prismjs) and console output
✅ **Node.js Executor**: Persistent Node.js server (Express + tsx) for fast JS/TS execution, replacing subprocess spawning
✅ **Component Palette**: Emoji icons with distinct dracula-themed category colors, localStorage persistence for collapsed sections
✅ **Android Integration**: 16 Android service nodes with ADB automation and remote WebSocket support
✅ **Conditional Parameter Display**: Dynamic UI rendering based on parameter values (displayOptions.show)
✅ **Execution Engine**: Full component execution with result display
✅ **Parameter Mapping**: Drag-and-drop output to parameter connections
✅ **AI Integration**: API key management and model selection
✅ **Location Services**: Interactive map picker with coordinate handling, Google Maps API key fetched from backend credentials
✅ **Code Cleanup**: Dead code removed, unused files deleted
✅ **Process Management**: Robust stop scripts with duplicate process detection
✅ **WhatsApp Integration**: Square node design with QR code viewer, group/sender name persistence, newsletter channel support (send, query, follow/unfollow, create, mute, mark viewed, react, live updates), media download, profile pics, and proper error handling
✅ **Backend Stability**: Fixed dependency injection and error handling preventing crashes
✅ **Development Server**: the app is **`http://localhost:${PYTHON_BACKEND_PORT}`** in every mode (defaults in `.env.template`). `company dev` = Vite HMR on that port proxying /api /ws /webhook to the backend (dev override in `.env.dev`); `company start` (production) = uvicorn alone on it (API + WS + SPA)
✅ **WebSocket Integration**: Persistent WebSocket connections for remote Android devices with background tasks and message queue
✅ **Real-time Status WebSocket**: Frontend-backend WebSocket at `/ws/status` for live Android status, node status, and variable updates
✅ **Event-Driven Trigger Nodes**: WhatsApp Receive and Webhook Trigger with asyncio.Future-based event waiting, filter builders, and cancel support
✅ **Continuous Scheduling Execution**: Temporal/Conductor pattern using `asyncio.wait(FIRST_COMPLETED)` for true parallel pipelines where dependent nodes start immediately when their specific dependency completes
✅ **Event-Driven Deployment**: n8n-style architecture where each trigger event spawns an independent, concurrent execution run (no iteration loop)
✅ **HTTP/Webhook Nodes**: HTTP Request for external APIs, Webhook Trigger for incoming requests, Webhook Response for custom responses
✅ **Theme System**: Neutral-slate (dark) + grey-blue paper (light) surfaces with Dracula accent palette, dark mode support, vibrant action buttons, and themed React Flow edges
✅ **Modular Backend Architecture**: workflow.py refactored from 2068 to 460 lines using facade pattern with NodeExecutor, ParameterResolver, and DeploymentManager modules
✅ **Node Rename System**: n8n-style node renaming via F2 keyboard shortcut, double-click on label, or right-click context menu with inline editing
✅ **UI State Persistence**: localStorage persistence for sidebar visibility, component palette visibility, dev mode, and collapsed sections
✅ **Normal/Dev Mode**: Toggle in toolbar to filter Component Palette - Normal mode shows only AI Agents, Models, and Skills; Dev mode shows all categories
✅ **Production Deployment**: Docker Compose deployment (4 containers: Redis, Backend, Frontend, WhatsApp), nginx reverse proxy, and Let's Encrypt SSL
✅ **Authentication System**: n8n-style JWT authentication with HttpOnly cookies, single-owner and multi-user modes, rate-limited login. Note `AUTH_MODE=multi` authenticates but does NOT isolate data — see Known Limitations in [authentication.md](./authentication.md)
✅ **Cache System**: n8n-pattern cache with Redis (production) / SQLite (local dev) / Memory fallback hierarchy
✅ **AI Thinking/Reasoning**: Extended thinking for Claude, Gemini 2.5/3, OpenAI GPT-5/o-series, Groq Qwen3 with output available in Input Data & Variables for downstream nodes
✅ **Onboarding Service**: 5-step welcome wizard with shadcn UI, database persistence, skip/resume/replay support
✅ **Proxy System**: Residential proxy provider management with template-based URL formatting, auto-selection by health score, transparent proxy injection on httpRequest/httpScraper nodes via `useProxy: true`
✅ **Markdown Formatter**: GFM markdown to platform-native formatting (Telegram HTML, WhatsApp syntax, plain text) using markdown-it-py

## File Structure Cleanup
**Removed Files:**
- `src/nodeDefinitions.ts` + `src/nodeDefinitions/` (27 files) — superseded by backend NodeSpec SSOT; frontend resolves specs via `lib/nodeSpec.ts` + `adapters/nodeSpecToDescription.ts`
- `src/nodeDefinitions.backup.ts` (backup file)
- `src/schemas/` directory (unused schema system)
- `src/utils/schemaParser.ts` (legacy parser)
- `src/utils/nodeSchemaParser.ts` (unused modern parser)
- `src/types/NodeSchema.ts` (legacy schema types)

**Cleaned Code:**
- Removed unused imports and dead functions
- Eliminated legacy NodeDefinition interface  
- Streamlined parameter handling logic
- Maintained backward compatibility only where actively used
