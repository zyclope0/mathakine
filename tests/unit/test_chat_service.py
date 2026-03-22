"""
Tests de caractérisation pour ChatService.

Valident le comportement des fonctions extraites du handler chatbot :
detect_image_request, build_chat_config, cleanup_markdown_images, generate_image.

Phase 3, item 3.2 — audit architecture 03/2026.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.config import settings
from app.services.communication.chat_service import (
    assistant_chat_metrics_key,
    build_chat_config,
    build_openai_chat_completion_kwargs,
    build_system_prompt,
    cleanup_markdown_images,
    detect_complexity,
    detect_image_request,
    estimate_age,
    extract_chat_usage_estimate,
    generate_image,
)

# ── detect_image_request ──────────────────────────────────────────────────


class TestDetectImageRequest:
    def test_image_and_math_keywords(self):
        is_img, is_math = detect_image_request("Dessine-moi un triangle")
        assert is_img is True
        assert is_math is True

    def test_create_exercise_is_not_routed_to_image_generation(self):
        is_img, is_math = detect_image_request("Créer un exercice")
        assert is_img is False
        assert is_math is True

    def test_image_only(self):
        is_img, is_math = detect_image_request("Dessine-moi un chien")
        assert is_img is True
        assert is_math is False

    def test_math_only(self):
        is_img, is_math = detect_image_request("Explique les fractions")
        assert is_img is False
        assert is_math is True

    def test_neither(self):
        is_img, is_math = detect_image_request("Bonjour comment vas-tu")
        assert is_img is False
        assert is_math is False

    def test_case_insensitive(self):
        is_img, _ = detect_image_request("DESSINE un cercle")
        assert is_img is True

    def test_math_general_keyword(self):
        _, is_math = detect_image_request("J'aime les mathématiques")
        assert is_math is True

    def test_generate_image_with_explicit_visual_keyword_still_routes_to_image(self):
        is_img, is_math = detect_image_request("Genere une image de triangle")
        assert is_img is True
        assert is_math is True


# ── build_chat_config ─────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _assistant_chat_policy_isolated(monkeypatch: pytest.MonkeyPatch) -> None:
    """Évite qu'un .env local impose un legacy OPENAI_MODEL pendant les tests."""
    monkeypatch.setattr(settings, "OPENAI_MODEL_ASSISTANT_CHAT_OVERRIDE", "")
    monkeypatch.setattr(settings, "OPENAI_MODEL", "")


