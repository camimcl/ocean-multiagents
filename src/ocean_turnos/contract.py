"""Contrato do JSON de decisão (POST /api/v1/turn/submit). Código puro, sem rede.

Formato (starter/exemplo_decisao_turno.json no repositório Ocean-1):
{
  "advance_ticks": 25, "stop_on_events": true,
  "decisions": [{"ship_id", "proposed_by", "proposal_rationale",
                 "reviewed_by", "review_result", "review_rationale", "action"}]
}
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

SHIPS = ("S1-FAROL", "S2-MARE", "S3-CORAL", "S4-ATLAS")
ROLES = ("navigation", "safety", "economy", "coordinator")
TOTAL_TICKS = 432

SPEED_RE = re.compile(r"^(0|[1-9]|1[0-8])\.(0|5)0$")
CODE_RE = re.compile(r"^[A-Z][A-Z0-9_]{2,63}$")
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{2,127}$")

ACTION_ARGS = {
    "SET_ROUTE": "route_id",
    "SET_SPEED": "speed_kn",
    "HOLD": "reason_code",
    "BUY_FUEL": "quantity_t",
    "CANCEL_FUEL": "order_id",
    "REPAIR": "fault_id",
    "SAFE_STOP": "reason_code",
}


# ---------- construtores de ação (use sempre estes, nunca dict escrito à mão) ----------
def set_speed(speed_centi: int) -> dict[str, Any]:
    """Velocidade em centésimos de nó (1250 = 12.50 kn), arredondada para baixo no passo 0.50."""
    speed_centi = max(0, min(1800, speed_centi - speed_centi % 50))
    return {"type": "SET_SPEED", "speed_kn": f"{speed_centi // 100}.{speed_centi % 100:02d}"}


def set_route(route_id: str) -> dict[str, Any]:
    return {"type": "SET_ROUTE", "route_id": route_id}


def buy_fuel(quantity_t: int) -> dict[str, Any]:
    return {"type": "BUY_FUEL", "quantity_t": quantity_t}


def hold(reason_code: str) -> dict[str, Any]:
    return {"type": "HOLD", "reason_code": reason_code}


def repair(fault_id: str) -> dict[str, Any]:
    return {"type": "REPAIR", "fault_id": fault_id}


def speed_centi(value: str) -> int:
    whole, frac = str(value).split(".")
    return int(whole) * 100 + int(frac)


# ---------- tipos trocados entre agentes ----------
@dataclass
class Proposal:
    ship_id: str
    proposed_by: str  # papel do agente que propõe
    action: dict[str, Any]
    rationale: str
    priority: int = 50  # menor = mais urgente (o coordenador ordena por isso)
    tags: list[str] = field(default_factory=list)


@dataclass
class Review:
    reviewed_by: str
    approved: bool
    rationale: str
    codes: list[str] = field(default_factory=list)


def to_decision(proposal: Proposal, review: Review) -> dict[str, Any]:
    return {
        "ship_id": proposal.ship_id,
        "proposed_by": proposal.proposed_by,
        "proposal_rationale": proposal.rationale,
        "reviewed_by": review.reviewed_by,
        "review_result": "approved" if review.approved else "rejected",
        "review_rationale": review.rationale,
        "action": proposal.action,
    }


# ---------- validação antes do envio ----------
def validate_action(action: Any) -> list[str]:
    if not isinstance(action, dict):
        return ["ACTION_NOT_OBJECT"]
    kind = action.get("type")
    if kind not in ACTION_ARGS:
        return [f"UNKNOWN_ACTION:{kind}"]
    arg = ACTION_ARGS[kind]
    if set(action) != {"type", arg}:
        return [f"INVALID_ARGUMENTS:{kind}"]
    value = action[arg]
    if kind == "SET_SPEED" and not (isinstance(value, str) and SPEED_RE.match(value) and speed_centi(value) <= 1800):
        return ["INVALID_SPEED"]
    if kind == "SET_ROUTE" and value not in ("direct", "protected"):
        return ["INVALID_ROUTE"]
    if kind == "BUY_FUEL" and (isinstance(value, bool) or not isinstance(value, int) or value < 5 or value % 5):
        return ["INVALID_FUEL_QUANTITY"]
    if kind in ("HOLD", "SAFE_STOP") and not (isinstance(value, str) and CODE_RE.match(value)):
        return ["INVALID_REASON_CODE"]
    if kind in ("REPAIR", "CANCEL_FUEL") and not (isinstance(value, str) and ID_RE.match(value)):
        return ["INVALID_ID"]
    return []


def validate_decision_doc(doc: Any) -> list[str]:
    """Lista vazia = documento pronto para enviar."""
    if not isinstance(doc, dict):
        return ["DOC_NOT_OBJECT"]
    problems: list[str] = []
    adv = doc.get("advance_ticks")
    if isinstance(adv, bool) or not isinstance(adv, int) or not 1 <= adv <= TOTAL_TICKS:
        problems.append("INVALID_ADVANCE_TICKS")
    if not isinstance(doc.get("stop_on_events"), bool):
        problems.append("INVALID_STOP_ON_EVENTS")
    decisions = doc.get("decisions")
    if not isinstance(decisions, list):
        return problems + ["DECISIONS_NOT_LIST"]
    for i, d in enumerate(decisions):
        prefix = f"decisions[{i}]"
        if not isinstance(d, dict):
            problems.append(f"{prefix}:NOT_OBJECT")
            continue
        if d.get("ship_id") not in SHIPS:
            problems.append(f"{prefix}:INVALID_SHIP")
        if not d.get("proposed_by") or not d.get("reviewed_by"):
            problems.append(f"{prefix}:MISSING_AGENT")
        elif d["proposed_by"] == d["reviewed_by"]:
            problems.append(f"{prefix}:SAME_PROPOSER_AND_REVIEWER")
        if d.get("review_result") not in ("approved", "rejected"):
            problems.append(f"{prefix}:INVALID_REVIEW_RESULT")
        for key in ("proposal_rationale", "review_rationale"):
            if not isinstance(d.get(key), str) or not d[key].strip():
                problems.append(f"{prefix}:EMPTY_{key.upper()}")
        problems += [f"{prefix}:{p}" for p in validate_action(d.get("action"))]
    return problems
