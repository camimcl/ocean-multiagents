import importlib.util
import json
import unittest
from pathlib import Path

_COMPARAR = Path(__file__).resolve().parents[1] / "evals" / "comparar.py"
_spec = importlib.util.spec_from_file_location("comparar", _COMPARAR)
comparar = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(comparar)
REF = json.loads(comparar.REFERENCIA.read_text(encoding="utf-8"))


def run(**dims):
    base = {"safety": "100.0000", "economy": "92.0000", "service": "100.0000",
            "engineering_resilience": "100.0000", "observability_governance": "100.0000"}
    base.update(dims)
    return {"score_final": "98.1000", "hard_gates": [], "rank_eligible": True, "dimensoes": base}


class TestComparar(unittest.TestCase):
    def test_aprova_melhora_de_economia(self):
        self.assertEqual(comparar.check(run(), REF), [])

    def test_reprova_queda_em_dimensao_100(self):
        problems = comparar.check(run(service="99.5000"), REF)
        self.assertTrue(any("service" in p for p in problems))

    def test_reprova_economia_abaixo(self):
        problems = comparar.check(run(economy="90.0000"), REF)
        self.assertTrue(any("economy" in p for p in problems))

    def test_reprova_hard_gate(self):
        r = run()
        r["hard_gates"] = ["HG_SINGLE_AGENT"]
        self.assertTrue(comparar.check(r, REF))


if __name__ == "__main__":
    unittest.main()
