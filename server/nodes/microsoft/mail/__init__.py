"""Outlook Mail via Microsoft Graph — multi-op ActionNode + AI tool.

Operations (dispatched off ``params.operation``):
- send   -> POST /me/sendMail
- read   -> GET  /me/messages/{id}  (or GET /me/messages?$top= when no id)
- search -> GET  /me/messages?$search="..."
- reply  -> POST /me/messages/{id}/reply
"""

from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from services.plugin import ActionNode, NodeContext, NodeUserError, Operation, TaskQueue

from .._base import graph_request, track_microsoft_usage
from .._credentials import MicrosoftCredential

_SEND = {"displayOptions": {"show": {"operation": ["send"]}}}
_READ = {"displayOptions": {"show": {"operation": ["read"]}}}
_SEARCH = {"displayOptions": {"show": {"operation": ["search"]}}}
_REPLY = {"displayOptions": {"show": {"operation": ["reply"]}}}


class MailParams(BaseModel):
    operation: Literal["send", "read", "search", "reply"] = "send"

    # Send
    to: str = Field(
        default="",
        json_schema_extra={"placeholder": "alice@contoso.com, bob@contoso.com", **_SEND},
    )
    cc: str = Field(default="", json_schema_extra=_SEND)
    bcc: str = Field(default="", json_schema_extra=_SEND)
    subject: str = Field(default="", json_schema_extra=_SEND)
    body: str = Field(
        default="",
        json_schema_extra={"rows": 4, "placeholder": "Write your message...", **_SEND},
    )
    body_type: Literal["text", "html"] = Field(default="text", json_schema_extra=_SEND)

    # Read (message_id optional: omit to list recent messages)
    message_id: str = Field(default="", json_schema_extra=_READ)
    max_results: int = Field(default=10, ge=1, le=100, json_schema_extra=_READ)

    # Search
    query: str = Field(
        default="",
        json_schema_extra={"placeholder": "from:jane subject:meeting", **_SEARCH},
    )
    search_max_results: int = Field(default=10, ge=1, le=100, json_schema_extra=_SEARCH)

    # Reply
    reply_message_id: str = Field(default="", json_schema_extra=_REPLY)
    comment: str = Field(
        default="",
        json_schema_extra={"rows": 4, "placeholder": "Your reply...", **_REPLY},
    )
    reply_all: bool = Field(default=False, json_schema_extra=_REPLY)

    model_config = ConfigDict(extra="ignore")


class MailOutput(BaseModel):
    operation: Optional[str] = None
    sent: Optional[bool] = None
    replied: Optional[bool] = None
    to: Optional[str] = None
    subject: Optional[str] = None
    message_id: Optional[str] = None
    from_: Optional[str] = Field(default=None)
    received: Optional[str] = None
    body_preview: Optional[str] = None
    body: Optional[str] = None
    web_link: Optional[str] = None
    messages: Optional[List[dict]] = None
    count: Optional[int] = None
    query: Optional[str] = None

    model_config = ConfigDict(extra="allow")


def _recipients(raw: str) -> list:
    """Comma/semicolon-separated addresses -> Graph recipient objects."""
    parts = [p.strip() for chunk in raw.split(",") for p in chunk.split(";")]
    return [{"emailAddress": {"address": addr}} for addr in parts if addr]


def _summarize(msg: dict) -> dict:
    """Compact a Graph message resource into a flat summary dict."""
    sender = (msg.get("from") or {}).get("emailAddress") or {}
    return {
        "message_id": msg.get("id"),
        "subject": msg.get("subject", ""),
        "from": sender.get("address", ""),
        "from_name": sender.get("name", ""),
        "received": msg.get("receivedDateTime"),
        "body_preview": msg.get("bodyPreview", ""),
        "is_read": msg.get("isRead"),
        "web_link": msg.get("webLink"),
    }


