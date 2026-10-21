from config import AppConfig, load_config
from custom_types.enums import Role
from interface.chat import Chat
from memory.memory_manager import SlidingWindowMem


class Cli:
    def __init__(self):
        self.current_chat: Chat = None
        self.chats: list[Chat] = []
        self.default_config: AppConfig = load_config()
        self.commands = {
            "/resume": self._resume,
            "/clear": self._clear,
            "/bye": self._bye,
            "/quit": self._bye,
            "/exit": self._bye,
        }

    def _clear_screen_ansi(self):
        print("\x1b[2J\x1b[H")

    def _unknown_command(self):
        print("Error: Unknown command.")

    def _bye(self):
        print("bye.")
        exit(0)

    def _resume(self):
        self._clear_screen_ansi()
        print("Chose a chat:\n")
        for i, chat in enumerate(self.chats):
            print(f"\t{i}: {chat.getId()}\n")
        while True:
            try:
                user_input = input("Chosen index: ")
            except (KeyboardInterrupt, EOFError):
                break
            if not user_input:
                break
            val = 0
            try:
                if not (0 <= (val := int(user_input)) < len(self.chats)):
                    print("Error: not a valid index.\n")
                    continue
            except ValueError:
                print("Error: not a valid input.\n")
                continue
            self.current_chat = self.chats[val]
            break
        self._clear_screen_ansi()
        self.current_chat.print_chat()

    def _new_chat(self):
        self.current_chat = Chat(
            self.default_config,
            SlidingWindowMem(self.default_config.system_prompt, 10),
        )
        self.chats.append(self.current_chat)

    def _clear(self):
        self._clear_screen_ansi()
        self._new_chat()

    def _handle_command(self, command: str):
        action = self.commands.get(command, self._unknown_command)
        action()

    def start(self):
        while True:
            if not self.current_chat:
                self._new_chat()
            # self.memory.print()
            try:
                prompt = input("You: ").strip()
            except (KeyboardInterrupt, EOFError):
                break
            if not prompt:
                continue
            if prompt.startswith("/"):
                self._handle_command(prompt.lower())
                continue
            print(f"{self.current_chat.config.model}: ", end="")
            reply = self.current_chat.send_prompt(prompt)
            if not reply:
                self.current_chat.memory.pop()
                continue
            self.current_chat.memory.add_msg(role=Role.ASSISTANT, content=reply)
            print()
