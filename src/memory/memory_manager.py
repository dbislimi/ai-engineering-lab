from abc import ABC, abstractmethod
from custom_types.enums import Role, Memory


class MemoryManager(ABC):
    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt
        self.memory: Memory = []

    def add_msg(self, role: Role, content: str) -> bool:
        self.memory.append({"role": role, "content": content})
        self._handle_memory()
        return True if len(self.memory) == 1 else False
    
    def _get_sys_prompt(self) -> Memory:
        if not self.system_prompt:
            return []
        return [{"role": Role.SYSTEM, "content": self.system_prompt}]

    def get_msgs(self) -> Memory:
        return self._get_sys_prompt() + self.memory

    def print(self):
        if self.system_prompt:
            print({"role": Role.SYSTEM, "content": self.system_prompt})
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

    def _get_active_window(self) -> Memory:
        idx = 2 * max(0, (len(self.memory) + 1) // 2 - self.max_user_messages)
        return self.memory[idx:]

    def _handle_memory(self):
        if len(self.memory) % 2 == 0:
            self.memory = self._get_active_window()

    def get_msgs(self) -> Memory:
        window = self._get_active_window()
        # print("[SENT]:")
        # for e in window:
        #     print(e)
        return self._get_sys_prompt() + window
