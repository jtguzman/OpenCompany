# Frontend Performance Architecture

Layered cache + slice-subscription model: TanStack Query persistence, `useNodeSpec` slice subscription, `nodeStatusStore`, `useAppStore` selector rule, `isOpen` vs `isReady`, debounced catalogue invalidation, `React.memo` on canvas nodes, icon/color resolution. Moved verbatim out of CLAUDE.md; the condensed rules stay in CLAUDE.md.

The frontend uses a layered cache + slice-subscription model so cold refreshes are instant and high-frequency status broadcasts do not cascade through the React tree. The patterns below are canonical -- follow them when adding new server-state queries, status broadcasts, or canvas node components.

### TanStack Query persistence ([client/src/lib/queryPersist.ts](../client/src/lib/queryPersist.ts))
- App is wrapped in `<PersistQueryClientProvider>` ([main.tsx](../client/src/main.tsx)) with a localStorage persister + `__APP_VERSION__` buster + 24h SWR window (RFC 5861).
- Only queries with key prefixes `nodeSpec` / `nodeGroups` / `pluginCatalogue` are dehydrated (see `shouldPersistQuery`). High-frequency / per-session queries stay in-memory.
- Hard refresh paints from cached specs **before** the WS connects, so canvas nodes never flash placeholder icons.

### `useNodeSpec` is a slice subscription, not a `useQuery` ([client/src/lib/nodeSpec.ts](../client/src/lib/nodeSpec.ts))
- Reads via `useSyncExternalStore` against `queryClient.getQueryCache().subscribe(...)` filtered by `hashKey(['nodeSpec', type])`. Per-spec observer count is **0**; only the matching slot triggers a re-render.
- Lazy fetch is one-shot via `useEffect`, gated on `isReady` (see below).
- **Do not re-introduce `useQuery(['nodeSpec', type])`** anywhere -- N consumers would create N observers, all woken on every cache write.
- **Critical: any cache entry consumed via `useSyncExternalStore` MUST set `gcTime: GC_TIME.FOREVER`** ([lib/queryConfig.ts](../client/src/lib/queryConfig.ts)). Slice subscribers don't register as observers, so without this override TanStack garbage-collects the entry after `GC_TIME.DEFAULT` (5 min) and every consumer reads `undefined`. Symptom: canvas nodes lose their icons + handles after idling on the page. Applies to `fetchNodeSpec`, `fetchNodeGroups`, `useNodeGroups`. The persistor in `lib/queryPersist.ts` only handles cross-reload survival, not in-session GC.

### `nodeStatusStore` for high-frequency state ([client/src/stores/nodeStatusStore.ts](../client/src/stores/nodeStatusStore.ts))
- Per-workflow node statuses live in a Zustand store (built on `useSyncExternalStore`). `useNodeStatus(id)` is a slice selector -- only the affected node's consumers re-render on a status tick.
- Mirror this pattern when adding any new high-frequency push state. Do **not** put it on `WebSocketContext.value` -- that's a context fan-out trap.

### `useAppStore` reads must be slice selectors, never whole-store destructure
- Always `const x = useAppStore((s) => s.x)`, never `const { x } = useAppStore()`. The whole-store form re-renders the consumer on ANY mutation (sidebar toggle, unrelated workflow rename, parameter save on another node), which defeats `React.memo` + `nodePropsEqual` on the canvas. Setters are stable refs from Zustand — single-field selectors are the cheapest read.
- Audited and converted across the canvas + parameter-panel hot paths: every node component, `Dashboard.tsx`, `useDragVariable`, `useParameterPanel`, `useReactFlowNodes`, `useWorkflowManagement`, `InputSection`, `MiddleSection`, `OutputPanel`, `ParameterRenderer`, `ToolSchemaEditor`, `ParameterPanel`, `InputNodesPanel`. New code should follow.

