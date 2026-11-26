"""Pacote de testes. Coloca src/ no caminho de importação (sem instalar o pacote)."""
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
