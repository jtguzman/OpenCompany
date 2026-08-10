# Frontend Key Files & Components

Core types, node system entry points, assets, UI components, specialized UI, hooks & state, WebSocket-first architecture. Moved verbatim out of CLAUDE.md. Pairs with frontend_architecture.md (patterns) and theme_system.md (tokens).

### Core Types
- `src/types/INodeProperties.ts` - Core interfaces for n8n-inspired node properties system
- `src/types/NodeTypes.ts` - Legacy compatibility types (NodeParameter, NodeOutput)
- `src/types/workspaceFiles.ts` - Wire types for the gallery / workspace file explorer (`WorkspaceEntry`, `WorkspaceFileRef`, `FILE_REF_KINDS`, `isWorkspaceFileRef`, `WORKSPACE_FILE_DRAG_TYPE`). Declarations only — it documents which decisions are server-owned and must not be re-derived client-side

### Node System
Node metadata is SSOT on the backend after Wave 11. Each node is a Python
plugin at `server/nodes/<category>/<plugin>/__init__.py` that emits a `NodeSpec` via
the registry. The frontend fetches specs through
[`client/src/lib/nodeSpec.ts`](../client/src/lib/nodeSpec.ts) and adapts
them via [`client/src/adapters/nodeSpecToDescription.ts`](../client/src/adapters/nodeSpecToDescription.ts).
See [`docs-internal/plugin_system.md`](./plugin_system.md)
and [`server/nodes/README.md`](../server/nodes/README.md) for the plugin
authoring model.

- `src/lib/nodeSpec.ts` - TanStack-Query-backed spec fetch, `resolveNodeDescription`, `listCachedNodeSpecs`, group lookup
- `src/lib/aiModelProviders.ts` - Frontend-only AI provider icon/credential map
- `src/adapters/nodeSpecToDescription.ts` - Backend `NodeSpec` → legacy `INodeTypeDescription` shape
- `src/services/executionService.ts` - Node execution routed through the backend WebSocket layer

### Assets
- `src/assets/icons/google/` - Official Google service SVG icons (Gmail, Calendar, Drive, Sheets, Tasks, Contacts) using n8n pattern with data URI exports

### UI Components
- `src/components/ParameterRenderer.tsx` - Universal parameter renderer (also handles AI-specific control rendering; the former `AIParameterRenderer.tsx` was absorbed here)
- `src/components/parameterPanel/MiddleSection.tsx` - Parameter panel middle section with conditional display logic
- `src/components/output/OutputPanel.tsx` - Connected node output display with drag mapping
- `src/components/LocationParameterPanel.tsx` - Location-specific parameter handling
- `src/components/parameterPanel/GalleryPanel.tsx` - Workspace file explorer for the `gallery` node (`isGalleryPanel` uiHint); supporting parts in `parameterPanel/gallery/` (`FilePreviewDialog`, `FileGlyph`, `fileIcons`)
- `src/components/AIAgentNode.tsx` - Spec-driven agent canvas component. Reads `useNodeSpec(type)` for handles / icon / colour / displayName / uiHints; renders any plugin whose backend `component_kind` is `"agent"` or `"chat"`. No `AGENT_CONFIGS` map.
- `src/ParameterPanel.tsx` - Main parameter configuration modal

### AI Chat Model Components
AI model nodes route through `SquareNode` via `Dashboard.tsx`'s `COMPONENT_BY_KIND['model']` lookup. Per-provider visual data (icon, color, displayName) comes from the backend `NodeSpec` declared in `server/nodes/model/<provider>_chat_model/__init__.py`. The pre-Wave-11 per-provider wrappers (`BaseChatModelNode`, `OpenAIChatModelNode`, `ClaudeChatModelNode`, `GeminiChatModelNode`, `ModelNode`) were deleted -- nothing imported them after the migration.

