"""Escolha do provedor de LLM pelo .env: groq (padrão), openrouter ou anthropic.

Toda chamada de LLM do projeto passa por `chat_model()`. Trocar de provedor = trocar o .env.
A chave nunca aparece no código, em log ou em mensagem de erro.
"""
from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass

PROVIDERS = {
    # provedor: (URL base compatível com OpenAI ou None, variável da chave, modelo padrão)
    "groq": ("https://api.groq.com/openai/v1", "GROQ_API_KEY", "openai/gpt-oss-120b"),
    "openrouter": ("https://openrouter.ai/api/v1", "OPENROUTER_API_KEY", "openai/gpt-oss-120b"),
    "anthropic": (None, "ANTHROPIC_API_KEY", "claude-haiku-5-5"),
}


@dataclass(frozen=True)
class LlmSettings:
    provider: str
    model: str
    base_url: str | None
    api_key_var: str
    temperature: float = 0.0
    max_tokens: int = 400
    timeout_s: float = 30.0


def resolve(env: Mapping[str, str] | None = None) -> LlmSettings:
    env = os.environ if env is None else env
    provider = env.get("LLM_PROVIDER", "groq").strip().lower()
    if provider not in PROVIDERS:
        raise ValueError(f"LLM_PROVIDER deve ser um de {sorted(PROVIDERS)}, recebido {provider!r}")
    base_url, key_var, default_model = PROVIDERS[provider]
    return LlmSettings(
        provider=provider,
        model=env.get("LLM_MODEL", "").strip() or default_model,
        base_url=env.get("LLM_BASE_URL", "").strip() or base_url,
        api_key_var=key_var,
        temperature=float(env.get("LLM_TEMPERATURE", "0")),
        max_tokens=int(env.get("LLM_MAX_TOKENS", "400")),
        timeout_s=float(env.get("LLM_TIMEOUT_S", "30")),
    )


def chat_model(settings: LlmSettings | None = None):  # pragma: no cover - depende de rede e chave
    s = settings or resolve()
    api_key = os.environ.get(s.api_key_var)
    if not api_key:
        raise RuntimeError(f"Defina {s.api_key_var} no .env para usar LLM_PROVIDER={s.provider}")
    if s.provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(model=s.model, api_key=api_key, temperature=s.temperature,
                             max_tokens=s.max_tokens, timeout=s.timeout_s)
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(model=s.model, base_url=s.base_url, api_key=api_key, temperature=s.temperature,
                      max_tokens=s.max_tokens, timeout=s.timeout_s)
