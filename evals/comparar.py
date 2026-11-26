"""Trava de regressão: uma execução só é aceita se não piorar o que já está em 100.

Uso:
  python evals/comparar.py runs/<execucao>                          # contra a referência do pacote
  python evals/comparar.py runs/<execucao> results/<baseline-equipe>  # contra a baseline da equipe também

Regras (docs/03, "Critérios imutáveis"):
  1. hard_gates vazio e rank_eligible verdadeiro;
  2. toda dimensão que está em 100 na referência continua em 100.0000;
  3. Economia >= referência (e >= baseline da equipe, se informada);
  4. score_final >= o maior dos valores de referência informados.
Sai com código 1 se alguma regra falhar (pode ser usado no CI e antes de abrir PR).
"""
from __future__ import annotations

import json
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

REFERENCIA = Path(__file__).with_name("baseline_referencia.json")


def _load_summary(path: Path) -> dict[str, Any]:
    target = path / "resumo.json" if path.is_dir() else path
    return json.loads(target.read_text(encoding="utf-8"))


def check(run: dict[str, Any], *refs: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    if run.get("hard_gates"):
        problems.append(f"hard_gates acionados: {run['hard_gates']}")
    if run.get("rank_eligible") is False:
        problems.append("rank_eligible = false")
    dims = {k: Decimal(str(v)) for k, v in (run.get("dimensoes") or {}).items() if v is not None}
    if not dims:
        return problems + ["execução sem 'dimensoes' no resumo (rode de novo com o runner atual)"]
    for ref in refs:
        for name, value in ref["dimensoes"].items():
            ref_value = Decimal(str(value))
            got = dims.get(name)
            if got is None:
                problems.append(f"{name}: ausente na execução")
            elif ref_value == Decimal("100") and got < ref_value:
                problems.append(f"{name}: caiu de 100 para {got} (critério imutável)")
            elif name == "economy" and got < ref_value:
                problems.append(f"economy: {got} abaixo da referência {ref_value}")
        if Decimal(str(run.get("score_final") or 0)) < Decimal(str(ref["score_final"])):
            problems.append(f"score_final {run.get('score_final')} abaixo da referência {ref['score_final']}")
    return problems


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    run = _load_summary(Path(sys.argv[1]))
    refs = [json.loads(REFERENCIA.read_text(encoding="utf-8"))]
    refs += [_load_summary(Path(p)) for p in sys.argv[2:]]
    problems = check(run, *refs)
    print(json.dumps({"score_final": run.get("score_final"), "dimensoes": run.get("dimensoes")}, indent=2))
    if problems:
        print("\nREPROVADO:")
        for p in problems:
            print(f"  - {p}")
        raise SystemExit(1)
    print("\nAPROVADO: nenhum critério imutável piorou e a Economia não caiu.")


if __name__ == "__main__":
    main()