class MailNode(ActionNode):
    type = "msMail"
    display_name = "Outlook Mail"
    subtitle = "Email Operations"
    group = ("microsoft", "tool")
    description = "Microsoft Outlook Mail send / read / search / reply via Graph (workflow + AI tool)"
    component_kind = "square"
    tool_name = "ms_mail"
    tool_description = (
        "Send, read, search, and reply to Outlook email via Microsoft Graph. "
        "Operations: send (compose), read (get message by ID or list recent), "
        "search (find messages by text), reply (respond to a message)."
    )
    handles = (
        {"name": "input-main", "kind": "input", "position": "left", "label": "Input", "role": "main"},
        {"name": "output-main", "kind": "output", "position": "right", "label": "Output", "role": "main"},
    )
    credentials = (MicrosoftCredential,)
    annotations = {"destructive": False, "readonly": False, "open_world": True}
    task_queue = TaskQueue.REST_API
    usable_as_tool = True

    Params = MailParams
    Output = MailOutput

    _SELECT = "id,subject,from,receivedDateTime,bodyPreview,isRead,webLink"

    @Operation("dispatch")
    async def dispatch(self, ctx: NodeContext, params: MailParams) -> MailOutput:
        op = params.operation

        if op == "send":
            return await self._send(ctx, params)
        if op == "read":
            return await self._read(ctx, params)
        if op == "search":
            return await self._search(ctx, params)
        if op == "reply":
            return await self._reply(ctx, params)
        raise NodeUserError(f"Unknown Mail operation: {op}")

    async def _send(self, ctx: NodeContext, params: MailParams) -> MailOutput:
        if not params.to:
            raise NodeUserError("Recipient email address (to) is required")
        if not params.subject:
            raise NodeUserError("Email subject is required")
        if not params.body:
            raise NodeUserError("Email body is required")

        message = {
            "subject": params.subject,
            "body": {
                "contentType": "HTML" if params.body_type == "html" else "Text",
                "content": params.body,
            },
            "toRecipients": _recipients(params.to),
        }
        if params.cc:
            message["ccRecipients"] = _recipients(params.cc)
        if params.bcc:
            message["bccRecipients"] = _recipients(params.bcc)

        await graph_request(
            ctx,
            "POST",
            "/me/sendMail",
            json={"message": message, "saveToSentItems": True},
        )
        await track_microsoft_usage(ctx.node_id, "send", 1, ctx.raw)
        return MailOutput(operation="send", sent=True, to=params.to, subject=params.subject)

    async def _read(self, ctx: NodeContext, params: MailParams) -> MailOutput:
        if params.message_id:
            msg = await graph_request(
                ctx,
                "GET",
                f"/me/messages/{params.message_id}",
                params={"$select": f"{self._SELECT},body"},
            )
            await track_microsoft_usage(ctx.node_id, "read", 1, ctx.raw)
            summary = _summarize(msg or {})
            body = ((msg or {}).get("body") or {}).get("content", "")
            return MailOutput(
                operation="read",
                message_id=summary["message_id"],
                subject=summary["subject"],
                from_=summary["from"],
                received=summary["received"],
                body_preview=summary["body_preview"],
                body=body,
                web_link=summary["web_link"],
            )

        # No id -> list most recent messages.
        data = await graph_request(
            ctx,
            "GET",
            "/me/messages",
            params={
                "$top": min(params.max_results, 100),
                "$select": self._SELECT,
                "$orderby": "receivedDateTime desc",
            },
        )
        items = (data or {}).get("value", [])
        formatted = [_summarize(m) for m in items]
        await track_microsoft_usage(ctx.node_id, "read", len(formatted), ctx.raw)
        return MailOutput(operation="read", messages=formatted, count=len(formatted))

    async def _search(self, ctx: NodeContext, params: MailParams) -> MailOutput:
        if not params.query:
            raise NodeUserError("Search query is required")
        # Graph $search must be a quoted string; it cannot combine with $orderby.
        data = await graph_request(
            ctx,
            "GET",
            "/me/messages",
            params={
                "$search": f'"{params.query}"',
                "$top": min(params.search_max_results, 100),
                "$select": self._SELECT,
            },
        )
        items = (data or {}).get("value", [])
        formatted = [_summarize(m) for m in items]
        await track_microsoft_usage(ctx.node_id, "search", len(formatted), ctx.raw)
        return MailOutput(
            operation="search",
            messages=formatted,
            count=len(formatted),
            query=params.query,
        )

    async def _reply(self, ctx: NodeContext, params: MailParams) -> MailOutput:
        if not params.reply_message_id:
            raise NodeUserError("reply_message_id is required")
        if not params.comment:
            raise NodeUserError("Reply comment is required")
        endpoint = "replyAll" if params.reply_all else "reply"
        await graph_request(
            ctx,
            "POST",
            f"/me/messages/{params.reply_message_id}/{endpoint}",
            json={"comment": params.comment},
        )
        await track_microsoft_usage(ctx.node_id, "reply", 1, ctx.raw)
        return MailOutput(operation="reply", replied=True, message_id=params.reply_message_id)
