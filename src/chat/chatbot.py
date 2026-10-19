from memory.memory_manager import *
from config import AppConfig
import openai

class ChatBot:
    def __init__(self, config: AppConfig, memory: MemoryManager):
        self.memory = memory
        self.config = config
        
    def _stream_reply(self, messages: list[dict]):
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


    def _send_prompt(self, stream: bool = True):
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

    def start_chat(self):
        while True:
            # self.memory.print()
            try:
                prompt = input("You: ").strip()
            except (KeyboardInterrupt, EOFError):
                break
            if prompt.lower() in ["quit", "exit", "bye"]:
                break
            if not prompt:
                continue
            self.memory.add_msg(role=Role.USER, content=prompt)
            print(f"{self.config.model}: ", end="")
            reply = self._send_prompt()
            if not reply:
                self.memory.pop()
                continue
            self.memory.add_msg(role=Role.ASSISTANT, content=reply)
            print()
            