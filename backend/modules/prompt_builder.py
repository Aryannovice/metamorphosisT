from typing import List, Tuple

import tiktoken

SYSTEM_PROMPT = (
    "You are an AI assistant. Be helpful, accurate, and concise. "
    "Respect user privacy — never ask for personal information."
)


class PromptBuilder:
    def __init__(self, model: str = "gpt-3.5-turbo"):
        try:
            self._encoder = tiktoken.encoding_for_model(model)
        except KeyError:
            self._encoder = tiktoken.get_encoding("cl100k_base")

    def build(
        self,
        masked_prompt: str,
        context: List[str] | None = None,
    ) -> Tuple[List[dict], int]:
        messages: List[dict] = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]

        if context:
            context_block = "\n---\n".join(context)
            messages.append(
                {"role": "system", "content": f"Relevant context:\n{context_block}"}
            )

        messages.append({"role": "user", "content": masked_prompt})

        token_count = self._count_messages(messages)
        return messages, token_count

    def count_tokens(self, text: str) -> int:
        return len(self._encoder.encode(text))

    def _count_messages(self, messages: List[dict]) -> int:
        total = 0
        for msg in messages:
            total += 4  # role + content overhead per message
            total += len(self._encoder.encode(msg["content"]))
        total += 2  # reply priming
        return total
