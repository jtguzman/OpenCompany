---
name: ms-mail-skill
description: Send, read, search, and reply to Outlook email via Microsoft Graph. Supports composing messages, listing recent mail, searching by text, and replying/reply-all.
allowed-tools: "ms_mail"
metadata:
  author: opencompany
  version: "1.0"
  category: productivity

---

# Outlook Mail Skill

Send, read, search, and reply to email using the Microsoft Graph API (Outlook / Microsoft 365).

## Tool: ms_mail

Consolidated Outlook Mail tool with an `operation` parameter.

### Operations

| Operation | Description | Required Fields |
|-----------|-------------|-----------------|
| `send` | Send an email | to, subject, body |
| `read` | Read a message by ID, or list recent mail when no ID is given | (message_id optional) |
| `search` | Search messages by text | query |
| `reply` | Reply to a message | reply_message_id, comment |

### send - Send an email

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| operation | string | Yes | Must be `"send"` |
| to | string | Yes | Recipient address(es), comma-separated |
| subject | string | Yes | Email subject line |
| body | string | Yes | Email body (plain text or HTML) |
| cc | string | No | CC recipients (comma-separated) |
| bcc | string | No | BCC recipients (comma-separated) |
| body_type | string | No | `"text"` or `"html"` (default: text) |

**Example - Send plain text email:**
```json
{
  "operation": "send",
  "to": "alice@contoso.com",
  "subject": "Meeting Tomorrow",
  "body": "Hi,\n\nJust a reminder about our meeting tomorrow at 2pm.\n\nBest regards"
}
```

**Example - Send to multiple recipients with CC:**
```json
{
  "operation": "send",
  "to": "alice@contoso.com, bob@contoso.com",
  "cc": "manager@contoso.com",
  "subject": "Weekly Report",
  "body": "<h1>Weekly Report</h1><p>Highlights...</p>",
  "body_type": "html"
}
```

### read - Read a message or list recent mail

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| operation | string | Yes | Must be `"read"` |
| message_id | string | No | Message ID to fetch (with body). Omit to list recent messages. |
| max_results | integer | No | Max messages when listing (default: 10, max: 100) |

**Example - Read a specific message:**
```json
{
  "operation": "read",
  "message_id": "AAMkAGI2..."
}
```

**Example - List the 20 most recent messages:**
```json
{
  "operation": "read",
  "max_results": 20
}
```

### search - Search messages

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| operation | string | Yes | Must be `"search"` |
| query | string | Yes | Free-text search (Microsoft Graph `$search`) |
| search_max_results | integer | No | Max results (default: 10, max: 100) |

Microsoft Graph search matches across subject, body, sender, and recipients.
Use natural keywords (e.g. `invoice`, `from:jane quarterly plan`); it does not
use Gmail-style operators.

**Example:**
```json
{
  "operation": "search",
  "query": "quarterly plan",
  "search_max_results": 20
}
```

### reply - Reply to a message

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| operation | string | Yes | Must be `"reply"` |
| reply_message_id | string | Yes | ID of the message to reply to (from search/read) |
| comment | string | Yes | The reply text |
| reply_all | boolean | No | Reply to all recipients (default: false) |

**Example:**
```json
{
  "operation": "reply",
  "reply_message_id": "AAMkAGI2...",
  "comment": "Thanks - looks good to me.",
  "reply_all": true
}
```

## Common Workflows

1. **Triage recent mail**: `read` with no ID to list recent messages, then `read` a specific `message_id` for full content.
2. **Find a thread**: `search` by keyword, take the `message_id`, then `reply`.
3. **Send an update**: `send` to one or more recipients, optionally as HTML.

## Setup Requirements

1. Connect the Outlook Mail node to an AI Agent's `input-tools` handle.
2. Authenticate with Microsoft Graph in the Credentials Modal (Work/School account).
3. Ensure the Mail.Send and Mail.ReadWrite scopes are granted.
