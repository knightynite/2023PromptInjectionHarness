"""Anthropic provider adapter."""
import os

import anthropic


class AnthropicAdapter:
    name = 'anthropic'

    def __init__(self, model='claude-2', api_key=None, max_tokens=512):
        self.model = model
        self.max_tokens = max_tokens
        self.client = anthropic.Anthropic(
            api_key=api_key or os.environ['ANTHROPIC_API_KEY']
        )

    def call(self, system: str, user: str) -> str:
        resp = self.client.messages.create(
            model=self.model,
            system=system,
            messages=[{'role': 'user', 'content': user}],
            max_tokens=self.max_tokens,
            temperature=0.0,
        )
        # Concatenate text content blocks
        out = []
        for block in resp.content:
            if hasattr(block, 'text'):
                out.append(block.text)
        return ''.join(out)

    def call_with_tools(self, system: str, user: str, tools: list) -> dict:
        resp = self.client.messages.create(
            model=self.model,
            system=system,
            messages=[{'role': 'user', 'content': user}],
            tools=tools,
            max_tokens=self.max_tokens,
            temperature=0.0,
        )
        text = []
        tool_calls = []
        for block in resp.content:
            if block.type == 'text':
                text.append(block.text)
            elif block.type == 'tool_use':
                tool_calls.append({'name': block.name, 'arguments': block.input})
        return {'text': ''.join(text), 'tool_calls': tool_calls}
