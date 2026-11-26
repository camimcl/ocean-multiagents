"""Agente de segurança: revisa cada proposta e aprova ou veta. Responsável: Lídia.

Regra do projeto: o veto é decidido em CÓDIGO (determinístico). O LLM, se ligado, só
reescreve a justificativa. O revisor não usa a justificativa do propositor para decidir.
"""
from __future__ import annotations

from ..contract import Proposal, Review, speed_centi, validate_action
from ..pack import ShipView, TurnView
from ..tools import fuel
from ..tools import navigation as nav

ROLE = "safety"


def review(proposal: Proposal, view: TurnView, reviewer: str = ROLE) -> Review:
    ship = view.ships[proposal.ship_id]
    action = proposal.action
    kind = action.get("type")

    def veto(code: str, why: str) -> Review:
        return Review(reviewer, False, f"VETO {code}: {why}", [code])

    if validate_action(action):
        return veto("INVALID_FORMAT", f"ação mal formada {validate_action(action)}")
    if not ship.can(kind):
        return veto("NOT_ALLOWED_NOW", ship.blocked.get(kind, f"{kind} não permitido no estado {ship.state}"))
    constraints = ship.allowed[kind]

    if kind == "SET_SPEED":
        target = speed_centi(action["speed_kn"])
        limit = speed_centi(constraints.get("active_limit_speed_kn", "18.00"))
        if target > limit:
            return veto("OVER_SPEED_LIMIT", f"{target / 100:.2f} kn acima do limite ativo {limit / 100:.2f} kn")
        if view.storm_active() and ship.in_exposed_segment and target > nav.storm_safe_speed_centi(ship.route_id):
            return veto("STORM_UNSAFE_SPEED", "acima da velocidade segura no trecho exposto durante a tempestade")
        if target > 0 and not _fuel_ok(ship, target):
            return veto("FUEL_RESERVE_RISK", "o combustível não cobre a viagem restante acima da reserva mínima")

    if kind == "BUY_FUEL":
        qty = action["quantity_t"]
        if qty > int(constraints.get("max_quantity_t", 0)):
            return veto("FUEL_LIMIT", f"{qty} t acima do máximo permitido agora ({constraints.get('max_quantity_t')} t)")

    return Review(reviewer, True, f"Aprovado: {kind} dentro das ações permitidas, limites e reserva de combustível.",
                  ["SAFETY_OK"])


def _fuel_ok(ship: ShipView, target_centi: int) -> bool:
    """Combustível + pendente cobre a viagem restante e ainda sobra a reserva? Sem dados de rota, aprova."""
    if ship.remaining_nm_milli <= 0 or ship.c14_t_per_h <= 0:
        return True
    need = fuel.fuel_needed_t(ship.remaining_nm_milli / 1000, target_centi / 100,
                              ship.c14_t_per_h, ship.hotel_t_per_h, weather_margin=1.0)
    return (ship.fuel_milli + ship.pending_fuel_milli) / 1000 - need >= ship.reserve_milli / 1000
