# Config Node Architecture (detail)

Config handle convention, detection, input inheritance, filtering logic, sub-node execution exclusion. Moved verbatim out of CLAUDE.md.

## Config Node Architecture

### Overview
Config nodes (context, tools, models) connect to parent nodes via special "config handles" (e.g., `input-context`, `input-tools`). These are auxiliary connections for configuration, not main data flow. The UI intelligently handles visibility of connected inputs based on this architecture.

### Config Handle Convention
Config handles follow the pattern `input-<type>` where type is NOT 'main':
- `input-context` - Context node (RFC-0002; observation surface onto the journal)
- `input-tools` - Tool nodes (including `simpleMemory`, which is a ToolNode)
- `input-model` - Model configuration nodes
- `input-skill` - Skill nodes
- `input-task` - Task completion trigger nodes
- `input-teammates` - Team member agent nodes
- `input-main` - Main data flow (NOT a config handle)
- `input-memory` - **retired.** Kept only so immutable V1 graph snapshots replay; no agent declares it. `normalize_workflow_graph` rewrites legacy `simpleMemory -> input-memory` edges into a Context node plus an ordinary tool edge.

**Note**: Trigger nodes (e.g., `taskTrigger`) connecting via config handles are excluded from downstream inclusion in `_get_downstream_nodes()` to prevent them from blocking as event waiters.

### Config Node Detection
Nodes are identified as config nodes by their `group` array in the node definition:
```typescript
// Config node example (simpleMemory)
group: ['skill', 'memory']  // 'memory' or 'tool' indicates config node
```

### Input Inheritance
Config nodes automatically inherit their parent node's main inputs in the parameter panel:
```
WhatsApp Trigger → AI Agent ← Simple Memory
       ↓              ↑
   main input    config handle

When viewing Simple Memory's parameters:
- Shows: "WhatsApp Trigger (via AI Agent)"
- Can drag WhatsApp outputs into Memory's parameters
```

### Filtering Logic
Located in `InputSection.tsx` and `OutputPanel.tsx`:
1. **Parent nodes** (AI Agent): Skip showing config node connections as inputs
2. **Config nodes** (Memory): Inherit parent's main input connections with "(via Parent)" label

### Key Functions
```typescript
// Check if handle is for config nodes (not main data flow)
const isConfigHandle = (handle: string | null | undefined): boolean => {
  if (!handle) return false;
  return handle.startsWith('input-') && handle !== 'input-main';
};

// Check if node is a config/auxiliary node — reads the backend-derived
// uiHint, not a frontend group-string heuristic.
const isConfigNode = (nodeType: string | undefined): boolean => {
  if (!nodeType) return false;
  const definition = resolveNodeDescription(nodeType);
  return definition?.uiHints?.isConfigNode === true;
};
```

The `isConfigNode` flag is **auto-derived on the backend** by `_derive_auto_ui_hints` in [`server/services/plugin/base.py`](../server/services/plugin/base.py): plugins whose `group` tuple contains `memory` or `tool` (the centralized `_CONFIG_NODE_GROUPS = frozenset({"memory", "tool"})`) automatically export `uiHints.isConfigNode: True`. Explicit `cls.ui_hints` always wins (merge order: auto-derived first, then `dict.update` with the plugin's declaration). Pytest invariant `test_ui_hints_only_carry_known_flags` locks the flag name in `server/tests/test_node_spec.py`.

### Adding New Config Node Types
1. Put the plugin in `('memory',)` or `('tool',)` (or any tuple containing one of those). The backend auto-derivation does the rest — do NOT declare `isConfigNode` in `ui_hints` unless you want to override.
2. Use `input-<type>` naming for the target handle on the parent node.
3. Input inheritance and filtering work automatically — the frontend reads `definition.uiHints.isConfigNode`, never the group strings.

### Sub-Node Execution Exclusion

Sub-nodes (tools, memory, skills, teammates) connect TO an agent, not from it, so in parallel execution mode Kahn's algorithm would see them with in-degree 0 and incorrectly schedule them in layer 0. The executor excludes them: any node whose edge targets an AI-agent config handle (`input-context`, `input-tools`, `input-skill`, `input-teammates`) is detected as a sub-node in `ExecutionContext.create()` / `_compute_execution_layers()` and skipped from execution layers — it executes only when the agent invokes it (e.g. as an AI tool).

Toolkit aggregator nodes (the former `androidTool` and its `TOOLKIT_NODE_TYPES` constant) were retired; Android service nodes now connect directly to the agent's `input-tools` handle. Legacy `service -> androidTool -> agent` graphs are migrated on load by `services/workflow_migrations.normalize_legacy_android_toolkit` (pure, idempotent: services re-wire directly to each agent, orphaned toolkits are removed with a warning).
