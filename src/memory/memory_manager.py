from abc import ABC, abstractmethod
from custom_types.enums import Role


class MemoryManager(ABC):
    def __init__(self, system_prompt: str):
        self.system_prompt = {"role": Role.SYSTEM, "content": system_prompt}
        self.memory = []

    def add_msg(self, role: Role, content: str):
        self.memory.append({"role": role, "content": content})
        self._handle_memory()

    def get_msgs(self):
        return [self.system_prompt] + self.memory
    
    def print(self):
        for e in self.memory:
            print(e)

    def pop(self):
        self.memory.pop()

    @abstractmethod
    def _handle_memory(self) -> list:
        pass


class SlidingWindowMem(MemoryManager):
    def __init__(self, system_prompt: str, max_user_messages: int = 4):
        super().__init__(system_prompt)
        self.max_user_messages = max_user_messages

    def _get_active_window(self):
        idx = 2 * max(0, (len(self.memory) + 1) // 2 - self.max_user_messages)
        return self.memory[idx:]
    
    def _handle_memory(self):
        if len(self.memory) % 2 == 0:
            self.memory = self._get_active_window()

    def get_msgs(self):
        print("[SENT]:")
        for e in self._get_active_window():
            print(e)
        return [self.system_prompt] + self._get_active_window()
