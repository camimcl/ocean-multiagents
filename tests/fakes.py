"""Pacotes de turno sintéticos, no mesmo formato de GET /api/v1/turn/pack (campos usados pelos agentes).

Quando a equipe tiver pacotes reais salvos em runs/, copie os mais interessantes para
tests/fixtures/ e teste contra eles também.
"""
from __future__ import annotations

import copy
from typing import Any

SPEED = {"action": "SET_SPEED", "constraints": {"min_speed_kn": "0.00", "max_speed_kn": "18.00",
                                                 "active_limit_speed_kn": "18.00", "step_kn": "0.50"}}


def ship(**over: Any) -> dict[str, Any]:
    base = {
        "operational_state": {
            "ship_state": "AT_ORIGIN", "route_id": "direct", "effective_speed_kn": "0.00",
            "target_speed_kn": "0.00", "active_limit_speed_kn": "18.00", "fuel_milli": 60_000,
            "reserve_min_milli": 33_000, "fuel_capacity_milli": 140_000, "pending_fuel_milli": 0,
            "e04_active": False, "state_age_ticks": 0,
        },
        "route_and_contract": {
            "remaining_nm_milli": 700_000, "ticks_until_deadline": 390, "in_exposed_segment_now": False,
            "c14_t_per_h": "1.20", "hotel_t_per_h": "0.10",
        },
        "allowed_actions_now": [
            copy.deepcopy(SPEED),
            {"action": "SET_ROUTE", "constraints": {"route_id": ["direct", "protected"]}},
            {"action": "BUY_FUEL", "constraints": {"max_quantity_t": 80, "multiple_of_t": 5,
                                                    "unit_price_cent_per_t": 61_000}},
        ],
        "blocked_actions_reasons": {"HOLD": "Permitido apenas em UNDERWAY/HOLDING."},
    }
    for key, value in over.items():
        section = "route_and_contract" if key in base["route_and_contract"] else "operational_state"
        if key in ("allowed_actions_now", "blocked_actions_reasons"):
            base[key] = value
        else:
            base[section][key] = value
    return base


def underway(**over: Any) -> dict[str, Any]:
    allowed = [copy.deepcopy(SPEED), {"action": "HOLD", "constraints": {}}]
    params = dict(ship_state="UNDERWAY", effective_speed_kn="14.00", target_speed_kn="14.00",
                  fuel_milli=90_000, remaining_nm_milli=400_000, allowed_actions_now=allowed,
                  blocked_actions_reasons={"BUY_FUEL": "Navio em movimento."})
    params.update(over)
    return ship(**params)


def pack(tick: int = 0, ships: dict[str, dict[str, Any]] | None = None, events: list[dict[str, Any]] | None = None,
         available_cent: int = 50_000_000) -> dict[str, Any]:
    all_ships = {sid: ship() for sid in ("S1-FAROL", "S2-MARE", "S3-CORAL", "S4-ATLAS")}
    all_ships.update(ships or {})
    return {
        "meta": {"current_tick": tick, "stop_reasons": [], "round_completed": False,
                 "governance_progress": {"credited_chains": 0}},
        "economy": {"available_cent": available_cent, "origin_fuel_price_cent_per_t": 61_000},
        "active_events": events or [],
        "ships": all_ships,
    }


def storm() -> dict[str, Any]:
    return {"event_code": "E01_STORM", "is_currently_active": True, "safe_action_due_tick": 126,
            "affected_logical_ships": ["S1-FAROL", "S2-MARE", "S3-CORAL", "S4-ATLAS"]}
