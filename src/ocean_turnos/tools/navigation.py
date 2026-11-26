"""Cálculos de navegação: velocidade segura, ETA e velocidade mínima para cumprir o prazo."""
from __future__ import annotations

import math

TICKS_PER_HOUR = 6
UNLOADING_TICKS = 12
STORM_SAFE_CENTI = {"direct": 1200, "protected": 1500}


def storm_safe_speed_centi(route_id: str) -> int:
    return STORM_SAFE_CENTI.get(route_id, 1200)


def eta_ticks(remaining_nm: float, speed_kn: float) -> int:
    if speed_kn <= 0:
        return 10**6
    return math.ceil(remaining_nm / (speed_kn / TICKS_PER_HOUR))


def min_speed_for_deadline_centi(remaining_nm: float, ticks_until_deadline: int, slack_ticks: int = 12) -> int:
    """Menor velocidade (centésimos, passo 0.50) que chega com descarga concluída e folga."""
    usable = ticks_until_deadline - UNLOADING_TICKS - slack_ticks
    if remaining_nm <= 0:
        return 0
    if usable <= 0:
        return 1800
    needed_kn = remaining_nm / (usable / TICKS_PER_HOUR)
    centi = math.ceil(needed_kn * 100 / 50) * 50
    return max(0, min(1800, centi))
