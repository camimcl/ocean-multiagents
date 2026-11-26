"""Métricas determinísticas de uma execução salva em runs/. Responsável: Rafaela.

Uso:  python evals/metricas.py runs/20261126-140000-baseline

Mede "como os agentes agiram" a partir dos arquivos da rodada, sem chamar o servidor:
- taxa de aceitação das decisões e quantidade de vetos;
- erros de validação devolvidos pelo servidor (devem ser zero);
- folga mínima de combustível sobre a reserva, por navio (nunca pode ficar negativa);
- tempo de reação a eventos: tick da 1ª decisão no navio afetado x safe_action_due_tick;
- cadeias creditadas e nota final.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def compute(run_dir: Path) -> dict[str, Any]:
    packs = sorted(run_dir.glob("turno_*_pack.json"))
    decisions = sorted(run_dir.glob("turno_*_decisao.json"))
    reports = sorted(run_dir.glob("turno_*_relatorio.json"))

    submitted = committed = vetoed = 0
    for rep in map(load, reports):
        submitted += rep.get("decisions_submitted", 0)
        committed += rep.get("decisions_committed", 0)
        vetoed += rep.get("decisions_vetoed", 0)

    min_margin: dict[str, float] = {}
    first_action_tick: dict[str, dict[str, int]] = {}  # evento -> navio -> tick
    events_due: dict[str, tuple[int, list[str]]] = {}
    for pack_path, dec_path in zip(packs, decisions, strict=True):
        pack, dec = load(pack_path), load(dec_path)
        tick = pack["meta"]["current_tick"]
        for sid, ship in pack["ships"].items():
            op = ship["operational_state"]
            margin = (op["fuel_milli"] - op["reserve_min_milli"]) / 1000
            min_margin[sid] = min(min_margin.get(sid, margin), margin)
        for ev in pack.get("active_events", []):
            if ev.get("safe_action_due_tick") is not None:
                events_due[ev["event_code"]] = (ev["safe_action_due_tick"], ev.get("affected_logical_ships", []))
        for d in dec["decisions"]:
            for code, (_, ships) in events_due.items():
                if d["ship_id"] in ships and d["review_result"] == "approved":
                    first_action_tick.setdefault(code, {}).setdefault(d["ship_id"], tick)

    reactions = {
        code: {
            "due": due,
            "acted": (acted := first_action_tick.get(code, {})),
            "on_time": bool(acted) and all(t <= due for t in acted.values()),
        }
        for code, (due, _) in events_due.items()
    }
    summary_path = run_dir / "resumo.json"
    summary = load(summary_path) if summary_path.exists() else {}
    return {
        "turnos": len(reports),
        "decisoes_enviadas": submitted,
        "decisoes_aceitas": committed,
        "vetos": vetoed,
        "taxa_aceitacao": round(committed / submitted, 3) if submitted else None,
        "folga_minima_combustivel_t": {k: round(v, 2) for k, v in min_margin.items()},
        "reacao_a_eventos": reactions,
        "score_final": summary.get("score_final"),
        "hard_gates": summary.get("hard_gates"),
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    print(json.dumps(compute(Path(sys.argv[1])), ensure_ascii=False, indent=2))
