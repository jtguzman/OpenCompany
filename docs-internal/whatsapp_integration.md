# WhatsApp Integration

Architecture, backend helpers, frontend component, historical bug fixes, error-handling pattern, group/sender name persistence. Moved verbatim out of CLAUDE.md.

## WhatsApp Integration

### Overview
WhatsApp nodes use square design with integrated QR code viewing and proper error handling. The integration proxies all requests through the Python backend to the WhatsApp RPC service (port from `WHATSAPP_RPC_PORT`, or the `--port` CLI flag). Supports individual chats, groups, and newsletter channels (sending, querying, follow/unfollow, create, mute, mark viewed, react, live updates, media download, profile pics). All 14 WhatsApp events handled.

### Architecture
```
Frontend (WhatsAppNode.tsx) → Python Backend (/api/whatsapp/*) → WhatsApp RPC Service (localhost:${WHATSAPP_RPC_PORT})
```

### Key Features
- **Square Node Design**: 80x80px square nodes with status indicators
- **QR Code Viewer**: Embedded QR code display via Python backend proxy
- **Error Handling**: Robust error handling with proper HTTP status codes (503, 504, 410)
- **No Mock Data**: All endpoints return proper errors instead of mock responses
- **Connection Status**: Real-time status display with device ID, session, and service info

### Backend Helpers (`server/services/whatsapp_service.py`)

Wave 11: renamed from `routers/whatsapp.py` (was misnamed — never an APIRouter). Provides RPC proxy helpers consumed by `nodes/whatsapp/*` plugins and the WhatsApp WebSocket handlers.

#### `/api/whatsapp/status` - Get Connection Status
- Returns WhatsApp connection status from Flask service
- Handles ConnectError, TimeoutException with 503/504 status codes
- Safe JSON parsing with error handling

#### `/api/whatsapp/qr` - Get QR Code
- Checks connection status first
- Returns QR code data if not connected
- Returns "Already connected" message if connected
- Handles errors gracefully without crashing

#### `/api/whatsapp/start` - Start Connection
- Proxies start request to Flask service
- Safe JSON parsing and error handling
- Returns proper HTTP errors on failure

#### `/api/whatsapp/send` - Send Message
- Enhanced messaging endpoint
- Comprehensive error handling with specific exception catches
- Never crashes on service unavailability

### Frontend Component (`client/src/components/WhatsAppNode.tsx`)
- **Node Type**: Square (80x80px, borderRadius: 8px)
- **Status Indicators**: Top-right corner indicator (green/yellow/red)
- **Connect Button**: Bottom-left corner for opening modal
- **QR Code Display**: Fetches QR via `fetchQRCode()` from Python backend
- **Connection Details**: Shows device ID, status, session, service, pairing, timestamp
- **Action Buttons**: Start, Restart, Refresh Status, Close (always visible)

### Critical Bug Fixes

#### 1. Missing Dependency Injection Wiring
**Problem**: `main.py` was missing `"routers.whatsapp"` in `container.wire()` modules list
**Impact**: Uvicorn reloader child process crashed with exit code 1, triggering SIGTERM
**Fix**: Added `"routers.whatsapp"` to wiring list in `server/main.py`

(Historical snippet — the router set has since changed: `routers.whatsapp` /
`routers.maps` / `routers.android` moved into plugin folders (Wave 11.I) and
`routers.nodejs_compat` was deleted (July 2026). The live wire list is in
`server/main.py`. The lesson stands: every wired module must be listed or the
reloader child crashes.)

#### 2. Unhandled JSON Parse Errors
**Problem**: `.json()` calls without error handling raised `JSONDecodeError` when Flask returned HTML errors
**Impact**: Server crashes when WhatsApp service unavailable
**Fix**: Wrapped all `.json()` calls in try-except blocks with proper error responses

#### 3. Unhandled HTTP Status Errors
**Problem**: `response.raise_for_status()` raised `httpx.HTTPStatusError` not caught by specific handlers
**Impact**: Unhandled exceptions crashed the server
**Fix**: Removed `.raise_for_status()`, manually check `response.status_code != 200`

#### 4. Missing HTTPException Re-raise
**Problem**: Generic `Exception` handlers didn't re-raise `HTTPException`
**Impact**: Double exception wrapping and unclear errors
**Fix**: Added `except HTTPException: raise` before generic handler

### Error Handling Pattern
All WhatsApp endpoints follow this pattern:
```python
try:
    response = await client.get(url, timeout=10.0)

    # Check status manually
    if response.status_code != 200:
        raise HTTPException(status_code=503, detail="...")

    # Safe JSON parsing
    try:
        data = response.json()
        return data
    except Exception as json_err:
        logger.error(f"Failed to parse JSON: {json_err}")
        raise HTTPException(status_code=503, detail="Invalid response")

except httpx.ConnectError as e:
    raise HTTPException(status_code=503, detail="Service not running")
except httpx.TimeoutException as e:
    raise HTTPException(status_code=504, detail="Service timeout")
except HTTPException:
    raise  # Re-raise HTTPException
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise HTTPException(status_code=503, detail="Service unavailable")
```

### Result
- Python backend never crashes when WhatsApp service is down
- Proper HTTP error codes (503, 504, 410) returned
- No SIGTERM crashes
- Frontend receives proper error messages
- QR code viewer works seamlessly
- All mock data removed from production code

### WhatsApp Group/Sender Name Persistence
The WhatsApp Receive node stores human-readable names alongside JIDs/phone numbers:

#### Problem
When reopening the parameter panel, group/sender selectors showed the raw JID (e.g., `120363123456789@g.us`) instead of the group name because the name was only fetched when the dropdown was opened.

#### Solution
Store the name as a separate parameter alongside the ID:
- `group_id` + `group_name` - Group JID and display name
- `phone_number` + `sender_name` - Phone number and contact name

#### Implementation
```typescript
// In ParameterRenderer.tsx - GroupIdSelector
<GroupIdSelector
  value={currentValue || ''}
  onChange={onChange}
  onNameChange={(name) => onParameterChange?.('group_name', name)}
  storedName={allParameters?.group_name || ''}
  ...
/>

// GroupIdSelector stores name when selection changes
const handleChange = (value: string, option: any) => {
  onChange(value);
  if (option?.label && onNameChange) {
    onNameChange(option.label);
  }
};

// Display uses storedName when available
const displayLabel = storedName || (value && !loading ? value : '');
```

#### Key Files
- `client/src/components/ParameterRenderer.tsx` - GroupIdSelector and SenderNumberSelector with `onNameChange` and `storedName` props
- `client/src/components/parameterPanel/MiddleSection.tsx` - Passes `onParameterChange` to ParameterRenderer
