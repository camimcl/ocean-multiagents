"""Leitura do pacote do turno (GET /api/v1/turn/pack) em objetos fáceis de usar.

Os agentes NÃO leem o JSON bruto diretamente: usam ShipView e TurnView. Se o servidor
mudar um nome de campo, corrigimos só aqui.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .contract import SHIPS, speed_centi


@dataclass(frozen=True)
class ShipView:
    ship_id: str
    state: str
    route_id: str
    speed_centi: int  # velocidade efetiva
    target_centi: int  # velocidade pedida
    limit_centi: int  # limite ativo (cai na pane E04)
    fuel_milli: int
    reserve_milli: int
    capacity_milli: int
    pending_fuel_milli: int
    e04_active: bool
    state_age_ticks: int
    remaining_nm_milli: int
    ticks_until_deadline: int
    in_exposed_segment: bool
    c14_t_per_h: float
    hotel_t_per_h: float
    allowed: dict[str, dict[str, Any]]  # ação -> constraints
    blocked: dict[str, str]  # ação -> motivo

    @property
    def stopped(self) -> bool:
        return self.speed_centi == 0

    def can(self, action_type: str) -> bool:
        return action_type in self.allowed


@dataclass(frozen=True)
class TurnView:
    tick: int
    stop_reasons: list[str]
    available_cent: int
    fuel_price_cent_per_t: int | None
    active_event_codes: set[str]
    ships: dict[str, ShipView]
    credited_chains: int
    round_completed: bool
    raw: dict[str, Any]

    def storm_active(self) -> bool:
        return any(code.startswith("E01_STORM") and "FORECAST" not in code for code in self.active_event_codes)


def _allowed_map(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {(a.get("action") or a.get("type")): a.get("constraints", {}) for a in items}


def parse_ship(ship_id: str, data: dict[str, Any]) -> ShipView:
    op = data["operational_state"]
    rc = data["route_and_contract"]
    return ShipView(
        ship_id=ship_id,
        state=op["ship_state"],
        route_id=op["route_id"],
        speed_centi=speed_centi(op["effective_speed_kn"]),
        target_centi=speed_centi(op["target_speed_kn"]),
        limit_centi=speed_centi(op["active_limit_speed_kn"]),
        fuel_milli=int(op["fuel_milli"]),
        reserve_milli=int(op["reserve_min_milli"]),
        capacity_milli=int(op["fuel_capacity_milli"]),
        pending_fuel_milli=int(op.get("pending_fuel_milli", 0)),
        e04_active=bool(op.get("e04_active", False)),
        state_age_ticks=int(op.get("state_age_ticks", 0)),
        remaining_nm_milli=int(rc["remaining_nm_milli"]),
        ticks_until_deadline=int(rc["ticks_until_deadline"]),
        in_exposed_segment=bool(rc.get("in_exposed_segment_now", False)),
        c14_t_per_h=float(rc.get("c14_t_per_h", 0)),
        hotel_t_per_h=float(rc.get("hotel_t_per_h", 0)),
        allowed=_allowed_map(data.get("allowed_actions_now", [])),
        blocked=dict(data.get("blocked_actions_reasons", {})),
    )


def parse_pack(pack: dict[str, Any]) -> TurnView:
    meta = pack["meta"]
    economy = pack["economy"]
    events = {
        str(e.get("event_code"))
        for e in pack.get("active_events", [])
        if e.get("is_currently_active") or str(e.get("event_code", "")).endswith("_FORECAST")
    }
    return TurnView(
        tick=int(meta["current_tick"]),
        stop_reasons=list(meta.get("stop_reasons", [])),
        available_cent=int(economy["available_cent"]),
        fuel_price_cent_per_t=economy.get("origin_fuel_price_cent_per_t"),
        active_event_codes=events,
        ships={sid: parse_ship(sid, pack["ships"][sid]) for sid in SHIPS},
        credited_chains=int(meta.get("governance_progress", {}).get("credited_chains", 0)),
        round_completed=bool(meta.get("round_completed", False)),
        raw=pack,
    )
