"""Cliente HTTP dos endpoints do Modo por Turnos."""
from __future__ import annotations

from typing import Any

import httpx

from .config import Settings
from .contract import validate_decision_doc


class TurnApiError(RuntimeError):
    def __init__(self, status_code: int, body: Any) -> None:
        super().__init__(f"HTTP {status_code}: {body}")
        self.status_code = status_code
        self.body = body


class TurnClient:
    def __init__(self, settings: Settings, http: httpx.Client | None = None) -> None:
        self.settings = settings
        self.http = http or httpx.Client(base_url=settings.base_url, timeout=settings.http_timeout_s)

    def close(self) -> None:
        self.http.close()

    def __enter__(self) -> "TurnClient":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def _check(self, resp: httpx.Response) -> dict[str, Any]:
        body = resp.json() if resp.content else {}
        if resp.status_code != 200:
            raise TurnApiError(resp.status_code, body)
        return body

    def setup_agents(self, reset: bool) -> dict[str, Any]:
        """Configura os 4 agentes. Com reset=True, reinicia a rodada no tick 0 (apaga a rodada atual!)."""
        payload: dict[str, Any] = {"reset": reset}
        if reset:
            payload["scenario_mode"] = self.settings.scenario_mode
        return self._check(self.http.post("/api/v1/turn/setup-agents", json=payload))

    def pack(self) -> dict[str, Any]:
        return self._check(self.http.get("/api/v1/turn/pack", params={"auto_open": "true"}))

    def submit(self, decision_doc: dict[str, Any]) -> dict[str, Any]:
        problems = validate_decision_doc(decision_doc)
        if problems:
            raise ValueError(f"Decisão inválida bloqueada antes do envio: {problems}")
        return self._check(self.http.post("/api/v1/turn/submit", json=decision_doc))

    def finalize(self) -> dict[str, Any]:
        return self._check(self.http.post("/api/v1/round/finalize", json={}))

    def result(self) -> dict[str, Any]:
        return self._check(self.http.get("/api/v1/result"))
