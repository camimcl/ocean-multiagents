"""Joga uma rodada inteira e guarda tudo em runs/<data-hora>/ para avaliação. Responsável: Rafaela.

Arquivos por turno: turno_NN_pack.json, turno_NN_decisao.json, turno_NN_relatorio.json.
No fim: resultado_final.json e resumo.json.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from .client import TurnClient
from .config import Settings
from .graph import deliberate

MAX_TURNS = 80  # trava contra laço infinito (uma rodada normal leva de 10 a 18 turnos)


def _save(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def play_round(client: TurnClient, settings: Settings, reset: bool, label: str = "") -> Path:
    run_dir = settings.runs_dir / (time.strftime("%Y%m%d-%H%M%S") + (f"-{label}" if label else ""))
    run_dir.mkdir(parents=True, exist_ok=True)

    if reset:
        _save(run_dir / "setup_agents.json", client.setup_agents(reset=True))
    pack = client.pack()
    turn = 0
    while not pack["meta"]["round_completed"]:
        turn += 1
        if turn > MAX_TURNS:
            raise RuntimeError(f"Mais de {MAX_TURNS} turnos: confira stop_on_events/advance_ticks")
        decision = deliberate(pack, settings.advance_ticks_max, settings.llm_enabled)
        _save(run_dir / f"turno_{turn:02d}_pack.json", pack)
        _save(run_dir / f"turno_{turn:02d}_decisao.json", decision)
        response = client.submit(decision)
        report = response["execution_report"]
        _save(run_dir / f"turno_{turn:02d}_relatorio.json", report)
        print(f"[turno {turn:02d}] tick {report['from_tick']:03d} -> {report['to_tick']:03d} | "
              f"{report['decisions_committed']} aceitas, {report['decisions_vetoed']} vetadas | "
              f"{'; '.join(report.get('stop_reasons') or [])[:160]}")
        pack = response["next_pack"]

    final = client.finalize()
    _save(run_dir / "resultado_final.json", final)
    payload = final.get("result_envelope", {}).get("payload", {})
    summary = {
        "turnos": turn,
        "score_final": payload.get("score_final"),
        "rank_eligible": payload.get("rank_eligible"),
        "hard_gates": payload.get("hard_gates"),
        "multi_agent_proof": payload.get("multi_agent_proof"),
        "scenario_mode": settings.scenario_mode,
    }
    _save(run_dir / "resumo.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return run_dir
