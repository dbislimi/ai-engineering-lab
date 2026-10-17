import openai

from config import AppConfig, load_config
from custom_types.enums import Role
from memory.memory_manager import MemoryManager, SlidingWindowMem


def stream_reply(cfg: AppConfig, messages: list[dict]):
    with cfg.complete(messages, stream=True) as stream:
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


def ask_llm(cfg: AppConfig, messages: list[dict], stream: bool = False):
    if stream:
        reply = ""
        for content in stream_reply(cfg, messages):
            print(content, end="", flush=True)
            reply += content
        print()
        return reply
    reply = cfg.complete(messages)
    content = reply.choices[0].message.content or ""
    print(content)
    return content


def start_llm(cfg: AppConfig, memory: MemoryManager):
    while True:
        memory.print()
        try:
            prompt = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            break
        if prompt.lower() in ["quit", "exit", "bye"]:
            break
        if not prompt:
            continue
        memory.add_msg(role=Role.USER, content=prompt)
        print("Chatbot: ", end="")
        reply = ""
        try:
            messages = memory.get_msgs()
            reply = ask_llm(cfg, messages, stream=True)
        except KeyboardInterrupt:
            print(" [Canceled]")
            if not reply:
                memory.pop()
                continue
        except (openai.APIError, ValueError) as e:
            print(f"\nError: {e}")
            memory.pop()
            continue
        memory.add_msg(role=Role.ASSISTANT, content=reply)
        print()


def main():
    cfg = load_config()
    memory = SlidingWindowMem(cfg.system_prompt, 2)
    start_llm(cfg, memory)


if __name__ == "__main__":
    main()
