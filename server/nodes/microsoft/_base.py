"""Shared helpers for Microsoft Graph plugins.

Every Microsoft plugin follows the same pattern:

    ensure a fresh access token -> ctx.connection("microsoft").<verb>(url)
    -> response.json() -> track usage -> return Output

``graph_request`` captures the token-freshness + base-URL + error
handling so each ``@Operation`` shrinks to the Graph-specific call +
argument shaping. Graph is plain bearer REST, so — unlike Google — no
SDK object is built; the :class:`Connection` facade injects the token
and retries once on 401/403.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import httpx

from core.logging import get_logger
from services.plugin import NodeUserError
from services.pricing import get_pricing_service

from ._auth_helper import ensure_fresh_microsoft_token

logger = get_logger(__name__)

GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"


async def graph_request(
    ctx,
    method: str,
    path: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    json: Optional[Any] = None,
) -> Optional[Dict[str, Any]]:
    """Issue an authed Microsoft Graph request.

    Args:
        ctx: NodeContext (provides the Connection factory + user_id).
        method: HTTP verb.
        path: Graph path beginning with ``/`` (appended to ``GRAPH_BASE_URL``),
            or an absolute URL (used verbatim, e.g. an ``@odata.nextLink``).
        params: Query string params.
        json: JSON request body.

    Returns:
        Parsed JSON dict, or ``None`` for empty-body responses (e.g. 202
        from sendMail, 204 from delete).

    Raises:
        NodeUserError: on a non-2xx Graph response, carrying Graph's own
            error message so the user/LLM can correct the input.
    """
    # Guarantee the STORED access token is fresh before the Connection
    # facade resolves + injects it (get_oauth_tokens does not refresh).
    await ensure_fresh_microsoft_token(getattr(ctx, "user_id", "owner"))

    url = path if path.startswith("http") else f"{GRAPH_BASE_URL}{path}"

    async with ctx.connection("microsoft") as conn:
        response = await conn.request(method, url, params=params, json=json)

    if response.status_code >= 400:
        raise NodeUserError(_format_graph_error(response))

    if response.status_code == 204 or not response.content:
        return None
    try:
        return response.json()
    except (ValueError, httpx.DecodingError):
        return None


def _format_graph_error(response: httpx.Response) -> str:
    """Extract Microsoft Graph's structured error message for a user-facing warning."""
    try:
        body = response.json()
    except (ValueError, httpx.DecodingError):
        body = None
    if isinstance(body, dict):
        err = body.get("error")
        if isinstance(err, dict):
            code = err.get("code", "")
            message = err.get("message", "")
            detail = f"{code}: {message}".strip(": ") if (code or message) else ""
            if detail:
                return f"Microsoft Graph error ({response.status_code}): {detail}"
    return f"Microsoft Graph request failed with HTTP {response.status_code}"


async def track_microsoft_usage(
    node_id: str,
    action: str,
    resource_count: int,
    context: Dict[str, Any],
) -> Dict[str, float]:
    """Record a Microsoft Graph call in ``api_usage_metrics``.

    ``action`` maps through ``pricing.json``'s ``microsoft_graph``
    operation_map (send / read / search / reply / create / update /
    delete / list). Graph is free at our tier — analytics bookkeeping,
    cost is $0.
    """
    from services.plugin.deps import get_database

    pricing = get_pricing_service()
    cost_data = pricing.calculate_api_cost("microsoft_graph", action, resource_count)

    db = get_database()
    await db.save_api_usage_metric(
        {
            "session_id": context.get("session_id", "default"),
            "node_id": node_id,
            "workflow_id": context.get("workflow_id"),
            "service": "microsoft_graph",
            "operation": cost_data.get("operation", action),
            "endpoint": action,
            "resource_count": resource_count,
            "cost": cost_data.get("total_cost", 0.0),
        }
    )
    return cost_data
