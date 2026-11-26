"""LLM opcional: reescreve as justificativas em linguagem clara. NUNCA muda a decisão.

Ligado com LLM_ENABLED=true no .env. Sem chave, sem biblioteca ou com erro, devolve o texto
original (fallback). Assim a rodada nunca depende do LLM para funcionar.
Responsável: Camile.
"""
from __future__ import annotations

import os
from typing import Any

PROMPT = (
    "Você é o agente {role} de uma frota de navios. Reescreva a justificativa abaixo em uma frase "
    "objetiva em português, citando os números que ela já contém. Não invente dados nem mude a decisão.\n"
    "Ação: {action}\nJustificativa técnica: {text}"
)


def _llm():  # pragma: no cover - depende de rede e chave
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=os.getenv("LLM_MODEL", "openrouter/free"),
        base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        api_key=os.environ["OPENROUTER_API_KEY"],
        temperature=0,
        max_tokens=120,
        timeout=30,
    )


def rewrite(decisions: list[dict[str, Any]], enabled: bool) -> list[dict[str, Any]]:
    if not enabled or not decisions:
        return decisions
    try:  # pragma: no cover
        model = _llm()
        out = []
        for d in decisions:
            new = dict(d)
            for role_key, text_key in (("proposed_by", "proposal_rationale"), ("reviewed_by", "review_rationale")):
                reply = model.invoke(PROMPT.format(role=d[role_key], action=d["action"], text=d[text_key]))
                text = str(getattr(reply, "content", "")).strip()
                if text:
                    new[text_key] = text[:500]
            out.append(new)
        return out
    except Exception:  # noqa: BLE001 - qualquer falha do LLM cai no texto determinístico
        return decisions
