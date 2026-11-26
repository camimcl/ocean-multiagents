"""Deliberação de um turno: pacote -> decisão. Responsável: Camile.

`deliberate(pack)` é a função que todo o resto usa (scripts, testes, avaliação).
`build_graph()` monta o mesmo fluxo em LangGraph, para quem quiser visualizar/estender:

    ler_turno -> coordenar (economia + navegação propõem, segurança revisa) -> justificar (LLM opcional) -> END
"""
from __future__ import annotations

from typing import Any, TypedDict

from .agents import coordinator
from .contract import validate_decision_doc
from .llm import justificativas
from .pack import TurnView, parse_pack


def deliberate(pack: dict[str, Any], advance_ticks_max: int = 50, llm_enabled: bool = False) -> dict[str, Any]:
    view = parse_pack(pack)
    doc, _ = coordinator.decide(view, advance_ticks_max=advance_ticks_max)
    doc["decisions"] = justificativas.rewrite(doc["decisions"], enabled=llm_enabled)
    problems = validate_decision_doc(doc)
    if problems:
        raise ValueError(f"Coordenador gerou decisão inválida: {problems}")
    return doc


class TurnState(TypedDict, total=False):
    pack: dict[str, Any]
    view: TurnView
    decision: dict[str, Any]
    advance_ticks_max: int
    llm_enabled: bool


def build_graph():  # pragma: no cover - requer langgraph instalado
    from langgraph.graph import END, START, StateGraph

    def ler_turno(state: TurnState) -> TurnState:
        return {"view": parse_pack(state["pack"])}

    def coordenar(state: TurnState) -> TurnState:
        doc, _ = coordinator.decide(state["view"], advance_ticks_max=state.get("advance_ticks_max", 50))
        return {"decision": doc}

    def justificar(state: TurnState) -> TurnState:
        doc = dict(state["decision"])
        doc["decisions"] = justificativas.rewrite(doc["decisions"], enabled=state.get("llm_enabled", False))
        return {"decision": doc}

    g = StateGraph(TurnState)
    g.add_node("ler_turno", ler_turno)
    g.add_node("coordenar", coordenar)
    g.add_node("justificar", justificar)
    g.add_edge(START, "ler_turno")
    g.add_edge("ler_turno", "coordenar")
    g.add_edge("coordenar", "justificar")
    g.add_edge("justificar", END)
    return g.compile()
