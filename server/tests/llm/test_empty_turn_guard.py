"""An agent with nothing to say must not become a provider 400.

Failure mode this covers, observed live on an ``aiAgent`` whose ``prompt``
was blank because the operator had put the trigger expression in
``system_message`` instead: the empty user turn is dropped by
``filter_empty_messages``, the request reaches Anthropic with no messages,
and the API answers ``400 messages: at least one message is required``. That
normalizes to ``LLMErrorCategory.INVALID_REQUEST``, whose user message is
"Anthropic rejected the model request configuration." — it names neither the
node nor the field, so the operator cannot get back to the empty Prompt.

Three invariants:

1. ``require_sendable_turn`` rejects a blank prompt when the thread carries
   no other content, and stays out of the way when it does.
2. ``run_native_llm_step`` refuses the call rather than sending an empty
   message list (the backstop for the Temporal path, which assembles its
   own messages).
3. The unifier logs the provider's own error text, so the next
   ``INVALID_REQUEST`` is diagnosable without a live probe.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.ai import require_sendable_turn
from services.agent_runtime import run_native_llm_step
from services.llm.protocol import LLMError, LLMErrorCategory, Message
from services.plugin import NodeUserError


# ---------------------------------------------------------------------------
# 1. require_sendable_turn
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("prompt", ["", "   ", None])
def test_blank_prompt_without_history_is_a_user_error(prompt):
    with pytest.raises(NodeUserError) as exc:
        require_sendable_turn(prompt, [Message(role="system", content="be nice")], "5:aiAgent:1")
    # The message must name the node and the parameter to fix.
    assert "5:aiAgent:1" in str(exc.value)
    assert "Prompt" in str(exc.value)


def test_blank_prompt_with_conversation_history_is_allowed():
    """A continuing thread already gives the model something to answer."""
    history = [
        Message(role="system", content="be nice"),
        Message(role="user", content="hola"),
        Message(role="assistant", content="¡Hola!"),
    ]
    require_sendable_turn("", history, "5:aiAgent:1")


def test_non_empty_prompt_is_allowed_without_history():
    require_sendable_turn("hola", [], "5:aiAgent:1")


# ---------------------------------------------------------------------------
# 2. run_native_llm_step backstop
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_all_empty_messages_never_reach_the_provider():
    unifier = MagicMock()
    unifier.chat = AsyncMock()
    with pytest.raises(NodeUserError):
        await run_native_llm_step(
            unifier,
            provider="anthropic",
            api_key="k",
            messages=[
                Message(role="system", content="be nice"),
                Message(role="user", content=""),
            ],
            model="claude-sonnet-4-6",
            temperature=0.7,
            max_tokens=1024,
        )
    unifier.chat.assert_not_awaited()


@pytest.mark.asyncio
async def test_surviving_content_still_calls_the_provider():
    unifier = MagicMock()
    unifier.chat = AsyncMock(return_value="sentinel")
    result = await run_native_llm_step(
        unifier,
        provider="anthropic",
        api_key="k",
        messages=[
            Message(role="system", content="be nice"),
            Message(role="user", content=""),
            Message(role="user", content="hola"),
        ],
        model="claude-sonnet-4-6",
        temperature=0.7,
        max_tokens=1024,
    )
    assert result == "sentinel"
    sent = unifier.chat.await_args.kwargs["messages"]
    assert [m.content for m in sent if m.role == "user"] == ["hola"]


# ---------------------------------------------------------------------------
# 3. the provider's own text survives into the log
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_provider_error_detail_is_logged():
    """The sanitized envelope is what the user sees; the log keeps the field."""
    raw = "Error code: 400 - {'error': {'message': 'messages: at least one message is required'}}"
    spec = MagicMock()
    spec.sdk_exception_types = (RuntimeError,)
    entry = MagicMock()
    entry.client = MagicMock()
    entry.client.chat = AsyncMock(side_effect=RuntimeError(raw))

    from services.llm.unifier import ChatUnifier

    unifier = ChatUnifier.__new__(ChatUnifier)
    unifier._acquire_client = AsyncMock(return_value=entry)
    unifier._release_client = AsyncMock()

    error = LLMError(
        provider="anthropic",
        category=LLMErrorCategory.INVALID_REQUEST,
        message=raw,
    )
    with (
        patch("services.llm.unifier.get_provider", return_value=spec),
        patch("services.llm.unifier.LLMError.from_exception", return_value=error),
        patch("services.llm.unifier.logger") as logger,
    ):
        with pytest.raises(NodeUserError):
            await unifier.chat(
                provider="anthropic",
                api_key="k",
                messages=[Message(role="user", content="hola")],
                model="claude-sonnet-4-6",
            )
    assert "at least one message is required" in logger.warning.call_args.kwargs["detail"]
