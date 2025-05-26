"""AI enrichment utilities and context management."""

import logging
import os
import sys
from typing import Any, Dict, Optional

import tiktoken
from anthropic import Anthropic
from openai import OpenAI
from rich.logging import RichHandler

# Configure logging on import
logging.basicConfig(level=logging.INFO, format="%(message)s", handlers=[RichHandler(markup=True)])
logger = logging.getLogger("autodoc_ai")


def load_file(file_path: str) -> Optional[str]:
    """Load file content."""
    try:
        with open(file_path, encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return None


def _get_anthropic_response(prompt: str, model_name: str, api_key: str, temperature: float) -> Any:
    """Get response from Anthropic API."""
    client = Anthropic(api_key=api_key)
    try:
        response = client.messages.create(model=model_name, messages=[{"role": "user", "content": prompt}], temperature=temperature, max_tokens=4096)

        # Wrap Anthropic response to match OpenAI format
        class AnthropicWrapper:
            def __init__(self, content):
                self.choices = [type("obj", (object,), {"message": type("obj", (object,), {"content": content})()})]

        return AnthropicWrapper(response.content[0].text)
    except Exception as e:
        logger.error(f"❌ Error from API: {e}")
        sys.exit(1)


def _get_openai_response(prompt: str, model_name: str, api_key: str, temperature: float, json_response: bool) -> Any:
    """Get response from OpenAI API."""
    client = OpenAI(api_key=api_key)
    try:
        kwargs = {"model": model_name, "messages": [{"role": "user", "content": prompt}], "temperature": temperature}
        if json_response:
            kwargs["response_format"] = {"type": "json_object"}
        return client.chat.completions.create(**kwargs)
    except Exception as e:
        logger.error(f"❌ Error from API: {e}")
        sys.exit(1)


def get_ai_response(prompt: str, ctx: Optional[Dict[str, Any]] = None, json_response: bool = False, temperature: float = 0.5) -> Any:
    """Get response from AI API (OpenAI or Anthropic)."""
    from .settings import Settings

    model_name = ctx.get("model", Settings.get_model()) if ctx else Settings.get_model()
    is_claude = model_name.startswith("claude")

    # Get API key based on model type
    env_key = "ANTHROPIC_API_KEY" if is_claude else "OPENAI_API_KEY"
    api_key = ctx.get("api_key") if ctx else os.getenv(env_key)

    if not api_key:
        logger.error("🔑 No API key found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY.")
        sys.exit(1)

    # Call appropriate API
    if is_claude:
        return _get_anthropic_response(prompt, model_name, api_key, temperature)
    return _get_openai_response(prompt, model_name, api_key, temperature, json_response)


def extract_ai_content(response: Any) -> str:
    """Extract content from OpenAI API response."""
    if (
        hasattr(response, "choices")
        and response.choices
        and hasattr(response.choices[0], "message")
        and hasattr(response.choices[0].message, "content")
        and response.choices[0].message.content
    ):
        return response.choices[0].message.content.strip()
    return ""


def count_tokens(text: str, model_name: str) -> int:
    """Count tokens in text for specific model."""
    # Use cl100k_base for Claude models
    if model_name.startswith("claude"):
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))

    # Try to get encoding for specific model
    try:
        enc = tiktoken.encoding_for_model(model_name)
    except KeyError:
        enc = tiktoken.get_encoding("cl100k_base")

    return len(enc.encode(text))
