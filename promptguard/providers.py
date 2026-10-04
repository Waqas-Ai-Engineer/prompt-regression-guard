"""LLM providers. `mock` is deterministic and offline so tests/CI need no API key."""
from __future__ import annotations
import json, os, urllib.request


class Provider:
    name = "base"

    def complete(self, prompt: str) -> str:  # pragma: no cover - interface
        raise NotImplementedError


class MockProvider(Provider):
    """Deterministic fake: echoes a canned reply chosen by keyword rules.

    Rules come from the suite's `mock_replies` map (substring -> reply); the
    fallback echoes the prompt. This lets you demo regressions offline.
    """
    name = "mock"

    def __init__(self, replies: dict[str, str] | None = None):
        self.replies = replies or {}

    def complete(self, prompt: str) -> str:
        for key, reply in self.replies.items():
            if key.lower() in prompt.lower():
                return reply
        return f"Echo: {prompt}"


class AnthropicProvider(Provider):
    name = "anthropic"

    def __init__(self, model: str | None = None):
        self.key = os.environ["ANTHROPIC_API_KEY"]
        self.model = model or os.environ.get("PROMPTGUARD_MODEL", "claude-haiku-4-5")

    def complete(self, prompt: str) -> str:
        body = json.dumps({"model": self.model, "max_tokens": 512,
                           "messages": [{"role": "user", "content": prompt}]}).encode()
        req = urllib.request.Request("https://api.anthropic.com/v1/messages", body, {
            "x-api-key": self.key, "anthropic-version": "2023-06-01",
            "content-type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.load(r)
        return "".join(b.get("text", "") for b in data["content"])


def get_provider(name: str, **kw) -> Provider:
    if name == "mock":
        return MockProvider(kw.get("replies"))
    if name == "anthropic":
        return AnthropicProvider(kw.get("model"))
    raise ValueError(f"unknown provider: {name}")