### Specialized UI
- `src/components/maps/GoogleMapsPicker.tsx` - Interactive location picker (click / drag marker); wrapped by `maps/MapsPreviewPanel.tsx` and rendered through `parameterPanel/MapsSection.tsx` for `gmaps_create`. Uses Google's default map styling.
- `src/components/output/OutputPanel.tsx` - Execution result display (the active renderer; the legacy `ui/OutputDisplayPanel.tsx` was deleted)
- `src/components/ui/ComponentPalette.tsx` - Searchable component library with emoji icons and dracula-themed category colors. Categories: Workflow, Triggers, AI Agents, AI Models, AI Skills, AI Abilities, AI Tools, Google Maps, Social Media Platforms (merged WhatsApp + Social), Android, Chat, Code Executors
- `src/components/ui/ComponentItem.tsx` - Draggable node items with hover effects and icon rendering
- `src/components/ui/CodeEditor.tsx` - Syntax-highlighted code editor (react-simple-code-editor + prismjs). Token colours come from the per-theme `--code-*` tokens (see [Theme System](./theme_system.md) tier 6) — the code editor, console/output JSON viewers, and chat code blocks all paint in the active theme's syntax palette, not a global dracula scheme. (Retired the old `--prism-*` block + dead `getPrismTokenCSS()`.)

### Hooks & State
- `src/hooks/useParameterPanel.ts` - Parameter management via WebSocket
- `src/services/executionService.ts` - Node execution via WebSocket (`executeNodeViaWebSocket`)
- `src/hooks/useApiKeys.ts` - API key management via WebSocket
- `src/hooks/useAndroidOperations.ts` - Android device operations via WebSocket
- `src/hooks/useWhatsApp.ts` - WhatsApp operations via WebSocket
- `src/hooks/useDragAndDrop.ts` - Drag-and-drop functionality (palette → canvas, `application/reactflow`)
- `src/hooks/useDragWorkspaceFile.ts` - Drag a workspace file onto another node's parameter (`workspaceFile` payload); mirrors `useDragVariable`'s dual-MIME contract — `application/json` for the structured payload, `text/plain` for the bare path
- `src/hooks/useComponentPalette.ts` - Component palette state with localStorage persistence
- `src/store/useAppStore.ts` - Zustand application state with localStorage persistence for UI settings

### Theme System

12-way visual theme system (2 base: light, dark + 5 utopian: renaissance, greek, edo, steampunk, atomic + 5 dystopian: cyber, wasteland, rot, plague, surveillance) driven by `<html data-theme>` (set by [ThemeContext.tsx](../client/src/contexts/ThemeContext.tsx), which also toggles `.dark` for DARK_FAMILY themes) + per-theme CSS in `client/src/themes/`. Token VALUES are hex + `color-mix()` (never HSL): per-theme files own shadcn/dracula/node/action hex, `base.css` owns the shared `--tint-*` scale, `index.css` is plumbing (`@theme inline` maps `--color-X: var(--X)`). Six token tiers, the per-theme `--pulse-keyframe` animation system, decorative-layer wrappers, the 10-pack WebAudio sound system, and the canvas-wide edge/node status rules (`canvasAnimations.ts`) are all documented in **[Theme System](./theme_system.md)** — read it before adding a theme or a canvas-node component. The strict frontend theme RULES remain normative under "Frontend Design + Theme System (strict)" above.

### WebSocket-First Architecture
The project uses WebSocket as the primary communication method between frontend and backend, replacing most REST API calls:
- `src/contexts/WebSocketContext.tsx` - Central WebSocket context with request/response pattern
- `server/routers/websocket.py` - WebSocket endpoint; the live handler set is the `MESSAGE_HANDLERS` dict plus plugin-registered handlers via `services.ws_handler_registry`. Don't hand-maintain a count here.
- `server/services/status_broadcaster.py` - Connection management and broadcasting

**Canvas mutations from the backend** -- any handler that needs to add / move / delete nodes or edges (auto-add-skill on tool connect, Agent Builder runtime tools called by the LLM mid-execution, future workflow-template features) returns a workflow-ops batch (`{operations: [...]}`) and the frontend applies it through `applyOperations` in [client/src/lib/workflowOps.ts](../client/src/lib/workflowOps.ts). Backend builders live in [server/services/workflow_ops.py](../server/services/workflow_ops.py). Two delivery modes: request/response (frontend-driven, e.g. auto-skill) and push broadcast (`send_custom_event('workflow_ops_apply', ...)`, picked up by `useWorkflowOpsListener`). Full spec: [docs-internal/workflow_ops_protocol.md](./workflow_ops_protocol.md).