### `isOpen` vs `isReady` -- gate every catalogue/spec query on `isReady` ([WebSocketContext.tsx](../client/src/contexts/WebSocketContext.tsx))
- `isOpen` flips when the socket opens. `isReady` flips only after the init burst (api-key probes, terminal / chat / console history) settles.
- The init burst runs **in parallel** via `Promise.allSettled`: 5 `probeApiKey(provider)` calls + `loadTerminalLogs()` + `loadChatHistory()` + `loadConsoleLogs()`, each owning its own request id, message handler, 5 s timeout, and state write via a small `sendBurstRequest` factory. Time-to-`isReady` is one wide round-trip, not 8 sequential ones. `drainPendingSends(ws)` still runs synchronously after the await and before `setIsReady(true)` so the queue replay ordering is preserved.
- Queries that depend on backend-served catalogue data (`useCatalogueQuery`, `useNodeParamsQuery`, `useUserSettingsQuery`, `useNodeGroups`, `useNodeSpec` lazy fetch, prefetch effect) gate on `isReady` so they fire once, post-burst, instead of racing the parallel init helpers.
- `WebSocketContext.value` is `useMemo`'d -- consumers only re-render when an actual field they read changes. Pending requests are rejected on `ws.onclose` so retries fire immediately on the new socket instead of waiting the 30 s `REQUEST_TIMEOUT`.

### Catalogue invalidation is debounced
- `invalidateCatalogue(queryClient)` in [`hooks/useCatalogueQuery.ts`](../client/src/hooks/useCatalogueQuery.ts) wraps `queryClient.invalidateQueries({ queryKey: CATALOGUE_QUERY_KEY })` with a 300 ms trailing-edge debounce via a single shared module-scope timer. **Always go through it** from broadcast handlers — direct `invalidateQueries` calls were the old pattern.
- All 8 broadcast handlers in `WebSocketContext.tsx` (`api_key_status`, `whatsapp_status`, `twitter_oauth_complete`, `google_oauth_complete`, `google_status`, `telegram_status`, `credential_catalogue_updated`, `initial_status`) now route through it. An OAuth burst or multi-service reconnect collapses to one refetch instead of N back-to-back round-trips.

### React.memo every canvas node component ([client/src/components/nodeMemoEquality.ts](../client/src/components/nodeMemoEquality.ts))
- React Flow's documented requirement. Use the shared `nodePropsEqual` comparator -- it skips drag-state props (`xPos` / `yPos` / `dragging`) so the memo isn't defeated during drag.
- Applies to `SquareNode`, `AIAgentNode`, `TriggerNode`, `ToolkitNode`, `StartNode`, `TeamMonitorNode`. Add new node components the same way.
- Reference: https://reactflow.dev/learn/advanced-use/performance

### Icon + color — per-plugin folder + visuals.json fallback

Plugin icons and colors live co-located in the plugin folder; `visuals.json` is the fallback registry for emoji / library icons and the skill reverse-map. Full resolution chain (per-node-type → shared → fallback) is documented in [server/nodes/README.md → Icon + color](../server/nodes/README.md) and [docs-internal/plugin_system.md](./plugin_system.md).

Backend endpoints serve SVGs at `GET /api/schemas/nodes/<type>/icon` (plugin icons) and `GET /api/schemas/credentials/<provider>/icon` (credential brand icons). Frontend resolver at [client/src/assets/icons/index.ts](../client/src/assets/icons/index.ts) dispatches `lib:brand` / URL passthrough / emoji / `asset:<key>`. The `asset:` branch is currently inert at runtime (the frontend `ICON_REGISTRY` glob finds no SVGs so it resolves to null) but it is NOT dead code — the backend still emits `asset:google` / `asset:stripe` for palette groups (`server/nodes/groups.py`) and the format is invariant-tested on both sides (`test_node_spec.py` Wave 10.B, `icons/index.test.ts`).

**Do not** declare `icon` / `color` as class attributes on a node (the override path was removed in F1). Drop `icon.svg` (or `icon_<nodeType>.svg` for multi-node folders like whatsapp) and `meta.json` into the plugin folder. SKILL.md icon/color resolves from the first node in `allowed-tools` — only orphan skills keep inline `metadata.icon` / `metadata.color`.
