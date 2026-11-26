"""Cálculos de combustível. Ferramentas determinísticas: o LLM pode chamá-las, nunca refazê-las.

Fórmula do servidor (server/ocean_server/sim_phases.py, compute_step_physics), por tick de 10 min:
    t/tick = (hotel + c14 * (v/14)^3 * carga * clima * avaria) / 6
    carga  = 1 + 0,15 * (carga a bordo / capacidade)  -> até 1,15 com o navio cheio
    clima  = 1,35 (tempestade, rota direta exposta) | 1,10 (protegida exposta) | 1
    avaria = 1,25 (E04) | 1,50 (E05) | 1
"""
from __future__ import annotations

import math

TICKS_PER_HOUR = 6
FULL_LOAD_FACTOR = 1.15


def burn_t_per_tick(c14_t_per_h: float, hotel_t_per_h: float, speed_kn: float,
                    load_factor: float = FULL_LOAD_FACTOR, weather: float = 1.0, damage: float = 1.0) -> float:
    if speed_kn <= 0:
        return hotel_t_per_h * damage / TICKS_PER_HOUR
    return (hotel_t_per_h + c14_t_per_h * (speed_kn / 14) ** 3 * load_factor * weather * damage) / TICKS_PER_HOUR


def ticks_to_cover(distance_nm: float, speed_kn: float) -> int:
    if speed_kn <= 0:
        raise ValueError("velocidade precisa ser maior que zero")
    return math.ceil(distance_nm / (speed_kn / TICKS_PER_HOUR))


def fuel_needed_t(distance_nm: float, speed_kn: float, c14_t_per_h: float, hotel_t_per_h: float,
                  weather_margin: float = 1.10) -> float:
    """Combustível para percorrer a distância a velocidade constante, com margem para clima."""
    ticks = ticks_to_cover(distance_nm, speed_kn)
    return ticks * burn_t_per_tick(c14_t_per_h, hotel_t_per_h, speed_kn) * weather_margin


def purchase_to_cover(need_t: float, fuel_t: float, reserve_t: float, pending_t: float,
                      max_quantity_t: int, safety_buffer_t: float = 5.0) -> int:
    """Quantas toneladas comprar (múltiplo de 5, limitado pelo servidor). 0 = não comprar."""
    missing = need_t + reserve_t + safety_buffer_t - fuel_t - pending_t
    if missing <= 0:
        return 0
    qty = int(math.ceil(missing / 5.0) * 5)
    qty = min(qty, max_quantity_t - max_quantity_t % 5)
    return qty if qty >= 5 else 0
