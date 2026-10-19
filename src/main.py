import openai

from config import AppConfig, load_config
from custom_types.enums import Role
from memory.memory_manager import MemoryManager, SlidingWindowMem
from chat.chatbot import ChatBot


def main():
    cfg = load_config()
    memory = SlidingWindowMem(cfg.system_prompt, 5)
    chatbot = ChatBot(cfg, memory)
    chatbot.start_chat()


if __name__ == "__main__":
    main()
