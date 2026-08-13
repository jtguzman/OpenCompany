# Logging Infrastructure & Error Contracts

Log levels, `.env` knobs, the canonical structlog patterns (timestamp-less console, `log_context`, per-plugin OTel span, source-tag resolver), the `NodeUserError` vs `Exception` contract, and `Output` contract enforcement. Moved verbatim out of CLAUDE.md.

- **Log at appropriate levels**: DEBUG for routine operations, INFO for significant events, ERROR for failures
- **Never suppress errors silently** - Always log or propagate
- **Use structured logging** - Include context (node_id, execution_id, etc.)
- **Configurable via `.env`**: Set `LOG_LEVEL=DEBUG` for verbose output, `LOG_LEVEL=INFO` for production

#### Logging Configuration
```bash
# In server/.env
LOG_LEVEL=INFO                  # Default: INFO, DEBUG for verbose
LOG_FORMAT=json                 # 'json' (default) or 'text' for console
LOG_FILE=                       # Optional rotating-file destination
LOG_FILE_MAX_BYTES=10485760     # 10 MiB ceiling per file
LOG_FILE_BACKUP_COUNT=5         # Keep 5 backups (50 MiB total cap)
```

**What logs at each level:**
- `DEBUG`: Template resolution, parameter resolution, node execution details, event waiter registration, downstream traversal
- `INFO`: Workflow completion, deployment start/stop, significant state changes
- `ERROR`: Failures, exceptions, validation errors

#### Logging Infrastructure (canonical patterns)

**Console mode is timestamp-less by design.** The supervisor
(`cli/colors.py`) prepends `[HH:MM:SS.fff]` to every aggregated
line, so `configure_logging` does NOT add an inner `TimeStamper` in
console mode. JSON mode keeps ISO timestamps for machine consumers.
Helpers that print pre-logger init (`_startup_log` in `main.py`,
`_clog` in `core/container.py`) emit raw `print()` so the CLI prefix
is the single timing source.

**Context propagation via `structlog.contextvars`.** Bind once at the
entry point; every log record inside that async context picks the
fields up automatically. Stdlib `contextvars` rides `asyncio.gather`
child tasks.

```python
from core.logging import log_context

async with log_context(workflow_id=wf_id, node_id=node_id):
    await do_work()  # all logs inside carry workflow_id + node_id
```

`BaseNode.execute()` already wraps its body in
`log_context(node_id, node_type, workflow_id?)` so plugin operation
logs are auto-tagged — don't pass these as kwargs at each call site.

**Per-plugin OpenTelemetry span.** `BaseNode.execute()` opens a
`node.<type>.execute` span with attributes `node.id` / `node.type` /
`workflow.id` around the operation body. Single edit instruments every
plugin — no per-plugin span code needed.

**Source-tag resolver for the Terminal UI panel.** `record.name`
collapses to a ≤12-char tag via `_resolve_source_tag` in
`core/logging.py`:

1. `nodes.<plugin>.*` → `<plugin>` (auto-rule; no per-plugin entry)
2. `routers.<name>.*` → `<name>` (auto-rule)
3. Explicit registry `_LOG_SOURCE_TAGS` — only for cross-cutting
   services with long module names (`workflow_validator` → `validator`,
   `status_broadcaster` → `broadcaster`, `user_auth` → `auth`, etc.)
4. Second-segment fallback (`services.ai` → `ai`)

Plugins that genuinely want a different label from their folder name
call `register_log_source_tag(prefix, tag)` from their package
`__init__.py` — same self-registration pattern as the five plugin
registries (`ws_handler`, `filter_builder`, `trigger_precheck`,
`service_refresh`, `output_schema`).

**RotatingFileHandler** swaps in when `LOG_FILE` is set — no
unbounded log growth.

**NodeUserError vs Exception contract** (`services/plugin/base.py`):
- `NodeUserError` → single WARN line, no traceback, structured response
- `PermissionError` annotated with `.provider` / `.reason` / `.auth` →
  `error_type="PermissionDeniedError"` + `credential` envelope block +
  CloudEvents `credential.{auth}.runtime_failed` broadcast
- Bare `Exception` → `logger.exception` with full traceback

Reach for `NodeUserError` for any user-correctable failure
(missing required field, unknown enum value, bad regex). Reserve
`RuntimeError` / `Exception` for genuinely unexpected server bugs.

**Output contract enforcement** (`BaseNode._serialize_result` in
`services/plugin/base.py`): the declared `Output` Pydantic model is
enforced at the serialization boundary, FastAPI-`response_model` style.
Dict results validate via `Output.model_validate(...).model_dump(mode="json",
exclude_unset=True)`; `BaseModel` results dump `mode="json"`; violations
produce an `error_type="OutputValidationError"` envelope at the producer.
Rules: prefer returning the `Output` instance; never put raw third-party
objects (SDK results, dataclasses) or pre-stringified JSON into result
dicts — return plain lists/dicts; Params fields that may receive
LLM-stringified JSON args coerce with `field_validator(mode="before")`
(canonical: `AndroidServiceParams._coerce_parameters`,
`WriteTodosParams._coerce_todos`). Below the plugin layer, the SQLAlchemy
engine sets `json_serializer` backed by `pydantic_core.to_jsonable_python`
(`core/database.py`) so every JSON column tolerates dataclasses /
datetimes / enums / sets. Full spec:
[docs-internal/plugin_system.md → Output contract enforcement](./plugin_system.md);
locked by `server/tests/test_output_contract.py`.
