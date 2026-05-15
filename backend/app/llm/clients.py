import json
from collections.abc import Sequence
from importlib import import_module
from typing import Any, Protocol, TypeVar, cast, overload

from pydantic import BaseModel
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import Settings, get_settings


class ChatMessage(BaseModel):
    role: str
    content: str


ResponseModelT = TypeVar("ResponseModelT", bound=BaseModel)


class LLMClient(Protocol):
    @overload
    async def complete(
        self,
        messages: Sequence[ChatMessage],
        model: str,
        response_model: None = None,
        temperature: float = 0,
    ) -> str: ...

    @overload
    async def complete(
        self,
        messages: Sequence[ChatMessage],
        model: str,
        response_model: type[ResponseModelT],
        temperature: float = 0,
    ) -> ResponseModelT: ...

    async def complete(
        self,
        messages: Sequence[ChatMessage],
        model: str,
        response_model: type[ResponseModelT] | None = None,
        temperature: float = 0,
    ) -> str | ResponseModelT: ...


class AnthropicClient:
    def __init__(self, api_key: str) -> None:
        anthropic = import_module("anthropic")
        self._client = anthropic.AsyncAnthropic(api_key=api_key)

    async def complete(
        self,
        messages: Sequence[ChatMessage],
        model: str,
        response_model: type[ResponseModelT] | None = None,
        temperature: float = 0,
    ) -> str | ResponseModelT:
        prompt_messages = _json_mode_messages(messages, response_model)
        async for attempt in _retrying():
            with attempt:
                response = await self._client.messages.create(
                    model=model,
                    max_tokens=2048,
                    temperature=temperature,
                    messages=[msg.model_dump() for msg in prompt_messages],
                )
        text = _anthropic_text(response)
        return _parse_response(text, response_model)


class OpenAIClient:
    def __init__(self, api_key: str) -> None:
        openai = import_module("openai")
        self._client = openai.AsyncOpenAI(api_key=api_key)

    async def complete(
        self,
        messages: Sequence[ChatMessage],
        model: str,
        response_model: type[ResponseModelT] | None = None,
        temperature: float = 0,
    ) -> str | ResponseModelT:
        kwargs: dict[str, Any] = {}
        if response_model is not None:
            kwargs["response_format"] = {"type": "json_object"}
        prompt_messages = _json_mode_messages(messages, response_model)
        async for attempt in _retrying():
            with attempt:
                response = await self._client.chat.completions.create(
                    model=model,
                    temperature=temperature,
                    messages=[msg.model_dump() for msg in prompt_messages],
                    **kwargs,
                )
        text = str(response.choices[0].message.content or "")
        return _parse_response(text, response_model)


class GeminiClient:
    def __init__(self, api_key: str) -> None:
        google_genai = import_module("google.genai")
        self._types = import_module("google.genai.types")
        self._client = google_genai.Client(api_key=api_key)

    async def complete(
        self,
        messages: Sequence[ChatMessage],
        model: str,
        response_model: type[ResponseModelT] | None = None,
        temperature: float = 0,
    ) -> str | ResponseModelT:
        prompt = "\n\n".join(f"{message.role.upper()}:\n{message.content}" for message in messages)
        config_kwargs: dict[str, Any] = {"temperature": temperature}
        if response_model is not None:
            config_kwargs["response_mime_type"] = "application/json"
            config_kwargs["response_schema"] = response_model
        config = self._types.GenerateContentConfig(**config_kwargs)
        async for attempt in _retrying():
            with attempt:
                response = await self._client.aio.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=config,
                )
        text = str(response.text or "")
        return _parse_response(text, response_model)


def get_llm_client(settings: Settings | None = None) -> LLMClient:
    resolved_settings = settings or get_settings()
    if resolved_settings.llm_provider == "gemini":
        if not resolved_settings.gemini_api_key:
            msg = "GEMINI_API_KEY is required when LLM_PROVIDER=gemini"
            raise ValueError(msg)
        return cast(LLMClient, GeminiClient(api_key=resolved_settings.gemini_api_key))
    if resolved_settings.llm_provider == "openai":
        if not resolved_settings.openai_api_key:
            msg = "OPENAI_API_KEY is required when LLM_PROVIDER=openai"
            raise ValueError(msg)
        return cast(LLMClient, OpenAIClient(api_key=resolved_settings.openai_api_key))
    if not resolved_settings.anthropic_api_key:
        msg = "ANTHROPIC_API_KEY is required when LLM_PROVIDER=anthropic"
        raise ValueError(msg)
    return cast(LLMClient, AnthropicClient(api_key=resolved_settings.anthropic_api_key))


def _retrying() -> AsyncRetrying:
    return AsyncRetrying(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
        retry=retry_if_exception_type((TimeoutError, ConnectionError)),
        reraise=True,
    )


def _json_mode_messages(
    messages: Sequence[ChatMessage],
    response_model: type[ResponseModelT] | None,
) -> list[ChatMessage]:
    if response_model is None:
        return list(messages)
    schema = json.dumps(response_model.model_json_schema(), indent=2)
    return [
        *messages,
        ChatMessage(
            role="user",
            content=f"Return valid JSON only. JSON schema:\n{schema}",
        ),
    ]


def _parse_response(
    text: str,
    response_model: type[ResponseModelT] | None,
) -> str | ResponseModelT:
    if response_model is None:
        return text
    return response_model.model_validate_json(text)


def _anthropic_text(response: Any) -> str:
    parts: list[str] = []
    for block in response.content:
        text = getattr(block, "text", None)
        if text:
            parts.append(str(text))
    return "\n".join(parts)
