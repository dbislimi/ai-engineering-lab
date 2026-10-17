import os
from dataclasses import dataclass, field

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


@dataclass
class AppConfig:
    client: OpenAI
    model: str
    system_prompt: str
    extra_body: dict = field(default_factory=dict)

    def complete(self, messages: list[dict], **kwargs):
        return self.client.chat.completions.create(
            model=self.model, messages=messages, extra_body=self.extra_body, **kwargs
        )


def load_config() -> AppConfig:
    reasoning_effort = "none" # Ollama : Disable thinking. Let Empty if the API refuses.
    return AppConfig(
        client=OpenAI(
            base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434/v1"),
            api_key=os.getenv("LLM_API_KEY", "ollama"),
            max_retries=3,
        ),
        model=os.getenv("CHAT_MODEL", "qwen3.5:4b"),
        system_prompt="",
        extra_body={"reasoning_effort": reasoning_effort} if reasoning_effort else {},
    )
