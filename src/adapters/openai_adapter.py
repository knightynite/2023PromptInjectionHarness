"""OpenAI provider adapter."""
import os

import openai


class OpenAIAdapter:
    name = 'openai'

    def __init__(self, model='gpt-3.5-turbo', api_key=None, max_tokens=512):
        self.model = model
        self.max_tokens = max_tokens
        self.client = openai.OpenAI(api_key=api_key or os.environ['OPENAI_API_KEY'])

    def call(self, system: str, user: str) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {'role': 'system', 'content': system},
                {'role': 'user', 'content': user},
            ],
            max_tokens=self.max_tokens,
            temperature=0.0,
        )
        return resp.choices[0].message.content or ''

    def call_with_tools(self, system: str, user: str, tools: list) -> dict:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {'role': 'system', 'content': system},
                {'role': 'user', 'content': user},
            ],
            tools=tools,
            tool_choice='auto',
            max_tokens=self.max_tokens,
            temperature=0.0,
        )
        msg = resp.choices[0].message
        return {
            'text': msg.content or '',
            'tool_calls': [
                {'name': tc.function.name, 'arguments': tc.function.arguments}
                for tc in (msg.tool_calls or [])
            ],
        }
