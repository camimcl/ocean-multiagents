# 6. Avaliação dos agentes

Como cada turno é "pacote entra, decisão sai", os agentes são uma função testável. Três camadas:

## 6.1 Testes de unidade (`tests/`, a cada mudança)
- Regras isoladas com pacotes sintéticos (`tests/fakes.py`): "tempestade + trecho exposto → 12 kn", "pane E04 → HOLD e depois REPAIR", "veto se a ação não está em `allowed_actions_now`".
- **Regressão com pacotes reais:** copiar pacotes interessantes de `runs/` para `tests/fixtures/` e fixar a decisão esperada (gabarito). Exemplos: tick 0; início da tempestade; tick 288 (pane).
- Rodar: `python -m pytest`.

## 6.2 Métricas determinísticas (`evals/metricas.py`, a cada rodada)
| Métrica | Bom valor | Por quê |
|---|---|---|
| Taxa de aceitação (`decisoes_aceitas / decisoes_enviadas`) | perto de 100% (fora vetos) | Comando rejeitado tira ponto de Segurança |
| Vetos | ≥ 1, todos justificados | Mostra governança real |
| Folga mínima de combustível sobre a reserva, por navio | > 0 sempre | Abaixo de 0 zera a Segurança |
| Reação a eventos (`acted` ≤ `due`) | `on_time: true` | Nota de resiliência |
| `score_final` e `hard_gates` | subir / vazio | Resultado oficial |

Comparar sempre duas execuções em conformance: a anterior e a nova.

## 6.3 Qualidade do raciocínio com DeepEval (opcional, fim do projeto)
Instale `deepeval` e use as execuções salvas. Exemplo de métrica com LLM como juiz:
```python
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

fidelidade = GEval(
    name="Justificativa fiel ao pacote",
    criteria="A justificativa cita apenas números presentes no contexto e é coerente com a ação.",
    evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.CONTEXT],
)
caso = LLMTestCase(
    input=str(decisao["action"]),
    actual_output=decisao["proposal_rationale"],
    context=[json.dumps(pacote["ships"][decisao["ship_id"]]["operational_state"])],
)
fidelidade.measure(caso)
```
- Métricas próprias determinísticas também podem herdar de `BaseMetric` do DeepEval, para aparecer no mesmo relatório.
- O juiz gasta chamadas de LLM: rode só nas execuções finais.

## 6.4 "Como deveriam agir × como agiram"
Para cada evento, a tabela de gabarito (docs/01, seção 1.4) diz a reação esperada. O `metricas.py` mostra quando cada navio reagiu. Divergências viram entrada no diário e, se for erro, teste de regressão.
