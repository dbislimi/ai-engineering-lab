from abc import ABC, abstractmethod

import ollama

from config import MODEL_CONTEXT_WINDOWS, Config
from custom_types.enums import Memory, Role
from memory.token_counter import TokenCounter


class MemoryManager(ABC):
    def __init__(self, system_prompt: str | None = None):
        self.system_prompt = system_prompt
        self.memory: Memory = []
        self.history: Memory = []

    def add_msg(self, role: Role, content: str) -> bool:
        self.memory.append({"role": role, "content": content})
        try:
            self._handle_memory()
        except ValueError as e:
            print(f"Error: {e}")
            return False
        return True

    def add_to_history(self, user: str, assistant: str):
        self.history.append({"role": Role.USER, "content": user})
        self.history.append({"role": Role.ASSISTANT, "content": assistant})

    def _get_sys_prompt(self) -> Memory:
        if not self.system_prompt:
            return []
        return {"role": Role.SYSTEM, "content": self.system_prompt}

    def get_memory(self) -> Memory:
        return [self._get_sys_prompt()] + self.memory

    def get_history(self) -> Memory:
        return self.history

    def print(self):
        print(self._get_sys_prompt())
        for e in self.memory:
            print(e)

    def pop(self):
        self.memory.pop()

    @abstractmethod
    def _handle_memory(self) -> Memory:
        pass


class SlidingWindowMem(MemoryManager):
    def __init__(self, system_prompt: str, max_user_messages: int = 4):
        super().__init__(system_prompt)
        self.max_user_messages = max_user_messages

    def _handle_memory(self):
        if self.memory[-1].get("role") != Role.USER:
            return
        idx = 2 * max(0, (len(self.memory) + 1) // 2 - self.max_user_messages)
        if idx != 0:
            print("Info: Memory shortened due to context window.")
            self.memory = self.memory[idx:]


class TokenSlidingWindowMem(MemoryManager):
    def __init__(self, config: Config):
        super().__init__(config.system_prompt)
        self.token_counter = TokenCounter()
        self.current_token = 0
        self.context_length = self._get_context_len(config) - (
            self.token_counter.count_message(self._get_sys_prompt()) + 500
        )

    def _find_context_len(self, model_info):
        for key, value in model_info.items():
            if "context_length" in key:
                return value
        return None

    def _get_context_len(self, config: Config):
        len: int = 4096
        if config.client.api_key == "ollama":
            info = ollama.show(config.model)
            if value := self._find_context_len(info.modelinfo):
                len = value
        elif config.model in MODEL_CONTEXT_WINDOWS.keys():
            len = MODEL_CONTEXT_WINDOWS[config.model]
        else:
            print(
                "(TokenSlidingWindowMem) Error: model not found in config.py/MODEL_CONTEXT_WINDOWS, please add it."
            )
        return len

    def _del_prev_msg(self, last_user_tokens: int):
        kept_tokens = last_user_tokens
        kept_start = len(self.memory) - 1
        for i in range(len(self.memory) - 2, 0, -2):
            user, assistant = self.memory[i - 1], self.memory[i]
            pair_tokens = self.token_counter.count_message(
                user
            ) + self.token_counter.count_message(assistant)
            if kept_tokens + pair_tokens >= self.context_length:
                break
            kept_tokens += pair_tokens
            kept_start = i - 1

        print("Info: Memory shortened due to context window.")
        self.memory = self.memory[kept_start:]
        self.current_token = kept_tokens

    def _handle_memory(self):
        msg = self.memory[-1]
        msg_tokens = self.token_counter.count_message(msg)
        if msg.get("role") != Role.USER:
            self.current_token += msg_tokens
            print(f"Current Tokens: {self.current_token}")
            return
        if msg_tokens >= self.context_length:
            raise ValueError("Context Overflow: Input too big.")    
        self.current_token += msg_tokens
        print(f"Current Tokens: {self.current_token}")
        if self.current_token >= self.context_length:
            self._del_prev_msg(msg_tokens)