"""Modo manual: lê um pacote baixado do site e gera o JSON de decisão para carregar no site.

Uso:
  python scripts/decidir_arquivo.py --input ocean_turno_tick_000.json --output decisao_turno.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ocean_turnos.config import Settings  # noqa: E402
from ocean_turnos.graph import deliberate  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("decisao_turno.json"))
    args = parser.parse_args()

    settings = Settings.from_env()
    pack = json.loads(args.input.read_text(encoding="utf-8"))
    decision = deliberate(pack, settings.advance_ticks_max, settings.llm_enabled)
    args.output.write_text(json.dumps(decision, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"tick {pack['meta']['current_tick']}: {len(decision['decisions'])} decisão(ões) em {args.output}")
    for d in decision["decisions"]:
        print(f"  {d['ship_id']:9s} {d['action']}  {d['proposed_by']} -> {d['reviewed_by']}: {d['review_result']}")


if __name__ == "__main__":
    main()
