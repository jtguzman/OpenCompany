# API Cost Tracking

Manual vs automatic HTTPX tracking, pricing config keys, storage, frontend display. Moved verbatim out of CLAUDE.md. Full reference in [pricing_service.md](./pricing_service.md).

Centralized cost tracking for third-party API services (Twitter/X, Google Maps). See [Pricing Service](./pricing_service.md) for full documentation.

### Two Tracking Methods

**1. Manual Tracking** - For services using native SDKs:
```python
# usage tracked inside server/nodes/twitter/
await _track_twitter_usage(node_id, 'tweet', 1, workflow_id, session_id)

# usage tracked inside server/nodes/location/_service.py
await _track_maps_usage(node_id, 'geocode', 1, workflow_id, session_id)
```

**2. Automatic HTTPX Tracking** - For services using httpx client:
```python
from services.tracked_http import get_tracked_client, set_tracking_context

set_tracking_context(node_id="twitter-1", session_id="user-123")
client = get_tracked_client()
response = await client.post("https://api.twitter.com/2/tweets", json={...})
# Automatically tracked via HTTPX response event hook!
```

### Pricing Configuration

All pricing in `server/config/pricing.json` (user-editable):
- `llm`: Per-model token pricing (USD/MTok)
- `api`: Per-service operation pricing (USD/request)
- `operation_map`: Maps handler actions to pricing operations
- `url_patterns`: Regex patterns for automatic HTTPX tracking

### Database Storage

`APIUsageMetric` table stores: service, operation, endpoint, resource_count, cost (USD)

### Frontend Display

`CredentialsModal.renderApiUsagePanel()` shows per-service usage and costs.
