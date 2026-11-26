"""Modo automático: joga a rodada inteira pela API e salva tudo em runs/.

Uso:
  python scripts/jogar_rodada.py --reset --label baseline        # nova rodada desde o tick 0
  python scripts/jogar_rodada.py                                  # continua a rodada atual
ATENÇÃO: --reset apaga a rodada em andamento no servidor. Combine com a equipe antes.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ocean_turnos.client import TurnClient  # noqa: E402
from ocean_turnos.config import Settings  # noqa: E402
from ocean_turnos.runner import play_round  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--reset", action="store_true", help="reinicia a rodada e configura os 4 agentes")
    parser.add_argument("--label", default="", help="nome curto da execução (vai no nome da pasta em runs/)")
    args = parser.parse_args()

    settings = Settings.from_env()
    print(f"Servidor: {settings.base_url} | modo: {settings.scenario_mode} | LLM: {settings.llm_enabled}")
    with TurnClient(settings) as client:
        run_dir = play_round(client, settings, reset=args.reset, label=args.label)
    print(f"Execução salva em {run_dir}")
    print(f"Métricas: python evals/metricas.py {run_dir}")


if __name__ == "__main__":
    main()
