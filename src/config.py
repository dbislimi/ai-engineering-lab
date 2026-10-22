import os
from dataclasses import dataclass, field

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Maximum context window (in tokens) per model
MODEL_CONTEXT_WINDOWS: dict[str, int] = {
    # --- OpenAI ---
    # GPT-6 family (flagship, oct. 2026)
    "gpt-6-astra":          1_050_000,
    "gpt-6.1-sol":          1_050_000,
    "gpt-6-luna":           1_050_000,
    # GPT-5.6 family
    "gpt-5.6-luna":         1_050_000,
    "gpt-5.6-cyber":        1_050_000,
    # GPT-5 family
    "gpt-5":                  400_000,
    # GPT-4.1 family
    "gpt-4.1":              1_047_576,
    "gpt-4.1-mini":         1_047_576,
    "gpt-4.1-nano":         1_047_576,
    # GPT-4o family
    "gpt-4o":                 128_000,
    "gpt-4o-mini":            128_000,
    "gpt-4o-audio-preview":   128_000,
    "gpt-4o-realtime-preview": 128_000,
    # o-series (reasoning models)
    "o1":                     200_000,
    "o1-mini":                128_000,
    "o1-pro":                 200_000,
    "o3":                     200_000,
    "o3-mini":                200_000,
    "o3-pro":                 200_000,
    "o4-mini":                200_000,
    # GPT-4 Turbo / GPT-4 (legacy)
    "gpt-4-turbo":            128_000,
    "gpt-4-turbo-preview":    128_000,
    "gpt-4":                    8_192,
    "gpt-4-32k":               32_768,
    # GPT-3.5 (legacy)
    "gpt-3.5-turbo":           16_385,
    "gpt-3.5-turbo-instruct":   4_096,

    # --- Anthropic Claude ---
    # Claude 5.5 family (oct. 2026) — 1M context
    "claude-fable-5-1":     1_000_000,
    "claude-opus-5-5":      1_000_000,
    "claude-sonnet-5-5":    1_000_000,
    "claude-haiku-5-5":     1_000_000,
    # Claude 4 family
    "claude-opus-4-5":        200_000,
    "claude-sonnet-4-5":      200_000,
    "claude-opus-4-0":        200_000,
    "claude-sonnet-4-0":      200_000,
    # Claude 3.7
    "claude-3-7-sonnet-20250219": 200_000,
    # Claude 3.5 family
    "claude-3-5-opus-20241022":   200_000,
    "claude-3-5-sonnet-20241022": 200_000,
    "claude-3-5-sonnet-20240620": 200_000,
    "claude-3-5-haiku-20241022":  200_000,
    # Claude 3 family (legacy)
    "claude-3-opus-20240229":   200_000,
    "claude-3-sonnet-20240229": 200_000,
    "claude-3-haiku-20240307":  200_000,
    # Claude 2 family (legacy)
    "claude-2.1":               200_000,
    "claude-2.0":               100_000,
    # Claude Instant (legacy)
    "claude-instant-1.2":       100_000,
}


@dataclass
class Config:
    client: OpenAI
    model: str
    system_prompt: str
    extra_body: dict = field(default_factory=dict)

    def complete(self, messages: list[dict], **kwargs):
        return self.client.chat.completions.create(
            model=self.model, messages=messages, extra_body=self.extra_body, **kwargs
        )


def load_config() -> Config:
    reasoning_effort = (
        "none"  # Ollama : Disable thinking. Let Empty if the API refuses.
    )
    return Config(
        client=OpenAI(
            base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434/v1"),
            api_key=os.getenv("LLM_API_KEY", "ollama"),
            max_retries=3,
        ),
        model=os.getenv("CHAT_MODEL", "qwen3.5:4b"),
        system_prompt="If any of your previous responses ends with [INTERRUPTED BY USER], it means the user intentionally stopped the text generation.",
        extra_body={"reasoning_effort": reasoning_effort} if reasoning_effort else {},
    )
