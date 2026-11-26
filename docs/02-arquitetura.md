# 2. Arquitetura

## 2.1 Fluxo de um turno
```
pacote ──► pack.parse_pack ──► TurnView (dados já convertidos: centi, milli, ações permitidas)
                                  │
             ┌────────────────────┼────────────────────┐
             ▼                                          ▼
     economy.propose                            navigation.propose
     (BUY_FUEL)                                 (SET_SPEED, HOLD, REPAIR)
             └───────────── Proposal ───────────────────┘
                                  ▼
                     coordinator.decide
                     - ordena por prioridade
                     - máx. 2 decisões por navio
                     - não manda velocidade junto com abastecimento
                     - safety.review(proposta)  → Review (aprovado/veto + motivo)
                     - desconta o caixa de cada compra aprovada
                                  ▼
                     llm.justificativas.rewrite (opcional, hoje só texto)
                                  ▼
                     contract.validate_decision_doc ──► decisão (JSON)
```

## 2.2 Princípios
1. **O modelo propõe, o código confere.** Contas (combustível, ETA, prazo) e vetos são código. Hoje o LLM só escreve justificativas; no M4 ele passa a **escolher entre opções já validadas** (seção 2.5).
2. **Agentes não leem o JSON bruto.** Usam `ShipView`/`TurnView`. Se o servidor mudar um campo, corrige-se em `pack.py`.
3. **Funções puras.** Cada agente é `propose(view) -> list[Proposal]` ou `review(proposal, view) -> Review`. Fácil de testar sem servidor.
4. **Decidir por estado, não por tick.** No official os eventos mudam de horário.
5. **Não repetir comando.** Se a velocidade pedida já é a atual, não propor de novo (evita churn).
6. **Vetos também saem no JSON.** Contam como governança e ficam no ledger.

## 2.3 Contratos entre as peças
```python
Proposal(ship_id, proposed_by, action, rationale, priority=50, tags=[])
Review(reviewed_by, approved, rationale, codes=[])
economy.propose(view) -> list[Proposal]
navigation.propose(view) -> list[Proposal]
safety.review(proposal, view, reviewer) -> Review
coordinator.decide(view, advance_ticks_max) -> (decisão, [(Proposal, Review)])
graph.deliberate(pack, advance_ticks_max, llm_enabled) -> decisão
```
Ações são criadas só pelos construtores de `contract.py` (`set_speed`, `buy_fuel`, `hold`, `repair`, `set_route`).

## 2.4 LangGraph
`graph.build_graph()` monta o mesmo fluxo como `StateGraph` (`ler_turno → coordenar → justificar`). Serve para mostrar o grafo na apresentação e para crescer (por exemplo, um nó de navegação com LLM e ferramentas). O caminho oficial do código continua sendo `deliberate()`, que funciona sem LangGraph instalado.

## 2.5 Evolução planejada: agente LLM com ferramentas (módulo M4)
| Etapa | Quem decide a ação | Papel do LLM |
|---|---|---|
| Hoje (M1) | Regras em código | Só reescreve justificativas (`LLM_ENABLED`) |
| M2 e M3 | Regras em código usando o simulador de custo (`tools/economia.py`) | Igual |
| M4 | **LLM de navegação**, escolhendo entre opções que as ferramentas calcularam (ex.: 12,5 / 13 / 13,5 kn com custo, prazo e reserva) | Chama as tools, decide e justifica (`LLM_DECIDE`) |

Regras do M4:
- O veto continua em código (`safety.review`). Proposta do LLM fora das regras é vetada.
- Se o LLM falhar, demorar ou propor algo vetado, entra a regra determinística (fallback).
- O LLM só é chamado para navios citados em `stop_reasons` ou com evento ativo, para caber na cota (cerca de 15 turnos por rodada).
- Provedor no `.env`: `LLM_PROVIDER=groq|openrouter|anthropic` (`llm/provider.py`). Temperatura 0.
