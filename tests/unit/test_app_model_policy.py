"""Model governance tests for IA10."""

import pytest

import app.core.app_model_policy as app_model_policy
from app.core.ai_generation_policy import DEFAULT_EXERCISES_AI_MODEL
from app.core.app_model_policy import (
    CHEAP_ASSISTANT_CHAT_FALLBACK_MODEL,
    DEFAULT_ASSISTANT_CHAT_MODEL,
    PREMIUM_ASSISTANT_CHAT_MODEL,
    AIWorkload,
    assert_assistant_chat_model_allowed,
    controlled_cheap_fallback_model_for_assistant_chat,
    normalize_openai_model_id,
    resolve_assistant_chat_model,
    resolve_assistant_chat_model_for_user,
    resolve_challenges_ai_fallback_public,
    resolve_challenges_ai_model_public,
    resolve_exercises_ai_model_public,
)
from app.core.config import settings
from app.services.challenges.challenge_ai_model_policy import (
    DEFAULT_CHALLENGE_STREAM_FALLBACK_MODEL,
)


def test_workload_enum_values() -> None:
    assert AIWorkload.ASSISTANT_CHAT.value == "assistant_chat"
    assert AIWorkload.EXERCISES_AI.value == "exercises_ai"
    assert AIWorkload.CHALLENGES_AI.value == "challenges_ai"


def test_assistant_default_is_gpt5_mini(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "OPENAI_MODEL_ASSISTANT_CHAT_OVERRIDE", "")
    monkeypatch.setattr(settings, "OPENAI_MODEL", "")
    assert (
        resolve_assistant_chat_model() == DEFAULT_ASSISTANT_CHAT_MODEL == "gpt-5-mini"
    )


def test_assistant_override_ops_wins(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "OPENAI_MODEL_ASSISTANT_CHAT_OVERRIDE", "gpt-4o")
    monkeypatch.setattr(settings, "OPENAI_MODEL", "o3")
    assert resolve_assistant_chat_model() == "gpt-4o"


def test_assistant_override_beats_premium_tier(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "OPENAI_MODEL_ASSISTANT_CHAT_OVERRIDE", "gpt-4o-mini")
    assert resolve_assistant_chat_model(user_tier="premium") == "gpt-4o-mini"


def test_assistant_legacy_openai_model_when_allowlisted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "OPENAI_MODEL_ASSISTANT_CHAT_OVERRIDE", "")
    monkeypatch.setattr(settings, "OPENAI_MODEL", "gpt-4o-mini")
    assert resolve_assistant_chat_model() == "gpt-4o-mini"


def test_assistant_legacy_gpt35_ignored(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "OPENAI_MODEL_ASSISTANT_CHAT_OVERRIDE", "")
    monkeypatch.setattr(settings, "OPENAI_MODEL", "gpt-3.5-turbo")
    assert resolve_assistant_chat_model() == DEFAULT_ASSISTANT_CHAT_MODEL


def test_assistant_premium_stub_seam(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "OPENAI_MODEL_ASSISTANT_CHAT_OVERRIDE", "")
    monkeypatch.setattr(settings, "OPENAI_MODEL", "")
    assert (
        resolve_assistant_chat_model(user_tier="premium")
        == PREMIUM_ASSISTANT_CHAT_MODEL
    )


def test_assistant_invalid_override_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        settings, "OPENAI_MODEL_ASSISTANT_CHAT_OVERRIDE", "gpt-3.5-turbo"
    )
    with pytest.raises(ValueError, match="fail-closed"):
        resolve_assistant_chat_model()


def test_assistant_override_o3_fail_closed_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "OPENAI_MODEL_ASSISTANT_CHAT_OVERRIDE", "o3")
    with pytest.raises(ValueError, match="fail-closed"):
        resolve_assistant_chat_model()


def test_assistant_override_o1_fail_closed_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "OPENAI_MODEL_ASSISTANT_CHAT_OVERRIDE", "o1-mini")
    with pytest.raises(ValueError, match="fail-closed"):
        resolve_assistant_chat_model()


def test_assistant_legacy_openai_model_o3_ignored(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    warnings: list[str] = []

    monkeypatch.setattr(settings, "OPENAI_MODEL_ASSISTANT_CHAT_OVERRIDE", "")
    monkeypatch.setattr(settings, "OPENAI_MODEL", "o3")
    monkeypatch.setattr(
        app_model_policy.logger,
        "warning",
        lambda msg, *args: warnings.append(msg % args if args else msg),
    )

    assert resolve_assistant_chat_model() == DEFAULT_ASSISTANT_CHAT_MODEL
    assert any("OPENAI_MODEL=o3" in message for message in warnings)


def test_assistant_allowlist_rejects_gpt35() -> None:
    with pytest.raises(ValueError, match="fail-closed"):
        assert_assistant_chat_model_allowed("gpt-3.5-turbo")


def test_normalize_openai_model_id() -> None:
    assert normalize_openai_model_id(" GPT-5-Mini ") == "gpt-5-mini"


def test_controlled_cheap_fallback() -> None:
    assert controlled_cheap_fallback_model_for_assistant_chat() == "gpt-4o-mini"
    assert CHEAP_ASSISTANT_CHAT_FALLBACK_MODEL == "gpt-4o-mini"


def test_resolve_exercises_ai_public_delegates_o4_mini(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "OPENAI_MODEL_EXERCISES_OVERRIDE", "")
    monkeypatch.setattr(settings, "OPENAI_MODEL_EXERCISES", "")
    assert (
        resolve_exercises_ai_model_public() == DEFAULT_EXERCISES_AI_MODEL == "o4-mini"
    )


def test_resolve_challenges_ai_public_delegates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "OPENAI_MODEL_CHALLENGES_OVERRIDE", "")
    monkeypatch.setattr(settings, "OPENAI_MODEL_REASONING", "")
    assert resolve_challenges_ai_model_public("sequence") == "o4-mini"


def test_resolve_challenges_fallback_public_delegates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "OPENAI_MODEL_CHALLENGES_FALLBACK_OVERRIDE", "")
    assert (
        resolve_challenges_ai_fallback_public("sequence")
        == DEFAULT_CHALLENGE_STREAM_FALLBACK_MODEL
    )


def test_resolve_assistant_chat_model_for_user_is_stub(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "OPENAI_MODEL_ASSISTANT_CHAT_OVERRIDE", "")
    monkeypatch.setattr(settings, "OPENAI_MODEL", "")
    assert resolve_assistant_chat_model_for_user(42) == DEFAULT_ASSISTANT_CHAT_MODEL
    assert resolve_assistant_chat_model_for_user(42, user_tier="premium") == "gpt-5.4"
