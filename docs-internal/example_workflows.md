# Example Workflows

Seed JSONs at `<repo>/.opencompany/workflows/`, auto-load on first fetch, JSON format, adding custom examples. Moved verbatim out of CLAUDE.md.

## Example Workflows

### Overview
Example workflows are pre-built workflow templates that auto-load on first use. They provide users with starting points to explore the platform's capabilities. Seeds live as JSON files at **`<repo>/.opencompany/workflows/`** — the only git-tracked content under `<repo>/.opencompany/` (everything else there is `.gitignore`d as runtime state). The path is also preserved by `company clean` (see `_OPENCOMPANY_KEEP` in `cli/commands/clean.py`).

### Architecture
```
<repo>/.opencompany/workflows/        # Shipped seed JSONs (git-tracked)
├── AI Assistant_example_workflow-*.json
├── AI Employee_example_workflow-*.json
└── Claude Assistant_example_workflow-*.json

server/services/
└── example_loader.py             # Loads and imports examples via core.paths.example_workflows_dir()

server/models/database.py         # UserSettings.examples_loaded flag
server/core/database.py           # Migration for examples_loaded column
server/routers/database.py        # Auto-load logic in get_all_workflows
```

### How It Works
1. **First Fetch Detection**: When `get_all_workflows` API is called, it checks `UserSettings.examples_loaded`
2. **Auto-Import**: If `examples_loaded=false`, calls `example_loader.get_example_workflows()` which reads from `core.paths.example_workflows_dir()` = `<repo>/.opencompany/workflows/`
3. **Mark Complete**: Sets `examples_loaded=true` to prevent re-import on subsequent fetches
4. **Anonymous Support**: Uses `user_id="default"` when `VITE_AUTH_ENABLED=false`

### Workflow JSON Format
Example workflows use the same format as UI exports:
```json
{
  "id": "hello_world",
  "name": "Hello World",
  "description": "A simple workflow with a start node",
  "nodes": [
    {
      "id": "start_1",
      "type": "start",
      "position": {"x": 250, "y": 150},
      "data": {"label": "Start"}
    }
  ],
  "edges": [],
  "nodeParameters": {
    "start_1": { "someParam": "value" }
  },
  "version": "0.0.36"
}
```

**Fields:**
| Field | Description |
|-------|-------------|
| `id` | Unique identifier (prefixed with `example_` when imported) |
| `name` | Display name in workflow sidebar |
| `description` | Optional description |
| `nodes` | Array of node objects with id, type, position, data |
| `edges` | Array of edge connections between nodes |
| `nodeParameters` | Optional map of node_id to parameter objects (saved to DB on import) |
| `version` | App version (e.g., "0.0.36") |

### Key Files
| File | Description |
|------|-------------|
| `.opencompany/workflows/*.json` | Shipped seed workflow JSONs (git-tracked) |
| `server/core/paths.py` | `example_workflows_dir()` → `<repo>/.opencompany/workflows/` (fixed path, NOT under `DATA_DIR`) |
| `server/services/example_loader.py` | `get_example_workflows()`, `import_examples_for_user()` |
| `server/models/database.py` | `UserSettings.examples_loaded` field |
| `server/core/database.py` | Migration adds `examples_loaded` column |
| `server/routers/database.py` | Auto-load check in `get_all_workflows` |

### Example Loader Service
```python
# server/services/example_loader.py
from core.paths import example_workflows_dir

def get_example_workflows() -> List[Dict[str, Any]]:
    """Load all example workflow JSON files from disk."""
    examples_dir = example_workflows_dir()
    ...

async def import_examples_for_user(database) -> int:
    """Import all examples using existing database.save_workflow().
    Returns count of workflows imported."""
```

### Auto-Load Logic
```python
# server/routers/database.py - get_all_workflows endpoint
user_id = "default"
settings = await database.get_user_settings(user_id)

if not settings or not settings.get("examples_loaded", False):
    count = await import_examples_for_user(database)
    if count > 0:
        logger.info(f"Auto-loaded {count} example workflows")
    current = settings or {}
    current["examples_loaded"] = True
    await database.save_user_settings(current, user_id)
```

### Adding Custom Examples
1. Export a workflow from the UI (File > Export)
2. Copy the JSON file to `<repo>/.opencompany/workflows/` (git-tracked seed location)
3. Edit the `id` and `name` fields as needed
4. Delete `~/.opencompany/workflow.db` (or set `examples_loaded=false` in DB)
5. Restart server - examples auto-load on first workflow list fetch

### Database Migration
The `examples_loaded` column is automatically added to existing databases:
```python
# server/core/database.py - _migrate_user_settings()
if "examples_loaded" not in columns:
    await conn.execute(text(
        "ALTER TABLE user_settings ADD COLUMN examples_loaded BOOLEAN DEFAULT 0"
    ))
```
