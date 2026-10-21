import openai

from config import AppConfig
from custom_types.enums import Memory, Role
from memory.memory_manager import MemoryManager


class Chat:
    def __init__(self, config: AppConfig, memory: MemoryManager):
        self.memory = memory
        self.config = config
        self.id = ""

    def getId(self):
        return self.id

    def _stream_reply(self, messages: Memory):
        with self.config.complete(messages, stream=True) as stream:
            finish_reason = None
            yielded = False
            for chunk in stream:
                if not chunk.choices:
                    continue
                choice = chunk.choices[0]
                if choice.finish_reason:
                    finish_reason = choice.finish_reason
                if not choice.delta.content:
                    continue
                yielded = True
                yield choice.delta.content
            if not yielded:
                raise ValueError(f"Empty answer (finish_reason: {finish_reason})")
            if finish_reason == "length":
                print(" [truncated]", end="")

    def send_prompt(self, prompt: str, stream: bool = True) -> str:
        if self.memory.add_msg(role=Role.USER, content=prompt):
            self.id = prompt
        messages = self.memory.get_msgs()
        reply = ""
        try:
            if stream:
                try:
                    for content in self._stream_reply(messages):
                        print(content, end="", flush=True)
                        reply += content
                    print()
                except KeyboardInterrupt:
                    print(" [interrupted]")
                    if reply:
                        reply += "\n\n[INTERRUPTED BY USER]"
            else:
                try:
                    content = self.config.complete(messages)
                    reply = content.choices[0].message.content or ""
                    print(reply)
                except KeyboardInterrupt:
                    print("[interrupted]")
        except (openai.APIError, ValueError) as e:
            print(f"\nError: {e}")
        return reply

    def print_chat(self):
        for msg in self.memory.get_msgs():
            role, content = msg.values()
            # print(f"MSG: {msg}\nROLE: {role}\nCONTENT: {content}")
            if role is Role.ASSISTANT:
                print(f"{self.config.model}: {content}\n")
            elif role is Role.USER:
                print(f"You: {content}")
