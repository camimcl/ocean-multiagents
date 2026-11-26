"""Agente de navegação: rota, velocidade, HOLD e REPAIR. Responsável: Matheus.

Versão inicial = política de referência do pacote (round-package/baseline/policy.json, 97,68 pts):
- rota direta; cruzeiro de 14 kn;
- tempestade E01 + navio no trecho exposto: velocidade segura (12 kn direta / 15 protegida);
- pane E04: HOLD até parar, depois REPAIR, depois volta ao cruzeiro.
Regra de ouro: decidir por ESTADO e EVENTOS, nunca por número de tick fixo.
"""
from __future__ import annotations

from ..contract import Proposal, hold, repair, set_speed
from ..pack import ShipView, TurnView
from ..tools import navigation as nav

ROLE = "navigation"
CRUISE_CENTI = 1400
FAULT_ID = "E04_ENGINE_FAULT"
MOVING_STATES = ("UNDERWAY",)
DEPARTURE_STATES = ("AT_ORIGIN", "AT_BUNKER_STATION", "HOLDING")


def propose(view: TurnView) -> list[Proposal]:
    proposals: list[Proposal] = []
    for ship in view.ships.values():
        proposal = _propose_for_ship(view, ship)
        if proposal is not None:
            proposals.append(proposal)
    return proposals


def desired_speed_centi(view: TurnView, ship: ShipView) -> tuple[int, str]:
    """Velocidade desejada agora e o motivo. Ponto principal de otimização (slow steaming)."""
    target = min(CRUISE_CENTI, ship.limit_centi)
    reason = f"cruzeiro de {target / 100:.2f} kn"
    if view.storm_active() and ship.in_exposed_segment:
        safe = nav.storm_safe_speed_centi(ship.route_id)
        if safe < target:
            return safe, (
                f"tempestade E01 no trecho exposto da rota {ship.route_id}: velocidade segura {safe / 100:.2f} kn"
            )
    # TODO (Matheus): slow steaming usando nav.min_speed_for_deadline_centi e o consumo cúbico.
    return target, reason


def _propose_for_ship(view: TurnView, ship: ShipView) -> Proposal | None:
    # 1) Pane de motor: segurar o navio para poder reparar.
    if ship.e04_active and ship.state in MOVING_STATES and ship.can("HOLD"):
        return Proposal(ship.ship_id, ROLE, hold(FAULT_ID),
                        "Pane E04 ativa: reduzir até parar para iniciar o reparo antes do agravamento E05.",
                        priority=1, tags=["E04"])
    if ship.e04_active and ship.stopped and ship.can("REPAIR"):
        return Proposal(ship.ship_id, ROLE, repair(FAULT_ID),
                        "Navio parado com pane E04 ativa: iniciar reparo de 12 ticks.",
                        priority=1, tags=["E04"])

    # 2) Velocidade (partida, tempestade, retomada após reparo/abastecimento).
    if not ship.can("SET_SPEED") or ship.pending_fuel_milli > 0:
        return None
    if ship.state not in MOVING_STATES + DEPARTURE_STATES or ship.e04_active:
        return None
    target, reason = desired_speed_centi(view, ship)
    if target == ship.target_centi:
        return None  # nada mudou: não repetir comando (evita churn)
    return Proposal(ship.ship_id, ROLE, set_speed(target), f"Ajuste de velocidade: {reason}.",
                    priority=20 if view.storm_active() else 30, tags=["speed"])