class TestBuildChatConfig:
    def test_simple_message_uses_policy_default_model(self):
        cfg = build_chat_config("Combien fait 2+2", [])
        assert cfg["model"] == "gpt-5-mini"
        assert cfg["complexity"] == "simple"
        assert cfg["temperature"] == 0.4
        assert cfg["max_tokens"] == 400

    def test_complex_message_same_model_routing_temperature_only(self):
        cfg = build_chat_config(
            "Peux-tu me démontrer le théorème de Pythagore étape par étape", []
        )
        assert cfg["model"] == "gpt-5-mini"
        assert cfg["complexity"] == "complex"
        assert cfg["temperature"] == 0.6
        assert cfg["max_tokens"] == 500

    def test_premium_tier_uses_policy_premium_model(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setattr(settings, "OPENAI_MODEL_ASSISTANT_CHAT_OVERRIDE", "")
        monkeypatch.setattr(settings, "OPENAI_MODEL", "")
        cfg = build_chat_config("Bonjour", [], user_tier="premium")
        assert cfg["model"] == "gpt-5.4"

    def test_messages_structure(self):
        history = [
            {"role": "user", "content": "Salut"},
            {"role": "assistant", "content": "Bonjour !"},
        ]
        cfg = build_chat_config("Suite de la discussion", history)
        msgs = cfg["messages"]
        assert msgs[0]["role"] == "system"
        assert msgs[1] == {"role": "user", "content": "Salut"}
        assert msgs[2] == {"role": "assistant", "content": "Bonjour !"}
        assert msgs[-1] == {"role": "user", "content": "Suite de la discussion"}

    def test_history_limited_to_last_5(self):
        history = [{"role": "user", "content": f"msg{i}"} for i in range(10)]
        cfg = build_chat_config("Nouveau", history)
        user_msgs = [m for m in cfg["messages"] if m["role"] != "system"]
        assert len(user_msgs) == 6  # 5 history + 1 current

    def test_age_detection_in_system_prompt(self):
        cfg = build_chat_config("Aide-moi avec ce problème de CM1", [])
        system_msg = cfg["messages"][0]["content"]
        assert "5-8" in system_msg


# ── build_openai_chat_completion_kwargs ───────────────────────────────────


def _sample_cfg(model: str) -> dict:
    return {
        "model": model,
        "messages": [{"role": "user", "content": "hi"}],
        "temperature": 0.4,
        "max_tokens": 400,
        "complexity": "simple",
    }


class TestBuildOpenaiChatCompletionKwargs:
    def test_gpt5_mini_uses_max_completion_tokens_not_max_tokens(self):
        kw = build_openai_chat_completion_kwargs(_sample_cfg("gpt-5-mini"), stream=True)
        assert kw["stream"] is True
        assert kw["max_completion_tokens"] == 400
        assert "max_tokens" not in kw
        assert kw["reasoning_effort"] == "low"
        assert kw["verbosity"] == "medium"
        assert "frequency_penalty" not in kw

    def test_gpt5_dot_form_uses_max_completion_tokens(self):
        kw = build_openai_chat_completion_kwargs(_sample_cfg("gpt-5.4"), stream=False)
        assert kw["max_completion_tokens"] == 400
        assert "max_tokens" not in kw

    def test_gpt4o_uses_classic_max_tokens_and_penalties(self):
        kw = build_openai_chat_completion_kwargs(_sample_cfg("gpt-4o"), stream=False)
        assert kw["max_tokens"] == 400
        assert kw["temperature"] == 0.4
        assert "max_completion_tokens" not in kw

    def test_gpt4o_mini_uses_classic_max_tokens_and_penalties(self):
        kw = build_openai_chat_completion_kwargs(
            _sample_cfg("gpt-4o-mini"), stream=False
        )
        assert kw["max_tokens"] == 400
        assert kw["temperature"] == 0.4
        assert kw["top_p"] == 0.9
        assert kw["frequency_penalty"] == 0.3
        assert "max_completion_tokens" not in kw


class TestChatObservabilityHelpers:
    def test_assistant_chat_metrics_key_uses_complexity_bucket(self):
        assert assistant_chat_metrics_key("simple") == "assistant_chat:simple"
        assert assistant_chat_metrics_key("complex") == "assistant_chat:complex"
        assert assistant_chat_metrics_key("unexpected") == "assistant_chat:simple"

    def test_extract_chat_usage_estimate_prefers_usage_when_available(self):
        usage = MagicMock(prompt_tokens=123, completion_tokens=45)
        response = MagicMock(usage=usage)
        prompt_tokens, completion_tokens = extract_chat_usage_estimate(
            response,
            messages=[{"role": "user", "content": "bonjour"}],
            completion_text="salut",
        )
        assert prompt_tokens == 123
        assert completion_tokens == 45

    def test_extract_chat_usage_estimate_falls_back_to_length(self):
        prompt_tokens, completion_tokens = extract_chat_usage_estimate(
            None,
            messages=[{"role": "user", "content": "1234" * 5}],
            completion_text="abcd" * 3,
        )
        assert prompt_tokens > 0
        assert completion_tokens > 0


# ── cleanup_markdown_images ───────────────────────────────────────────────


class TestCleanupMarkdownImages:
    def test_removes_placeholder_images(self):
        text = "Voici ![triangle](https://via.placeholder.com/150) un exemple"
        result = cleanup_markdown_images(text)
        assert "placeholder" not in result
        assert "triangle" in result

    def test_removes_example_com_images(self):
        text = "![fig](https://example.com/img.png)"
        result = cleanup_markdown_images(text)
        assert "example.com" not in result
        assert "fig" in result

    def test_keeps_real_http_images(self):
        text = "![photo](https://real-cdn.com/math.png)"
        result = cleanup_markdown_images(text)
        assert "https://real-cdn.com/math.png" in result

    def test_removes_relative_path_images(self):
        text = "![diagram](./local/path.png)"
        result = cleanup_markdown_images(text)
        assert "./local/path.png" not in result
        assert "diagram" in result

    def test_empty_string(self):
        assert cleanup_markdown_images("") == ""

    def test_no_images(self):
        text = "Texte normal sans images"
        assert cleanup_markdown_images(text) == text


# ── generate_image ────────────────────────────────────────────────────────


class TestGenerateImage:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_client = AsyncMock()
        mock_data = MagicMock()
        mock_data.url = "https://dalle.example.com/image.png"
        mock_client.images.generate.return_value = MagicMock(data=[mock_data])

        url = await generate_image(mock_client, "Un triangle isocèle")
        assert url == "https://dalle.example.com/image.png"
        mock_client.images.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_failure_returns_none(self):
        mock_client = AsyncMock()
        mock_client.images.generate.side_effect = Exception("API down")

        url = await generate_image(mock_client, "Un carré")
        assert url is None
