# Planned Features

Workflow-level (parallel) execution design sketch. Moved verbatim out of CLAUDE.md.

## Planned Features

### Workflow-Level Execution (n8n-style Parallel Workflows)

**Current Limitations:**
- Single workflow execution at a time (global `_deployment_running` flag)
- Nodes fetch status on component mount, not when workflow is selected
- Status broadcasts to all clients without workflow filtering
- No isolation between workflow executions

**Planned Architecture:**

1. **Defer Node Status Checks Until Workflow Selected**
   - Remove eager `getStatus()` calls from WhatsAppNode mount (lines 44-48)
   - Remove eager `checkConfiguration()` from SquareNode mount (lines 46-92)
   - Status should only fetch when workflow containing those nodes is selected
   - Use cached status from WebSocket context instead of per-node fetching

2. **Workflow-Isolated Execution Context**
   ```python
   # server/services/workflow.py
   class ExecutionContext:
       def __init__(self, workflow_id: str, session_id: str):
           self.workflow_id = workflow_id
           self.session_id = session_id
           self.outputs: Dict[str, Any] = {}
           self.iteration = 0
           self.running = False
           self.task: Optional[asyncio.Task] = None

   # Replace single deployment state with:
   self._execution_contexts: Dict[str, ExecutionContext] = {}
   ```

3. **Parallel Workflow Deployment**
   - Each workflow gets unique `workflow_id` in execution requests
   - Backend tracks `_execution_contexts[workflow_id]` instead of single `_deployment_running`
   - Cancel by `workflow_id` instead of globally
   - Status broadcasts include `workflow_id` for client filtering

4. **Frontend Changes**
   - `WebSocketContext`: Add `activeWorkflowId`, filter status by workflow
   - `useAppStore`: Add `runningWorkflows: Set<string>` to track parallel executions
   - `WorkflowSidebar`: Show running indicator next to deployed workflows
   - `Dashboard`: Pass `workflow_id` to all execution calls

**Files to Modify:**
- `client/src/components/WhatsAppNode.tsx` - Remove mount status fetch
- `client/src/components/SquareNode.tsx` - Remove mount config check
- `client/src/contexts/WebSocketContext.tsx` - Add workflow filtering
- `client/src/store/useAppStore.ts` - Track running workflows
- `server/services/workflow.py` - ExecutionContext class, parallel support
- `server/routers/websocket.py` - workflow_id in messages
- `server/services/status_broadcaster.py` - workflow_id filtering
