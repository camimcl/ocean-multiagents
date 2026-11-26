import unittest

from ocean_turnos.llm import justificativas
from ocean_turnos.llm.provider import resolve


class TestProvider(unittest.TestCase):
    def test_padrao_e_groq(self):
        s = resolve({})
        self.assertEqual(
            (s.provider, s.base_url, s.api_key_var),
            ("groq", "https://api.groq.com/openai/v1", "GROQ_API_KEY"),
        )

    def test_anthropic_sem_base_url(self):
        s = resolve({"LLM_PROVIDER": "anthropic"})
        self.assertIsNone(s.base_url)
        self.assertEqual(s.api_key_var, "ANTHROPIC_API_KEY")

    def test_modelo_e_url_sobrescritos(self):
        s = resolve({"LLM_PROVIDER": "openrouter", "LLM_MODEL": "x/y", "LLM_BASE_URL": "http://proxy"})
        self.assertEqual((s.model, s.base_url), ("x/y", "http://proxy"))

    def test_provedor_invalido(self):
        with self.assertRaises(ValueError):
            resolve({"LLM_PROVIDER": "grok"})

    def test_llm_desligado_nao_altera_texto(self):
        decisions = [{"proposal_rationale": "a", "review_rationale": "b"}]
        self.assertIs(justificativas.rewrite(decisions, enabled=False), decisions)

    def test_falha_do_llm_mantem_texto(self):
        decisions = [{"proposed_by": "navigation", "reviewed_by": "safety", "action": {},
                      "proposal_rationale": "a", "review_rationale": "b"}]
        # sem chave/biblioteca, o LLM falha e o texto determinístico continua
        self.assertEqual(justificativas.rewrite(decisions, enabled=True), decisions)


if __name__ == "__main__":
    unittest.main()
