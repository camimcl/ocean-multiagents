# 5. Cronograma até a entrega (sexta)

| Sessão | Quando | Meta da equipe | Saída |
|---|---|---|---|
| S0 | Quinta, manhã (1 h) | Todos com o projeto rodando e 1 turno feito à mão | `pytest` verde em todas as máquinas |
| S1 | Quinta, tarde | **Linha de base**: rodada completa em conformance com a política inicial e com o exemplo do professor | Nota baseline no diário |
| S2 | Quinta, noite | Primeiras melhorias (slow steaming, margem de combustível, vetos novos), uma por PR | 2 a 4 PRs com antes/depois |
| S3 | Sexta, manhã | Consolidar a melhor versão; rodada com LLM; primeira rodada **official** | Nota official, `rank_eligible = true` |
| S4 | Sexta, tarde | Congelar o código, rodada final, documentação e apresentação | `results/final_result.json`, diário, README, slides |

## Marcos de controle
- **Fim de S1:** temos nota? `hard_gates` vazio? ≥ 10 cadeias? Se não, todo mundo para e corrige isso primeiro.
- **Fim de S2:** a melhor nota em conformance ≥ a do baseline.
- **Sexta 12h:** código congelado. À tarde, só documentação e ensaio.

## Plano B
- Se a API der problema: modo manual pelo site com `scripts/decidir_arquivo.py` (baixa o JSON, gera a decisão, carrega no site).
- Se o LLM falhar ou acabar a cota: `LLM_ENABLED=false`. A rodada funciona igual, só com justificativas determinísticas.
- Se uma melhoria piorar a nota: reverter o PR e registrar no diário (também conta como aprendizado).
