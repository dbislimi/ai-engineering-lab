import openai

from config import Config
from custom_types.enums import Memory, Role
from memory.memory_manager import MemoryManager


class Chat:
    def __init__(self, config: Config, memory: MemoryManager):
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

    def _get_reply(self, messages: Memory, stream: bool) -> str:
        reply = ""
        try:
            if stream:
                for content in self._stream_reply(messages):
                    print(content, end="", flush=True)
                    reply += content
                print()
            else:
                content = self.config.complete(messages)
                reply = content.choices[0].message.content or ""
                print(reply)
        except KeyboardInterrupt:
            print(" [interrupted]")
            if reply:
                reply += "\n\n[INTERRUPTED BY USER]"
        except (openai.APIError, ValueError) as e:
            print(f"\nError: {e}")
        return reply

    def send_prompt(self, prompt: str, stream: bool = True):
        reply = ""
        if self.memory.add_msg(role=Role.USER, content=prompt):
            self.id = prompt
            print(f"{self.config.model}: ", end="")
            reply = self._get_reply(self.memory.get_memory(), stream)
        if not reply:
            self.memory.pop()
            return
        self.memory.add_msg(role=Role.ASSISTANT, content=reply)
        self.memory.add_to_history(prompt, reply)

    def print_history(self):
        for msg in self.memory.get_history():
            role, content = msg.values()
            if role is Role.ASSISTANT:
                print(f"{self.config.model}: {content}\n")
            elif role is Role.USER:
                print(f"You: {content}")
