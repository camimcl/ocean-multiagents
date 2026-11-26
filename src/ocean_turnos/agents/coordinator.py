"""Coordenador: junta as propostas, manda revisar, resolve conflitos e monta a decisão.
Responsável: Camile.

Regras:
- no máximo 2 decisões por navio por turno (a 2ª o servidor aplica em T+1);
- quem propõe nunca revisa a própria proposta;
- vetos também vão no JSON (contam como governança e ficam no ledger);
- o caixa é descontado localmente a cada compra aprovada, para não gastar duas vezes.
"""
from __future__ import annotations

from typing import Any

from ..contract import Proposal, Review, to_decision
from ..pack import TurnView
from . import economy, navigation, safety

ROLE = "coordinator"
MAX_DECISIONS_PER_SHIP = 2


def pick_reviewer(proposed_by: str) -> str:
    return safety.ROLE if proposed_by != safety.ROLE else ROLE


def gather_proposals(view: TurnView) -> list[Proposal]:
    proposals = economy.propose(view) + navigation.propose(view)
    return sorted(proposals, key=lambda p: (p.priority, p.ship_id))


def decide(view: TurnView, advance_ticks_max: int = 50) -> tuple[dict[str, Any], list[tuple[Proposal, Review]]]:
    available = view.available_cent
    per_ship: dict[str, int] = {}
    reviewed: list[tuple[Proposal, Review]] = []

    for proposal in gather_proposals(view):
        if per_ship.get(proposal.ship_id, 0) >= MAX_DECISIONS_PER_SHIP:
            continue
        # navio que vai abastecer neste turno não recebe velocidade junto (ficaria em serviço)
        if "speed" in proposal.tags and any(
            p.ship_id == proposal.ship_id and "fuel" in p.tags and r.approved for p, r in reviewed
        ):
            continue
        review = safety.review(proposal, view, reviewer=pick_reviewer(proposal.proposed_by))
        if review.approved and proposal.action["type"] == "BUY_FUEL":
            price = int(view.ships[proposal.ship_id].allowed["BUY_FUEL"].get("unit_price_cent_per_t") or 0)
            cost = proposal.action["quantity_t"] * price
            if cost > available:
                review = Review(review.reviewed_by, False, "VETO CASH_LIMIT: caixa livre insuficiente neste turno.",
                                ["CASH_LIMIT"])
            else:
                available -= cost
        reviewed.append((proposal, review))
        per_ship[proposal.ship_id] = per_ship.get(proposal.ship_id, 0) + 1

    remaining = max(1, 432 - view.tick)
    doc = {
        "advance_ticks": min(advance_ticks_max, remaining),
        "stop_on_events": True,
        "decisions": [to_decision(p, r) for p, r in reviewed],
    }
    return doc, reviewed
