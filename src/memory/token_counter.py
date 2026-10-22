import tiktoken


class TokenCounter:
    def __init__(self, encoding_name: str = "cl100k_base"):
        self.encoding = tiktoken.get_encoding(encoding_name)
        self.token_per_message = 3

    def _count_text(self, text: str):
        return len(self.encoding.encode(text))

    def count_message(self, message: dict[str,str]):
        num_tokens = self.token_per_message
        for _, value in message.items():
            num_tokens += self._count_text(value)
        return num_tokens
