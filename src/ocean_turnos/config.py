"""Configurações lidas do ambiente ou do arquivo `.env` na raiz do repositório."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def load_dotenv(path: Path | None = None) -> None:
    """Carrega KEY=valor do .env sem sobrescrever variáveis já definidas."""
    target = path or REPO_ROOT / ".env"
    if not target.is_file():
        return
    for raw in target.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


@dataclass(frozen=True)
class Settings:
    base_url: str
    scenario_mode: str = "conformance"
    advance_ticks_max: int = 50
    http_timeout_s: float = 60.0
    llm_enabled: bool = False
    runs_dir: Path = REPO_ROOT / "runs"
    results_dir: Path = REPO_ROOT / "results"

    def __post_init__(self) -> None:
        if not self.base_url.startswith(("http://", "https://")):
            raise ValueError(f"OCEAN_BASE_URL inválida: {self.base_url!r}")
        if self.scenario_mode not in ("conformance", "official"):
            raise ValueError("OCEAN_SCENARIO_MODE deve ser 'conformance' ou 'official'")
        if not 1 <= self.advance_ticks_max <= 432:
            raise ValueError("OCEAN_ADVANCE_TICKS_MAX deve estar entre 1 e 432")

    @classmethod
    def from_env(cls) -> Settings:
        load_dotenv()
        return cls(
            base_url=os.getenv("OCEAN_BASE_URL", "http://127.0.0.1:8000").rstrip("/"),
            scenario_mode=os.getenv("OCEAN_SCENARIO_MODE", "conformance").strip(),
            advance_ticks_max=int(os.getenv("OCEAN_ADVANCE_TICKS_MAX", "50")),
            http_timeout_s=float(os.getenv("OCEAN_HTTP_TIMEOUT_S", "60")),
            llm_enabled=os.getenv("LLM_ENABLED", "false").strip().lower() == "true",
        )
