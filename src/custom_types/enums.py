from enum import StrEnum


class Role(StrEnum):
    SYSTEM: str = "system"
    USER: str = "user"
    ASSISTANT: str = "assistant"

type Memory = list[dict[str,str]]