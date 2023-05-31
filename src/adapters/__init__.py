"""Provider-specific LLM adapters with a uniform interface."""
from .openai_adapter import OpenAIAdapter
from .anthropic_adapter import AnthropicAdapter

__all__ = ['OpenAIAdapter', 'AnthropicAdapter']
