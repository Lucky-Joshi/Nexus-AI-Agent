"""
LLM Provider abstraction for NEXUS.
Supports Ollama (local) and OpenAI (cloud) with a unified interface.
"""

import json
import requests
from typing import Any, Dict, List, Optional, Generator
from core.config import Config
from core.logger import Logger


class LLMProvider:
    """Unified LLM interface supporting Ollama and OpenAI."""

    def __init__(self, config: Optional[Config] = None):
        self.logger = Logger().get_logger("LLMProvider")
        self.config = config or Config()
        self._provider = self.config.get("llm.provider", "ollama")
        self._client = None
        self._init_client()

    def _init_client(self):
        if self._provider == "openai":
            try:
                from openai import OpenAI
                api_key = self.config.get("llm.openai.api_key", "")
                if not api_key:
                    self.logger.warning("OpenAI API key not set, falling back to Ollama")
                    self._provider = "ollama"
                else:
                    self._client = OpenAI(api_key=api_key)
                    self.logger.info("OpenAI client initialized")
            except ImportError:
                self.logger.warning("openai package not installed, falling back to Ollama")
                self._provider = "ollama"
        else:
            self.logger.info(f"Using Ollama provider at {self.config.get('llm.ollama.base_url', 'http://localhost:11434')}")

    def chat(self, messages: List[Dict[str, str]], model: Optional[str] = None, temperature: Optional[float] = None) -> str:
        """
        Send a chat conversation and get a response.
        messages: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
        """
        if self._provider == "openai":
            return self._chat_openai(messages, model, temperature)
        return self._chat_ollama(messages, model, temperature)

    def generate(self, prompt: str, system_prompt: Optional[str] = None, model: Optional[str] = None, temperature: Optional[float] = None) -> str:
        """
        Generate a response for a single prompt.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return self.chat(messages, model, temperature)

    def stream(self, messages: List[Dict[str, str]], model: Optional[str] = None, temperature: Optional[float] = None) -> Generator[str, None, None]:
        """
        Stream response tokens one at a time.
        """
        if self._provider == "openai":
            yield from self._stream_openai(messages, model, temperature)
        else:
            yield from self._stream_ollama(messages, model, temperature)

    def is_available(self) -> bool:
        """Check if the LLM provider is reachable."""
        if self._provider == "openai":
            return self._client is not None
        try:
            base_url = self.config.get("llm.ollama.base_url", "http://localhost:11434")
            resp = requests.get(f"{base_url}/api/tags", timeout=3)
            return resp.status_code == 200
        except Exception:
            return False

    def get_model(self) -> str:
        if self._provider == "openai":
            return self.config.get("llm.openai.model", "gpt-4")
        return self.config.get("llm.ollama.model", "llama3.2")

    def get_provider_name(self) -> str:
        return self._provider

    def _chat_ollama(self, messages: List[Dict[str, str]], model: Optional[str] = None, temperature: Optional[float] = None) -> str:
        base_url = self.config.get("llm.ollama.base_url", "http://localhost:11434")
        model_name = model or self.config.get("llm.ollama.model", "llama3.2")
        temp = temperature if temperature is not None else self.config.get("llm.ollama.temperature", 0.7)

        payload = {
            "model": model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temp,
            }
        }

        try:
            resp = requests.post(f"{base_url}/api/chat", json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            return data.get("message", {}).get("content", "No response from Ollama")
        except requests.exceptions.ConnectionError:
            self.logger.error(f"Cannot connect to Ollama at {base_url}. Is Ollama running?")
            return f"[LLM Offline] Cannot connect to Ollama at {base_url}. Start Ollama with: ollama serve"
        except requests.exceptions.Timeout:
            self.logger.error("Ollama request timed out")
            return "[LLM Timeout] Request timed out. Try a shorter prompt or check Ollama."
        except Exception as e:
            self.logger.error(f"Ollama error: {e}")
            return f"[LLM Error] {str(e)}"

    def _stream_ollama(self, messages: List[Dict[str, str]], model: Optional[str] = None, temperature: Optional[float] = None) -> Generator[str, None, None]:
        base_url = self.config.get("llm.ollama.base_url", "http://localhost:11434")
        model_name = model or self.config.get("llm.ollama.model", "llama3.2")
        temp = temperature if temperature is not None else self.config.get("llm.ollama.temperature", 0.7)

        payload = {
            "model": model_name,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temp,
            }
        }

        try:
            resp = requests.post(f"{base_url}/api/chat", json=payload, stream=True, timeout=120)
            resp.raise_for_status()
            for line in resp.iter_lines():
                if line:
                    data = json.loads(line)
                    token = data.get("message", {}).get("content", "")
                    if token:
                        yield token
                    if data.get("done", False):
                        break
        except Exception as e:
            self.logger.error(f"Ollama stream error: {e}")
            yield f"\n[Stream Error] {str(e)}"

    def _chat_openai(self, messages: List[Dict[str, str]], model: Optional[str] = None, temperature: Optional[float] = None) -> str:
        if not self._client:
            return "[OpenAI] Client not initialized. Check API key."

        model_name = model or self.config.get("llm.openai.model", "gpt-4")
        temp = temperature if temperature is not None else self.config.get("llm.openai.temperature", 0.7)

        try:
            response = self._client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=temp,
            )
            return response.choices[0].message.content or "No response"
        except Exception as e:
            self.logger.error(f"OpenAI error: {e}")
            return f"[OpenAI Error] {str(e)}"

    def _stream_openai(self, messages: List[Dict[str, str]], model: Optional[str] = None, temperature: Optional[float] = None) -> Generator[str, None, None]:
        if not self._client:
            yield "[OpenAI] Client not initialized."
            return

        model_name = model or self.config.get("llm.openai.model", "gpt-4")
        temp = temperature if temperature is not None else self.config.get("llm.openai.temperature", 0.7)

        try:
            stream = self._client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=temp,
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield delta.content
        except Exception as e:
            self.logger.error(f"OpenAI stream error: {e}")
            yield f"\n[Stream Error] {str(e)}"
