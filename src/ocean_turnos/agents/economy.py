"""Agente de economia: decide QUANTO combustível comprar e QUANDO. Responsável: Lídia.

Versão inicial (linha de base): compra na origem o suficiente para a viagem a velocidade
de cruzeiro, com margem, enquanto o fornecedor da origem está aberto (até o tick 95).
"""
from __future__ import annotations

from ..contract import Proposal, buy_fuel
from ..pack import ShipView, TurnView
from ..tools import fuel

ROLE = "economy"
CRUISE_KN = 14.0


def propose(view: TurnView) -> list[Proposal]:
    proposals: list[Proposal] = []
    for ship in view.ships.values():
        proposal = _propose_for_ship(view, ship)
        if proposal is not None:
            proposals.append(proposal)
    return proposals


def _propose_for_ship(view: TurnView, ship: ShipView) -> Proposal | None:
    if not ship.can("BUY_FUEL") or not ship.stopped or ship.pending_fuel_milli > 0:
        return None
    constraints = ship.allowed["BUY_FUEL"]
    need_t = fuel.fuel_needed_t(
        ship.remaining_nm_milli / 1000, CRUISE_KN, ship.c14_t_per_h, ship.hotel_t_per_h
    )
    qty = fuel.purchase_to_cover(
        need_t=need_t,
        fuel_t=ship.fuel_milli / 1000,
        reserve_t=ship.reserve_milli / 1000,
        pending_t=ship.pending_fuel_milli / 1000,
        max_quantity_t=int(constraints.get("max_quantity_t", 0)),
    )
    if qty == 0:
        return None
    price = int(constraints.get("unit_price_cent_per_t") or view.fuel_price_cent_per_t or 0)
    return Proposal(
        ship_id=ship.ship_id,
        proposed_by=ROLE,
        action=buy_fuel(qty),
        rationale=(
            f"Viagem restante de {ship.remaining_nm_milli / 1000:.0f} nm a {CRUISE_KN:.0f} kn exige cerca de "
            f"{need_t:.1f} t; tanque {ship.fuel_milli / 1000:.1f} t, reserva {ship.reserve_milli / 1000:.0f} t. "
            f"Compra de {qty} t a D$ {price / 100:,.0f}/t."
        ),
        priority=10,
        tags=["fuel"],
    )
